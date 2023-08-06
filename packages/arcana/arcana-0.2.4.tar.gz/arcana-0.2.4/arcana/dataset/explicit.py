from builtins import str
from past.builtins import basestring
import os.path
import pydicom
from arcana.file_format import FileFormat, directory_format
from arcana.utils import split_extension
from arcana.exception import (
    ArcanaError, ArcanaFileFormatError, ArcanaUsageError,
    ArcanaFileFormatNotRegisteredError, ArcanaNameError)
from .base import BaseDataset, BaseField

DICOM_SERIES_NUMBER_TAG = ('0020', '0011')


class Dataset(BaseDataset):
    """
    A representation of a dataset within the repository.

    Parameters
    ----------
    name : str
        The name of the dataset
    format : FileFormat
        The file format used to store the dataset. Can be one of the
        recognised formats
    frequency : str
        One of 'per_session', 'per_subject', 'per_visit' and 'per_project',
        specifying whether the dataset is present for each session, subject,
        visit or project.
    derived : bool
        Whether the scan was generated or acquired. Depending on the repository
        used to store the dataset this is used to determine the location of the
        dataset.
    path : str | None
        The path to the dataset (for repositorys on the local system)
    id : int | None
        The ID of the dataset in the session. To be used to
        distinguish multiple datasets with the same scan type in the
        same session, e.g. scans taken before and after a task. For
        repositorys where this isn't stored (i.e. Local), id can be None
    subject_id : int | str | None
        The id of the subject which the dataset belongs to
    visit_id : int | str | None
        The id of the visit which the dataset belongs to
    repository : BaseRepository
        The repository which the dataset is stored
    """

    is_spec = False


    def __init__(self, name, format=None, derived=False,  # @ReservedAssignment @IgnorePep8
                 frequency='per_session', path=None,
                 id=None, uri=None, subject_id=None, visit_id=None,  # @ReservedAssignment @IgnorePep8
                 repository=None):
        super(Dataset, self).__init__(name, format, frequency)
        self._derived = derived
        self._path = path
        self._uri = uri
        self._subject_id = subject_id
        self._visit_id = visit_id
        self._repository = repository
        if id is None and path is not None and format.name == 'dicom':
            self._id = int(self.dicom_values([DICOM_SERIES_NUMBER_TAG])
                           [DICOM_SERIES_NUMBER_TAG])
        else:
            self._id = id

    def __eq__(self, other):
        return (super(Dataset, self).__eq__(other) and
                self.derived == other.derived and
                self._path == other._path and
                self.id == other.id and
                self.subject_id == other.subject_id and
                self.visit_id == other.visit_id)

    def __hash__(self):
        return (super(Dataset, self).__hash__() ^
                hash(self.derived) ^
                hash(self._path) ^
                hash(self.id) ^
                hash(self.subject_id) ^
                hash(self.visit_id))

    def __lt__(self, other):
        if isinstance(self.id, int) and isinstance(other.id, str):
            return True
        elif isinstance(self.id, str) and isinstance(other.id, int):
            return False
        else:
            return self.id < other.id

    def find_mismatch(self, other, indent=''):
        mismatch = super(Dataset, self).find_mismatch(other, indent)
        sub_indent = indent + '  '
        if self.derived != other.derived:
            mismatch += ('\n{}derived: self={} v other={}'
                         .format(sub_indent, self.derived,
                                 other.derived))
        if self._path != other._path:
            mismatch += ('\n{}path: self={} v other={}'
                         .format(sub_indent, self._path,
                                 other._path))
        if self._id != other._id:
            mismatch += ('\n{}id: self={} v other={}'
                         .format(sub_indent, self._id,
                                 other._id))
        if self.subject_id != other.subject_id:
            mismatch += ('\n{}subject_id: self={} v other={}'
                         .format(sub_indent, self.subject_id,
                                 other.subject_id))
        if self.visit_id != other.visit_id:
            mismatch += ('\n{}visit_id: self={} v other={}'
                         .format(sub_indent, self.visit_id,
                                 other.visit_id))
        if self.repository != other.repository:
            mismatch += ('\n{}repository: self={} v other={}'
                         .format(sub_indent, self.repository,
                                 other.repository))
        return mismatch

    @property
    def path(self):
        if self._path is None:
            if self.repository is not None:
                self._path = self.repository.cache(self)
            else:
                raise ArcanaError(
                    "Neither path nor repository has been set for Dataset "
                    "{}".format(self.name))
        return self._path

    def basename(self, **kwargs):  # @UnusedVariable
        return self.name

    @property
    def derived(self):
        return self._derived

    @property
    def id(self):
        if self._id is None:
            return self.name
        else:
            return self._id

    @property
    def uri(self):
        return self._uri

    @property
    def repository(self):
        return self._repository

    @property
    def subject_id(self):
        return self._subject_id

    @property
    def visit_id(self):
        return self._visit_id

    @classmethod
    def from_path(cls, path, frequency='per_session', format=None,  # @ReservedAssignment @IgnorePep8
                  subject_id=None, visit_id=None, repository=None):
        if not os.path.exists(path):
            raise ArcanaUsageError(
                "Attempting to read Dataset from path '{}' but it "
                "does not exist".format(path))
        if os.path.isdir(path):
            within_exts = frozenset(
                split_extension(f)[1] for f in os.listdir(path)
                if not f.startswith('.'))
            if format is None:
                # Try to guess format
                try:
                    format = FileFormat.by_within_dir_exts(within_exts)  # @ReservedAssignment @IgnorePep8
                except ArcanaFileFormatNotRegisteredError:
                    # Fall back to general directory format
                    format = directory_format  # @ReservedAssignment
            name = os.path.basename(path)
        else:
            filename = os.path.basename(path)
            name, ext = split_extension(filename)
            if format is None:
                try:
                    format = FileFormat.by_ext(ext)  # @ReservedAssignment @IgnorePep8
                except ArcanaFileFormatNotRegisteredError as e:
                    raise ArcanaFileFormatNotRegisteredError(
                        str(e) + ", which is required to identify the "
                        "format of the dataset at '{}'".format(path))
        return cls(name, format, frequency=frequency,
                   path=path, derived=False, subject_id=subject_id,
                   visit_id=visit_id, repository=repository)

    def dicom(self, index):
        """
        Returns a PyDicom object for the DICOM file at index 'index'

        Parameters
        ----------
        dataset : Dataset
            The dataset to read a DICOM file from
        index : int
            The index of the DICOM file in the dataset to read

        Returns
        -------
        dcm : pydicom.DICOM
            A PyDicom file object
        """
        if self.format.name != 'dicom':
            raise ArcanaFileFormatError(
                "Can not read DICOM header as {} is not in DICOM format"
                .format(self))
        fnames = sorted([f for f in os.listdir(self.path)
                         if not f.startswith('.')])
        with open(os.path.join(self.path, fnames[index]), 'rb') as f:
            dcm = pydicom.dcmread(f)
        return dcm

    def dicom_values(self, tags, repository_login=None):
        """
        Returns a dictionary with the DICOM header fields corresponding
        to the given tag names

        Parameters
        ----------
        tags : List[Tuple[str, str]]
            List of DICOM tag values as 2-tuple of strings, e.g.
            [('0080', '0020')]
        repository_login : <repository-login-object>
            A login object for the repository to avoid having to relogin
            for every dicom_header call.

        Returns
        -------
        dct : Dict[Tuple[str, str], str|int|float]
        """
        try:
            if (self._path is None and self._repository is not None and
                    hasattr(self.repository, 'dicom_header')):
                hdr = self.repository.dicom_header(
                    self, prev_login=repository_login)
                dct = {t: hdr[t] for t in tags}
            else:
                # Get the DICOM object for the first file in the dataset
                dcm = self.dicom(0)
                dct = {t: dcm[t].value for t in tags}
        except KeyError as e:
            raise ArcanaNameError(
                e.args[0], "{} does not have dicom tag {}".format(
                    self, e.args[0]))
        return dct

    def initkwargs(self):
        dct = super(Dataset, self).initkwargs()
        dct['derived'] = self.derived
        dct['path'] = self.path
        dct['id'] = self.id
        dct['uri'] = self.uri
        dct['repository'] = self.repository
        return dct


class Field(BaseField):
    """
    A representation of a value field in the repository.

    Parameters
    ----------
    name : str
        The name of the dataset
    dtype : type
        The datatype of the value. Can be one of (float, int, str)
    frequency : str
        One of 'per_session', 'per_subject', 'per_visit' and 'per_project',
        specifying whether the dataset is present for each session, subject,
        visit or project.
    derived : bool
        Whether or not the value belongs in the derived session or not
    subject_id : int | str | None
        The id of the subject which the field belongs to
    visit_id : int | str | None
        The id of the visit which the field belongs to
    repository : BaseRepository
        The repository which the field is stored
    """

    def __init__(self, name, value, frequency='per_session',
                 derived=False, subject_id=None, visit_id=None,
                 repository=None):
        if isinstance(value, int):
            dtype = int
        elif isinstance(value, float):
            dtype = float
        elif isinstance(value, basestring):
            # Attempt to implicitly convert from string
            try:
                value = int(value)
                dtype = int
            except ValueError:
                try:
                    value = float(value)
                    dtype = float
                except ValueError:
                    dtype = str
        else:
            raise ArcanaError(
                "Unrecognised field dtype {} (can be int, float or str)"
                .format(value))
        super(Field, self).__init__(
            name, dtype, frequency=frequency)
        self._value = value
        self._derived = derived
        self._subject_id = subject_id
        self._visit_id = visit_id
        self._repository = repository

    def __eq__(self, other):
        return (super(Field, self).__eq__(other) and
                self.derived == other.derived and
                self.value == other.value and
                self.subject_id == other.subject_id and
                self.visit_id == other.visit_id)

    def __hash__(self):
        return (super(Field, self).__hash__() ^
                hash(self.derived) ^
                hash(self.value) ^
                hash(self.subject_id) ^
                hash(self.visit_id))

    def find_mismatch(self, other, indent=''):
        mismatch = super(Field, self).find_mismatch(other, indent)
        sub_indent = indent + '  '
        if self.derived != other.derived:
            mismatch += ('\n{}derived: self={} v other={}'
                         .format(sub_indent, self.derived,
                                 other.derived))
        if self.value != other.value:
            mismatch += ('\n{}value: self={} v other={}'
                         .format(sub_indent, self.value,
                                 other.value))
        if self.subject_id != other.subject_id:
            mismatch += ('\n{}subject_id: self={} v other={}'
                         .format(sub_indent, self.subject_id,
                                 other.subject_id))
        if self.visit_id != other.visit_id:
            mismatch += ('\n{}visit_id: self={} v other={}'
                         .format(sub_indent, self.visit_id,
                                 other.visit_id))
        if self.repository != other.repository:
            mismatch += ('\n{}repository: self={} v other={}'
                         .format(sub_indent, self.repository,
                                 other.repository))
        return mismatch

    def __int__(self):
        return int(self.value)

    def __float__(self):
        return float(self.value)

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return ("{}(name='{}', value={}, frequency='{}', derived={},"
                " subject_id={}, visit_id={}, repository={})".format(
                    type(self).__name__, self.name, self.value,
                    self.frequency, self.derived, self.subject_id,
                    self.visit_id, self.repository))

    @property
    def derived(self):
        return self._derived

    def basename(self, **kwargs):  # @UnusedVariable
        return self.name

    @property
    def repository(self):
        return self._repository

    @property
    def value(self):
        return self._value

    @property
    def subject_id(self):
        return self._subject_id

    @property
    def visit_id(self):
        return self._visit_id

    def initkwargs(self):
        dct = {}
        dct['name'] = self.name
        dct['value'] = self.value
        dct['frequency'] = self.frequency
        dct['derived'] = self.derived
        dct['repository'] = self.repository
        return dct
