from _pytest.assertion.util import assertrepr_compare
from io import StringIO, FileIO
import sys
from unittest import mock


def fake_open(file_contents):
    def _f(file, mode='r'):
        if file in file_contents:
            if mode == 'r':
                return StringIO(file_contents[file])
            elif mode == 'a':
                return FakeFileWriter(file, file_contents)
            elif mode == 'w':
                file_contents[file] = ''
                return FakeFileWriter(file, file_contents)
        else:
            raise ValueError(f'You tried to open {file}, but you didn\'t fake it out!')

    return _f


class FakeFileWriter:
    def __init__(self, file, contents):
        self.file = file
        self.contents = contents

    def write(self, s):
        self.contents[self.file] += s

    def __enter__(self, *args):
        return self

    def __exit__(self, *args):
        return self


class FakeStringIO(StringIO):
    def __eq__(self, other):
        if isinstance(other, str):
            return self.getvalue().strip() == other.strip()
        else:
            return super().__eq__(other)

    def __repr__(self):
        return repr(self.getvalue().strip())


class FakeStdIn:
    def __init__(self, responses):
        self.responses = responses
        self.idx = 0

    def readline(self):
        if self.idx >= len(self.responses):
            raise AssertionError('No more input provided!')
        else:
            self.idx += 1
            sys.stdout.write(self.responses[self.idx - 1] + '\n')
            return self.responses[self.idx - 1]


def pytest_assertrepr_compare(config, op, left, right):
    if isinstance(left, FakeStringIO) and isinstance(right, str) and op == '==':
        return assertrepr_compare(
            config,
            op,
            left.getvalue().strip(),
            right.strip(),
        )
