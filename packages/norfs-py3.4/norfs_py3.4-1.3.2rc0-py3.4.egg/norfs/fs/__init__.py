

class NotAFileError(Exception):
    pass

class FileSystemOperationError(Exception):
    pass

class Path():

    def __init__(self, drive, *tail):
        self._drive = drive
        self._tail = tail

    @property
    def drive(self):
        return self._drive

    @property
    def tail(self):
        return self._tail

    @property
    def basename(self):
        return self._tail[(- 1)]

    @property
    def parent(self):
        return Path(self._drive, *self._tail[:(- 1)])

    def child(self, name):
        return Path(self._drive, *(list(self._tail) + [name]))

    def __repr__(self):
        return '{0}(drive={1}, tail={2})'.format(self.__class__.__name__, self._drive.__repr__(), self._tail)

    def __hash__(self):
        return hash(self.__repr__())

    def __eq__(self, other):
        if isinstance(other, Path):
            return ((self._drive == other.drive) and (self._tail == other.tail))
        return False

class DirListResult():

    def __init__(self, files, dirs, others):
        self._files = files
        self._dirs = dirs
        self._others = others

    @property
    def files(self):
        return self._files

    @property
    def dirs(self):
        return self._dirs

    @property
    def others(self):
        return self._others

    def __eq__(self, other):
        if (other is self):
            return True
        if (not isinstance(other, DirListResult)):
            return False
        if (set(other.files) != set(self.files)):
            return False
        if (set(other.dirs) != set(self.dirs)):
            return False
        if (set(other.others) != set(self.others)):
            return False
        return True

    def __repr__(self):
        return '{0}(files={1}, dirs={2}, others={3})'.format(self.__class__.__name__, self._files, self._dirs, self._others)

class BaseFileSystem():
    ERROR_MESSAGE = 'BaseFileSystem: operation not implemented'

    def parse_path(self, path):
        raise FileSystemOperationError(self.ERROR_MESSAGE)

    def path_exists(self, path):
        raise FileSystemOperationError(self.ERROR_MESSAGE)

    def path_to_string(self, path):
        raise FileSystemOperationError(self.ERROR_MESSAGE)

    def path_to_uri(self, path):
        raise FileSystemOperationError(self.ERROR_MESSAGE)

    def file_read(self, path):
        raise FileSystemOperationError(self.ERROR_MESSAGE)

    def file_write(self, path, content):
        raise FileSystemOperationError(self.ERROR_MESSAGE)

    def file_remove(self, path):
        raise FileSystemOperationError(self.ERROR_MESSAGE)

    def dir_list(self, path):
        raise FileSystemOperationError(self.ERROR_MESSAGE)

    def dir_remove(self, path):
        raise FileSystemOperationError(self.ERROR_MESSAGE)

    def __repr__(self):
        return '{0}()'.format(self.__class__.__name__)

    def __eq__(self, other):
        return (hash(self) == hash(other))

    def __hash__(self):
        return hash(id(self))
