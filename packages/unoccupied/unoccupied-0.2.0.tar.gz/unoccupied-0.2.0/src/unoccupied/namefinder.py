"""Name finder - find and return a unoccupied name."""

import os

from itertools import count
from functools import lru_cache


def _standard_name_finder(
        basename, norm_occupied,
        ids_generator=lambda: count(start=1),
        formatter=lambda **frags: '{basename}-{id}'.format(**frags),
):
    """Help to build a name finder.

    Args:
        ids_generator: (callable)
            Signature:
                ids_generator() -> Iterable

            `ids_generator` create a series of id and push to `formatter`.

        formatter: (callable)
            Signature:
                formatter(basename, id) -> str

            The `id` is one of `ids_generator` generated result.

    Returns:
        None or a unoccupied string.

    """
    checked = set()

    for id_ in ids_generator():
        testing_name = formatter(id=id_, basename=basename)

        if testing_name in checked:
            return None
        else:
            checked.add(testing_name)

        if testing_name not in norm_occupied:
            return testing_name


class BaseNameFinder:
    """Base class for create a name finder easily.

    Usually, you shouldn't use this class directly but should inherit it.
    """

    def __call__(self, basename, norm_occupied):
        """Run a name finder.

        This function usually not need to re-implement.
        """
        return _standard_name_finder(
            basename, norm_occupied,
            ids_generator=self.ids_generator,
            formatter=self.formatter,
        )

    def ids_generator(self):
        """Generate iterable multiple ids or container.

        The result `id` will inject to self.formatter(basename, id)

        Re-implement this if need.
        """
        return count(start=1)

    def formatter(self, basename, id):
        """Generate testing name.

        Re-implement this if need.
        """
        return '{basename}-{id}'.format(basename=basename, id=id)


class NumberNameFinder(BaseNameFinder):
    """Use `basename` and increasing `num` to find a new name."""

    def __init__(self, template='{basename}-{num}', start=1):
        """Configure NumberNameFinder.

        Args:
            template: (str)
                a python str.format template.
                this template can include 2 keyword params:
                    {basename}: wanted basename
                    {num}: increasing number

            start: (int)
                start testing value for {num} in template.
        """
        self.template = template
        self.start = start

    def ids_generator(self):  # noqa: D102
        return count(start=self.start)

    def formatter(self, basename, id):  # noqa: D102
        return self.template.format(basename=basename, num=id)


class FileNameFinder(BaseNameFinder):
    """Auto process filename extension then find a new name."""

    def __init__(self, template='{base}-{num}', start=1):
        """Configure FileNameFinder.

        Args:
            template: (str)
                a python str.format template.
                this template can include 2 keyword params:
                    {base}: filename base part from wanted filename
                    {num}: increasing number

                Result will be auto append the original filename extension.

            start: (int)
                start testing value for {num} in template.
        """
        self.template = template
        self.start = start

    @lru_cache()
    def __split_basename(self, basename):
        """Cache splited result of basename."""
        return os.path.splitext(basename)

    def ids_generator(self):  # noqa: D102
        return count(start=self.start)

    def formatter(self, basename, id):  # noqa: D102
        base, ext = self.__split_basename(basename)

        return self.template.format(num=id, base=base) + ext
