
from .fs import BaseFileSystem, DirListResult, FileSystemOperationError, NotAFileError, Path
from .copy import CopyHandler
from .copy import CopyDirectory, CopyFile, CopyFileSystemObject

class BaseFileSystemObject():

    def __init__(self, filesystem, path_str, copy_handler, *, _path=None):
        ' Constructor for BaseFileSystemObjects.\n        One of `path_str` and `_path` **MUST** be present.\n        '
        self._copy_handler = copy_handler
        self._fs = filesystem
        self._path = (_path or self._fs.parse_path((path_str or '')))

    @property
    def path(self):
        ' The full, absolute, path of self in the file system. '
        return self._fs.path_to_string(self._path)

    @property
    def uri(self):
        ' The URI that points to self in the file system. '
        return self._fs.path_to_uri(self._path)

    @property
    def name(self):
        ' The name of self. '
        return self._path.basename

    def is_file(self):
        ' Returns wether self is a File. '
        return False

    def is_dir(self):
        ' Returns wether self is a Directory. '
        return False

    def as_file(self):
        ' Returns itself as a File instance or raises a NotAFileError. '
        raise NotAFileError()

    def as_dir(self):
        ' Returns itself as a Directory instance or raises a NotADirectoryError. '
        raise NotADirectoryError()

    def exists(self):
        ' Returns whether self exists in the file system. '
        return self._fs.path_exists(self._path)

    def remove(self):
        ' Tries to remove self from the file system.\n        On failure it raises a FileSystemOperationError\n        '
        raise FileSystemOperationError('Cannot remove {0}'.format(str(self)))

    def parent(self):
        ' Return parent Directory of self. '
        return Directory(self._fs, None, self._copy_handler, _path=self._path.parent)

    def copy(self, destination):
        ' Copy this to `destination`. '
        self._copy_handler.copy(self._copy_object(), destination._copy_object())

    def _copy_object(self):
        return CopyFileSystemObject(self._fs, self._path)

    def __repr__(self):
        return '{0}(fs={1}, path={2}, copy_handler={3})'.format(self.__class__.__name__, self._fs, self.path, self._copy_handler)

    def __hash__(self):
        return hash(self.__repr__())

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            other_casted = other
            return ((self._path == other_casted._path) and (self._fs == other_casted._fs) and (self._copy_handler == other_casted._copy_handler))
        return False

class Directory(BaseFileSystemObject):

    def is_dir(self):
        ' Returns wether self is a Directory. '
        return True

    def as_dir(self):
        ' Returns itself as a Directory instance or raises a NotADirectoryError. '
        return self

    def list(self):
        ' Returns the contents of the Directory in the file system as a list of BaseFileSystemObjects.\n\n        If the Directory does not exist the list will be empty.\n        '
        contents = self._fs.dir_list(self._path)
        result = []
        for dir_path in contents.dirs:
            result.append(Directory(self._fs, None, self._copy_handler, _path=dir_path))
        for file_path in contents.files:
            result.append(File(self._fs, None, self._copy_handler, _path=file_path))
        for other_path in contents.others:
            result.append(BaseFileSystemObject(self._fs, None, self._copy_handler, _path=other_path))
        return result

    def remove(self):
        ' Tries to remove self from the file system.\n\n        On failure it raises a FileSystemOperationError\n        '
        self._fs.dir_remove(self._path)

    def subdir(self, path):
        ' Returns a Directory with its path as being the given path relative to the current Directory. '
        return Directory(self._fs, None, self._copy_handler, _path=self._path.child(path))

    def file(self, path):
        ' Returns a File with its path as being the given `path` relative to the current Directory. '
        return File(self._fs, None, self._copy_handler, _path=self._path.child(path))

    def _copy_object(self):
        return CopyDirectory(self._fs, self._path)

class File(BaseFileSystemObject):

    def is_file(self):
        ' Returns wether self is a File. '
        return True

    def as_file(self):
        ' Returns itself as a File instance or raises a NotAFileError. '
        return self

    def remove(self):
        ' Tries to remove self from the file system.\n\n        On failure it raises a FileSystemOperationError\n        '
        self._fs.file_remove(self._path)

    def read(self):
        ' Returns the contents of the File.\n\n        If it fails to read the file a FileSystemOperationError will be raised.\n        '
        return self._fs.file_read(self._path)

    def write(self, content):
        ' Sets the contents of the File. If the parent directory does not exist it is created.\n\n        If it fails to read the file a FileSystemOperationError will be raised.\n        '
        self._fs.file_write(self._path, content)

    def _copy_object(self):
        return CopyFile(self._fs, self._path)
