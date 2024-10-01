import os

import json
from typing import List
from .models import ObjectMetadata, StorageObject
from utils.file_utils import calculate_md5, get_mime_type, compress_data, decompress_data

from datetime import datetime

class ObjectStorage:
    def __init__(self, root_dir: str):
        self.root_dir = root_dir
        self._create_directory_structure()

    def _create_directory_structure(self):
        os.makedirs(os.path.join(self.root_dir, "buckets"), exist_ok=True)
        os.makedirs(os.path.join(self.root_dir, "metadata"), exist_ok=True)
        os.makedirs(os.path.join(self.root_dir, "temp"), exist_ok=True)

    def upload_file(self, bucket_name: str, object_key: str, data: bytes, owner_id: str, compress: bool = False) -> StorageObject:
        if compress:
            data = compress_data(data)

        metadata = ObjectMetadata(
            object_key=object_key,
            bucket_name=bucket_name,
            size=len(data),
            md5_hash=calculate_md5(data),
            mime_type="application/octet-stream",  # Используем общий тип для загруженных данных
            created_at=datetime.now(),
            modified_at=datetime.now(),
            owner_id=owner_id,
            acl={"owner": "FULL_CONTROL"},
            is_compressed=compress
        )

        storage_object = StorageObject(metadata=metadata, data=data)
        self._save_object(storage_object)

        return storage_object

    def get_object(self, bucket_name: str, object_key: str) -> StorageObject:
        metadata_path = os.path.join(self.root_dir, "metadata", bucket_name, f"{object_key}.meta")
        object_path = os.path.join(self.root_dir, "buckets", bucket_name, object_key)

        if not os.path.exists(metadata_path) or not os.path.exists(object_path):
            raise FileNotFoundError(f"Object {object_key} not found in bucket {bucket_name}")

        with open(metadata_path, "r") as file:
            metadata_dict = json.load(file)
            metadata = ObjectMetadata(**metadata_dict)

        with open(object_path, "rb") as file:
            data = file.read()

        if metadata.is_compressed:
            data = decompress_data(data)

        return StorageObject(metadata=metadata, data=data)

    def _save_object(self, storage_object: StorageObject):
        bucket_path = os.path.join(self.root_dir, "buckets", storage_object.metadata.bucket_name)
        os.makedirs(bucket_path, exist_ok=True)

        object_path = os.path.join(bucket_path, storage_object.metadata.object_key)
        with open(object_path, "wb") as file:
            file.write(storage_object.data)

        metadata_path = os.path.join(self.root_dir, "metadata", storage_object.metadata.bucket_name)
        os.makedirs(metadata_path, exist_ok=True)

        metadata_file = os.path.join(metadata_path, f"{storage_object.metadata.object_key}.meta")
        with open(metadata_file, "w") as file:
            # Convert datetime objects to strings
            metadata_dict = storage_object.metadata.__dict__.copy()
            metadata_dict['created_at'] = metadata_dict['created_at'].isoformat()
            metadata_dict['modified_at'] = metadata_dict['modified_at'].isoformat()
            json.dump(metadata_dict, file)

    def list_objects(self, bucket_name: str) -> List[ObjectMetadata]:
        metadata_path = os.path.join(self.root_dir, "metadata", bucket_name)
        objects = []
        
        if os.path.exists(metadata_path):
            for filename in os.listdir(metadata_path):
                if filename.endswith(".meta"):
                    with open(os.path.join(metadata_path, filename), "r") as file:
                        metadata_dict = json.load(file)
                        # Convert string dates back to datetime objects
                        metadata_dict['created_at'] = datetime.fromisoformat(metadata_dict['created_at'])
                        metadata_dict['modified_at'] = datetime.fromisoformat(metadata_dict['modified_at'])
                        metadata = ObjectMetadata(**metadata_dict)
                        objects.append(metadata)
        
        return objects
