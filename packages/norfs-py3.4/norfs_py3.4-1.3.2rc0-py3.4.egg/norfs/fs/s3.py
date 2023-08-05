
import traceback
from io import BytesIO
from . import BaseFileSystem, DirListResult, FileSystemOperationError, Path

class S3FileSystem(BaseFileSystem):

    def __init__(self, s3_client, *, uri_protocol='s3', separator='/'):
        self._s3_client = s3_client
        self._protocol = uri_protocol
        self._separator = separator

    def parse_path(self, path):
        bucket_path_separator_position = path.find('/')
        drive = path[:bucket_path_separator_position]
        tail = path[(bucket_path_separator_position + 1):].split(self._separator)
        return Path(drive, *tail)

    def path_exists(self, path):
        prefix = self._separator.join(path.tail)
        response = self._s3_client.list_objects_v2(Bucket=path.drive, Prefix=prefix, Delimiter=self._separator)
        contents = response.get('Contents', [])
        for item in contents:
            file_name = item['Key']
            if (file_name == prefix):
                return True
        prefixes = response.get('CommonPrefixes', [])
        for item in prefixes:
            dir_name = item['Prefix']
            if (dir_name == (prefix + self._separator)):
                return True
        return False

    def path_to_string(self, path):
        return '{0}/{1}'.format(path.drive, self._separator.join(path.tail))

    def path_to_uri(self, path):
        return '{0}://{1}'.format(self._protocol, self.path_to_string(path))

    def file_read(self, path):
        prefix = self._separator.join(path.tail)
        try:
            data = BytesIO()
            self._s3_client.download_fileobj(path.drive, prefix, data)
            data.seek(0)
            return data.read()
        except Exception:
            raise FileSystemOperationError(traceback.format_exc())

    def file_write(self, path, content):
        try:
            dirs = path.parent.tail
            acc_prefix = ''
            for dir_ in dirs:
                if acc_prefix:
                    acc_prefix = self._separator.join((acc_prefix, dir_))
                else:
                    acc_prefix = dir_
                self._s3_client.upload_fileobj(BytesIO(b''), path.drive, (acc_prefix + self._separator))
            path_str = self.path_to_string(path)
            tail = path_str[(path_str.find('/') + 1):]
            self._s3_client.upload_fileobj(BytesIO(content), path.drive, tail)
        except Exception:
            raise FileSystemOperationError(traceback.format_exc())

    def file_remove(self, path):
        prefix = self._separator.join(path.tail)
        try:
            response = self._s3_client.list_objects_v2(Bucket=path.drive, Prefix=prefix)
            contents = response.get('Contents', [])
            if contents:
                self._s3_client.delete_objects(Bucket=path.drive, Delete={
                    'Objects': [{
                        'Key': f['Key'],
                    } for f in contents if (f['Key'] == prefix)],
                })
        except Exception:
            raise FileSystemOperationError(traceback.format_exc())

    def dir_list(self, path):
        tail_str = self._separator.join(path.tail)
        if tail_str:
            tail_str += self._separator
        files = []
        dirs = []
        try:
            response = self._s3_client.list_objects_v2(Bucket=path.drive, Prefix=tail_str, Delimiter=self._separator)
        except Exception:
            raise FileSystemOperationError(traceback.format_exc())
        (files, dirs) = self._extend_files_and_dirs_with_response(tail_str, path, files, dirs, response)
        while response.get('IsTruncated', False):
            try:
                response = self._s3_client.list_objects_v2(Bucket=path.drive, Prefix=tail_str, Delimiter=self._separator, ContinuationToken=response.get('NextContinuationToken', ''))
            except Exception:
                raise FileSystemOperationError(traceback.format_exc())
            (files, dirs) = self._extend_files_and_dirs_with_response(tail_str, path, files, dirs, response)
        return DirListResult(files, dirs, [])

    def dir_remove(self, path):
        try:
            response = self._s3_client.list_objects_v2(Bucket=path.drive, Prefix=(self._separator.join(path.tail) + self._separator))
            contents = response.get('Contents', [])
            if contents:
                self._s3_client.delete_objects(Bucket=path.drive, Delete={
                    'Objects': [{
                        'Key': f['Key'],
                    } for f in contents],
                })
        except Exception:
            raise FileSystemOperationError(traceback.format_exc())

    def __repr__(self):
        return '{0}(s3_client={1}, uri_protocol={2}, separator={3})'.format(self.__class__.__name__, self._s3_client, self._protocol, self._separator)

    def _extend_files_and_dirs_with_response(self, tail_str, path, files, dirs, response):
        for item in response.get('Contents', []):
            file_name = item['Key']
            if (file_name != tail_str):
                if file_name.endswith(self._separator):
                    dirs.append(Path(path.drive, *file_name.split(self._separator)[:(- 1)]))
                else:
                    files.append(Path(path.drive, *file_name.split(self._separator)))
        for item in response.get('CommonPrefixes', []):
            dir_name = item['Prefix']
            dirs.append(Path(path.drive, *dir_name.split(self._separator)[:(- 1)]))
        return (files, dirs)
