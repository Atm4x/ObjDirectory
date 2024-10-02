import os
import struct
from typing import List, Tuple
from config import config

class BlockStorage:
    BLOCK_SIZE = 4096  # 4 KB blocks

    def __init__(self):
        self.storage_path = config.BLOCK_STORAGE_PATH
        os.makedirs(self.storage_path, exist_ok=True)

    def _get_block_file_path(self, block_id: int) -> str:
        return os.path.join(self.storage_path, f"block_{block_id:08x}")

    def write_blocks(self, data: bytes) -> List[int]:
        block_ids = []
        for i in range(0, len(data), self.BLOCK_SIZE):
            block = data[i:i+self.BLOCK_SIZE]
            block_id = self._write_block(block)
            block_ids.append(block_id)
        return block_ids

    def _write_block(self, block: bytes) -> int:
        block_id = self._generate_block_id()
        path = self._get_block_file_path(block_id)
        with open(path, 'wb') as f:
            f.write(block)
        return block_id

    def read_blocks(self, block_ids: List[int]) -> bytes:
        data = b''
        for block_id in block_ids:
            data += self._read_block(block_id)
        return data

    def _read_block(self, block_id: int) -> bytes:
        path = self._get_block_file_path(block_id)
        with open(path, 'rb') as f:
            return f.read()

    def delete_blocks(self, block_ids: List[int]):
        for block_id in block_ids:
            path = self._get_block_file_path(block_id)
            if os.path.exists(path):
                os.remove(path)

    def _generate_block_id(self) -> int:
        # This is a simple implementation. In a production system,
        # you'd want a more robust method of generating unique IDs.
        return int.from_bytes(os.urandom(4), byteorder='big')