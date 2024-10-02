import json
from typing import List, Dict
from .models import ObjectMetadata, StorageObject
from .block_storage import BlockStorage
from utils.file_utils import calculate_md5, compress_data, decompress_data
from datetime import datetime
import rocksdbpy
import os
from config import config

class ObjectStorage:
    def __init__(self):
        opts = rocksdbpy.Option()
        opts.create_if_missing(True)
        self.db = rocksdbpy.open(config.ROCKSDB_PATH, opts)
        self.block_storage = BlockStorage()

    def upload_file(self, bucket_name: str, object_key: str, data: bytes, owner_id: str, compress: bool = False) -> StorageObject:
        if compress:
            data = compress_data(data)

        block_ids = self.block_storage.write_blocks(data)

        metadata = ObjectMetadata(
            object_key=object_key,
            bucket_name=bucket_name,
            size=len(data),
            md5_hash=calculate_md5(data),
            mime_type="application/octet-stream",
            created_at=datetime.now(),
            modified_at=datetime.now(),
            owner_id=owner_id,
            acl={"owner": "FULL_CONTROL"},
            is_compressed=compress,
            block_ids=block_ids
        )

        storage_object = StorageObject(metadata=metadata, data=data)
        self._save_metadata(storage_object.metadata)

        return storage_object

    def get_object(self, bucket_name: str, object_key: str) -> StorageObject:
        metadata = self._get_metadata(bucket_name, object_key)

        data = self.block_storage.read_blocks(metadata.block_ids)

        if metadata.is_compressed:
            data = decompress_data(data)

        return StorageObject(metadata=metadata, data=data)

    def _metadata_to_dict(self, metadata: ObjectMetadata) -> dict:
        metadata_dict = metadata.__dict__.copy()
        metadata_dict['created_at'] = metadata_dict['created_at'].isoformat()
        metadata_dict['modified_at'] = metadata_dict['modified_at'].isoformat()
        return metadata_dict

    def _get_metadata(self, bucket_name: str, object_key: str) -> ObjectMetadata:
        metadata_key = f"{bucket_name}:{object_key}".encode()
        metadata_json = self.db.get(metadata_key)

        if metadata_json is None:
            raise FileNotFoundError(f"Object {object_key} not found in bucket {bucket_name}")

        metadata_dict = json.loads(metadata_json)
        metadata_dict['created_at'] = datetime.fromisoformat(metadata_dict['created_at'])
        metadata_dict['modified_at'] = datetime.fromisoformat(metadata_dict['modified_at'])
        return ObjectMetadata(**metadata_dict)

    def _save_metadata(self, metadata: ObjectMetadata):
        metadata_key = f"{metadata.bucket_name}:{metadata.object_key}".encode()
        metadata_dict = self._metadata_to_dict(metadata)
        metadata_json = json.dumps(metadata_dict)
        self.db.set(metadata_key, metadata_json.encode())

    def list_objects(self, bucket_name: str) -> List[ObjectMetadata]:
        objects = []
        iterator = self.db.iterator(mode='from', key=bucket_name.encode())
        for key, value in iterator:
            key = key.decode()
            if not key.startswith(f"{bucket_name}:"):
                break
            metadata_dict = json.loads(value)
            metadata_dict['created_at'] = datetime.fromisoformat(metadata_dict['created_at'])
            metadata_dict['modified_at'] = datetime.fromisoformat(metadata_dict['modified_at'])
            metadata = ObjectMetadata(**metadata_dict)
            objects.append(metadata)
        return objects

    def delete_object(self, bucket_name: str, object_key: str):
        metadata = self._get_metadata(bucket_name, object_key)

        # Delete metadata from RocksDB
        metadata_key = f"{bucket_name}:{object_key}".encode()
        self.db.delete(metadata_key)

        # Delete blocks from block storage
        self.block_storage.delete_blocks(metadata.block_ids)

    def __del__(self):
        self.db.close()