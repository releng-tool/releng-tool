#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2018 releng-tool

from releng_tool.util.hash import HashResult
from releng_tool.util.hash import BadFileHashLoadError
from releng_tool.util.hash import BadFormatHashLoadError
from releng_tool.util.hash import load as load_hashes
from releng_tool.util.hash import verify as verify_hashes
import os
import unittest

ASSETS_DIR = 'assets'
SAMPLES_DIR = 'hash-samples'

class TestUtilHash(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        base_dir = os.path.dirname(os.path.realpath(__file__))
        self.samples_dir = os.path.join(base_dir, ASSETS_DIR, SAMPLES_DIR)

    def test_utilhash_loading(self):
        samples = self.samples_dir

        # generates exception if missing
        file = os.path.join(samples, 'a-file-that-does-not-exist')
        self.assertRaises(BadFileHashLoadError, load_hashes, file)

        # generates a format exception if hashes are not properly defined
        invalid_samples = [
            'invalid-hash-sample-a',
            'invalid-hash-sample-b',
            'invalid-hash-sample-c',
        ]
        for sample in invalid_samples:
            file = os.path.join(samples, sample)
            self.assertRaises(BadFormatHashLoadError, load_hashes, file)

        # test
        file = os.path.join(samples, 'valid-hash-sample-a')
        data = load_hashes(file)
        self.assertEqual(data, [
            ('type', 'hash', 'file')
        ])

        # test
        file = os.path.join(samples, 'valid-hash-sample-b')
        data = load_hashes(file)
        self.assertEqual(data, [
            ('type1', 'hash1', 'file1'),
            ('type2', 'hash2', 'file2'),
            ('type3', 'hash3', 'file3'),
            ('type4', 'hash4', 'file4'),
            ('type5', 'hash5', 'file5'),
        ])

        # test
        file = os.path.join(samples, 'valid-hash-sample-c')
        data = load_hashes(file)
        self.assertEqual(data, [
            ('md5',
                '37a460dd2f87f3c04a4a85b38d922eb1',
                'sample-asset'),
            ('sha1',
                'b713d8fc4807ff7f0b186b618ae65b6e7fa66f5a',
                'sample-asset'),
            ('sha224',
                '5d03e966de09ffc2f3c7416963c0a20631e4a950f965ffc7e6f2588d',
                'sample-asset'),
            ('sha256',
                '0f595a93a91e678d592dd7978b1d215be1adc27123509eabb6b7f02eaf1315'
                'd0a4',
                'sample-asset'),
            ('sha384',
                '60d4b57034872b8617bb1a0a0e076d0a97a6d44485c5e013e9156b8f51346d'
                '58b36ea1be51c57c23600aed1fb301e07f',
                'sample-asset'),
            ('sha512',
                '741695d2189840162a19d9a8f8c99e7adc4621f452b43d20081a5ebb23b9d7'
                '3e15c3ffb9b06c65621da269686da2d5991f5ac415cdd2cfcd5faf10d3aa47'
                'd728',
                'sample-asset'),
        ])

        # empty hash file provided an empty list
        file = os.path.join(samples, 'valid-hash-sample-d')
        data = load_hashes(file)
        self.assertEqual(data, [])

    def test_utilhash_verify(self):
        samples = self.samples_dir

        # archive-specific check
        target_sample = os.path.join(samples, 'sample-asset')

        file = os.path.join(samples, 'verify-missing-archive')
        result = verify_hashes(file, target_sample, quiet=True)
        self.assertEqual(result, HashResult.MISSING_ARCHIVE)

        file = os.path.join(samples, 'verify-success')
        result = verify_hashes(file, target_sample, quiet=True)
        self.assertEqual(result, HashResult.VERIFIED)

        # directory-specific check
        file = os.path.join(samples, 'verify-bad-format')
        result = verify_hashes(file, samples, quiet=True)
        self.assertEqual(result, HashResult.BAD_FORMAT)

        file = os.path.join(samples, 'verify-some-file-that-should-not-exist')
        result = verify_hashes(file, samples, quiet=True)
        self.assertEqual(result, HashResult.BAD_PATH)

        file = os.path.join(samples, 'verify-bad-hash')
        result = verify_hashes(file, samples, quiet=True)
        self.assertEqual(result, HashResult.MISMATCH)

        file = os.path.join(samples, 'verify-empty')
        result = verify_hashes(file, samples, quiet=True)
        self.assertEqual(result, HashResult.EMPTY)

        file = os.path.join(samples, 'verify-missing-listed')
        result = verify_hashes(file, samples, quiet=True)
        self.assertEqual(result, HashResult.MISSING_LISTED)

        file = os.path.join(samples, 'verify-success')
        result = verify_hashes(file, samples, quiet=True)
        self.assertEqual(result, HashResult.VERIFIED)

        file = os.path.join(samples, 'verify-unknown-hash-type')
        result = verify_hashes(file, samples, quiet=True)
        self.assertEqual(result, HashResult.UNSUPPORTED)
