from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional
import hashlib

@dataclass
class ObjectMetadata:
    object_key: str
    bucket_name: str
    size: int
    md5_hash: str
    mime_type: str
    created_at: datetime
    modified_at: datetime
    owner_id: str
    acl: Dict[str, str]
    version: Optional[str] = None
    is_compressed: bool = False
    user_metadata: Dict[str, str] = None
    parts: List[Dict[str, any]] = None
    is_encrypted: bool = False
    replication_info: Dict[str, any] = None
    block_ids: List[int] = None
    

@dataclass
class StorageObject:
    metadata: ObjectMetadata
    data: bytes

    def __post_init__(self):
        if not self.metadata.size:
            self.metadata.size = len(self.data)
        if not self.metadata.md5_hash:
            self.metadata.md5_hash = self._calculate_md5()

    def _calculate_md5(self) -> str:
        return hashlib.md5(self.data).hexdigest()