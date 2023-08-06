"""Main module."""

from .namefinder import NumberNameFinder


class UnoccupiedNameNotFound(Exception):
    """Raise when unoccupied name not found."""


def unoccupied(
        basename, occupied, name_finder=NumberNameFinder(), nobase=False):
    """Get unoccupied name by base name, occupied names & name gen func.

    Args:
        basename: (str)
            base name (the wanted name)
        occupied: (container of str)
            the names already be occupied.
        name_finder: (callable)
            unoccupied name generator.

            Signature:
                name_finder(basename, occupied) -> unoccupied_name

                `name_finder()` must return str type or None.

                If return None, mean not found any unoccupied name.
                == raise UnoccupiedNameNotFound exception

        nobase: (bool)
            not allow use `basename` directly. even basename not in occupied.

    Returns:
        basename, if basename already be occupied, return a unoccupied_name

    """
    if isinstance(occupied, str):
        raise TypeError('`occupied` can not a str type object.')

    occupied = set(occupied)

    if nobase:
        occupied.add(basename)

    if basename not in occupied:
        return basename
    else:
        new_name = name_finder(basename, occupied)

    if isinstance(new_name, str):
        if new_name in occupied:
            raise UnoccupiedNameNotFound(
                '`name_finder` should not return a name "{}"'
                ' already in occupied.'
                .format(new_name)
            )

        return new_name

    elif new_name is None:
        raise UnoccupiedNameNotFound('can not found a unoccupied name.')

    else:
        raise TypeError('name_finder ({}) not return a `str` but {}.'
                        .format(name_finder.__name__,
                                type(new_name).__name__))
