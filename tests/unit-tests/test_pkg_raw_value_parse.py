# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from pathlib import Path
from releng_tool.defs import VOID
from releng_tool.packages import PkgKeyType
from releng_tool.packages import raw_value_parse
from tests import RelengToolTestCase
import os


class TestPkgRawValueParse(RelengToolTestCase):
    def test_pkg_rvp_bool_only(self):
        rv = raw_value_parse(True, PkgKeyType.BOOL)  # noqa: FBT003
        self.assertTrue(rv)

        rv = raw_value_parse(False, PkgKeyType.BOOL)  # noqa: FBT003
        self.assertFalse(rv)

        with self.assertRaises(TypeError):
            raw_value_parse(None, PkgKeyType.BOOL)

        with self.assertRaises(TypeError):
            raw_value_parse('value', PkgKeyType.BOOL)

    def test_pkg_rvp_bool_or_str(self):
        rv = raw_value_parse(True, PkgKeyType.BOOL_OR_STR)  # noqa: FBT003
        self.assertTrue(rv)

        rv = raw_value_parse(False, PkgKeyType.BOOL_OR_STR)  # noqa: FBT003
        self.assertFalse(rv)

        rv = raw_value_parse('value', PkgKeyType.BOOL_OR_STR)
        self.assertEqual(rv, 'value')

        with self.assertRaises(TypeError):
            raw_value_parse(None, PkgKeyType.BOOL_OR_STR)

        with self.assertRaises(TypeError):
            raw_value_parse(123, PkgKeyType.BOOL_OR_STR)

    def test_pkg_rvp_dict(self):
        rv = raw_value_parse({}, PkgKeyType.DICT)
        self.assertEqual(rv, {})

        rv = raw_value_parse({'a': 'b'}, PkgKeyType.DICT)
        self.assertEqual(rv, {'a': 'b'})

        rv = raw_value_parse({'a': True, 'b': 123}, PkgKeyType.DICT)
        self.assertEqual(rv, {'a': True, 'b': 123})

        with self.assertRaises(TypeError):
            raw_value_parse(None, PkgKeyType.DICT)

        with self.assertRaises(TypeError):
            raw_value_parse('value', PkgKeyType.DICT)

    def test_pkg_rvp_dict_str_pstr(self):
        rv = raw_value_parse({}, PkgKeyType.DICT_STR_PSTR)
        self.assertEqual(rv, {})

        rv = raw_value_parse({'a': 'b'}, PkgKeyType.DICT_STR_PSTR)
        self.assertEqual(rv, {'a': 'b'})

        rv = raw_value_parse({'c': Path('d')}, PkgKeyType.DICT_STR_PSTR)
        self.assertEqual(rv, {'c': 'd'})

        with self.assertRaises(TypeError):
            raw_value_parse(None, PkgKeyType.DICT_STR_PSTR)

        with self.assertRaises(TypeError):
            raw_value_parse('value', PkgKeyType.DICT_STR_PSTR)

        with self.assertRaises(TypeError):
            raw_value_parse({'a': 'valid', 'b': 123}, PkgKeyType.DICT_STR_PSTR)

        with self.assertRaises(TypeError):
            raw_value_parse({'a': True, 'b': 123}, PkgKeyType.DICT_STR_PSTR)

    def test_pkg_rvp_dict_str_str_or_str(self):
        rv = raw_value_parse('', PkgKeyType.DICT_STR_STR_OR_STR)
        self.assertEqual(rv, '')

        rv = raw_value_parse('value', PkgKeyType.DICT_STR_STR_OR_STR)
        self.assertEqual(rv, 'value')

        rv = raw_value_parse({}, PkgKeyType.DICT_STR_STR_OR_STR)
        self.assertEqual(rv, {})

        rv = raw_value_parse({'a': 'b'}, PkgKeyType.DICT_STR_STR_OR_STR)
        self.assertEqual(rv, {'a': 'b'})

        with self.assertRaises(TypeError):
            raw_value_parse(None, PkgKeyType.DICT_STR_STR_OR_STR)

        with self.assertRaises(TypeError):
            raw_value_parse(123, PkgKeyType.DICT_STR_STR_OR_STR)

        with self.assertRaises(TypeError):
            raw_value_parse(
                {'a': 'valid', 'b': 123}, PkgKeyType.DICT_STR_STR_OR_STR)

        with self.assertRaises(TypeError):
            raw_value_parse(
                {'a': True, 'b': 123}, PkgKeyType.DICT_STR_STR_OR_STR)

    def test_pkg_rvp_int_nonnegative(self):
        rv = raw_value_parse(1, PkgKeyType.INT_NONNEGATIVE)
        self.assertEqual(rv, 1)

        rv = raw_value_parse(0, PkgKeyType.INT_NONNEGATIVE)
        self.assertEqual(rv, 0)

        with self.assertRaises(TypeError):
            raw_value_parse(None, PkgKeyType.INT_NONNEGATIVE)

        with self.assertRaises(TypeError):
            raw_value_parse('value', PkgKeyType.INT_NONNEGATIVE)

        with self.assertRaises(ValueError):
            raw_value_parse(-1, PkgKeyType.INT_NONNEGATIVE)

    def test_pkg_rvp_int_positive(self):
        rv = raw_value_parse(1, PkgKeyType.INT_POSITIVE)
        self.assertEqual(rv, 1)

        with self.assertRaises(TypeError):
            raw_value_parse(None, PkgKeyType.INT_POSITIVE)

        with self.assertRaises(TypeError):
            raw_value_parse('value', PkgKeyType.INT_POSITIVE)

        with self.assertRaises(ValueError):
            raw_value_parse(0, PkgKeyType.INT_POSITIVE)

        with self.assertRaises(ValueError):
            raw_value_parse(-1, PkgKeyType.INT_POSITIVE)

    def test_pkg_rvp_opts(self):
        rv = raw_value_parse({}, PkgKeyType.OPTS)
        self.assertEqual(rv, {})

        rv = raw_value_parse({'a': 'b'}, PkgKeyType.OPTS)
        self.assertEqual(rv, {'a': 'b'})

        rv = raw_value_parse({'c': Path('d')}, PkgKeyType.OPTS)
        self.assertEqual(rv, {'c': 'd'})

        rv = raw_value_parse('', PkgKeyType.OPTS)
        self.assertEqual(rv, {'': VOID})

        rv = raw_value_parse(['e', Path('f')], PkgKeyType.OPTS)
        self.assertEqual(rv, {'e': VOID, 'f': VOID})

        rv = raw_value_parse('value', PkgKeyType.OPTS)
        self.assertEqual(rv, {'value': VOID})

        with self.assertRaises(TypeError):
            raw_value_parse(None, PkgKeyType.OPTS)

        with self.assertRaises(TypeError):
            raw_value_parse(123, PkgKeyType.OPTS)

        with self.assertRaises(TypeError):
            raw_value_parse(
                {'a': 'valid', 'b': 123}, PkgKeyType.OPTS)

        with self.assertRaises(TypeError):
            raw_value_parse(
                {'a': True, 'b': 123}, PkgKeyType.OPTS)

    def test_pkg_rvp_pstr(self):
        rv = raw_value_parse('', PkgKeyType.PSTR)
        self.assertEqual(rv, '')

        rv = raw_value_parse('value', PkgKeyType.PSTR)
        self.assertEqual(rv, 'value')

        rv = raw_value_parse(Path('value'), PkgKeyType.PSTR)
        self.assertEqual(rv, 'value')

        rv = raw_value_parse(Path('some') / 'value', PkgKeyType.PSTR)
        self.assertEqual(rv, f'some{os.sep}value')

        with self.assertRaises(TypeError):
            raw_value_parse(None, PkgKeyType.PSTR)

        with self.assertRaises(TypeError):
            raw_value_parse(['value'], PkgKeyType.PSTR)

        with self.assertRaises(TypeError):
            raw_value_parse([True], PkgKeyType.PSTR)

        with self.assertRaises(TypeError):
            raw_value_parse(1, PkgKeyType.PSTR)

    def test_pkg_rvp_str(self):
        rv = raw_value_parse('', PkgKeyType.STR)
        self.assertEqual(rv, '')

        rv = raw_value_parse('value', PkgKeyType.STR)
        self.assertEqual(rv, 'value')

        with self.assertRaises(TypeError):
            raw_value_parse(None, PkgKeyType.STR)

        with self.assertRaises(TypeError):
            raw_value_parse(['value'], PkgKeyType.STR)

        with self.assertRaises(TypeError):
            raw_value_parse([True], PkgKeyType.STR)

        with self.assertRaises(TypeError):
            raw_value_parse(1, PkgKeyType.STR)

    def test_pkg_rvp_strs(self):
        rv = raw_value_parse([], PkgKeyType.STRS)
        self.assertEqual(rv, [])

        rv = raw_value_parse([''], PkgKeyType.STRS)
        self.assertEqual(rv, [''])

        rv = raw_value_parse('value', PkgKeyType.STRS)
        self.assertEqual(rv, ['value'])

        rv = raw_value_parse(['value'], PkgKeyType.STRS)
        self.assertEqual(rv, ['value'])

        with self.assertRaises(TypeError):
            raw_value_parse(None, PkgKeyType.STRS)

        with self.assertRaises(TypeError):
            raw_value_parse([True], PkgKeyType.STRS)

        with self.assertRaises(TypeError):
            raw_value_parse(1, PkgKeyType.STRS)
