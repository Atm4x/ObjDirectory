import math
import mmh3

class BloomFilter:
    def __init__(self, size, hash_count):
        self.size = size
        self.hash_count = hash_count
        self.bit_array = [0] * size

    def add(self, item):
        item_bytes = self._to_bytes(item)
        for seed in range(self.hash_count):
            index = mmh3.hash(item_bytes, seed) % self.size
            self.bit_array[index] = 1

    def check(self, item):
        item_bytes = self._to_bytes(item)
        for seed in range(self.hash_count):
            index = mmh3.hash(item_bytes, seed) % self.size
            if self.bit_array[index] == 0:
                return False
        return True

    @staticmethod
    def _to_bytes(item):
        if isinstance(item, bytes):
            return item
        elif isinstance(item, str):
            return item.encode('utf-8')
        elif isinstance(item, int):
            return str(item).encode('utf-8')
        else:
            raise ValueError(f"Unsupported type for Bloom filter: {type(item)}")

    @classmethod
    def get_size(cls, n, p):
        m = -(n * math.log(p)) / (math.log(2)**2)
        return int(m)

    @classmethod
    def get_hash_count(cls, m, n):
        k = (m/n) * math.log(2)
        return int(k)