
import traceback
from collections import deque
from . import BaseFileSystem, DirListResult, FileSystemOperationError, NotAFileError, Path

class MemoryDirectory():

    def __init__(self):
        self._subdirs = {
            
        }
        self._files = {
            
        }

    def list_dirs(self):
        return list(self._subdirs.keys())

    def list_files(self):
        return list(self._files.keys())

    def put_dir(self, name, dir_):
        self._subdirs[name] = dir_

    def put_file(self, name, file_):
        self._files[name] = file_

    def get_dir(self, name):
        try:
            return self._subdirs[name]
        except KeyError:
            raise NotADirectoryError()

    def get_file(self, name):
        try:
            return self._files[name]
        except KeyError:
            raise NotAFileError()

    def remove_dir(self, name):
        try:
            del self._subdirs[name]
        except KeyError:
            raise NotADirectoryError()

    def remove_file(self, name):
        try:
            del self._files[name]
        except KeyError:
            raise NotADirectoryError()

class MemoryFile():

    def __init__(self, contents):
        self._contents = contents

    @property
    def contents(self):
        return self._contents

class MemoryFileSystem(BaseFileSystem):

    def __init__(self, root, *, separator='/'):
        self._root = root
        self._separator = separator

    def _get_dir(self, path):
        current_dir = self._root
        for dir_name in path.tail:
            current_dir = current_dir.get_dir(dir_name)
        return current_dir

    def parse_path(self, path):
        tail = path.split(self._separator)
        return Path('', *tail)

    def path_exists(self, path):
        try:
            parent_dir = self._get_dir(path.parent)
        except NotADirectoryError:
            return False
        else:
            return (path.basename in (parent_dir.list_dirs() + parent_dir.list_files()))

    def path_to_string(self, path):
        return self._separator.join(path.tail)

    def path_to_uri(self, path):
        return 'memory://{0}'.format(self.path_to_string(path))

    def file_read(self, path):
        try:
            parent_dir = self._get_dir(path.parent)
            return parent_dir.get_file(path.basename).contents
        except (NotADirectoryError, NotAFileError):
            raise FileSystemOperationError(traceback.format_exc())

    def file_write(self, path, content):
        parent_dir = self._root
        queue = deque(path.parent.tail)
        while queue:
            dir_name = queue.popleft()
            try:
                parent_dir = parent_dir.get_dir(dir_name)
            except NotADirectoryError:
                new_dir = MemoryDirectory()
                parent_dir.put_dir(dir_name, new_dir)
                parent_dir = new_dir
                break
        while queue:
            dir_name = queue.popleft()
            new_dir = MemoryDirectory()
            parent_dir.put_dir(dir_name, new_dir)
            parent_dir = new_dir
        parent_dir.put_file(path.basename, MemoryFile(content))

    def file_remove(self, path):
        try:
            parent_dir = self._get_dir(path.parent)
            parent_dir.remove_file(path.basename)
        except (NotADirectoryError, NotAFileError):
            raise FileSystemOperationError(traceback.format_exc())

    def dir_list(self, path):
        try:
            current_dir = self._get_dir(path)
        except NotADirectoryError:
            files = []
            dirs = []
        else:
            files = [path.child(file_) for file_ in current_dir.list_files()]
            dirs = [path.child(dir_) for dir_ in current_dir.list_dirs()]
        return DirListResult(files, dirs, [])

    def dir_remove(self, path):
        try:
            current_dir = self._get_dir(path.parent)
            current_dir.remove_dir(path.basename)
        except NotADirectoryError:
            raise FileSystemOperationError(traceback.format_exc())

    def __repr__(self):
        return '{0}(root={1})'.format(self.__class__.__name__, self._root)
