
import os
import shutil
from . import GenericCopier, CopyFile
from ..fs import Path

class LocalToLocalCopier(GenericCopier):

    def copy_file_to_file(self, src, dst):
        parent_dir = dst.path.parent
        if (not dst.fs.path_exists(parent_dir)):
            os.makedirs(dst.fs.path_to_string(parent_dir))
        shutil.copyfile(src.fs.path_to_string(src.path), dst.fs.path_to_string(dst.path))

class LocalToS3Copier(GenericCopier):

    def __init__(self, s3_client):
        self._s3_client = s3_client

    def copy_file_to_file(self, src, dst):
        dst_path_str = dst.fs.path_to_string(dst.path)
        dst_tail = dst_path_str[(dst_path_str.find('/') + 1):]
        self._s3_client.upload_file(src.fs.path_to_string(src.path), dst.path.drive, dst_tail)
