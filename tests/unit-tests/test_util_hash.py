# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.util.hash import HashResult
from releng_tool.util.hash import BadFileHashLoadError
from releng_tool.util.hash import BadFormatHashLoadError
from releng_tool.util.hash import load as load_hashes
from releng_tool.util.hash import verify as verify_hashes
from tests import RelengToolTestCase
import os


ASSETS_DIR = 'assets'
SAMPLES_DIR = 'hash-samples'


class TestUtilHash(RelengToolTestCase):
    @classmethod
    def setUpClass(cls):
        base_dir = os.path.dirname(os.path.realpath(__file__))
        cls.samples_dir = os.path.join(base_dir, ASSETS_DIR, SAMPLES_DIR)

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
            ('type', 'hash', 'file'),
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
            ('blake2b',
                '2de3fb97c83a6c959f7ca1f6dffd7a2a4533a54b0542a49069ff15d45c928f'
                'f7747488c4b697a82a6bc133d4b0b99ca23d97d0e244347a8f3966740afbc5'
                'bb24',
                'sample-asset'),
            ('blake2s',
                '223725c4a88bc1c93f7d073ce37085e51fc8150137a3607531ea3025df9b65'
                'eb',
                'sample-asset'),
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
            ('sha3_224',
                '3aff99f4000c02453dad244565c74bc764b27b77aafda64e88fb1765',
                'sample-asset'),
            ('sha3_256',
                '933114c8a52661f9a8e6a3e659fc307f3454cff30da97035a556d095fd9caa'
                '23',
                'sample-asset'),
            ('sha3_384',
                '4d206cf4bae2d4465a43ffab5c76bb2e8e7dfd593dd4793f64eb5a81431877'
                '089851c9f4de6ec3a4244154d6dc3e3e6c',
                'sample-asset'),
            ('sha3_512',
                'e8bf4924c9df7604fc3e8eed08a0fe3e83d4c00ce8458106a737a3bb71f59b'
                '370df6ffa977ac5056484c45de2a3944c13435f7af75d069c8b6143717bd79'
                '1f0d',
                'sample-asset'),
            ('sha512',
                '741695d2189840162a19d9a8f8c99e7adc4621f452b43d20081a5ebb23b9d7'
                '3e15c3ffb9b06c65621da269686da2d5991f5ac415cdd2cfcd5faf10d3aa47'
                'd728',
                'sample-asset'),
            ('shake_128:32',
                'd31029b471ea2797944b90c578d7f683caf5026aca5e02043e688066473ad9'
                '85',
                'sample-asset'),
            ('shake_256:64',
                '039bf1dc6f102006eacd32fdd4bea405303bc09d1739ec1c4e52b956fd282a'
                '7d50e8580232e653cd191605226a3c06f178e3b6eafa6b7a6e7944e2cbbb2e'
                '4329',
                'sample-asset'),
        ])

        # empty hash file provided an empty list
        file = os.path.join(samples, 'valid-hash-sample-d')
        data = load_hashes(file)
        self.assertEqual(data, [])

    def test_utilhash_verify(self):
        samples = self.samples_dir
        target_sample = os.path.join(samples, 'sample-asset')

        # archive-specific check
        file = os.path.join(samples, 'verify-missing-archive')
        result = verify_hashes(file, target_sample, quiet=True)
        self.assertEqual(result, HashResult.MISSING_ARCHIVE)

        file = os.path.join(samples, 'verify-success')
        result = verify_hashes(file, target_sample)
        self.assertEqual(result, HashResult.VERIFIED)

        # directory-specific check
        file = os.path.join(samples, 'verify-bad-format-keylen-int')
        result = verify_hashes(file, samples, quiet=True)
        self.assertEqual(result, HashResult.BAD_FORMAT)

        file = os.path.join(samples, 'verify-bad-format-keylen-nonint')
        result = verify_hashes(file, samples, quiet=True)
        self.assertEqual(result, HashResult.BAD_FORMAT)

        file = os.path.join(samples, 'verify-bad-format-missing-file')
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

        # missing check
        result = verify_hashes('', '', quiet=True)
        self.assertEqual(result, HashResult.BAD_PATH)

        # excluded/empty
        exclude = ['sample-asset']
        file = os.path.join(samples, 'verify-success')
        result = verify_hashes(file, target_sample, exclude=exclude)
        self.assertEqual(result, HashResult.EMPTY)
