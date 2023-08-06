"""Test main module."""

import pytest

from src.unoccupied.main import unoccupied
from src.unoccupied.main import UnoccupiedNameNotFound


class TestUnoccupied:
    @pytest.mark.parametrize('basename, occupied, expected', [
        ('foo', [], 'foo'),
        ('foo', ['bar'], 'foo'),
        ('foo', ['foo'], 'foo-1'),
    ])
    def test_basic(self, basename, occupied, expected):
        assert unoccupied(basename, occupied) == expected

    def test_occupied_is_str(self):
        with pytest.raises(TypeError):
            unoccupied('foo', 'bar')  # str as `occupied` are not allow

    def test_nobase(self):
        assert unoccupied('foo', [], nobase=True) == 'foo-1'

    def test_call_name_finder_only_needed(self):
        called = False

        def pseudo_name_finder(basename, occupied):
            nonlocal called
            called = True

            return 'whatever'

        unoccupied('foo', [], pseudo_name_finder)
        assert called is False

        unoccupied('foo', ['foo'], pseudo_name_finder)
        assert called is True

    def test_occupied_become_frozenset(self):
        def pseudo_name_finder(basename, occupied):
            assert isinstance(occupied, frozenset)

            return 'whatever'

        unoccupied('foo', ['foo'], pseudo_name_finder)

    def test_name_finder_return_none(self):
        with pytest.raises(UnoccupiedNameNotFound):
            def pseudo_name_finder(basename, occupied):
                return None

            unoccupied('foo', ['foo'], pseudo_name_finder)

    def test_name_finder_return_basename(self):
        with pytest.raises(UnoccupiedNameNotFound):
            def pseudo_name_finder(basename, occupied):
                return basename

            unoccupied('foo', ['foo'], pseudo_name_finder)

    def test_name_finder_return_elem_in_occupied(self):
        with pytest.raises(UnoccupiedNameNotFound):
            def pseudo_name_finder(basename, occupied):
                return 'bar'

            unoccupied('foo', ['foo', 'bar'], pseudo_name_finder)

    def test_name_finder_return_elem_not_str_or_none(self):
        with pytest.raises(TypeError):
            def pseudo_name_finder(basename, occupied):
                return ['return a list']

            unoccupied('foo', ['foo', 'bar'], pseudo_name_finder)
