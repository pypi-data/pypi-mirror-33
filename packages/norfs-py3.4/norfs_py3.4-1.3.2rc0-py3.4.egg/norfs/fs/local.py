
import os
import shutil
import traceback
from . import BaseFileSystem, DirListResult, FileSystemOperationError, Path

class LocalFileSystem(BaseFileSystem):

    def parse_path(self, path):
        abs_path = os.path.abspath(os.path.normpath(path))
        (drive, tail_str) = os.path.splitdrive(abs_path)
        tail = tail_str.split(os.sep)
        return Path(drive, *tail)

    def path_exists(self, path):
        return os.path.exists(self.path_to_string(path))

    def path_to_string(self, path):
        return os.path.join(path.drive, os.sep.join(path.tail))

    def path_to_uri(self, path):
        return 'file:///{}/{}'.format(path.drive, os.path.join(*path.tail))

    def file_read(self, path):
        try:
            with open(self.path_to_string(path), 'rb') as f:
                return f.read()
        except Exception:
            raise FileSystemOperationError(traceback.format_exc())

    def file_write(self, path, content):
        try:
            parent_path = self.path_to_string(path.parent)
            if (not os.path.exists(parent_path)):
                os.makedirs(parent_path)
            with open(self.path_to_string(path), 'wb') as f:
                f.write(content)
        except Exception:
            raise FileSystemOperationError(traceback.format_exc())

    def file_remove(self, path):
        try:
            os.remove(self.path_to_string(path))
        except Exception:
            raise FileSystemOperationError(traceback.format_exc())

    def dir_list(self, path):
        path_str = self.path_to_string(path)
        try:
            items = os.listdir(path_str)
        except FileNotFoundError:
            items = []
        files = []
        dirs = []
        others = []
        for item in items:
            full_path = os.path.join(path_str, item)
            item_path = path.child(item)
            if os.path.isfile(full_path):
                files.append(item_path)
            else:
                if os.path.isdir(full_path):
                    dirs.append(item_path)
                else:
                    others.append(item_path)
        return DirListResult(files, dirs, others)

    def dir_remove(self, path):
        try:
            shutil.rmtree(self.path_to_string(path))
        except Exception:
            raise FileSystemOperationError(traceback.format_exc())
