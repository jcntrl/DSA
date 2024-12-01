from collections import OrderedDict

class LRUCache(OrderedDict):
    def __init__(self, capacity: int= 3):
        super().__init__()
        # self.LRUCache = OrderedDict()
        self.capacity = capacity


    def put(self, key, value):
        # Evict the least recently used element if the queue is at capacity
        if len(self) >= self.capacity:
            self.popitem(last=False)
        self[key] = value


    def get(self, key):
        value = super().get(key, None) # use the battle-hardened get implementation from OrderedDict
        if value is not None:
            # Getting it is using it, makes it most recent, so move it to the recent side of the queue
            self.move_to_end(key, last=True) 
        return value
    

    def update(self, key, new_value):
        if key not in self:
            # technically allowing an update to a non-existent key, 
            # just as a new addition
            self.put(key, new_value)
        else:
            # Updating it is using it, makes it most recent, so move it to the recent side of the queue
            self.move_to_end(key, last=True)
            self[key] = new_value 


if __name__ == "__main__":
    import unittest
    class TestLRUCache(unittest.TestCase):
        def test_eviction(self):
            cache = LRUCache(capacity=4)
            for i, v in enumerate(["a", "b", "c", "d", "e"]):
                cache.put(v, i)
            self.assertEqual(list(cache.keys()), ["b", "c", "d", "e"])  # "a" should be evicted

        def test_get_updates_usage(self):
            cache = LRUCache(capacity=5)
            for i, v in enumerate(["a", "b", "c", "d", "e"]):
                cache.put(v, i)
            cache.get("a")
            self.assertEqual(list(cache.keys()), ["b", "c", "d", "e", "a"])  # "a" should now be MRU

        def test_update_existing_key(self):
            cache = LRUCache(capacity=5)
            for i, v in enumerate(["a", "b", "c", "d", "e"]):
                cache.put(v, i)
            cache.update("a", 77)
            self.assertEqual(cache["a"], 77)
            self.assertEqual(list(cache.keys()), ["b", "c", "d", "e", "a"])  # "a" is MRU

        def test_addition_triggers_eviction(self):
            cache = LRUCache(capacity=5)
            for i, v in enumerate(["a", "b", "c", "d", "e"]):
                cache.put(v, i)
            cache.put("f", 88)
            self.assertEqual(list(cache.keys()), ["b", "c", "d", "e", "f"])  # "a" should be evicted

        def test_get_nonexistent_key(self):
            cache = LRUCache(capacity=5)
            for i, v in enumerate(["a", "b", "c", "d", "e"]):
                cache.put(v, i)
            result = cache.get("thiskeydoesntexist")
            self.assertIsNone(result)  # Nonexistent key should return None
            self.assertEqual(list(cache.keys()), ["a", "b", "c", "d", "e"])  # No change in cache

        def test_update_nonexistent_key(self):
            cache = LRUCache(capacity=5)
            for i, v in enumerate(["a", "b", "c", "d", "e"]):
                cache.put(v, i)
            cache.update("thiskeydoesntexistYET", 99)
            self.assertEqual(cache["thiskeydoesntexistYET"], 99)
            self.assertEqual(list(cache.keys()), ["b", "c", "d", "e", "thiskeydoesntexistYET"])  # "a" evicted

        def test_repeated_access(self):
            cache = LRUCache(capacity=4)
            for i, v in enumerate(["a", "b", "c", "d", "e"]):
                cache.put(v, i)
            cache.get("c")
            cache.get("c")
            self.assertEqual(list(cache.keys()), ["b", "d", "e", "c"])  # "c" is most recently used

        def test_zero_capacity(self):
            cache = LRUCache(capacity=0)
            cache.put("a", 1)
            self.assertEqual(len(cache), 0)  # Cache should remain empty
            self.assertIsNone(cache.get("a"))  # No items should be retrievable

        def test_single_capacity(self):
            cache = LRUCache(capacity=1)
            cache.put("a", 1)
            self.assertEqual(list(cache.keys()), ["a"])  # Only "a" should exist
            cache.put("b", 2)
            self.assertEqual(list(cache.keys()), ["b"])  # "a" should be evicted
            self.assertIsNone(cache.get("a"))
            self.assertEqual(cache.get("b"), 2)

        def test_duplicate_put(self):
            cache = LRUCache(capacity=3)
            cache.put("a", 1)
            cache.put("b", 2)
            cache.put("a", 99)  # Update "a" with a new value
            self.assertEqual(cache["a"], 99)
            self.assertEqual(list(cache.keys()), ["b", "a"])  # "a" should now be MRU

        def test_sequential_access(self):
            cache = LRUCache(capacity=3)
            cache.put("a", 1)
            cache.put("b", 2)
            cache.put("c", 3)
            cache.get("a")
            cache.get("b")
            self.assertEqual(list(cache.keys()), ["c", "a", "b"])  # Reordered by access

        def test_overflowing_update(self):
            cache = LRUCache(capacity=3)
            cache.put("a", 1)
            cache.put("b", 2)
            cache.put("c", 3)
            cache.update("d", 4)  # This should evict "a"
            self.assertEqual(list(cache.keys()), ["b", "c", "d"])
            self.assertIsNone(cache.get("a"))

        def test_mixed_operations(self):
            cache = LRUCache(capacity=3)
            cache.put("a", 1)
            cache.put("b", 2)
            cache.put("c", 3)
            cache.get("a")  # "a" becomes MRU
            cache.update("b", 22)  # "b" is updated and becomes MRU
            cache.put("d", 4)  # Evicts "c" (LRU)
            self.assertEqual(list(cache.keys()), ["a", "b", "d"])
            self.assertEqual(cache["b"], 22)
            self.assertIsNone(cache.get("c"))

        def test_mutable_values(self):
            cache = LRUCache(capacity=3)
            mutable_value = [1, 2, 3]
            cache.put("a", mutable_value)
            mutable_value.append(4)
            self.assertEqual(cache["a"], [1, 2, 3, 4])  # Stored value should reflect changes

        def test_manual_deletion(self):
            cache = LRUCache(capacity=3)
            cache.put("a", 1)
            cache.put("b", 2)
            cache.put("c", 3)
            del cache["b"]  # Manually delete a key
            self.assertEqual(list(cache.keys()), ["a", "c"])  # "b" is gone
            cache.put("d", 4)  # Adding new key
            self.assertEqual(list(cache.keys()), ["a", "c", "d"])  # No corruption

        def test_large_capacity(self):
            cache = LRUCache(capacity=1000)
            for i in range(2000):
                cache.put(f"key{i}", i)
            self.assertEqual(len(cache), 1000)  # Only 1000 items should remain
            self.assertIn("key1999", cache)  # Most recent keys should exist
            self.assertNotIn("key0", cache)  # Oldest keys should be evicted

            
