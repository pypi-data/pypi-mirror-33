import array
import os
import unittest
import random
import struct
import sys
import xxhash


def getrefcount(obj):
    if hasattr(sys, "getrefcount"):
        return sys.getrefcount(obj)
    else:
        # Non-CPython implementation
        return 0


class TestXXHASH(unittest.TestCase):
    def test_version(self):
        self.assertTrue(xxhash.VERSION)
        self.assertTrue(xxhash.XXHASH_VERSION)

    def test_xxh32(self):
        self.assertEqual(xxhash.xxh32('a').intdigest(), 1426945110)
        self.assertEqual(xxhash.xxh32('a', 0).intdigest(), 1426945110)
        self.assertEqual(xxhash.xxh32('a', 1).intdigest(), 4111757423)
        self.assertEqual(xxhash.xxh32('a', 2**32-1).intdigest(), 3443684653)

    def test_xxh64(self):
        self.assertEqual(xxhash.xxh64('a').intdigest(), 15154266338359012955)
        self.assertEqual(xxhash.xxh64('a', 0).intdigest(), 15154266338359012955)
        self.assertEqual(xxhash.xxh64('a', 1).intdigest(), 16051599287423682246)
        self.assertEqual(xxhash.xxh64('a', 2**64-1).intdigest(), 6972758980737027682)

    def test_xxh32_update(self):
        x = xxhash.xxh32()
        x.update('a')
        self.assertEqual(xxhash.xxh32('a').digest(), x.digest())
        x.update('b')
        self.assertEqual(xxhash.xxh32('ab').digest(), x.digest())
        x.update('c')
        self.assertEqual(xxhash.xxh32('abc').digest(), x.digest())

        seed = random.randint(0, 2**32)
        x = xxhash.xxh32(seed=seed)
        x.update('a')
        self.assertEqual(xxhash.xxh32('a', seed).digest(), x.digest())
        x.update('b')
        self.assertEqual(xxhash.xxh32('ab', seed).digest(), x.digest())
        x.update('c')
        self.assertEqual(xxhash.xxh32('abc', seed).digest(), x.digest())

    def test_xxh64_update(self):
        x = xxhash.xxh64()
        x.update('a')
        self.assertEqual(xxhash.xxh64('a').digest(), x.digest())
        x.update('b')
        self.assertEqual(xxhash.xxh64('ab').digest(), x.digest())
        x.update('c')
        self.assertEqual(xxhash.xxh64('abc').digest(), x.digest())
        seed = random.randint(0, 2**64)
        x = xxhash.xxh64(seed=seed)
        x.update('a')
        self.assertEqual(xxhash.xxh64('a', seed).digest(), x.digest())
        x.update('b')
        self.assertEqual(xxhash.xxh64('ab', seed).digest(), x.digest())
        x.update('c')
        self.assertEqual(xxhash.xxh64('abc', seed).digest(), x.digest())

    def test_xxh32_reset(self):
        x = xxhash.xxh32()
        h = x.intdigest()

        for i in range(10, 50):
            x.update(os.urandom(i))

        x.reset()

        self.assertEqual(h, x.intdigest())

    def test_xxh64_reset(self):
        x = xxhash.xxh64()
        h = x.intdigest()

        for i in range(10, 50):
            x.update(os.urandom(i))

        x.reset()

        self.assertEqual(h, x.intdigest())

    def test_xxh32_copy(self):
        a = xxhash.xxh32()
        a.update('xxhash')

        b = a.copy()
        self.assertEqual(a.digest(), b.digest())
        self.assertEqual(a.intdigest(), b.intdigest())
        self.assertEqual(a.hexdigest(), b.hexdigest())

        b.update('xxhash')
        self.assertNotEqual(a.digest(), b.digest())
        self.assertNotEqual(a.intdigest(), b.intdigest())
        self.assertNotEqual(a.hexdigest(), b.hexdigest())

        a.update('xxhash')
        self.assertEqual(a.digest(), b.digest())
        self.assertEqual(a.intdigest(), b.intdigest())
        self.assertEqual(a.hexdigest(), b.hexdigest())

    def test_xxh64_copy(self):
        a = xxhash.xxh64()
        a.update('xxhash')

        b = a.copy()
        self.assertEqual(a.digest(), b.digest())
        self.assertEqual(a.intdigest(), b.intdigest())
        self.assertEqual(a.hexdigest(), b.hexdigest())

        b.update('xxhash')
        self.assertNotEqual(a.digest(), b.digest())
        self.assertNotEqual(a.intdigest(), b.intdigest())
        self.assertNotEqual(a.hexdigest(), b.hexdigest())

        a.update('xxhash')
        self.assertEqual(a.digest(), b.digest())
        self.assertEqual(a.intdigest(), b.intdigest())
        self.assertEqual(a.hexdigest(), b.hexdigest())

    def test_xxh32_overflow(self):
        a = xxhash.xxh32('I want an unsigned 32-bit seed!', seed=0)
        b = xxhash.xxh32('I want an unsigned 32-bit seed!', seed=2**32)
        self.assertEqual(a.seed, b.seed)
        self.assertEqual(a.intdigest(), b.intdigest())
        self.assertEqual(a.hexdigest(), b.hexdigest())
        self.assertEqual(a.digest(), b.digest())

        a = xxhash.xxh32('I want an unsigned 32-bit seed!', seed=1)
        b = xxhash.xxh32('I want an unsigned 32-bit seed!', seed=2**32+1)
        self.assertEqual(a.seed, b.seed)
        self.assertEqual(a.intdigest(), b.intdigest())
        self.assertEqual(a.hexdigest(), b.hexdigest())
        self.assertEqual(a.digest(), b.digest())

        a = xxhash.xxh32('I want an unsigned 32-bit seed!', seed=2**33-1)
        b = xxhash.xxh32('I want an unsigned 32-bit seed!', seed=2**34-1)
        self.assertEqual(a.seed, b.seed)
        self.assertEqual(a.intdigest(), b.intdigest())
        self.assertEqual(a.hexdigest(), b.hexdigest())
        self.assertEqual(a.digest(), b.digest())

        a = xxhash.xxh32('I want an unsigned 32-bit seed!', seed=2**65-1)
        b = xxhash.xxh32('I want an unsigned 32-bit seed!', seed=2**66-1)
        self.assertEqual(a.seed, b.seed)
        self.assertEqual(a.intdigest(), b.intdigest())
        self.assertEqual(a.hexdigest(), b.hexdigest())
        self.assertEqual(a.digest(), b.digest())

    def test_xxh64_overflow(self):
        a = xxhash.xxh64('I want an unsigned 64-bit seed!', seed=0)
        b = xxhash.xxh64('I want an unsigned 64-bit seed!', seed=2**64)
        self.assertEqual(a.seed, b.seed)
        self.assertEqual(a.intdigest(), b.intdigest())
        self.assertEqual(a.hexdigest(), b.hexdigest())
        self.assertEqual(a.digest(), b.digest())

        a = xxhash.xxh64('I want an unsigned 64-bit seed!', seed=1)
        b = xxhash.xxh64('I want an unsigned 64-bit seed!', seed=2**64+1)
        self.assertEqual(a.seed, b.seed)
        self.assertEqual(a.intdigest(), b.intdigest())
        self.assertEqual(a.hexdigest(), b.hexdigest())
        self.assertEqual(a.digest(), b.digest())

        a = xxhash.xxh64('I want an unsigned 64-bit seed!', seed=2**65-1)
        b = xxhash.xxh64('I want an unsigned 64-bit seed!', seed=2**66-1)
        self.assertEqual(a.seed, b.seed)
        self.assertEqual(a.intdigest(), b.intdigest())
        self.assertEqual(a.hexdigest(), b.hexdigest())
        self.assertEqual(a.digest(), b.digest())

    def test_buffer_types(self):
        # Various buffer-like objects are accepted, and they give similar values
        args = [b'ab\x00c', bytearray(b'ab\x00c'), array.array('b', b'ab\x00c')]
        # An array object with non-1 itemsize
        a = array.array('i', struct.unpack('i', b'ab\x00c'))
        assert a.itemsize == 4
        args.append(a)
        # A memoryview, where supported
        if sys.version_info >= (2, 7):
            args.append(memoryview(b'ab\x00c'))

        for func in [xxhash.xxh32, xxhash.xxh64]:
            old_refcounts = list(map(getrefcount, args))
            # With constructor
            values = set(func(arg).hexdigest() for arg in args)
            self.assertEqual(len(values), 1, values)
            # With update()
            values = set()
            for arg in args:
                x = func()
                x.update(arg)
                values.add(x.hexdigest())
            self.assertEqual(len(values), 1, values)
            # No reference leak in CPython extension
            del arg
            self.assertEqual(list(map(getrefcount, args)), old_refcounts)


if __name__ == '__main__':
    unittest.main()
