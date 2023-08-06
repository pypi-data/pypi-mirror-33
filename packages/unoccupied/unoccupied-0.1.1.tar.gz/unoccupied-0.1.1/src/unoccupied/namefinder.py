"""Name finder - find and return a unoccupied name."""

import os

from itertools import count


class NumberNameFinder:
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

    def __call__(self, basename, occupied):
        """Get the first unoccupied name (not include `basename` itself)."""
        checked = set()

        for num in count(start=self.start):
            testing_name = self.template.format(basename=basename, num=num)

            if testing_name in checked:
                return None
            else:
                checked.add(testing_name)

            if testing_name not in occupied:
                return testing_name


class FileNameFinder:
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

    def __call__(self, basename, occupied):
        """Get the first unoccupied name (not include `basename` itself)."""
        checked = set()
        base, ext = os.path.splitext(basename)

        for num in count(start=self.start):
            testing_name = self.template.format(base=base, num=num) + ext

            if testing_name in checked:
                return None
            else:
                checked.add(testing_name)

            if testing_name not in occupied:
                return testing_name
