"""Test namefinder module."""

import pytest

from src.unoccupied.namefinder import BaseNameFinder
from src.unoccupied.namefinder import NumberNameFinder
from src.unoccupied.namefinder import FileNameFinder


class TestBaseNameFinder:
    @pytest.mark.parametrize('basename, occupied, expected', [
        ('foo', [], 'foo-1'),
        ('foo', ['foo'], 'foo-1'),
        ('foo', ['foo', 'foo-1'], 'foo-2'),
        ('foo', ['foo', 'foo-2'], 'foo-1'),
    ])
    def test_usage(self, basename, occupied, expected):
        base_name_finder = BaseNameFinder()

        assert base_name_finder(basename, occupied) == expected


class TestNumberNameFinder:
    @pytest.mark.parametrize('template, start, expected', [
        ('{basename}', 0, None),
        ('{basename}-{num}', 0, 'foo-0'),
        ('{basename}-{num}', 1, 'foo-1'),
        ('{basename}{num}', 2, 'foo2'),
        ('{basename}.{num}', 2, 'foo.2'),
        ('{num}-{basename}', 2, '2-foo'),
        ('{basename}-{num:04}', 2, 'foo-0002'),
    ])
    def test_define(self, template, start, expected):
        number_name_finder = NumberNameFinder(template=template, start=start)

        basename = 'foo'
        occupied = ['foo']

        assert number_name_finder(basename, occupied) == expected

    @pytest.mark.parametrize('basename, occupied, expected', [
        ('foo', [], 'foo-1'),
        ('foo', ['foo'], 'foo-1'),
        ('foo', ['foo', 'foo-1'], 'foo-2'),
        ('foo', ['foo', 'foo-2'], 'foo-1'),
    ])
    def test_usage_with_default_define(self, basename, occupied, expected):
        number_name_finder = NumberNameFinder()

        assert number_name_finder(basename, occupied) == expected


class TestFileNameFinder:
    @pytest.mark.parametrize('template, start, expected', [
        ('{base}', 0, None),
        ('{base}-{num}', 0, 'foo-0.txt'),
        ('{base}-{num}', 1, 'foo-1.txt'),
        ('{base}{num}', 2, 'foo2.txt'),
        ('{base}.{num}', 2, 'foo.2.txt'),
        ('{num}-{base}', 2, '2-foo.txt'),
        ('{base}-{num:04}', 2, 'foo-0002.txt'),
    ])
    def test_define(self, template, start, expected):
        file_name_finder = FileNameFinder(template=template, start=start)

        basename = 'foo.txt'
        occupied = ['foo.txt']

        assert file_name_finder(basename, occupied) == expected

    @pytest.mark.parametrize('basename, occupied, expected', [
        ('foo.txt', [], 'foo-1.txt'),
        ('foo.txt', ['foo.txt'], 'foo-1.txt'),
        ('foo.txt', ['foo.txt', 'foo-1.txt'], 'foo-2.txt'),
        ('foo.txt', ['foo.txt', 'foo-2.txt'], 'foo-1.txt'),
    ])
    def test_usage_with_default_define(self, basename, occupied, expected):
        file_name_finder = FileNameFinder()

        assert file_name_finder(basename, occupied) == expected
