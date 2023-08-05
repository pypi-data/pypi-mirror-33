
import traceback
from ..fs import BaseFileSystem, DirListResult, Path

class CopyError(Exception):
    pass

class CopyFileSystemObject():

    def __init__(self, fs, path):
        self._fs = fs
        self._path = path

    @property
    def fs(self):
        return self._fs

    @property
    def path(self):
        return self._path

    def copy(self, dst, copier):
        raise TypeError('Cannot copy from filesystem object that is not file or directory')

    def copy_from_file(self, src, copier):
        raise TypeError('Cannot copy to filesystem object that is not file or directory')

    def copy_from_dir(self, src, copier):
        raise TypeError('Cannot copy to filesystem object that is not file or directory')

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            other_casted = other
            return ((self._fs == other_casted._fs) and (self._path == other_casted._path))
        return False

    def __repr__(self):
        return '{0}(fs={1}, path={2})'.format(self.__class__.__name__, self._fs, self._path)

class CopyFile(CopyFileSystemObject):

    def copy(self, dst, copier):
        dst.copy_from_file(self, copier)

    def copy_from_file(self, src, copier):
        copier.copy_file_to_file(src, self)

    def copy_from_dir(self, src, copier):
        raise TypeError('Cannot copy Directory into a File.')

class CopyDirectory(CopyFileSystemObject):

    def file(self, suffix):
        return CopyFile(self._fs, self._path.child(suffix))

    def subdir(self, suffix):
        return CopyDirectory(self._fs, self._path.child(suffix))

    def copy(self, dst, copier):
        dst.copy_from_dir(self, copier)

    def copy_from_file(self, src, copier):
        copier.copy_file_to_file(src, self.file(src.path.basename))

    def copy_from_dir(self, src, copier):
        copier.copy_dir_to_dir(src, self)

class GenericCopier():

    def copy_dir_to_dir(self, src, dst):
        contents = src.fs.dir_list(src.path)
        for file_ in contents.files:
            src_child_file = src.file(file_.basename)
            dst_child_file = dst.file(file_.basename)
            self.copy_file_to_file(src_child_file, dst_child_file)
        for dir_ in contents.dirs:
            src_child_dir = src.subdir(dir_.basename)
            dst_child_dir = dst.subdir(dir_.basename)
            self.copy_dir_to_dir(src_child_dir, dst_child_dir)

    def copy_file_to_file(self, src, dst):
        dst.fs.file_write(dst.path, src.fs.file_read(src.path))

class CopyHandler():

    def __init__(self, default_copier):
        self._copiers = {}
        self._default = default_copier

    def set_copy_policy(self, src_fs, dst_fs, copier):
        self._copiers[(src_fs, dst_fs)] = copier

    def copy(self, src, dst):
        copier = self._copiers.get((src.fs, dst.fs), self._default)
        try:
            src.copy(dst, copier)
        except Exception:
            raise CopyError(traceback.format_exc())
