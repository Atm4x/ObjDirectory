import hashlib
import mimetypes
import gzip

def calculate_md5(data: bytes) -> str:
    print(data)
    return hashlib.md5(data).hexdigest()

def get_mime_type(file_path: str) -> str:
    return mimetypes.guess_type(file_path)[0] or "application/octet-stream"


def compress_data(data: bytes) -> bytes:
    return gzip.compress(data)

def decompress_data(data: bytes) -> bytes:
    return gzip.decompress(data)