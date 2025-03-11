# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from collections import OrderedDict
from releng_tool.tool.python import PYTHON
from releng_tool.util.io import execute
from releng_tool.util.io import interpret_stem_extension as ise
from releng_tool.util.io import prepare_arguments
from releng_tool.util.io import prepare_definitions
from releng_tool.util.io import prepend_shebang_interpreter as psi
from releng_tool.util.io import run_script
from releng_tool.util.log import is_verbose
from tests import RelengToolTestCase
from tests import prepare_workdir
from tests import redirect_stdout
from tests.support import fetch_unittest_assets_dir
import os
import sys
import unittest


class TestUtilIo(RelengToolTestCase):
    def test_utilio_execution(self):
        result = execute(None, quiet=True, critical=False)
        self.assertFalse(result)

        result = execute([], quiet=True, critical=False)
        self.assertFalse(result)

        test_cmd = [PYTHON.tool, '-c', 'print("Hello")']
        result = execute(test_cmd, quiet=True, critical=False)
        self.assertTrue(result)

        result = execute(['an_unknown_command'], quiet=True, critical=False)
        self.assertFalse(result)

        result = execute('whoami', quiet=True, critical=False)
        self.assertTrue(result)

        # skip output checks if verbose mode is enabled
        if is_verbose():
            raise unittest.SkipTest(
                'ignoring execution output checks while in verbose mode')

        # verify output
        with redirect_stdout() as stream:
            test_cmd = [
                sys.executable,
                '-c',
                'import sys; print("Hello", file=sys.stderr); print("World")',
            ]
            result = execute(test_cmd, critical=False)
            self.assertTrue(result)
        self.assertEqual(stream.getvalue().strip(), 'Hello\nWorld')

        # verify output (no stderr)
        with redirect_stdout() as stream:
            test_cmd = [
                sys.executable,
                '-c',
                'import sys; print("Hello", file=sys.stderr); print("World")',
            ]
            result = execute(test_cmd, critical=False, ignore_stderr=True)
            self.assertTrue(result)
        self.assertEqual(stream.getvalue().strip(), 'World')

        # verify variable expansion
        os.environ['VERIFY_EXPANSION'] = 'abc123'
        with redirect_stdout() as stream:
            test_cmd = [sys.executable, '-c', 'print("$VERIFY_EXPANSION")']
            result = execute(test_cmd, critical=False)
            self.assertTrue(result)
        self.assertEqual(stream.getvalue().strip(), 'abc123')

        # verify disabled variable expansion
        os.environ['VERIFY_EXPANSION'] = 'abc123'
        with redirect_stdout() as stream:
            test_cmd = [sys.executable, '-c', 'print("$VERIFY_EXPANSION")']
            result = execute(test_cmd, critical=False, expand=False)
            self.assertTrue(result)
        self.assertEqual(stream.getvalue().strip(), '$VERIFY_EXPANSION')

        # verify quiet mode
        with redirect_stdout() as stream:
            test_cmd = [sys.executable, '-c', 'print("Hello")']
            result = execute(test_cmd, quiet=True, critical=False)
            self.assertTrue(result)
        self.assertEqual(stream.getvalue().strip(), '')

        # verify capture mode which will be silent
        out = []
        with redirect_stdout() as stream:
            test_cmd = [sys.executable, '-c', 'print("Hello")']
            result = execute(test_cmd, critical=False, capture=out)
            self.assertTrue(result)
        self.assertEqual(''.join(out), 'Hello')
        self.assertEqual(stream.getvalue().strip(), '')

        # verify capture mode that is also verbose
        out = []
        with redirect_stdout() as stream:
            test_cmd = [sys.executable, '-c', 'print("Hello")']
            result = execute(test_cmd, quiet=False, critical=False, capture=out)
            self.assertTrue(result)
        self.assertEqual(''.join(out), 'Hello')
        self.assertEqual(stream.getvalue().strip(), 'Hello')

    def test_utilio_ise(self):
        provided = 'my-file.txt'
        expected = ('my-file', 'txt')
        self.assertEqual(ise(provided), expected)

        provided = 'my-file.tar.Z'
        expected = ('my-file', 'tar.Z')
        self.assertEqual(ise(provided), expected)

        provided = 'my-file.tar.gz'
        expected = ('my-file', 'tar.gz')
        self.assertEqual(ise(provided), expected)

        provided = 'my-file.tar.xz'
        expected = ('my-file', 'tar.xz')
        self.assertEqual(ise(provided), expected)

        provided = 'my.file.name.dat'
        expected = ('my.file.name', 'dat')
        self.assertEqual(ise(provided), expected)

        provided = 'my-file'
        expected = ('my-file', None)
        self.assertEqual(ise(provided), expected)

        provided = None
        expected = (None, None)
        self.assertEqual(ise(provided), expected)

    def test_utilio_prepare_helpers(self):
        prepared = prepare_arguments(None)
        expected = []
        self.assertEqual(prepared, expected)

        prepared = prepare_arguments({})
        expected = []
        self.assertEqual(prepared, expected)

        args = OrderedDict()
        args['foo'] = 'bar'
        args['xyz'] = ''
        prepared = prepare_arguments(args)
        expected = ['foo', 'bar', 'xyz']
        self.assertEqual(prepared, expected)

        args = OrderedDict()
        args['foo'] = 'bar'
        args['test'] = None
        prepared = prepare_arguments(args)
        expected = ['foo', 'bar']
        self.assertEqual(prepared, expected)

        prepared = prepare_definitions(None)
        expected = []
        self.assertEqual(prepared, expected)

        prepared = prepare_definitions({})
        expected = []
        self.assertEqual(prepared, expected)

        args = OrderedDict()
        args['foo'] = 'bar'
        args['xyz'] = ''
        prepared = prepare_definitions(args)
        expected = ['foo=bar', 'xyz=']
        self.assertEqual(prepared, expected)

        args = OrderedDict()
        args['foo'] = 'bar'
        args['test'] = None
        prepared = prepare_definitions(args)
        expected = ['foo=bar']
        self.assertEqual(prepared, expected)

    def test_utilio_runscript(self):
        with prepare_workdir() as work_dir:
            valid_script = os.path.join(work_dir, 'valid')
            with open(valid_script, 'a') as f:
                f.write('test=1\n')

            result = run_script(valid_script, {})
            self.assertEqual(result['test'], 1)

            invalid_script = os.path.join(work_dir, 'invalid')
            with open(invalid_script, 'a') as f:
                f.write('bad-line\n')

            result = run_script(invalid_script, {})
            self.assertIsNone(result)

            with self.assertRaises(NameError):
                run_script(invalid_script, {}, catch=False)

    def test_utilio_shebang_interpreter(self):
        si_dir = fetch_unittest_assets_dir('shebang-interpreter')
        si01 = [os.path.join(si_dir, 'interpreter')]
        si02 = [os.path.join(si_dir, 'interpreter-arg')]
        si03 = [os.path.join(si_dir, 'interpreter-args-multiple')]
        si04 = [os.path.join(si_dir, 'interpreter-extremely-long')]
        si05 = [os.path.join(si_dir, 'interpreter-whitespaces')]
        si06 = [os.path.join(si_dir, 'example.py')]

        # encode helper as helper utility will execute with encoded strings
        def E(val):
            rv = []
            for v in val:
                rv.append(v.encode())
            return rv

        # simple interpreter
        self.assertEqual(psi(si01), [b'interpreter', *E(si01)])
        # interpreter with a single argument
        self.assertEqual(psi(si02), [b'interpreter', b'arg', *E(si02)])
        # interpreter with a single argument (with whitespaces)
        self.assertEqual(psi(si03), [b'interpreter', b'arg1 arg2', *E(si03)])
        # too long of an interpreter
        self.assertEqual(psi(si04), si04)
        # interpreter with whitespaces
        self.assertEqual(psi(si05), [b'interpreter', *E(si05)])
        # real example of an interpreter
        self.assertEqual(psi(si06), [b'/usr/bin/env', b'python', *E(si06)])
