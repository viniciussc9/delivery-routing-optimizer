# Custom hash table implementation for storing packages by ID
class HashTable:
    def __init__(self, initial_capacity=128):
        self.capacity = initial_capacity
        self.buckets = [[] for _ in range(self.capacity)]
        self.size = 0

# Simple modulus-based hashing for bucket index
    def _hash(self, key):
        return hash(key) % self.capacity

# Insert or update a package in the table by ID
# Resizes if load factor exceeds 0.75
    def put(self, key, value):
        idx = self._hash(key)
        bucket = self.buckets[idx]
        for i, (k, _) in enumerate(bucket):
            if k == key:
                bucket[i] = (key, value)
                return
        bucket.append((key, value))
        self.size += 1
        if self.size / self.capacity > 0.75:
            self._resize()

    # Look up and return package by ID
    def get(self, key):
        idx = self._hash(key)
        for k, v in self.buckets[idx]:
            if k == key:
                return v
        return None

    # Doubles table capacity and rehashes all items
    def _resize(self):
        old = self.buckets
        self.capacity *= 2
        self.buckets = [[] for _ in range(self.capacity)]
        self.size = 0
        for bucket in old:
            for k, v in bucket:
                self.put(k, v)

    # Iterator for all key/value pairs
    def items(self):
        for bucket in self.buckets:
            for k, v in bucket:
                yield (k, v)
