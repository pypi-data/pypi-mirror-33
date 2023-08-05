"""
Module to encompass various tools for the manipulation of feature-extracted MS data sets.
"""

import scipy
import os
import inspect
import numpy
import pandas
import re
import warnings
import numbers
from datetime import datetime
import logging
import copy
import networkx
from .._toolboxPath import toolboxPath
from ._dataset import Dataset
from ..utilities import rsd
from ..utilities._internal import _vcorrcoef
from ..utilities._getMetadataFromWatersRaw import getSampleMetadataFromWatersRawFiles
from ..enumerations import VariableType, DatasetLevel, AssayRole, SampleType
from ..utilities import removeTrailingColumnNumbering
from ..utilities._filters import blankFilter
from ..utilities.normalisation._normaliserABC import Normaliser


class MSDataset(Dataset):
	"""
	MSDataset(datapath, fileType='QI', sop='GenericMS', **kwargs)

	:py:class:`MSDataset` extends :py:class:`Dataset` to represent both peak-picked LC- or DI-MS datasets (discrete variables), and Continuum mode (spectral) DI-MS datasets.

	Objects can be initialised from a variety of common data formats, currently peak-picked data from Progenesis QI or XCMS, and targeted Biocrates datasets.

	* Progenesis QI
		QI import operates on csv files exported *via* the 'Export Compound Measurements' menu option in QI. Import requires the presence of both normalised and raw datasets, but will only import the raw meaturenents.

	* XCMS
		XCMS import operates on csv files, by default it expects 14 column of feature parameters, but this can be overriden with the ``noFeatureParams=`` keyword argument.

	* Biocrates
		Operates on spreadsheets exported from Biocrates MetIDQ. By default loads data from the sheet named 'Data Export', this may be overridden with the ``sheetName=`` argument, If the number of sample metadata columns differes from the default, this can be overridden with the ``noSampleParams=`` argument.
	"""

	def __init__(self, datapath, fileType='xcms', sop='GenericMS', **kwargs):
		"""
		Basic initialisation.
		"""

		super().__init__(sop=sop, **kwargs)
		self.corrExclusions = None
		self._correlationToDilution = numpy.array(None)
		try:
			self.Attributes['artifactualFilter'] = (self.Attributes['artifactualFilter'] == 'True')
		except:
			pass
		self._tempArtifactualLinkageMatrix = pandas.DataFrame(None)
		self._artifactualLinkageMatrix = pandas.DataFrame(None)
		self.Attributes['Raw Data Path'] = None
		self.Attributes['Feature Names'] = 'Feature Name'
		self.filePath, fileName = os.path.split(datapath)
		self.fileName, fileExtension = os.path.splitext(fileName)

		self.name = self.fileName

		# Load the QI output file
		fileType = fileType.lower()
		if fileType == 'qi':
			self._loadQIDataset(datapath)
			self.Attributes['FeatureExtractionSoftware'] = 'Progenesis QI'
			self.VariableType = VariableType.Discrete
		elif fileType == 'csv export':
			raise NotImplementedError
		elif fileType == 'xcms':
			self._loadXCMSDataset(datapath, **kwargs)
			self.Attributes['FeatureExtractionSoftware'] = 'XCMS'
			self.VariableType = VariableType.Discrete
		elif fileType == 'biocrates':
			self._loadBiocratesDataset(datapath, **kwargs)
			self.Attributes['FeatureExtractionSoftware'] = 'Biocrates'
			self.VariableType = VariableType.Discrete
		elif fileType == 'metaboscape':
			self._loadMetaboscapeDataset(datapath, **kwargs)
			self.Attributes['FeatureExtractionSoftware'] = 'Metaboscape'
			self.VariableType = VariableType.Discrete
		elif fileType == 'empty':
			# Lets us build an empty object for testing &c
			pass
		else:
			raise NotImplementedError

		self.Attributes['Log'].append([datetime.now(), '%s instance inited, with %d samples, %d features, from \%s\'' % (self.__class__.__name__, self.noSamples, self.noFeatures, datapath)])

	# When making a deepcopy, all artifactual linkage are reset
	def __deepcopy__(self, memo):
		cls = self.__class__
		result = cls.__new__(cls)
		memo[id(self)] = result
		for k, v in self.__dict__.items():
			# Check for pandas dataframe, and use the
			if isinstance(v, pandas.DataFrame):
				setattr(result, k, v.copy())
			else:
				setattr(result, k, copy.deepcopy(v, memo))
		result._tempArtifactualLinkageMatrix = pandas.DataFrame(None)
		result._artifactualLinkageMatrix = pandas.DataFrame(None)

		return(result)


	# Lazily calculate expensive operations
	@property
	def correlationToDilution(self):
		"""
		Returns the correlation of features to dilution as calculated on samples marked as 'Dilution Series' in :py:attr:`~Dataset.sampleMetadata`, with dilution expressed in 'Dilution'.

		:return: Vector of feature correlations to dilution
		:rtype: numpy.ndarray
		"""
		if self.corrExclusions is None:
			self.corrExclusions = copy.deepcopy(self.sampleMask)
			self.__corrExclusions = copy.deepcopy(self.corrExclusions)

		if not self._correlationToDilution.any():

			self._correlationToDilution = self.__correlateToDilution(method=self.Attributes['corrMethod'], exclusions=self.corrExclusions)

			self.__corrMethod = self.Attributes['corrMethod']
			self.__corrExclusions = self.corrExclusions

		elif (self.__corrMethod != self.Attributes['corrMethod']) | (numpy.array_equal(self.__corrExclusions, self.corrExclusions) == False):

			self._correlationToDilution = self.__correlateToDilution(method=self.Attributes['corrMethod'], exclusions=self.corrExclusions)

			self.__corrMethod = self.Attributes['corrMethod']
			self.__corrExclusions = copy.deepcopy(self.corrExclusions)

		return self._correlationToDilution


	@correlationToDilution.deleter
	def correlationToDilution(self):
		self._correlationToDilution = numpy.array(None)


	@property
	def artifactualLinkageMatrix(self):
		"""Gets overlapping artifactual features."""
		if self._artifactualLinkageMatrix.empty:
			self._artifactualLinkageMatrix = self.__generateArtifactualLinkageMatrix()

		return self._artifactualLinkageMatrix


	@artifactualLinkageMatrix.deleter
	def artifactualLinkageMatrix(self):
		self._artifactualLinkageMatrix = pandas.DataFrame(None)
		self._tempArtifactualLinkageMatrix = pandas.DataFrame(None)


	@property
	def rsdSP(self):
		"""
		Returns percentage :term:`relative standard deviations<RSD>` for each feature in the dataset, calculated on samples with the Assay Role :py:attr:`~nPYc.enumerations.AssayRole.PrecisionReference` and Sample Type :py:attr:`~nPYc.enumerations.SampleType.StudyPool` in :py:attr:`~Dataset.sampleMetadata`.

		:return: Vector of feature RSDs
		:rtype: numpy.ndarray
		"""
		# Check we have Study Reference samples defined
		if not ('AssayRole' in self.sampleMetadata.keys() or 'SampleType' in self.sampleMetadata.keys()):
			raise ValueError('Assay Roles and Sample Types must be defined to calculate RSDs.')
		if not sum(self.sampleMetadata['AssayRole'].values == AssayRole.PrecisionReference) > 1:
			raise ValueError('More than one precision reference is required to calculate RSDs.')

		mask = numpy.logical_and(self.sampleMetadata['AssayRole'].values == AssayRole.PrecisionReference,
								 self.sampleMetadata['SampleType'].values == SampleType.StudyPool)

		return rsd(self._intensityData[mask & self.sampleMask])


	def applyMasks(self):
		"""
		Permanently delete elements masked (those set to ``False``) in :py:attr:`~Dataset.sampleMask` and :py:attr:`~Dataset.featureMask`, from :py:attr:`~Dataset.featureMetadata`, :py:attr:`~Dataset.sampleMetadata`, and :py:attr:`~Dataset.intensityData`.

		Resets feature linkage matrix and feature correlations.
		"""
		changeFeature = sum(self.featureMask==False) != 0					# True if featuresMask has a feature set to False

		if changeFeature:
			if hasattr(self, 'fit'):
				self.fit = self.fit[:, self.featureMask]

		# if a change is made to the features, the whole artifactualLinkageMatrix must be updated (feature IDs change), else only correlation calculation
		super().applyMasks()																			# applyMasks
		if self.Attributes['artifactualFilter'] == True:
			if not self._artifactualLinkageMatrix.empty:
				if changeFeature:
					self._artifactualLinkageMatrix = self.__generateArtifactualLinkageMatrix()								# change features, recalculate all
				else:
					self._artifactualLinkageMatrix = self.__generateArtifactualLinkageMatrix(corrOnly=True)		# change samples, recalculate correlation only
		# Reset correlations
		del(self.correlationToDilution)


	def updateMasks(self, filterSamples=True, filterFeatures=True, sampleTypes=[SampleType.StudySample, SampleType.StudyPool], assayRoles=[AssayRole.Assay, AssayRole.PrecisionReference], correlationThreshold=None, rsdThreshold=None, varianceRatio=None, withArtifactualFiltering=None, deltaMzArtifactual=None, overlapThresholdArtifactual=None, corrThresholdArtifactual=None, blankThreshold=None, **kwargs):
		"""
		Update :py:attr:`~Dataset.sampleMask` and :py:attr:`~Dataset.featureMask` according to QC parameters.

		:py:meth:`updateMasks` sets :py:attr:`~Dataset.sampleMask` or :py:attr:`~Dataset.featureMask` to ``False`` for those items failing analytical criteria.

		.. note:: To avoid reintroducing items manually excluded, this method only ever sets items to ``False``, therefore if you wish to move from more stringent criteria to a less stringent set, you will need to reset the mask to all ``True`` using :py:meth:`~Dataset.initialiseMasks`.

		:param bool filterSamples: If ``False`` don't modify sampleMask
		:param bool filterFeatures: If ``False`` don't modify featureMask
		:param sampleTypes: List of types of samples to retain
		:type sampleTypes: SampleType
		:param assayRoles: List of assays roles to retain
		:type assayRoles: AssayRole
		:param correlationThreshold: Mask features with a correlation below this value. If ``None``, use the value from *Attributes['corrThreshold']*
		:type correlationThreshold: None or float
		:param rsdThreshold: Mask features with a RSD below this value. If ``None``, use the value from *Attributes['rsdThreshold']*
		:type rsdThreshold: None or float
		:param varianceRatio: Mask features where the RSD measured in study samples is below that measured in study reference samples multiplied by *varianceRatio*
		:type varianceRatio: None or float
		:param withArtifactualFiltering: If ``None`` use the value from ``Attributes['artifactualFilter']``. If ``False`` doesn't apply artifactual filtering. If ``Attributes['artifactualFilter']`` is set to ``False`` artifactual filtering will not take place even if ``withArtifactualFiltering`` is set to ``True``.
		:type withArtifactualFiltering: None or bool
		:param deltaMzArtifactual: Maximum allowed m/z distance between two grouped features. If ``None``, use the value from *Attributes['deltaMzArtifactual']*
		:type deltaMzArtifactual: None or float
		:param overlapThresholdArtifactual: Minimum peak overlap between two grouped features. If ``None``, use the value from *Attributes['overlapThresholdArtifactual']*
		:type overlapThresholdArtifactual: None or float
		:param corrThresholdArtifactual: Minimum correlation between two grouped features. If ``None``, use the value from *Attributes['corrThresholdArtifactual']*
		:type corrThresholdArtifactual: None or float
		:param blankThreshold: Mask features thats median intesity falls below *blankThreshold x the level in the blank*. If ``False`` do not filter, if ``None`` use the cutoff from *Attributes['blankThreshold']*, otherwise us the cutoff scaling factor provided
		:type blankThreshold: None, False, or float
		"""

		if rsdThreshold is None:
			rsdThreshold = self.Attributes['rsdThreshold']
		if not isinstance(rsdThreshold, numbers.Number):
			raise TypeError('rsdThreshold must be a number, %s provided' % (type(rsdThreshold)))
		elif rsdThreshold <= 0:
			raise ValueError('rsdThreshold must be a positive value, %f provided' % (rsdThreshold))

		if correlationThreshold is None:
			correlationThreshold = self.Attributes['corrThreshold']
		if not isinstance(correlationThreshold, numbers.Number):
			raise TypeError('correlationThreshold must be a number in the range -1 to 1, %s provided' % (type(correlationThreshold)))
		elif (correlationThreshold < -1) or (correlationThreshold > 1):
			raise ValueError('correlationThreshold must be a number in the range -1 to 1, %f provided' % (correlationThreshold))

		if varianceRatio is None:
			varianceRatio = self.Attributes['varianceRatio']
		if not isinstance(varianceRatio, numbers.Number):
			raise TypeError('varianceRatio must be a number, %s provided' % (type(varianceRatio)))

		if withArtifactualFiltering is not None:
			if not isinstance(withArtifactualFiltering, bool):
				raise TypeError('withArtifactualFiltering must be a bool, %s provided' % (type(withArtifactualFiltering)))
		if withArtifactualFiltering is None:
			withArtifactualFiltering = self.Attributes['artifactualFilter']
		# if self.Attributes['artifactualFilter'] is False, can't/shouldn't apply it. However if self.Attributes['artifactualFilter'] is True, the user can have the choice to not apply it (withArtifactualFilering=False).
		if (withArtifactualFiltering is True) & (self.Attributes['artifactualFilter'] is False):
			warnings.warn("Warning: Attributes['artifactualFilter'] set to \'False\', artifactual filtering cannot be applied.")
			withArtifactualFiltering = False

		if deltaMzArtifactual is not None:
			if not isinstance(deltaMzArtifactual, numbers.Number):
				raise TypeError('deltaMzArtifactual must be a number , %s provided' % (type(deltaMzArtifactual)))
			self.Attributes['deltaMzArtifactual'] = deltaMzArtifactual

		if corrThresholdArtifactual is not None:
			if not isinstance(corrThresholdArtifactual, numbers.Number):
				raise TypeError('corrThresholdArtifactual must be a number in the range 0 to 1, %s provided' % (type(corrThresholdArtifactual)))
			elif (corrThresholdArtifactual < 0) or (corrThresholdArtifactual > 1):
				raise ValueError('corrThresholdArtifactual must be a number in the range 0 to 1, %f provided' % (corrThresholdArtifactual))
			self.Attributes['corrThresholdArtifactual'] = corrThresholdArtifactual

		if overlapThresholdArtifactual is not None:
			if not isinstance(overlapThresholdArtifactual, numbers.Number):
				raise TypeError('overlapThresholdArtifactual must be a number , %s provided' % (type(overlapThresholdArtifactual)))
			self.Attributes['overlapThresholdArtifactual'] = overlapThresholdArtifactual

		if filterFeatures:

			blankMask = blankFilter(self, threshold=blankThreshold)

			# Calculate RSD in SP samples and SS
			mask = numpy.logical_and(self.sampleMetadata['AssayRole'].values == AssayRole.Assay,
									 self.sampleMetadata['SampleType'].values == SampleType.StudySample)

			mask = numpy.logical_and(mask,
									 self.sampleMask)

			rsdSS = rsd(self._intensityData[mask, :])

			featureMask = (self.correlationToDilution >= correlationThreshold) & (self.rsdSP <= rsdThreshold) & ((self.rsdSP * varianceRatio) <= rsdSS) & self.featureMask

			featureMask = numpy.logical_and(featureMask, blankMask)

			# Artifactual filtering
			if withArtifactualFiltering:
				if (deltaMzArtifactual is not None) | (corrThresholdArtifactual is not None) | (overlapThresholdArtifactual is not None):
					# Linkage update
					self.updateArtifactualLinkageMatrix()
				featureMask = self.artifactualFilter(featMask=featureMask)

			self.featureMask = featureMask

		# Sample Exclusions
		if filterSamples:

			super().updateMasks(filterSamples=True,
								filterFeatures=False,
								sampleTypes=sampleTypes,
								assayRoles=assayRoles,
								**kwargs)

		self.Attributes['Log'].append([datetime.now(), "Dataset filtered with: filterSamples=%s, filterFeatures=%s, sampleTypes=%s, assayRoles=%s, correlationThreshold=%s, rsdThreshold=%s, varianceRatio=%s, %s." % (
																																							filterSamples,
																																							filterFeatures,
																																							sampleTypes,
																																							assayRoles,
																																							correlationThreshold,
																																							rsdThreshold,
																																							varianceRatio,
																																							', '.join("{!s}={!r}".format(key,val) for (key,val) in kwargs.items()))])


	def addSampleInfo(self, descriptionFormat=None, filePath=None, filenameSpec=None, **kwargs):
		"""
		Load additional metadata and map it in to the :py:attr:`~Dataset.sampleMetadata` table.

		Possible options:

		* **'NPC LIMS'** NPC LIMS files mapping files names of raw analytical data to sample IDs
		* **'NPC Subject Info'** Map subject metadata from a NPC sample manifest file (format defined in 'PCSOP.082')
		* **'Raw Data'** Extract analytical parameters from raw data files
		* **'ISATAB'** ISATAB study designs
		* **'Filenames'** Parses sample information out of the filenames, based on the named capture groups in the regex passed in *filenamespec*
		* **'Basic CSV'** Joins the :py:attr:`sampleMetadata` table with the data in the ``csv`` file at *filePath=*, matching on the 'Sample File Name' column in both.
		* **'Batches'** Interpolate batch numbers for samples between those with defined batch numbers based on sample acquisitions times

		:param str descriptionFormat: Format of metadata to be added
		:param str filePath: Path to the additional data to be added
		:param filenameSpec: Only used if *descriptionFormat* is 'Filenames'. A regular expression that extracts sample-type information into the following named capture groups: 'fileName', 'baseName', 'study', 'chromatography' 'ionisation', 'instrument', 'groupingKind' 'groupingNo', 'injectionKind', 'injectionNo', 'reference', 'exclusion' 'reruns', 'extraInjections', 'exclusion2'. if ``None`` is passed, use the *filenameSpec* key in *Attributes*, loaded from the SOP json
		:type filenameSpec: None or str
		:raises NotImplementedError: if the descriptionFormat is not understood
		"""

		if descriptionFormat == 'Filenames':
			if filenameSpec is None: # Use spec from SOP
				filenameSpec = self.Attributes['filenameSpec']
			self._getSampleMetadataFromFilename(filenameSpec)
		elif descriptionFormat == 'Batches':
			self._fillBatches()
		else:
			super().addSampleInfo(descriptionFormat=descriptionFormat, filePath=filePath, filenameSpec=filenameSpec, **kwargs)


	def _loadQIDataset(self, path):

		# Get index positions for QIs data blocks
		dataT = pandas.read_csv(path, index_col=0, header=[0], nrows=1)
		startIndex = dataT.columns.get_loc("Normalised abundance")
		endIndex = dataT.columns.get_loc("Raw abundance")

		dataSize = endIndex - startIndex

		# Now read for real
		dataT = pandas.read_csv(path, header=2)
		values = dataT.iloc[:,endIndex+1:endIndex+dataSize+1]
		self._intensityData = values.values.transpose()

		# Get the sample names as the only metadata we have
		sampleMetadata = dict()
		sampleMetadata['Sample File Name'] = [name[:-2] for name in list(values.columns.values)]

		# Peak info
		featureMetadata = dict()
		featureMetadata['Feature Name'] = dataT['Compound'].values
		featureMetadata['m/z'] = dataT['m/z'].values
		featureMetadata['Retention Time'] = dataT['Retention time (min)'].values
		featureMetadata['Peak Width'] = dataT['Chromatographic peak width (min)'].values
		featureMetadata['Isotope Distribution'] = dataT['Isotope Distribution'].values
		featureMetadata['Adducts'] = dataT['Adducts'].values

		self.featureMetadata = pandas.DataFrame(numpy.vstack([featureMetadata[c] for c in featureMetadata.keys()]).T, columns=featureMetadata.keys())
		# keep the default empty sampleMetadata (column names) and fill it
		for c in sampleMetadata.keys():
			self.sampleMetadata[c] = sampleMetadata[c]

		self.featureMetadata['Peak Width'] = self.featureMetadata['Peak Width'].astype(float)
		self.featureMetadata['Retention Time'] = self.featureMetadata['Retention Time'].astype(float)
		self.featureMetadata['m/z'] = self.featureMetadata['m/z'].astype(float)

		self.initialiseMasks()

		self.sampleMetadata['AssayRole'] = AssayRole.Assay
		self.sampleMetadata['SampleType'] = SampleType.StudySample
		self.sampleMetadata['Dilution'] = 100
		self.sampleMetadata['Metadata Available'] = False

		self.Attributes['Log'].append([datetime.now(), 'Progenesis QI dataset loaded from %s' % (path)])


	def _loadXCMSDataset(self, path, noFeatureParams=14):

		# Import into dataframe
		dataT = pandas.read_csv(path, index_col=False)

		# Find start of data
		startIndex = noFeatureParams
		endIndex = len(dataT.columns)

		dataSize = endIndex - startIndex

		# Now read for real
		values = dataT.iloc[:,startIndex:]
		self._intensityData = values.values.transpose()

		# Get the sample names as the only metadata we have
		sampleMetadata = dict()
		sampleMetadata['Sample File Name'] = [name for name in list(values.columns.values)]

		# Peak info
		featureMetadata = dict()

		# for when peakTable methods is used directly instead of diffreport
		# If no feature name is present, assume peakTable was used to derive the dataset and adjust accordingly
		# If the try fails,
		if 'name' not in dataT.columns:
			try:
				# build feature name by combination of rt and m/z
				feature_names = [str(round(row['rt'], 2)) + '_' + str(round(row['mz'], 4)) + 'm/z' for idx,row in dataT.iterrows()]
				# insert feature name
				dataT.insert(0, 'name', feature_names)
				# rename mz to mzmed like in diffreport
				dataT.rename(columns={'mz': 'mzmed', 'rt': 'rtmed'}, inplace=True)
			except:
				raise ValueError('XCMS data frame should be obtained with either peakTable or diffreport methods')

		featureMetadata['Feature Name'] = dataT['name'].values
		featureMetadata['m/z'] = dataT['mzmed'].values
		featureMetadata['Retention Time'] = dataT['rtmed'].values
		featureMetadata['m/z - Minimum'] = dataT['mzmin'].values
		featureMetadata['m/z - Maximum'] = dataT['mzmax'].values
		featureMetadata['Retention Time - Minimum'] = dataT['rtmin'].values
		featureMetadata['Retention Time - Maximum'] = dataT['rtmax'].values

		self.featureMetadata = pandas.DataFrame(numpy.vstack([featureMetadata[c] for c in featureMetadata.keys()]).T, columns=featureMetadata.keys())
		self.sampleMetadata = pandas.DataFrame(numpy.concatenate([sampleMetadata[c] for c in sampleMetadata.keys()], axis=0), columns=sampleMetadata.keys())

		# Put Feature Names first
		name = self.featureMetadata['Feature Name']
		self.featureMetadata.drop(labels=['Feature Name'], axis=1, inplace=True)
		self.featureMetadata.insert(0, 'Feature Name', name)

		self.featureMetadata['Retention Time'] = self.featureMetadata['Retention Time'].astype(float) / 60.0
		self.featureMetadata['m/z'] = self.featureMetadata['m/z'].astype(float)

		self.sampleMetadata['AssayRole'] = AssayRole.Assay
		self.sampleMetadata['SampleType'] = SampleType.StudySample
		self.sampleMetadata['Dilution'] = 100
		self.sampleMetadata['Metadata Available'] = False

		fileNameAndExtension = self.sampleMetadata['Sample File Name'].apply(os.path.splitext)
		self.sampleMetadata['Sample File Name'] = [x[0] for x in fileNameAndExtension]

		self.initialiseMasks()

		self.Attributes['Log'].append([datetime.now(), 'XCMS dataset loaded from %s' % (path)])


	def _loadBiocratesDataset(self, path, noSampleParams=15, sheetName='Data Export'):

		# Read in data
		dataT = pandas.read_excel(path, sheet_name=sheetName, skiprows=[0])

		##
		# Intensity matrix
		##
		# Find start of data
		endIndex = len(dataT.index)

		# Now read  intensities
		self._intensityData = dataT.iloc[2:endIndex,noSampleParams+1:].values

		##
		# Feature info
		##
		featureMetadata = dict()
		featureMetadata['Feature Name'] = list(dataT.columns.values)[noSampleParams+1:]
		featureMetadata['Class'] = list(dataT.iloc[0,noSampleParams+1:].values)
		featureMetadata['LOD (μM)'] = list(dataT.iloc[1,noSampleParams+1:].values)

		self.featureMetadata = pandas.DataFrame(numpy.vstack([featureMetadata[c] for c in featureMetadata.keys()]).T, columns=featureMetadata.keys())
		self.featureMetadata['LOD (μM)'] = pandas.to_numeric(self.featureMetadata['LOD (μM)'])
		##
		# Sample info
		##
		self.sampleMetadata = pandas.read_excel(path, sheet_name=sheetName, skiprows=[0, 2,3], usecols=noSampleParams)

		# If there are multiple 'LOD (calc.) ' strings we have several sheets concatenated.
		sampleMask = self.sampleMetadata['Measurement Time'].str.match('LOD \(calc\.\).+').values

		# Take the highest overall LOD
		newLOD = numpy.amax(self._intensityData[sampleMask, :], axis=0)
		self.featureMetadata.loc[self.featureMetadata['LOD (μM)'].values < newLOD, 'LOD (μM)'] = newLOD[self.featureMetadata['LOD (μM)'].values < newLOD]
		self.featureMetadata['LOD (μM)'] = pandas.to_numeric(self.featureMetadata['LOD (μM)'])
		# Delete data
		self._intensityData = self._intensityData[sampleMask == False, :]

		# Delete sample data
		self.sampleMetadata = self.sampleMetadata[sampleMask == False]
		self.sampleMetadata.reset_index(drop=True, inplace=True)

		self.sampleMetadata['Collection Date'] = pandas.to_datetime(self.sampleMetadata['Collection Date'])
		self.sampleMetadata['Measurement Time'] = pandas.to_datetime(self.sampleMetadata['Measurement Time'])
		self.sampleMetadata['Sample Bar Code'] = self.sampleMetadata['Sample Bar Code'].astype(int)
		self.sampleMetadata['Well Position'] = self.sampleMetadata['Well Position'].astype(int)
		self.sampleMetadata['Run Number'] = self.sampleMetadata['Run Number'].astype(int)
		self.sampleMetadata['Acquired Time'] = self.sampleMetadata['Measurement Time'].astype(datetime)

		# Rename sample IDs
		ids = self.sampleMetadata['Sample Identification']
		self.sampleMetadata.drop(labels=['Sample Identification'], axis=1, inplace=True)
		self.sampleMetadata.insert(0, 'Sampling ID', ids)

		# Put Feature Names first
		names = self.featureMetadata['Feature Name']
		self.featureMetadata.drop(labels=['Feature Name'], axis=1, inplace=True)
		self.featureMetadata.insert(0, 'Feature Name', names)

		self.sampleMetadata['Metadata Available'] = False
		self.initialiseMasks()

		self.Attributes['Log'].append([datetime.now(), 'Biocrates dataset loaded from %s' % (path)])


	def _loadMetaboscapeDataset(self, path, noFeatureParams=None, sheetName=None):

		prefix, fileType = os.path.splitext(path)

		if fileType.lower() in ('.xls', '.xlsx'):
			dataT = pandas.read_excel(path, sheet_name=sheetName)
		elif fileType.lower() == '.csv':
			dataT = pandas.read_csv(path)
		else:
			raise ValueError('"%s" is not a known file type!' % (fileType))

		if noFeatureParams is None:
			if 'RT [min]' in dataT.columns:
				noFeatureParams = 18
			else:
				noFeatureParams = 14

		# Find start of data
		startIndex = noFeatureParams
		endIndex = len(dataT.columns)

		dataSize = endIndex - startIndex

		# Now read for real
		values = dataT.iloc[:,startIndex:]
		intensityData = values.values.transpose()

		# Get the sample names as the only metadata we have
		sampleMetadata = dict()
		sampleMetadata['Sample File Name'] = [name for name in list(values.columns.values)]

		# Peak info
		featureMetadata = dict()

		dataT.rename(columns={'m/z meas.': 'm/z',
							  'M meas.': 'Neutral Mass',
							  'Δm/z [mDa]': 'm/z Deviation',
		#					   'mSigma': '',
		#					   'MS/MS score': '',
		#					   'Include': '',
		#					   'Molecular Formula': '',
		#					   'Annotations': '',
		#					   'Ions': '',
		#					   'AQ': '',
		#					   'Boxplot': '',
		#					   'Flags': '',
		#					   'MS/MS': '',
		#					   'Name': '',
		#					   'Δm/z [ppm]': '',
		#					   'Annotation Source':''
							 }, inplace=True)

		for column in dataT.columns[:noFeatureParams]:
			featureMetadata[column] = dataT[column].values

		if 'RT [min]' in dataT.columns:
			featureMetadata['Retention Time'] = dataT['RT [min]'].values
			featureMetadata['Retention Time Deviation'] = dataT['ΔRT'].values

			featureMetadata['Feature Name'] = [str(round(row['RT [min]'], 2)) + '_' + str(round(row['m/z'], 4)) + 'm/z' for idx,row in dataT.iterrows()]
			featureMetadata['Retention Time'] = featureMetadata['Retention Time'].astype(float)

		else:
			featureMetadata['Feature Name'] = dataT['m/z'].apply(lambda mz: str(mz) + 'm/z').values


		featureMetadata = pandas.DataFrame(numpy.vstack([featureMetadata[c] for c in featureMetadata.keys()]).T, columns=featureMetadata.keys())
		sampleMetadata = pandas.DataFrame(numpy.concatenate([sampleMetadata[c] for c in sampleMetadata.keys()], axis=0), columns=sampleMetadata.keys())

		sampleMetadata['AssayRole'] = AssayRole.Assay
		sampleMetadata['SampleType'] = SampleType.StudySample
		sampleMetadata['Dilution'] = 100

		# Put Feature Names first
		name = featureMetadata['Feature Name']
		featureMetadata.drop(labels=['Feature Name'], axis=1, inplace=True)
		featureMetadata.insert(0, 'Feature Name', name)

		featureMetadata['m/z'] = featureMetadata['m/z'].astype(float)

		if 'Retention Time' in featureMetadata.columns:
			featureMetadata['Retention Time'] = featureMetadata['Retention Time'].astype(float)
			featureMetadata['Retention Time Deviation'] = featureMetadata['Retention Time Deviation'].astype(float)


		self._intensityData = intensityData
		self.sampleMetadata = sampleMetadata
		self.featureMetadata = featureMetadata

		self.initialiseMasks()

		self.Attributes['Log'].append([datetime.now(), 'Metaboscape dataset loaded from %s' % (path)])


	def _getSampleMetadataFromRawData(self, rawDataPath):
		"""
		Pull metadata out of raw experiment files.
		"""
		# Validate inputs
		if not os.path.isdir(rawDataPath):
			raise ValueError('No directory found at %s' % (rawDataPath))

		# Store the location
		self.Attributes['Raw Data Path'] = rawDataPath

		# Infer data format here - for now assume Waters RAW.
		instrumentParams = getSampleMetadataFromWatersRawFiles(rawDataPath)

		# Merge back into sampleMetadata
		# Check if we already have these columns in sampleMetadata, if not, merge, if so, use combine_first to patch
		if not 'Acquired Time' in self.sampleMetadata.columns:
			self.sampleMetadata = pandas.merge(self.sampleMetadata, instrumentParams, left_on='Sample File Name', right_on='Sample File Name', how='left', sort=False)
			self.Attributes['Log'].append([datetime.now(), 'Acquisition metadata added from raw data at: %s' % (rawDataPath)])

		else:
			# Delete the items not currenty in self.sampleMetadata
			instrumentParams = instrumentParams[instrumentParams['Sample File Name'].isin(self.sampleMetadata['Sample File Name'])]
			# Create an empty template
			sampleMetadata = pandas.DataFrame(self.sampleMetadata['Sample File Name'], columns=['Sample File Name'])

			instrumentParams = pandas.merge(sampleMetadata, instrumentParams, left_on='Sample File Name', right_on='Sample File Name', how='left', sort=False)
			self.sampleMetadata = self.sampleMetadata.combine_first(instrumentParams)
			self.Attributes['Log'].append([datetime.now(), 'Additional acquisition metadata added from raw data at: %s' % (rawDataPath)])

		# Generate the integer run order.
		# Explicity convert datetime format
		self.sampleMetadata['Acquired Time'] = self.sampleMetadata['Acquired Time'].astype(datetime)
		self.sampleMetadata['Order'] = self.sampleMetadata.sort_values(by='Acquired Time').index
		self.sampleMetadata['Run Order'] = self.sampleMetadata.sort_values(by='Order').index
		self.sampleMetadata.drop('Order', axis=1, inplace=True)

		# Flag samples for exclusion:
		if 'Exclusion Details' not in self.sampleMetadata:
			self.sampleMetadata['Exclusion Details'] = None

		# Flag samples with missing instrument parameters
		headerNull = self.sampleMetadata.loc[self.sampleMetadata['Measurement Date'].isnull(), 'Sample File Name'].values
		externNull = self.sampleMetadata.loc[self.sampleMetadata['Backing'].isnull(), 'Sample File Name'].values

		# Output sample names to screen, for user checking
		# Exclude samples from subsequent processing
		if(headerNull.shape[0] != 0):
			print('\n_HEADER.txt file (raw data folder) missing for:')
			for i in headerNull:
				print(i)
			self.excludeSamples(headerNull, message='unable to load _HEADER.txt file')

		if(externNull.shape[0] != 0):
			print('\n_extern.inf file (raw data folder) missing for:')
			for i in externNull:
				print(i)
			self.excludeSamples(externNull, message='unable to load _extern.inf file')

		if((headerNull.shape[0] != 0) | (externNull.shape[0] != 0)):
			print('\n****** Please check and correct before continuing - these samples will be automatically marked for exclusion from subsequent processing ******\n')


	def _getSampleMetadataFromFilename(self, filenameSpec):
		"""
		Infer sample acquisition metadata from standardised filename template.
		"""

		# If the dilution series design is not defined in the SOP, load the defualt.
		if not 'dilutionMap' in self.Attributes.keys():
			dilutionMap = pandas.read_csv(os.path.join(toolboxPath(), 'StudyDesigns', 'DilutionSeries.csv'), index_col='Sample Name')
			self.Attributes['dilutionMap'] = dilutionMap['Dilution Factor (%)'].to_dict()

		# Strip any whitespace from 'Sample File Name'
		self.sampleMetadata['Sample File Name'] = self.sampleMetadata['Sample File Name'].str.strip()

		# Break filename down into constituent parts.
		baseNameParser = re.compile(filenameSpec, re.VERBOSE)
		fileNameParts = self.sampleMetadata['Sample File Name'].str.extract(baseNameParser, expand=False)

		# Deal with badly ordered exclusions
		fileNameParts['exclusion'].loc[fileNameParts['exclusion2'].isnull() == False] = fileNameParts['exclusion2'].loc[fileNameParts['exclusion2'].isnull() == False]
		fileNameParts.drop('exclusion2', axis=1, inplace=True)

		# Pass masks into enum fields
		fileNameParts.loc[:,'AssayRole'] = AssayRole.Assay
		fileNameParts.loc[fileNameParts['reference'] == 'SR', 'AssayRole'] = AssayRole.PrecisionReference
		fileNameParts.loc[fileNameParts['baseName'].str.match('.+[B]\d+?[SE]\d+?', na=False).astype(bool), 'AssayRole'] = AssayRole.PrecisionReference
		fileNameParts.loc[fileNameParts['reference'] == 'LTR', 'AssayRole'] = AssayRole.PrecisionReference
		fileNameParts.loc[fileNameParts['reference'] == 'MR', 'AssayRole'] = AssayRole.PrecisionReference
		fileNameParts.loc[fileNameParts['injectionKind'] == 'SRD', 'AssayRole'] = AssayRole.LinearityReference
		fileNameParts.loc[fileNameParts['groupingKind'].str.match('Blank', na=False).astype(bool), 'AssayRole'] = AssayRole.LinearityReference
		fileNameParts.loc[fileNameParts['groupingKind'].str.match('E?IC', na=False).astype(bool), 'AssayRole'] = AssayRole.Assay

		fileNameParts.loc[:,'SampleType'] = SampleType.StudySample
		fileNameParts.loc[fileNameParts['reference'] == 'SR', 'SampleType'] = SampleType.StudyPool
		fileNameParts.loc[fileNameParts['baseName'].str.match('.+[B]\d+?[SE]\d+?', na=False).astype(bool), 'SampleType'] = SampleType.StudyPool
		fileNameParts.loc[fileNameParts['reference'] == 'LTR', 'SampleType'] = SampleType.ExternalReference
		fileNameParts.loc[fileNameParts['reference'] == 'MR', 'SampleType'] = SampleType.MethodReference
		fileNameParts.loc[fileNameParts['injectionKind'] == 'SRD', 'SampleType'] = SampleType.StudyPool
		fileNameParts.loc[fileNameParts['groupingKind'].str.match('Blank', na=False).astype(bool), 'SampleType'] = SampleType.ProceduralBlank
		fileNameParts.loc[fileNameParts['groupingKind'].str.match('E?IC', na=False).astype(bool), 'SampleType'] = SampleType.StudyPool

		# Skipped runs
		fileNameParts['Skipped'] = fileNameParts['exclusion'].str.match('[Xx]', na=False)

		# Get matrix
		fileNameParts['Matrix'] = fileNameParts['groupingKind'].str.extract('^([AC-Z]{1,2})(?<!IC)$', expand=False)
		fileNameParts['Matrix'].fillna('', inplace=True)

		# Get well numbers
		fileNameParts.loc[fileNameParts['groupingKind'].str.match('Blank|E?IC', na=False).astype(bool) ,'injectionNo'] = -1
		fileNameParts['Well'] = pandas.to_numeric(fileNameParts['injectionNo'])

		# Plate / grouping no
		fileNameParts['Plate'] = pandas.to_numeric(fileNameParts['groupingNo'])

		# Get batch where it is explicit in file name
		fileNameParts['Batch'] = pandas.to_numeric(fileNameParts['baseName'].str.extract('B(\d+?)[SE]', expand=False))
		fileNameParts['Correction Batch'] = numpy.nan

		# Map dilution series names to dilution level
		fileNameParts['Dilution'] = fileNameParts['baseName'].str.extract('(?:.+_?)(SRD\d\d)(?:_?.*)', expand=False).replace(self.Attributes['dilutionMap'])

		# Blank out NAs for neatness
		fileNameParts['reruns'].fillna('', inplace=True)
		fileNameParts['extraInjections'].fillna('', inplace=True)

		# Drop unwanted columns
		fileNameParts.drop(['exclusion', 'reference', 'groupingKind', 'injectionNo', 'injectionKind', 'groupingNo'], axis=1, inplace=True)

		# Swap in user friendly file names
		fileNameParts.rename(columns={'chromatography': 'Chromatography'}, inplace=True)
		fileNameParts.rename(columns={'instrument': 'Instrument'}, inplace=True)
		fileNameParts.rename(columns={'study': 'Study'}, inplace=True)
		fileNameParts.rename(columns={'baseName': 'Sample Base Name'}, inplace=True)
		fileNameParts.rename(columns={'fileName': 'Sample File Name'}, inplace=True)
		fileNameParts.rename(columns={'suplementalInfo': 'Suplemental Info'}, inplace=True)
		fileNameParts.rename(columns={'ionisation': 'Ionisation'}, inplace=True)
		fileNameParts.rename(columns={'extraInjections': 'Suplemental Injections'}, inplace=True)
		fileNameParts.rename(columns={'reruns': 'Re-Run'}, inplace=True)

		# Merge metadata back into the sampleInfo table.
		# first remove duplicate columns (from _dataset _init_)
		if 'AssayRole' in self.sampleMetadata.columns: self.sampleMetadata.drop(['AssayRole'], axis=1, inplace=True)
		if 'SampleType' in self.sampleMetadata.columns: self.sampleMetadata.drop(['SampleType'], axis=1, inplace=True)
		if 'Sample Base Name' in self.sampleMetadata.columns: self.sampleMetadata.drop(['Sample Base Name'], axis=1, inplace=True)
		if 'Dilution' in self.sampleMetadata.columns: self.sampleMetadata.drop(['Dilution'], axis=1, inplace=True)
		if 'Batch' in self.sampleMetadata.columns: self.sampleMetadata.drop(['Batch'], axis=1, inplace=True)
		if 'Correction Batch' in self.sampleMetadata.columns: self.sampleMetadata.drop(['Correction Batch'], axis=1, inplace=True)
		# merge
		self.sampleMetadata = pandas.merge(self.sampleMetadata, fileNameParts, left_on='Sample File Name', right_on='Sample File Name', how='left', sort=False)

		# Add 'Exclusion Details' column
		self.sampleMetadata['Exclusion Details'] = ''
		self.sampleMetadata['Metadata Available'] = True
		self.Attributes['Log'].append([datetime.now(), 'Sample metadata parsed from filenames.'])


	def _fillBatches(self):
		"""
		Use sample names and acquisition times to infer batch info
		"""

		batchRE = r"""
			B
			(?P<observebatch>\d+?)
			(?P<startend>[SE])
			(?P<sequence>\d+?)
			_SR
			(?:_(?P<extraInjections>\d+?|\w+?))?
			$
			"""
		batchRE = re.compile(batchRE,re.VERBOSE)
		# We canot infer batches unless we have runorder
		if 'Run Order' not in self.sampleMetadata.columns:
			warnings.warn('Unable to infer batches without run order, skipping.')
		elif self.sampleMetadata['Run Order'].isnull().all():
			warnings.warn('Unable to infer batches without run order, skipping.')
		else:
			self.__corrExclusions = None
			currentBatch = 0
			dilutionSeries = 0
			contiguousDilution = False
			# Loop over samples in run order
			for index, row in self.sampleMetadata.sort_values(by='Run Order').iterrows():
				nameComponents = batchRE.search(row['Sample File Name'])
				if nameComponents:
					# Batch start
					if nameComponents.group('startend') == 'S':
						# New batch - increment batch no
						if nameComponents.group('sequence') == '1':
							currentBatch = currentBatch + 1

				# Don't include the dilution series or blanks
				if not ((row['AssayRole'] == AssayRole.LinearityReference) or (row['SampleType'] == SampleType.ProceduralBlank)):
					self.sampleMetadata.loc[index, 'Batch'] = currentBatch
					self.sampleMetadata.loc[index, 'Correction Batch'] = currentBatch
					contiguousDilution = False

				elif row['AssayRole'] == AssayRole.LinearityReference and row['SampleType'] != SampleType.ProceduralBlank:
					if not contiguousDilution:
						dilutionSeries += 1
						contiguousDilution = True

					self.sampleMetadata.loc[index, 'Dilution Series'] = dilutionSeries


	def amendBatches(self, sampleRunOrder):
		"""
		Creates a new batch starting at the sample index in *sampleRunOrder*, and amends subsequent batch numbers in :py:attr:`~Dataset.sampleMetadata`\ ['Correction Batch']

		:param int sampleRunOrder: Index of first sample in new batch
		"""

		newBatch = copy.deepcopy(self.sampleMetadata['Correction Batch'])
		newBatch[self.sampleMetadata['Run Order'] >= sampleRunOrder] = newBatch[self.sampleMetadata['Run Order'] >= sampleRunOrder] + 1

		self.sampleMetadata.loc[:, 'Correction Batch'] = newBatch


	def __correlateToDilution(self, method='pearson', sampleType=SampleType.StudyPool, assayRole=AssayRole.LinearityReference, exclusions=True):
		"""
		Calculates correlation of feature intesities to dilution.

		If a 'Dilution Series' column is present in sampleMetadata, correlation are calcualted on each sub-series, then averaged, otherwise they are

		:params str method: 'pearson' or 'spearman'
		:params list exclusion: list of Linarity Reference sample subsets to mask from correlation calculation
		"""

		# Check inputs
		if not 'Dilution' in self.sampleMetadata.columns:
			raise KeyError('Unable to calculate correlation without dilution values, skipping')
		if not isinstance(method, str) & (method in {'pearson', 'spearman'}):
			raise ValueError('method must be == \'pearson\' or \'spearman\'')

		if not 'Dilution Series' in self.sampleMetadata.columns:
			##
			# If indervidual dilution sereis are not defined, consider all LR samples together
			##
			lrMask = numpy.logical_and(self.sampleMetadata['SampleType'] == sampleType,
									   self.sampleMetadata['AssayRole'] == assayRole)
			lrMask = numpy.logical_and(lrMask,
									   exclusions)

			if sum(lrMask) == 0:
				raise ValueError('No %s samples defined with an AssayRole of %s' % (sampleType, assayRole))

			returnValues = _vcorrcoef(self._intensityData,
									  self.sampleMetadata['Dilution'].values,
									  method=method,
									  sampleMask=lrMask)

		else:
			##
			# If sub-series are defined, calcuate corrs for each then average
			##
			batches = self.sampleMetadata['Dilution Series'].unique()
			mask = pandas.notnull(batches)
			batches = batches[mask]

			correlations = numpy.zeros((len(batches), self.noFeatures))
			index = 0
			for batch in batches:
				lrMask = self.sampleMetadata['Dilution Series'].values == batch
				lrMask = numpy.logical_and(lrMask,
										   exclusions)

				correlations[index,:] = _vcorrcoef(self._intensityData,
												   self.sampleMetadata['Dilution'].values,
												   method=method,
												   sampleMask=lrMask)

				index += 1

			returnValues = numpy.mean(correlations, axis=0)

		returnValues[numpy.isnan(returnValues)] = 0

		self.Attributes['Log'].append([datetime.now(), 'Feature correlation to dilution calculated with : method(%s); exclusions(%s)' % (method, exclusions)])

		return returnValues


	def __generateArtifactualLinkageMatrix(self,corrOnly=False):
		""" Identify potentially artifactual features, generate the linkage between similar features
			input:
				msDataset
				deltaMZ				   maximum allowed m/z distance between two grouped features
				deltaOverlap			  minimum peak overlap between two grouped features
				deltaCorr				 minimum correlation between two grouped features
				corrOnly				  recalculate the correlation but not the overlap
			output:
				artifactualLinkageMatrix  feature pairs (row)(feature index), feature1-feature2 (col)
			raise:
				ValueError if self.Attributes['artifactualFilter'] = False
				LookupError if the Feature Name, Retention Time, m/z or Peak Width are missing.
		"""
		def find_similar_peakwidth(featureMetadata,deltaMZ,deltaOverlap):
			"""Find 'identical' features based on m/z and peakwidth overlap
				input:
					featureMetada   msDataset.featureMetadata
					deltaMZ		 m/z distance to consider two features identical [ <= ] (same unit as m/z)
					delta overlap   minimum peak overlap between two grouped features (0-100%)
				output:
					pandas.DataFrame listing matched features based on deltaMZ and deltaOverlap
			"""
			def get_match(i,ds,deltaMZ):
				"""Find identical features for a given variable
					output:
						pandas.DataFrames listing the matching features based overlap of peakwidth
				"""
				match = (abs(ds.loc[i,'Retention Time']-ds.loc[:,'Retention Time']) <= (ds.loc[i,'Peak Width']+ds.loc[:,'Peak Width'])/2) & (abs(ds.loc[i,'m/z']-ds.loc[:,'m/z']) <= deltaMZ)	 # find match
				return( pandas.DataFrame(data = {'node1': ds.index[i], 'node2': ds.index[match], 'Peak Overlap': ((((ds.loc[i,'Peak Width']+ds.loc[match,'Peak Width'])/2)-abs(ds.loc[i,'Retention Time']-ds.loc[match,'Retention Time']))/((ds.loc[i,'Peak Width']+ds.loc[match,'Peak Width'])/2))*100 } ) )  # return the matching rows

			# get feature overlap
			ds	  = featureMetadata[['Feature Name','Retention Time','m/z','Peak Width']]
			# By concatenating all the matches once, save ~22% compared to do it at each loop round
			matches = [ get_match(i,ds,deltaMZ) for i in range(ds.shape[0]) ] # get a list of matches
			res	 = pandas.concat(matches)
			res	 = res.loc[ res.node1 < res.node2 ]	  # keeps feat1-feat2, removes feat1-feat1 and feat2-feat1

			#filter interactions by overlap
			res	 = res.loc[ res.loc[:,'Peak Overlap']>=deltaOverlap, ['node1','node2'] ]
			res.reset_index( drop=True, inplace=True )

			return( res )
		# end find_similar_peakwidth

		def remove_min_corr_overlap(overlappingFeatures,intensityData,corrCutoff):
			""" Return the overlap match DataFrame with overlap of metabolites correlated < cut-off removed (and correlation added)
				input:
					overlappingFeatures pandas.DataFrame as generated by find_similar_peakwidth
					intensityData	   pandas.DataFrame of data value for each sample (row) / feature (column)
					corrCutoff		  minimum percentage of overlap (0-1)
				output:
					overlapping features filtered
			"""
			link_corr = numpy.zeros([overlappingFeatures.shape[0]])
			for jrow in range(0,len(link_corr)):
				link_corr[jrow] = numpy.corrcoef( intensityData[:,overlappingFeatures.loc[jrow,'node1']], intensityData[:,overlappingFeatures.loc[jrow,'node2']])[0,1]

			return( overlappingFeatures.loc[ link_corr>=corrCutoff, ] )
		# end remove_min_corr_overlap

		# check required info in featureMetadata for artifactual filtering. If missing, sets self.Attributes['artifactualFilter'] to False
		if self.Attributes['artifactualFilter'] == False:
			raise ValueError('Attributes[\'artifactualFilter\'] set to \'False\', artifactual filtering cannot be run, use \'updateMasks(withArtifactualFiltering=False)\' and \'generateReport(data, reportType=\'feature selection\', withArtifactualFiltering=False)\'')
		if 'Feature Name' not in self.featureMetadata.columns:
			self.Attributes['artifactualFilter'] = False
			raise LookupError('Missing feature metadata \"Feature Name\". Artifactual filtering cannot be run, set MSDataset.Attributes[\'artifactualFilter\'] = \'False\', or use \'updateMasks(withArtifactualFiltering=False)\' and \'generateReport(data, reportType=\'feature selection\', withArtifactualFiltering=False)\'')
		if 'Retention Time' not in self.featureMetadata.columns:
			self.Attributes['artifactualFilter'] = False
			raise LookupError('Missing feature metadata \"Retention Time\". Artifactual filtering cannot be run, set MSDataset.Attributes[\'artifactualFilter\'] = \'False\', or use \'updateMasks(withArtifactualFiltering=False)\' and \'generateReport(data, reportType=\'feature selection\', withArtifactualFiltering=False)\'')
		if 'm/z' not in self.featureMetadata.columns:
			self.Attributes['artifactualFilter'] = False
			raise LookupError('Missing feature metadata \"m/z\". Artifactual filtering cannot be run, set MSDataset.Attributes[\'artifactualFilter\'] = \'False\', or use \'updateMasks(withArtifactualFiltering=False)\' and \'generateReport(data, reportType=\'feature selection\', withArtifactualFiltering=False)\'')
		if 'Peak Width' not in self.featureMetadata.columns:
			self.Attributes['artifactualFilter'] = False
			raise LookupError('Missing feature metadata \"Peak Width\". Artifactual filtering cannot be run, set MSDataset.Attributes[\'artifactualFilter\'] = \'False\', or use \'updateMasks(withArtifactualFiltering=False)\' and \'generateReport(data, reportType=\'feature selection\', withArtifactualFiltering=False)\'')

		if ((not corrOnly) | (corrOnly & self._tempArtifactualLinkageMatrix.empty)):
			self._tempArtifactualLinkageMatrix = find_similar_peakwidth(featureMetadata=self.featureMetadata, deltaMZ=self.Attributes['deltaMzArtifactual'], deltaOverlap=self.Attributes['overlapThresholdArtifactual'])
		artifactualLinkageMatrix = remove_min_corr_overlap(self._tempArtifactualLinkageMatrix, self._intensityData, self.Attributes['corrThresholdArtifactual'])

		return(artifactualLinkageMatrix)


	def updateArtifactualLinkageMatrix(self):
		self._artifactualLinkageMatrix = self.__generateArtifactualLinkageMatrix()
		return


	def artifactualFilter(self,featMask=None):
		"""
		Filter artifactual features on top of the featureMask already present if none given as input
		Keep feature with the highest intensity on the mean spectra

		:param featMask: A featureMask (``True`` for inclusion), if ``None``, use :py:attr:`~Dataset.featureMask`
		:type featMask: numpy.ndarray or None
		:return: Amended featureMask
		:rtype: numpy.ndarray
		"""
		# if no featureMask provided, get the one from the msDataset (faster for reportType='feature selection')
		if featMask is not None:
			assert ((type(featMask[0])==numpy.bool_) and (featMask.shape == self.featureMask.shape)), 'check featMask'
			newFeatureMask = copy.deepcopy(featMask)
		else:
			newFeatureMask = copy.deepcopy(self.featureMask)

		# remove features in LinkageMatrix previously filtered (in newFeatMask)
		tmpLinkage		 = copy.deepcopy(self.artifactualLinkageMatrix)
		keptPreviousFilter = self.featureMetadata.index[newFeatureMask]	 # index of previously kept features
		tmpLinkage		 = tmpLinkage[tmpLinkage.node1.isin(keptPreviousFilter) & tmpLinkage.node2.isin(keptPreviousFilter)]

		meanIntensity = self._intensityData.mean(axis=0)

		# make graphs
		g	  = networkx.from_pandas_edgelist(df=tmpLinkage, source='node1', target='node2', edge_attr=True)
		graphs = list((g.subgraph(c).copy() for c in networkx.connected_components(g)))		  # a list of clusters

		# update FeatureMask with features to remove (all but max intensity)
		for i in range(0,len(graphs)):
			newFeatureMask[list(graphs[i].nodes)] = False												 # remove  all nodes in a cluster
			newFeatureMask[list(graphs[i].nodes)[meanIntensity[list(graphs[i].nodes)].argmax()]] = True   # keep max intensity

		return(newFeatureMask)


	def extractRTslice(msrun, target_rt):
		pass


	def getFuctionNo(self, spectrum):
		pass

	def initialiseMasks(self):
		"""
		Re-initialise :py:attr:`featureMask` and :py:attr:`sampleMask` to match the current dimensions of :py:attr:`intensityData`, and include all samples.
		"""
		super().initialiseMasks()
		self.corrExclusions = copy.deepcopy(self.sampleMask)
		self.__corrExclusions = copy.deepcopy(self.corrExclusions)

	def _exportISATAB(self, destinationPath, detailsDict):
		"""
		Export the dataset's metadata to the directory *destinationPath* as ISATAB
		detailsDict should have the format:
		detailsDict = {
			'investigation_identifier' : "i1",
			'investigation_title' : "Give it a title",
			'investigation_description' : "Add a description",
			'investigation_submission_date' : "2016-11-03",
			'investigation_public_release_date' : "2016-11-03",
			'first_name' : "Noureddin",
			'last_name' : "Sadawi",
			'affiliation' : "University",
			'study_filename' : "my_ms_study",
			'study_material_type' : "Serum",
			'study_identifier' : "s1",
			'study_title' : "Give the study a title",
			'study_description' : "Add study description",
			'study_submission_date' : "2016-11-03",
			'study_public_release_date' : "2016-11-03",
			'assay_filename' : "my_ms_assay"
		}

		:param str destinationPath: Path to a directory in which the output will be saved
		:param dict detailsDict: Contains several key: value pairs required to for ISATAB
		:raises IOError: If writing one of the files fails
		"""

		from isatools.model import Investigation, Study, Assay, OntologyAnnotation, OntologySource, Person,Publication,Protocol, Source
		from isatools.model import  Comment, Sample, Characteristic, Process, Material, DataFile, ParameterValue, plink
		from isatools import isatab
		import isaExplorer as ie

		investigation = Investigation()

		investigation.identifier = detailsDict['investigation_identifier']
		investigation.title = detailsDict['investigation_title']
		investigation.description = detailsDict['investigation_description']
		investigation.submission_date = detailsDict['investigation_submission_date']#use today if not specified
		investigation.public_release_date = detailsDict['investigation_public_release_date']
		study = Study(filename='s_'+detailsDict['study_filename']+'.txt')
		study.identifier = detailsDict['study_identifier']
		study.title = detailsDict['study_title']
		study.description = detailsDict['study_description']
		study.submission_date = detailsDict['study_submission_date']
		study.public_release_date = detailsDict['study_public_release_date']
		investigation.studies.append(study)
		obi = OntologySource(name='OBI', description="Ontology for Biomedical Investigations")
		investigation.ontology_source_references.append(obi)
		intervention_design = OntologyAnnotation(term_source=obi)
		intervention_design.term = "intervention design"
		intervention_design.term_accession = "http://purl.obolibrary.org/obo/OBI_0000115"
		study.design_descriptors.append(intervention_design)

		# Other instance variables common to both Investigation and Study objects include 'contacts' and 'publications',
		# each with lists of corresponding Person and Publication objects.

		contact = Person(first_name=detailsDict['first_name'], last_name=detailsDict['last_name'], affiliation=detailsDict['affiliation'], roles=[OntologyAnnotation(term='submitter')])
		study.contacts.append(contact)
		publication = Publication(title="Experiments with Data", author_list="Auther 1, Author 2")
		publication.pubmed_id = "12345678"
		publication.status = OntologyAnnotation(term="published")
		study.publications.append(publication)

		# To create the study graph that corresponds to the contents of the study table file (the s_*.txt file), we need
		# to create a process sequence. To do this we use the Process class and attach it to the Study object's
		# 'process_sequence' list instance variable. Each process must be linked with a Protocol object that is attached to
		# a Study object's 'protocols' list instance variable. The sample collection Process object usually has as input
		# a Source material and as output a Sample material.

		sample_collection_protocol = Protocol(id_="sample collection",name="sample collection",protocol_type=OntologyAnnotation(term="sample collection"))
		aliquoting_protocol = Protocol(id_="aliquoting",name="aliquoting",protocol_type=OntologyAnnotation(term="aliquoting"))

		for index, row in self.sampleMetadata.iterrows():
		    src_name = row['Sample File Name']
		    source = Source(name=src_name)

		    source.comments.append(Comment(name='Study Name', value=row['Study']))
		    study.sources.append(source)

		    sample_name = src_name

		    #sample_name = 'sample_'+str(index)
		    sample = Sample(name=sample_name, derives_from=[source])
		    # check if field exists first
		    status = row['Status'] if 'Status' in self.sampleMetadata.columns else 'N/A'
		    characteristic_material_type = Characteristic(category=OntologyAnnotation(term="material type"), value=status)
		    sample.characteristics.append(characteristic_material_type)

		    #characteristic_material_role = Characteristic(category=OntologyAnnotation(term="material role"), value=row['SampleType'])
		    #sample.characteristics.append(characteristic_material_role)

		    # check if field exists first
		    age = row['Age'] if 'Age' in self.sampleMetadata.columns else 'N/A'
		    characteristic_age = Characteristic(category=OntologyAnnotation(term="Age"), value=age,unit='Year')
		    sample.characteristics.append(characteristic_age)
		    # check if field exists first
		    gender = row['Gender'] if 'Gender' in self.sampleMetadata.columns else 'N/A'
		    characteristic_gender = Characteristic(category=OntologyAnnotation(term="Gender"), value=gender)
		    sample.characteristics.append(characteristic_gender)

		    ncbitaxon = OntologySource(name='NCBITaxon', description="NCBI Taxonomy")
		    characteristic_organism = Characteristic(category=OntologyAnnotation(term="Organism"),value=OntologyAnnotation(term="Homo Sapiens", term_source=ncbitaxon,term_accession="http://purl.bioontology.org/ontology/NCBITAXON/9606"))
		    sample.characteristics.append(characteristic_organism)
		    # check if field exists first
		    sampling_date = row['Sampling Date'] if not pandas.isnull(row['Sampling Date']) else None
		    sample_collection_process = Process(id_='sam_coll_proc',executes_protocol=sample_collection_protocol,date_=sampling_date)
		    aliquoting_process = Process(id_='sam_coll_proc',executes_protocol=aliquoting_protocol,date_=sampling_date)

		    sample_collection_process.inputs = [source]
		    aliquoting_process.outputs = [sample]

		    # links processes
		    plink(sample_collection_process, aliquoting_process)

		    study.process_sequence.append(sample_collection_process)
		    study.process_sequence.append(aliquoting_process)

		    study.samples.append(sample)


		study.protocols.append(sample_collection_protocol)
		study.protocols.append(aliquoting_protocol)

		### Add MS Assay ###
		ms_assay = Assay(filename='a_'+detailsDict['assay_filename']+'.txt',measurement_type=OntologyAnnotation(term="metabolite profiling"),technology_type=OntologyAnnotation(term="mass spectrometry"))
		extraction_protocol = Protocol(name='extraction', protocol_type=OntologyAnnotation(term="material extraction"))

		study.protocols.append(extraction_protocol)
		ms_protocol = Protocol(name='mass spectrometry', protocol_type=OntologyAnnotation(term="MS Assay"))
		ms_protocol.add_param('Run Order')
		ms_protocol.add_param('Instrument')
		ms_protocol.add_param('Sample Batch')
		ms_protocol.add_param('Acquisition Batch')


		study.protocols.append(ms_protocol)

		#for index, row in sampleMetadata.iterrows():
		for index, sample in enumerate(study.samples):
			row = self.sampleMetadata.loc[self.sampleMetadata['Sample File Name'].astype(str) == sample.name]

			# create an extraction process that executes the extraction protocol
			extraction_process = Process(executes_protocol=extraction_protocol)

			# extraction process takes as input a sample, and produces an extract material as output
			sample_name = sample.name
			sample = Sample(name=sample_name, derives_from=[source])

			extraction_process.inputs.append(sample)
			material = Material(name="extract-{}".format(index))
			material.type = "Extract Name"
			extraction_process.outputs.append(material)

			# create a ms process that executes the nmr protocol
			ms_process = Process(executes_protocol=ms_protocol,date_=datetime.isoformat(datetime.strptime(str(row['Acquired Time'].values[0]), '%Y-%m-%d %H:%M:%S')))

			ms_process.name = "assay-name-{}".format(index)
			ms_process.inputs.append(extraction_process.outputs[0])
			# nmr process usually has an output data file
			# check if field exists first
			assay_data_name = row['Assay data name'].values[0] if 'Assay data name' in self.sampleMetadata.columns else 'N/A'
			datafile = DataFile(filename=assay_data_name, label="MS Assay Name", generated_from=[sample])
			ms_process.outputs.append(datafile)

			#nmr_process.parameter_values.append(ParameterValue(category='Run Order',value=str(i)))
			ms_process.parameter_values = [ParameterValue(category=ms_protocol.get_param('Run Order'),value=row['Run Order'].values[0])]
			# check if field exists first
			instrument = row['Instrument'].values[0] if 'Instrument' in self.sampleMetadata.columns else 'N/A'
			ms_process.parameter_values.append(ParameterValue(category=ms_protocol.get_param('Instrument'),value=instrument))
			# check if field exists first
			sbatch = row['Sample batch'].values[0] if 'Sample batch' in self.sampleMetadata.columns else 'N/A'
			ms_process.parameter_values.append(ParameterValue(category=ms_protocol.get_param('Sample Batch'),value=sbatch))

			ms_process.parameter_values.append(ParameterValue(category=ms_protocol.get_param('Acquisition Batch'),value=row['Batch'].values[0]))

			# ensure Processes are linked forward and backward
			plink(extraction_process, ms_process)
			# make sure the extract, data file, and the processes are attached to the assay
			ms_assay.samples.append(sample)
			ms_assay.data_files.append(datafile)
			ms_assay.other_material.append(material)
			ms_assay.process_sequence.append(extraction_process)
			ms_assay.process_sequence.append(ms_process)
			ms_assay.measurement_type = OntologyAnnotation(term="metabolite profiling")
			ms_assay.technology_type = OntologyAnnotation(term="mass spectrometry")

		# attach the assay to the study
		study.assays.append(ms_assay)

		if os.path.exists(os.path.join(destinationPath,'i_Investigation.txt')):
			ie.appendStudytoISA(study, destinationPath)
		else:
			isatab.dump(isa_obj=investigation, output_path=destinationPath)


	def validateObject(self, verbose=True, raiseError=False, raiseWarning=True):
		"""
		Checks that all the attributes specified in the class definition are present and of the required class and/or values.

		Returns 4 boolean: is the object a *Dataset* < a *basic MSDataset* < has the object *parameters for QC* < *has the object sample metadata*.

		To employ all class methods, the most inclusive (*has the object sample metadata*) must be successful:

		* *'Basic MSDataset'* checks Dataset types and uniqueness as well as additional attributes.
		* *'has parameters for QC'* is *'Basic MSDataset'* + *sampleMetadata[['SampleType, AssayRole, Dilution, Run Order, Batch, Correction Batch, Sample Base Name]]*
		* *'has sample metadata'* is *'has parameters for QC'* + *sampleMetadata[['Sample ID', 'Subject ID', 'Matrix']]*

		Column type() in pandas.DataFrame are established on the first sample when necessary
		Does not check for uniqueness in :py:attr:`~sampleMetadata['Sample File Name']`
		Does not currently check :py:attr:`~Attributes['Raw Data Path']` type
		Does not currently check :py:attr:`~corrExclusions` type

		:param verbose: if True the result of each check is printed (default True)
		:type verbose: bool
		:param raiseError: if True an error is raised when a check fails and the validation is interrupted (default False)
		:type raiseError: bool
		:param raiseWarning: if True a warning is raised when a check fails
		:type raiseWarning: bool
		:return: A dictionary of 4 boolean with True if the Object conforms to the corresponding test. *'Dataset'* conforms to :py:class:`~Dataset`, *'BasicMSDataset'* conforms to :py:class:`~Dataset` + basic :py:class:`~MSDataset`, *'QC'* BasicMSDataset + object has QC parameters, *'sampleMetadata'* QC + object has sample metadata information
		:rtype: dict

		:raises TypeError: if the Object class is wrong
		:raises AttributeError: if self.Attributes['rtWindow'] does not exist
		:raises TypeError: if self.Attributes['rtWindow'] is not an int or float
		:raises AttributeError: if self.Attributes['msPrecision'] does not exist
		:raises TypeError: if self.Attributes['msPrecision'] is not an int or float
		:raises AttributeError: if self.Attributes['varianceRatio'] does not exist
		:raises TypeError: if self.Attributes['varianceRatio'] is not an int or float
		:raises AttributeError: if self.Attributes['blankThreshold'] does not exist
		:raises TypeError: if self.Attributes['blankThreshold'] is not an int or float
		:raises AttributeError: if self.Attributes['corrMethod'] does not exist
		:raises TypeError: if self.Attributes['corrMethod'] is not a str
		:raises AttributeError: if self.Attributes['corrThreshold'] does not exist
		:raises TypeError: if self.Attributes['corrThreshold'] is not an int or float
		:raises AttributeError: if self.Attributes['rsdThreshold'] does not exist
		:raises TypeError: if self.Attributes['rsdThreshold'] is not an int or float
		:raises AttributeError: if self.Attributes['artifactualFilter'] does not exist
		:raises TypeError: if self.Attributes['artifactualFilter'] is not a bool
		:raises AttributeError: if self.Attributes['deltaMzArtifactual'] does not exist
		:raises TypeError: if self.Attributes['deltaMzArtifactual'] is not an int or float
		:raises AttributeError: if self.Attributes['overlapThresholdArtifactual'] does not exist
		:raises TypeError: if self.Attributes['overlapThresholdArtifactual'] is not an int or float
		:raises AttributeError: if self.Attributes['corrThresholdArtifactual'] does not exist
		:raises TypeError: if self.Attributes['corrThresholdArtifactual'] is not an int or float
		:raises AttributeError: if self.Attributes['FeatureExtractionSoftware'] does not exist
		:raises TypeError: if self.Attributes['FeatureExtractionSoftware'] is not a str
		:raises AttributeError: if self.Attributes['Raw Data Path'] does not exist
		:raises TypeError: if self.Attributes['Raw Data Path'] is not a str
		:raises AttributeError: if self.Attributes['Feature Names'] does not exist
		:raises TypeError: if self.Attributes['Feature Names'] is not a str
		:raises TypeError: if self.VariableType is not an enum 'VariableType'
		:raises AttributeError: if self.corrExclusions does not exist
		:raises AttributeError: if self._correlationToDilution does not exist
		:raises TypeError: if self._correlationToDilution is not a numpy.ndarray
		:raises AttributeError: if self._artifactualLinkageMatrix does not exist
		:raises TypeError: if self._artifactualLinkageMatrix is not a pandas.DataFrame
		:raises AttributeError: if self._tempArtifactualLinkageMatrix does not exist
		:raises TypeError: if self._tempArtifactualLinkageMatrix is not a pandas.DataFrame
		:raises AttributeError: if self.fileName does not exist
		:raises TypeError: if self.fileName is not a str
		:raises AttributeError: if self.filePath does not exist
		:raises TypeError: if self.filePath is not a str
		:raises ValueError: if self.sampleMetadata does not have the same number of samples as self._intensityData
		:raises TypeError: if self.sampleMetadata['Sample File Name'] is not str
		:raises TypeError: if self.sampleMetadata['AssayRole'] is not an enum 'AssayRole'
		:raises TypeError: if self.sampleMetadata['SampleType'] is not an enum 'SampleType'
		:raises TypeError: if self.sampleMetadata['Dilution'] is not an int or float
		:raises TypeError: if self.sampleMetadata['Batch'] is not an int or float
		:raises TypeError: if self.sampleMetadata['Correction Batch'] is not an int or float
		:raises TypeError: if self.sampleMetadata['Run Order'] is not an int
		:raises TypeError: if self.sampleMetadata['Acquired Time'] is not a datetime
		:raises TypeError: if self.sampleMetadata['Sample Base Name'] is not str
		:raises LookupError: if self.sampleMetadata does not have a Matrix column
		:raises TypeError: if self.sampleMetadata['Matrix'] is not a str
		:raises LookupError: if self.sampleMetadata does not have a Subject ID column
		:raises TypeError: if self.sampleMetadata['Subject ID'] is not a str
		:raises TypeError: if self.sampleMetadata['Sampling ID'] is not a str
		:raises ValueError: if self.featureMetadata does not have the same number of features as self._intensityData
		:raises TypeError: if self.featureMetadata['Feature Name'] is not a str
		:raises ValueError: if self.featureMetadata['Feature Name'] is not unique
		:raises LookupError: if self.featureMetadata does not have a m/z column
		:raises TypeError: if self.featureMetadata['m/z'] is not an int or float
		:raises LookupError: if self.featureMetadata does not have a Retention Time column
		:raises TypeError: if self.featureMetadata['Retention Time'] is not an int or float
		:raises ValueError: if self.sampleMask has not been initialised
		:raises ValueError: if self.sampleMask does not have the same number of samples as self._intensityData
		:raises ValueError: if self.featureMask has not been initialised
		:raises ValueError: if self.featureMask does not have the same number of features as self._intensityData
		"""

		def conditionTest(successCond, successMsg, failureMsg, allFailures, verb, raiseErr, raiseWarn, exception):
			if not successCond:
				allFailures.append(failureMsg)
				msg = failureMsg
				if raiseWarn:
					warnings.warn(msg)
				if raiseErr:
					raise exception
			else:
				msg = successMsg
			if verb:
				print(msg)
			return (allFailures)

		## init
		failureListBasic = []
		failureListQC	= []
		failureListMeta  = []
		# reference number of samples / features, from _intensityData
		refNumSamples = None
		refNumFeatures = None
		# reference number of exclusions in list, from sampleMetadataExcluded
		refNumExcluded = None

		# First check it conforms to Dataset
		if super().validateObject(verbose=verbose, raiseError=raiseError, raiseWarning=raiseWarning):
			## Check object class
			condition = isinstance(self, MSDataset)
			success = 'Check Object class:\tOK'
			failure = 'Check Object class:\tFailure, not MSDataset, but ' + str(type(self))
			failureListBasic = conditionTest(condition, success, failure, failureListBasic, verbose, raiseError, raiseWarning, exception=TypeError(failure))

			# Attributes
			## rtWindow
			# exist
			condition = 'rtWindow' in self.Attributes
			success = 'Check self.Attributes[\'rtWindow\'] exists:\tOK'
			failure = 'Check self.Attributes[\'rtWindow\'] exists:\tFailure, no attribute \'self.Attributes[\'rtWindow\']\''
			failureListBasic = conditionTest(condition, success, failure, failureListBasic, verbose, raiseError, raiseWarning, exception=AttributeError(failure))
			if condition:
				# is an int or float
				condition = isinstance(self.Attributes['rtWindow'], (int, float, numpy.integer, numpy.floating))
				success = 'Check self.Attributes[\'rtWindow\'] is an int or float:\tOK'
				failure = 'Check self.Attributes[\'rtWindow\'] is an int or float:\tFailure, \'self.Attributes[\'rtWindow\']\' is ' + str(type(self.Attributes['rtWindow']))
				failureListBasic = conditionTest(condition, success, failure, failureListBasic, verbose, raiseError, raiseWarning, exception=TypeError(failure))
			# end self.Attributes['rtWindow']
			## msPrecision
			# exist
			condition = 'msPrecision' in self.Attributes
			success = 'Check self.Attributes[\'msPrecision\'] exists:\tOK'
			failure = 'Check self.Attributes[\'msPrecision\'] exists:\tFailure, no attribute \'self.Attributes[\'msPrecision\']\''
			failureListBasic = conditionTest(condition, success, failure, failureListBasic, verbose, raiseError, raiseWarning, exception=AttributeError(failure))
			if condition:
				# is an int or float
				condition = isinstance(self.Attributes['msPrecision'], (int, float, numpy.integer, numpy.floating))
				success = 'Check self.Attributes[\'msPrecision\'] is an int or float:\tOK'
				failure = 'Check self.Attributes[\'msPrecision\'] is an int or float:\tFailure, \'self.Attributes[\'msPrecision\']\' is ' + str(type(self.Attributes['msPrecision']))
				failureListBasic = conditionTest(condition, success, failure, failureListBasic, verbose, raiseError, raiseWarning, exception=TypeError(failure))
			# end self.Attributes['rtWindow']
			## varianceRatio
			# exist
			condition = 'varianceRatio' in self.Attributes
			success = 'Check self.Attributes[\'varianceRatio\'] exists:\tOK'
			failure = 'Check self.Attributes[\'varianceRatio\'] exists:\tFailure, no attribute \'self.Attributes[\'varianceRatio\']\''
			failureListBasic = conditionTest(condition, success, failure, failureListBasic, verbose, raiseError, raiseWarning, exception=AttributeError(failure))
			if condition:
				# is an int or float
				condition = isinstance(self.Attributes['varianceRatio'],(int, float, numpy.integer, numpy.floating))
				success = 'Check self.Attributes[\'varianceRatio\'] is an int or float:\tOK'
				failure = 'Check self.Attributes[\'varianceRatio\'] is an int or float:\tFailure, \'self.Attributes[\'varianceRatio\']\' is ' + str(type(self.Attributes['varianceRatio']))
				failureListBasic = conditionTest(condition, success, failure, failureListBasic, verbose, raiseError, raiseWarning, exception=TypeError(failure))
			# end self.Attributes['varianceRatio']
			## blankThreshold
			# exist
			condition = 'blankThreshold' in self.Attributes
			success = 'Check self.Attributes[\'blankThreshold\'] exists:\tOK'
			failure = 'Check self.Attributes[\'blankThreshold\'] exists:\tFailure, no attribute \'self.Attributes[\'blankThreshold\']\''
			failureListBasic = conditionTest(condition, success, failure, failureListBasic, verbose, raiseError, raiseWarning, exception=AttributeError(failure))
			if condition:
				# is an int or float
				condition = isinstance(self.Attributes['blankThreshold'], (int, float, numpy.integer, numpy.floating))
				success = 'Check self.Attributes[\'blankThreshold\'] is an int or float:\tOK'
				failure = 'Check self.Attributes[\'blankThreshold\'] is an int or float:\tFailure, \'self.Attributes[\'blankThreshold\']\' is ' + str(type(self.Attributes['blankThreshold']))
				failureListBasic = conditionTest(condition, success, failure, failureListBasic, verbose, raiseError, raiseWarning, exception=TypeError(failure))
			# end self.Attributes['blankThreshold']
			## peakWidthWindow
			# exist
			condition = 'peakWidthWindow' in self.Attributes
			success = 'Check self.Attributes[\'peakWidthWindow\'] exists:\tOK'
			failure = 'Check self.Attributes[\'peakWidthWindow\'] exists:\tFailure, no attribute \'self.Attributes[\'peakWidthWindow\']\''
			failureListBasic = conditionTest(condition, success, failure, failureListBasic, verbose, raiseError, raiseWarning, exception=AttributeError(failure))
			if condition:
				# is an int or float
				condition = isinstance(self.Attributes['peakWidthWindow'], (int, float, numpy.integer, numpy.floating))
				success = 'Check self.Attributes[\'peakWidthWindow\'] is an int or float:\tOK'
				failure = 'Check self.Attributes[\'peakWidthWindow\'] is an int or float:\tFailure, \'self.Attributes[\'peakWidthWindow\']\' is ' + str(type(self.Attributes['peakWidthWindow']))
				failureListBasic = conditionTest(condition, success, failure, failureListBasic, verbose, raiseError, raiseWarning, exception=TypeError(failure))
			# end self.Attributes['peakWidthWindow']
			## corrMethod
			# exist
			condition = 'corrMethod' in self.Attributes
			success = 'Check self.Attributes[\'corrMethod\'] exists:\tOK'
			failure = 'Check self.Attributes[\'corrMethod\'] exists:\tFailure, no attribute \'self.Attributes[\'corrMethod\']\''
			failureListBasic = conditionTest(condition, success, failure, failureListBasic, verbose, raiseError, raiseWarning, exception=AttributeError(failure))
			if condition:
				# is a str
				condition = isinstance(self.Attributes['corrMethod'], str)
				success = 'Check self.Attributes[\'corrMethod\'] is a str:\tOK'
				failure = 'Check self.Attributes[\'corrMethod\'] is a str:\tFailure, \'self.Attributes[\'corrMethod\']\' is ' + str(type(self.Attributes['corrMethod']))
				failureListBasic = conditionTest(condition, success, failure, failureListBasic, verbose, raiseError, raiseWarning, exception=TypeError(failure))
			# end self.Attributes['corrMethod']
			## corrThreshold
			# exist
			condition = 'corrThreshold' in self.Attributes
			success = 'Check self.Attributes[\'corrThreshold\'] exists:\tOK'
			failure = 'Check self.Attributes[\'corrThreshold\'] exists:\tFailure, no attribute \'self.Attributes[\'corrThreshold\']\''
			failureListBasic = conditionTest(condition, success, failure, failureListBasic, verbose, raiseError, raiseWarning, exception=AttributeError(failure))
			if condition:
				# is an int or float
				condition = isinstance(self.Attributes['corrThreshold'], (int, float, numpy.integer, numpy.floating))
				success = 'Check self.Attributes[\'corrThreshold\'] is an int or float:\tOK'
				failure = 'Check self.Attributes[\'corrThreshold\'] is an int or float:\tFailure, \'self.Attributes[\'corrThreshold\']\' is ' + str(type(self.Attributes['corrThreshold']))
				failureListBasic = conditionTest(condition, success, failure, failureListBasic, verbose, raiseError, raiseWarning, exception=TypeError(failure))
			# end self.Attributes['corrThreshold']
			## rsdThreshold
			# exist
			condition = 'rsdThreshold' in self.Attributes
			success = 'Check self.Attributes[\'rsdThreshold\'] exists:\tOK'
			failure = 'Check self.Attributes[\'rsdThreshold\'] exists:\tFailure, no attribute \'self.Attributes[\'rsdThreshold\']\''
			failureListBasic = conditionTest(condition, success, failure, failureListBasic, verbose, raiseError, raiseWarning, exception=AttributeError(failure))
			if condition:
				# is an int or float
				condition = isinstance(self.Attributes['rsdThreshold'], (int, float, numpy.integer, numpy.floating))
				success = 'Check self.Attributes[\'rsdThreshold\'] is an int or float:\tOK'
				failure = 'Check self.Attributes[\'rsdThreshold\'] is an int or float:\tFailure, \'self.Attributes[\'rsdThreshold\']\' is ' + str(type(self.Attributes['rsdThreshold']))
				failureListBasic = conditionTest(condition, success, failure, failureListBasic, verbose, raiseError, raiseWarning, exception=TypeError(failure))
			# end self.Attributes['rsdThreshold']
			## artifactualFilter
			# exist
			condition = 'artifactualFilter' in self.Attributes
			success = 'Check self.Attributes[\'artifactualFilter\'] exists:\tOK'
			failure = 'Check self.Attributes[\'artifactualFilter\'] exists:\tFailure, no attribute \'self.Attributes[\'artifactualFilter\']\''
			failureListBasic = conditionTest(condition, success, failure, failureListBasic, verbose, raiseError, raiseWarning, exception=AttributeError(failure))
			if condition:
				# is a bool
				condition = isinstance(self.Attributes['artifactualFilter'], bool)
				success = 'Check self.Attributes[\'artifactualFilter\'] is a bool:\tOK'
				failure = 'Check self.Attributes[\'artifactualFilter\'] is a bool:\tFailure, \'self.Attributes[\'artifactualFilter\']\' is ' + str(type(self.Attributes['artifactualFilter']))
				failureListBasic = conditionTest(condition, success, failure, failureListBasic, verbose, raiseError, raiseWarning, exception=TypeError(failure))
			# end self.Attributes['artifactualFilter']
			## deltaMzArtifactual
			# exist
			condition = 'deltaMzArtifactual' in self.Attributes
			success = 'Check self.Attributes[\'deltaMzArtifactual\'] exists:\tOK'
			failure = 'Check self.Attributes[\'deltaMzArtifactual\'] exists:\tFailure, no attribute \'self.Attributes[\'deltaMzArtifactual\']\''
			failureListBasic = conditionTest(condition, success, failure, failureListBasic, verbose, raiseError, raiseWarning, exception=AttributeError(failure))
			if condition:
				# is an int or float
				condition = isinstance(self.Attributes['deltaMzArtifactual'], (int, float, numpy.integer, numpy.floating))
				success = 'Check self.Attributes[\'deltaMzArtifactual\'] is an int or float:\tOK'
				failure = 'Check self.Attributes[\'deltaMzArtifactual\'] is an int or float:\tFailure, \'self.Attributes[\'deltaMzArtifactual\']\' is ' + str(type(self.Attributes['deltaMzArtifactual']))
				failureListBasic = conditionTest(condition, success, failure, failureListBasic, verbose, raiseError, raiseWarning, exception=TypeError(failure))
			# end self.Attributes['deltaMzArtifactual']
			## overlapThresholdArtifactual
			# exist
			condition = 'overlapThresholdArtifactual' in self.Attributes
			success = 'Check self.Attributes[\'overlapThresholdArtifactual\'] exists:\tOK'
			failure = 'Check self.Attributes[\'overlapThresholdArtifactual\'] exists:\tFailure, no attribute \'self.Attributes[\'overlapThresholdArtifactual\']\''
			failureListBasic = conditionTest(condition, success, failure, failureListBasic, verbose, raiseError, raiseWarning, exception=AttributeError(failure))
			if condition:
				# is an int or float
				condition = isinstance(self.Attributes['overlapThresholdArtifactual'], (int, float, numpy.integer, numpy.floating))
				success = 'Check self.Attributes[\'overlapThresholdArtifactual\'] is an int or float:\tOK'
				failure = 'Check self.Attributes[\'overlapThresholdArtifactual\'] is an int or float:\tFailure, \'self.Attributes[\'overlapThresholdArtifactual\']\' is ' + str(type(self.Attributes['overlapThresholdArtifactual']))
				failureListBasic = conditionTest(condition, success, failure, failureListBasic, verbose, raiseError, raiseWarning, exception=TypeError(failure))
			# end self.Attributes['overlapThresholdArtifactual']
			## corrThresholdArtifactual
			# exist
			condition = 'corrThresholdArtifactual' in self.Attributes
			success = 'Check self.Attributes[\'corrThresholdArtifactual\'] exists:\tOK'
			failure = 'Check self.Attributes[\'corrThresholdArtifactual\'] exists:\tFailure, no attribute \'self.Attributes[\'corrThresholdArtifactual\']\''
			failureListBasic = conditionTest(condition, success, failure, failureListBasic, verbose, raiseError, raiseWarning, exception=AttributeError(failure))
			if condition:
				# is an int or float
				condition = isinstance(self.Attributes['corrThresholdArtifactual'], (int, float, numpy.integer, numpy.floating))
				success = 'Check self.Attributes[\'corrThresholdArtifactual\'] is an int or float:\tOK'
				failure = 'Check self.Attributes[\'corrThresholdArtifactual\'] is an int or float:\tFailure, \'self.Attributes[\'corrThresholdArtifactual\']\' is ' + str(type(self.Attributes['corrThresholdArtifactual']))
				failureListBasic = conditionTest(condition, success, failure, failureListBasic, verbose, raiseError, raiseWarning, exception=TypeError(failure))
			# end self.Attributes['corrThresholdArtifactual']
			## FeatureExtractionSoftware
			# exist
			condition = 'FeatureExtractionSoftware' in self.Attributes
			success = 'Check self.Attributes[\'FeatureExtractionSoftware\'] exists:\tOK'
			failure = 'Check self.Attributes[\'FeatureExtractionSoftware\'] exists:\tFailure, no attribute \'self.Attributes[\'FeatureExtractionSoftware\']\''
			failureListBasic = conditionTest(condition, success, failure, failureListBasic, verbose, raiseError, raiseWarning, exception=AttributeError(failure))
			if condition:
				# is a str
				condition = isinstance(self.Attributes['FeatureExtractionSoftware'], str)
				success = 'Check self.Attributes[\'FeatureExtractionSoftware\'] is a str:\tOK'
				failure = 'Check self.Attributes[\'FeatureExtractionSoftware\'] is a str:\tFailure, \'self.Attributes[\'FeatureExtractionSoftware\']\' is ' + str(type(self.Attributes['FeatureExtractionSoftware']))
				failureListBasic = conditionTest(condition, success, failure, failureListBasic, verbose, raiseError, raiseWarning, exception=TypeError(failure))
			# end self.Attributes['FeatureExtractionSoftware']
			## Raw Data Path
			# exist
			condition = 'Raw Data Path' in self.Attributes
			success = 'Check self.Attributes[\'Raw Data Path\'] exists:\tOK'
			failure = 'Check self.Attributes[\'Raw Data Path\'] exists:\tFailure, no attribute \'self.Attributes[\'Raw Data Path\']\''
			failureListBasic = conditionTest(condition, success, failure, failureListBasic, verbose, raiseError, raiseWarning, exception=AttributeError(failure))
			if condition:
				if self.Attributes['Raw Data Path'] is not None:
					# is a str
					condition = isinstance(self.Attributes['Raw Data Path'], str)
					success = 'Check self.Attributes[\'Raw Data Path\'] is a str:\tOK'
					failure = 'Check self.Attributes[\'Raw Data Path\'] is a str:\tFailure, \'self.Attributes[\'Raw Data Path\']\' is ' + str(type(self.Attributes['Raw Data Path']))
					failureListBasic = conditionTest(condition, success, failure, failureListBasic, verbose, raiseError, raiseWarning, exception=TypeError(failure))
			# end self.Attributes['Raw Data Path']
			## Feature Names
			# exist
			condition = 'Feature Names' in self.Attributes
			success = 'Check self.Attributes[\'Feature Names\'] exists:\tOK'
			failure = 'Check self.Attributes[\'Feature Names\'] exists:\tFailure, no attribute \'self.Attributes[\'Feature Names\']\''
			failureListBasic = conditionTest(condition, success, failure, failureListBasic, verbose, raiseError, raiseWarning, exception=AttributeError(failure))
			if condition:
				# is a str
				condition = isinstance(self.Attributes['Feature Names'], str)
				success = 'Check self.Attributes[\'Feature Names\'] is a str:\tOK'
				failure = 'Check self.Attributes[\'Feature Names\'] is a str:\tFailure, \'self.Attributes[\'Feature Names\']\' is ' + str(type(self.Attributes['Feature Names']))
				failureListBasic = conditionTest(condition, success, failure, failureListBasic, verbose, raiseError, raiseWarning, exception=TypeError(failure))
			# end self.Attributes['Feature Names']
			# end self.Attributes

			## self.VariableType
			# is a enum VariableType
			condition = isinstance(self.VariableType, VariableType)
			success = 'Check self.VariableType is an enum \'VariableType\':\tOK'
			failure = 'Check self.VariableType is an enum \'VariableType\':\tFailure, \'self.VariableType\' is ' + str(type(self.VariableType))
			failureListBasic = conditionTest(condition, success, failure, failureListBasic, verbose, raiseError, raiseWarning, exception=TypeError(failure))
			# end Variabletype

			## self.corrExclusions
			# exist
			condition = hasattr(self, 'corrExclusions')
			success = 'Check self.corrExclusions exists:\tOK'
			failure = 'Check self.corrExclusions exists:\tFailure, no attribute \'self.corrExclusions\''
			failureListBasic = conditionTest(condition, success, failure, failureListBasic, verbose, raiseError, raiseWarning, exception=AttributeError(failure))
			#if condition:
			# 	 # which test here?
			#	 condition = isinstance(self.corrExclusions, str)
			#	 success = 'Check self.corrExclusions is a str:\tOK'
			#	 failure = 'Check self.corrExclusions is a str:\tFailure, \'self.corrExclusions\' is ' + str(type(self.corrExclusions))
			#	 failureListBasic = conditionTest(condition, success, failure, failureListBasic, verbose, raiseError, raiseWarning, exception=TypeError(failure))
			# end self.corrExclusions

			## self._correlationToDilution
			# exist
			condition = hasattr(self, '_correlationToDilution')
			success = 'Check self._correlationToDilution exists:\tOK'
			failure = 'Check self._correlationToDilution exists:\tFailure, no attribute \'self._correlationToDilution\''
			failureListBasic = conditionTest(condition, success, failure, failureListBasic, verbose, raiseError, raiseWarning, exception=AttributeError(failure))
			if condition:
				# is numpy.ndarray
				condition = isinstance(self._correlationToDilution, numpy.ndarray)
				success = 'Check self._correlationToDilution is a numpy.ndarray:\tOK'
				failure = 'Check self._correlationToDilution is a numpy.ndarray:\tFailure, \'self._correlationToDilution\' is ' + str(type(self._correlationToDilution))
				failureListBasic = conditionTest(condition, success, failure, failureListBasic, verbose, raiseError, raiseWarning, exception=TypeError(failure))
			# end self._correlationToDilution

			## self._artifactualLinkageMatrix
			# exist
			condition = hasattr(self, '_artifactualLinkageMatrix')
			success = 'Check self._artifactualLinkageMatrix exists:\tOK'
			failure = 'Check self._artifactualLinkageMatrix exists:\tFailure, no attribute \'self._artifactualLinkageMatrix\''
			failureListBasic = conditionTest(condition, success, failure, failureListBasic, verbose, raiseError, raiseWarning, exception=AttributeError(failure))
			if condition:
				# is pandas.DataFrame
				condition = isinstance(self._artifactualLinkageMatrix, pandas.DataFrame)
				success = 'Check self._artifactualLinkageMatrix is a pandas.DataFrame:\tOK'
				failure = 'Check self._artifactualLinkageMatrix is a pandas.DataFrame:\tFailure, \'self._artifactualLinkageMatrix\' is ' + str(type(self._artifactualLinkageMatrix))
				failureListBasic = conditionTest(condition, success, failure, failureListBasic, verbose, raiseError, raiseWarning, exception=TypeError(failure))
			# end self._artifactualLinkageMatrix

			## self._tempArtifactualLinkageMatrix
			# exist
			condition = hasattr(self, '_tempArtifactualLinkageMatrix')
			success = 'Check self._tempArtifactualLinkageMatrix exists:\tOK'
			failure = 'Check self._tempArtifactualLinkageMatrix exists:\tFailure, no attribute \'self._tempArtifactualLinkageMatrix\''
			failureListBasic = conditionTest(condition, success, failure, failureListBasic, verbose, raiseError, raiseWarning, exception=AttributeError(failure))
			if condition:
				# is pandas.DataFrame
				condition = isinstance(self._tempArtifactualLinkageMatrix, pandas.DataFrame)
				success = 'Check self._tempArtifactualLinkageMatrix is a pandas.DataFrame:\tOK'
				failure = 'Check self._tempArtifactualLinkageMatrix is a pandas.DataFrame:\tFailure, \'self._tempArtifactualLinkageMatrix\' is ' + str(type(self._tempArtifactualLinkageMatrix))
				failureListBasic = conditionTest(condition, success, failure, failureListBasic, verbose, raiseError, raiseWarning, exception=TypeError(failure))
			# end self._tempArtifactualLinkageMatrix

			## self.fileName
			# exist
			condition = hasattr(self, 'fileName')
			success = 'Check self.fileName exists:\tOK'
			failure = 'Check self.fileName exists:\tFailure, no attribute \'self.fileName\''
			failureListBasic = conditionTest(condition, success, failure, failureListBasic, verbose, raiseError, raiseWarning, exception=AttributeError(failure))
			if condition:
				# is a str
				condition = isinstance(self.fileName, str)
				success = 'Check self.fileName is a str:\tOK'
				failure = 'Check self.fileName is a str:\tFailure, \'self.fileName\' is ' + str(type(self.fileName))
				failureListBasic = conditionTest(condition, success, failure, failureListBasic, verbose, raiseError, raiseWarning, exception=TypeError(failure))
			# end self.fileName

			## self.filePath
			# exist
			condition = hasattr(self, 'filePath')
			success = 'Check self.filePath exists:\tOK'
			failure = 'Check self.filePath exists:\tFailure, no attribute \'self.filePath\''
			failureListBasic = conditionTest(condition, success, failure, failureListBasic, verbose, raiseError, raiseWarning, exception=AttributeError(failure))
			if condition:
				# is a str
				condition = isinstance(self.filePath, str)
				success = 'Check self.filePath is a str:\tOK'
				failure = 'Check self.filePath is a str:\tFailure, \'self.filePath\' is ' + str(type(self.filePath))
				failureListBasic = conditionTest(condition, success, failure, failureListBasic, verbose, raiseError, raiseWarning, exception=TypeError(failure))
			# end self.filePath

			## self._intensityData
			# Use _intensityData as size reference for all future tables
			if (self._intensityData.all() != numpy.array(None).all()):
				refNumSamples = self._intensityData.shape[0]
				refNumFeatures = self._intensityData.shape[1]
				if verbose:
					print('---- self._intensityData used as size reference ----')
					print('\t' + str(refNumSamples) + ' samples, ' + str(refNumFeatures) + ' features')
			# end self._intensityData

			## self.sampleMetadata
			# number of samples
			condition = (self.sampleMetadata.shape[0] == refNumSamples)
			success = 'Check self.sampleMetadata number of samples (rows):\tOK'
			failure = 'Check self.sampleMetadata number of samples (rows):\tFailure, \'self.sampleMetadata\' has ' + str(self.sampleMetadata.shape[0]) + ' samples, ' + str(refNumSamples) + ' expected'
			failureListBasic = conditionTest(condition, success, failure, failureListBasic, verbose, raiseError, raiseWarning, exception=ValueError(failure))
			if condition:
				# sampleMetadata['Sample File Name'] is str
				condition = isinstance(self.sampleMetadata['Sample File Name'][0], str)
				success = 'Check self.sampleMetadata[\'Sample File Name\'] is str:\tOK'
				failure = 'Check self.sampleMetadata[\'Sample File Name\'] is str:\tFailure, \'self.sampleMetadata[\'Sample File Name\']\' is ' + str(type(self.sampleMetadata['Sample File Name'][0]))
				failureListBasic = conditionTest(condition, success, failure, failureListBasic, verbose, raiseError, raiseWarning, exception=TypeError(failure))

				## Fields required for QC
				# sampleMetadata['AssayRole'] is enum AssayRole
				condition = isinstance(self.sampleMetadata['AssayRole'][0], AssayRole)
				success = 'Check self.sampleMetadata[\'AssayRole\'] is an enum \'AssayRole\':\tOK'
				failure = 'Check self.sampleMetadata[\'AssayRole\'] is an enum \'AssayRole\':\tFailure, \'self.sampleMetadata[\'AssayRole\']\' is ' + str(type(self.sampleMetadata['AssayRole'][0]))
				failureListQC = conditionTest(condition, success, failure, failureListQC, verbose, raiseError, raiseWarning, exception=TypeError(failure))
				# sampleMetadata['SampleType'] is enum SampleType
				condition = isinstance(self.sampleMetadata['SampleType'][0], SampleType)
				success = 'Check self.sampleMetadata[\'SampleType\'] is an enum \'SampleType\':\tOK'
				failure = 'Check self.sampleMetadata[\'SampleType\'] is an enum \'SampleType\':\tFailure, \'self.sampleMetadata[\'SampleType\']\' is ' + str(type(self.sampleMetadata['SampleType'][0]))
				failureListQC = conditionTest(condition, success, failure, failureListQC, verbose, raiseError, raiseWarning, exception=TypeError(failure))
				# sampleMetadata['Dilution'] is an int or float
				condition = isinstance(self.sampleMetadata['Dilution'][0], (int, float, numpy.integer, numpy.floating))
				success = 'Check self.sampleMetadata[\'Dilution\'] is int or float:\tOK'
				failure = 'Check self.sampleMetadata[\'Dilution\'] is int or float:\tFailure, \'self.sampleMetadata[\'Dilution\']\' is ' + str(type(self.sampleMetadata['Dilution'][0]))
				failureListQC = conditionTest(condition, success, failure, failureListQC, verbose, raiseError, raiseWarning, exception=TypeError(failure))
				# sampleMetadata['Batch'] is an int or float
				condition = isinstance(self.sampleMetadata['Batch'][0], (int, float, numpy.integer, numpy.floating))
				success = 'Check self.sampleMetadata[\'Batch\'] is int or float:\tOK'
				failure = 'Check self.sampleMetadata[\'Batch\'] is int or float:\tFailure, \'self.sampleMetadata[\'Batch\']\' is ' + str(type(self.sampleMetadata['Batch'][0]))
				failureListQC = conditionTest(condition, success, failure, failureListQC, verbose, raiseError, raiseWarning, exception=TypeError(failure))
				# sampleMetadata['Correction Batch'] is an int or float
				condition = isinstance(self.sampleMetadata['Correction Batch'][0], (int, float, numpy.integer, numpy.floating))
				success = 'Check self.sampleMetadata[\'Correction Batch\'] is int or float:\tOK'
				failure = 'Check self.sampleMetadata[\'Correction Batch\'] is int or float:\tFailure, \'self.sampleMetadata[\'Correction Batch\']\' is ' + str(type(self.sampleMetadata['Correction Batch'][0]))
				failureListQC = conditionTest(condition, success, failure, failureListQC, verbose, raiseError, raiseWarning, exception=TypeError(failure))
				# sampleMetadata['Run Order'] is an int
				condition = isinstance(self.sampleMetadata['Run Order'][0], (int, numpy.integer))
				success = 'Check self.sampleMetadata[\'Run Order\'] is int:\tOK'
				failure = 'Check self.sampleMetadata[\'Run Order\'] is int:\tFailure, \'self.sampleMetadata[\'Run Order\']\' is ' + str(type(self.sampleMetadata['Run Order'][0]))
				failureListQC = conditionTest(condition, success, failure, failureListQC, verbose, raiseError, raiseWarning, exception=TypeError(failure))
				# sampleMetadata['Acquired Time'] is datetime.datetime
				condition = isinstance(self.sampleMetadata['Acquired Time'][0], datetime)
				success = 'Check self.sampleMetadata[\'Acquired Time\'] is datetime:\tOK'
				failure = 'Check self.sampleMetadata[\'Acquired Time\'] is datetime:\tFailure, \'self.sampleMetadata[\'Acquired Time\']\' is ' + str(type(self.sampleMetadata['Acquired Time'][0]))
				failureListQC = conditionTest(condition, success, failure, failureListQC, verbose, raiseError, raiseWarning, exception=TypeError(failure))
				# sampleMetadata['Sample Base Name'] is str
				condition = isinstance(self.sampleMetadata['Sample Base Name'][0], str)
				success = 'Check self.sampleMetadata[\'Sample Base Name\'] is str:\tOK'
				failure = 'Check self.sampleMetadata[\'Sample Base Name\'] is str:\tFailure, \'self.sampleMetadata[\'Sample Base Name\']\' is ' + str(type(self.sampleMetadata['Sample Base Name'][0]))
				failureListQC = conditionTest(condition, success, failure, failureListQC, verbose, raiseError, raiseWarning, exception=TypeError(failure))

				## Sample metadata fields
				# ['Matrix']
				condition = ('Matrix' in self.sampleMetadata.columns)
				success = 'Check self.sampleMetadata[\'Matrix\'] exists:\tOK'
				failure = 'Check self.sampleMetadata[\'Matrix\'] exists:\tFailure, \'self.sampleMetadata\' lacks a \'Matrix\' column'
				failureListMeta = conditionTest(condition, success, failure, failureListMeta, verbose, raiseError, raiseWarning, exception=LookupError(failure))
				if condition:
					# sampleMetadata['Matrix'] is str
					condition = isinstance(self.sampleMetadata['Matrix'][0], str)
					success = 'Check self.sampleMetadata[\'Matrix\'] is str:\tOK'
					failure = 'Check self.sampleMetadata[\'Matrix\'] is str:\tFailure, \'self.sampleMetadata[\'Matrix\']\' is ' + str(type(self.sampleMetadata['Matrix'][0]))
					failureListMeta = conditionTest(condition, success, failure, failureListMeta, verbose, raiseError, raiseWarning, exception=TypeError(failure))
				# end self.sampleMetadata['Matrix']
				# ['Subject ID']
				condition = ('Subject ID' in self.sampleMetadata.columns)
				success = 'Check self.sampleMetadata[\'Subject ID\'] exists:\tOK'
				failure = 'Check self.sampleMetadata[\'Subject ID\'] exists:\tFailure, \'self.sampleMetadata\' lacks a \'Subject ID\' column'
				failureListMeta = conditionTest(condition, success, failure, failureListMeta, verbose, raiseError, raiseWarning, exception=LookupError(failure))
				if condition:
					# sampleMetadata['Subject ID'] is str
					condition = (self.sampleMetadata['Subject ID'].dtype == numpy.dtype('O'))
					success = 'Check self.sampleMetadata[\'Subject ID\'] is str:\tOK'
					failure = 'Check self.sampleMetadata[\'Subject ID\'] is str:\tFailure, \'self.sampleMetadata[\'Subject ID\']\' is ' + str(type(self.sampleMetadata['Subject ID'][0]))
					failureListMeta = conditionTest(condition, success, failure, failureListMeta, verbose, raiseError, raiseWarning, exception=TypeError(failure))
				# end self.sampleMetadata['Subject ID']
				# sampleMetadata['Sampling ID'] is str
				condition = (self.sampleMetadata['Sampling ID'].dtype == numpy.dtype('O'))
				success = 'Check self.sampleMetadata[\'Sampling ID\'] is str:\tOK'
				failure = 'Check self.sampleMetadata[\'Sampling ID\'] is str:\tFailure, \'self.sampleMetadata[\'Sampling ID\']\' is ' + str(type(self.sampleMetadata['Sampling ID'][0]))
				failureListMeta = conditionTest(condition, success, failure, failureListMeta, verbose, raiseError, raiseWarning, exception=TypeError(failure))
			# end self.sampleMetadata number of samples
			# end self.sampleMetadata

			## self.featureMetadata
			# number of features
			condition = (self.featureMetadata.shape[0] == refNumFeatures)
			success = 'Check self.featureMetadata number of features (rows):\tOK'
			failure = 'Check self.featureMetadata number of features (rows):\tFailure, \'self.featureMetadata\' has ' + str(self.featureMetadata.shape[0]) + ' features, ' + str(refNumFeatures) + ' expected'
			failureListBasic = conditionTest(condition, success, failure, failureListBasic, verbose, raiseError, raiseWarning, exception=ValueError(failure))
			if condition & (self.featureMetadata.shape[0] != 0):
				# No point checking columns if the number of features is wrong or no samples
				# featureMetadata['Feature Name'] is str
				condition = isinstance(self.featureMetadata['Feature Name'][0], str)
				success = 'Check self.featureMetadata[\'Feature Name\'] is str:\tOK'
				failure = 'Check self.featureMetadata[\'Feature Name\'] is str:\tFailure, \'self.featureMetadata[\'Feature Name\']\' is ' + str(type(self.featureMetadata['Feature Name'][0]))
				failureListBasic = conditionTest(condition, success, failure, failureListBasic, verbose, raiseError, raiseWarning, exception=TypeError(failure))
				if condition:
					# featureMetadata['Feature Name'] are unique
					u_ids, u_counts = numpy.unique(self.featureMetadata['Feature Name'], return_counts=True)
					condition = all(u_counts == 1)
					success = 'Check self.featureMetadata[\'Feature Name\'] are unique:\tOK'
					failure = 'Check self.featureMetadata[\'Feature Name\'] are unique:\tFailure, the following \'self.featureMetadata[\'Feature Name\']\' are present more than once ' + str(u_ids[u_counts > 1].tolist())
					failureListBasic = conditionTest(condition, success, failure, failureListBasic, verbose, raiseError, raiseWarning, exception=ValueError(failure))
				# end self.featureMetadata['Feature Name']
				# ['m/z']
				condition = ('m/z' in self.featureMetadata.columns)
				success = 'Check self.featureMetadata[\'m/z\'] exists:\tOK'
				failure = 'Check self.featureMetadata[\'m/z\'] exists:\tFailure, \'self.featureMetadata\' lacks a \'m/z\' column'
				failureListBasic = conditionTest(condition, success, failure, failureListBasic, verbose, raiseError, raiseWarning, exception=LookupError(failure))
				if condition:
					# featureMetadata['m/z'] is int or float
					condition = isinstance(self.featureMetadata['m/z'][0], (int, float, numpy.integer, numpy.floating))
					success = 'Check self.featureMetadata[\'m/z\'] is int or float:\tOK'
					failure = 'Check self.featureMetadata[\'m/z\'] is int or float:\tFailure, \'self.featureMetadata[\'m/z\']\' is ' + str(type(self.featureMetadata['m/z'][0]))
					failureListBasic = conditionTest(condition, success, failure, failureListBasic, verbose, raiseError, raiseWarning, exception=TypeError(failure))
				# end self.featureMetadata['m/z']
				# ['Retention Time']
				condition = ('Retention Time' in self.featureMetadata.columns)
				success = 'Check self.featureMetadata[\'Retention Time\'] exists:\tOK'
				failure = 'Check self.featureMetadata[\'Retention Time\'] exists:\tFailure, \'self.featureMetadata\' lacks a \'Retention Time\' column'
				failureListBasic = conditionTest(condition, success, failure, failureListBasic, verbose, raiseError, raiseWarning, exception=LookupError(failure))
				if condition:
					# featureMetadata['Retention Time'] is int or float
					condition = isinstance(self.featureMetadata['Retention Time'][0], (int, float, numpy.integer, numpy.floating))
					success = 'Check self.featureMetadata[\'Retention Time\'] is int or float:\tOK'
					failure = 'Check self.featureMetadata[\'Retention Time\'] is int or float:\tFailure, \'self.featureMetadata[\'Retention Time\']\' is ' + str(type(self.featureMetadata['Retention Time'][0]))
					failureListBasic = conditionTest(condition, success, failure, failureListBasic, verbose, raiseError, raiseWarning, exception=TypeError(failure))
				# end self.featureMetadata['Retention Time']
			# end self.featureMetadata number of features
			# end self.featureMetadata

			## self.sampleMask
			# is initialised
			condition = (self.sampleMask.shape != ())
			success = 'Check self.sampleMask is initialised:\tOK'
			failure = 'Check self.sampleMask is initialised:\tFailure, \'self.sampleMask\' is not initialised'
			failureListBasic = conditionTest(condition, success, failure, failureListBasic, verbose, raiseError, raiseWarning, exception=ValueError(failure))
			if condition:
				# number of samples
				condition = (self.sampleMask.shape == (refNumSamples,))
				success = 'Check self.sampleMask number of samples:\tOK'
				failure = 'Check self.sampleMask number of samples:\tFailure, \'self.sampleMask\' has ' + str(self.sampleMask.shape[0]) + ' samples, ' + str(refNumSamples) + ' expected'
				failureListBasic = conditionTest(condition, success, failure, failureListBasic, verbose, raiseError, raiseWarning, exception=ValueError(failure))
			## end self.sampleMask

			## self.featureMask
			# is initialised
			condition = (self.featureMask.shape != ())
			success = 'Check self.featureMask is initialised:\tOK'
			failure = 'Check self.featureMask is initialised:\tFailure, \'self.featureMask\' is not initialised'
			failureListBasic = conditionTest(condition, success, failure, failureListBasic, verbose, raiseError, raiseWarning, exception=ValueError(failure))
			if condition:
				# number of features
				condition = (self.featureMask.shape == (refNumFeatures,))
				success = 'Check self.featureMask number of features:\tOK'
				failure = 'Check self.featureMask number of features:\tFailure, \'self.featureMask\' has ' + str(self.featureMask.shape[0]) + ' features, ' + str(refNumFeatures) + ' expected'
				failureListBasic = conditionTest(condition, success, failure, failureListBasic, verbose, raiseError, raiseWarning, exception=ValueError(failure))
			## end self.featureMask


			## List additional attributes (print + log)
			expectedSet = set({'Attributes', 'VariableType', '_Normalisation', '_name', 'fileName', 'filePath',
							   '_intensityData', 'sampleMetadata', 'featureMetadata', 'sampleMask',  'featureMask',
							   'sampleMetadataExcluded', 'intensityDataExcluded', 'featureMetadataExcluded', 'excludedFlag',
							   'corrExclusions', '_correlationToDilution', '_artifactualLinkageMatrix', '_tempArtifactualLinkageMatrix'})
			objectSet = set(self.__dict__.keys())
			additionalAttributes = objectSet - expectedSet
			if len(additionalAttributes) > 0:
				if verbose:
					print('--------')
					print(str(len(additionalAttributes)) + ' additional attributes in the object:')
					print('\t' + str(list(additionalAttributes)))
			else:
				if verbose:
					print('--------')
					print('No additional attributes in the object')

			## Log and final Output
			# Basic failure might compromise logging, failure of QC compromises sample meta
			if len(failureListBasic) == 0:
				# Prepare log text and bool
				if len(failureListQC) != 0:
					QCText = 'lacks parameters for QC'
					QCBool = False
					MetaText = 'lacks sample metadata'
					MetaBool = False
				else:
					QCText = 'has parameters for QC'
					QCBool = True
					if len(failureListMeta) != 0:
						MetaText = 'lacks sample metadata'
						MetaBool = False
					else:
						MetaText = 'has sample metadata'
						MetaBool = True
				# Log
				self.Attributes['Log'].append([datetime.now(), 'Dataset conforms to basic MSDataset (0 errors), %s (%d errors), %s (%d errors), (%i samples and %i features), with %d additional attributes in the object: %s. QC errors: %s, Meta errors: %s' % (QCText, len(failureListQC), MetaText, len(failureListMeta), self.noSamples, self.noFeatures, len(additionalAttributes), list(additionalAttributes), list(failureListQC), list(failureListMeta))])
				# print results
				if verbose:
					print('--------')
					print('Conforms to Dataset:\t 0 errors found')
					print('Conforms to basic MSDataset:\t 0 errors found')
					if QCBool:
						print('Has required parameters for QC:\t %d errors found' % ((len(failureListQC))))
					else:
						print('Does not have QC parameters:\t %d errors found' % ((len(failureListQC))))
					if MetaBool:
						print('Has sample metadata information:\t %d errors found' % ((len(failureListMeta))))
					else:
						print('Does not have sample metadata information:\t %d errors found' % ((len(failureListMeta))))
				# output
				if (not QCBool) & raiseWarning:
					warnings.warn('Does not have QC parameters:\t %d errors found' % ((len(failureListQC))))
				if (not MetaBool) & raiseWarning:
					warnings.warn('Does not have sample metadata information:\t %d errors found' % ((len(failureListMeta))))
				return({'Dataset': True, 'BasicMSDataset': True, 'QC': QCBool, 'sampleMetadata': MetaBool})

			# Try logging to something that might not have a log
			else:
				# try logging
				try:
					self.Attributes['Log'].append([datetime.now(), 'Failed basic MSDataset validation, with the following %d issues: %s' % (len(failureListBasic), failureListBasic)])
				except (AttributeError, KeyError, TypeError):
					if verbose:
						print('--------')
						print('Logging failed')
				# print results
				if verbose:
					print('--------')
					print('Conforms to Dataset:\t 0 errors found')
					print('Does not conform to basic MSDataset:\t %i errors found' % (len(failureListBasic)))
					print('Does not have QC parameters')
					print('Does not have sample metadata information')
				# output
				if raiseWarning:
					warnings.warn('Does not conform to basic MSDataset:\t %i errors found' % (len(failureListBasic)))
					warnings.warn('Does not have QC parameters')
					warnings.warn('Does not have sample metadata information')
				return({'Dataset': True, 'BasicMSDataset': False, 'QC': False, 'sampleMetadata': False})

		# If it's not a Dataset, no point checking anything more
		else:
			# try logging
			try:
				self.Attributes['Log'].append([datetime.now(), 'Failed basic MSDataset validation, Failed Dataset validation'])
			except (AttributeError, KeyError, TypeError):
				if verbose:
					print('--------')
					print('Logging failed')
			# print results
			if verbose:
				print('--------')
				print('Does not conform to Dataset')
				print('Does not conform to basic MSDataset')
				print('Does not have QC parameters')
				print('Does not have sample metadata information')
			# output
			if raiseWarning:
				warnings.warn('Does not conform to basic MSDataset')
				warnings.warn('Does not have QC parameters')
				warnings.warn('Does not have sample metadata information')
			return ({'Dataset': False, 'BasicMSDataset': False, 'QC': False, 'sampleMetadata': False})


def main():
	print("Implementation of " + os.path.split(os.path.dirname(inspect.getfile(nPYc)))[1])

if __name__=='__main__':
	main()
