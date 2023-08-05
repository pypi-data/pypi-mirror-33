"""
Utilities
=========

"""
import os


def rwalk(bottom, topdown=False, onerror=None, followlinks=False):
    """Reverse variant of os.walk. Walks from the bottom directory till
    root.

    Parameters
    ----------
    bottom : str
    topdown : bool
    onerror : callable
    followlinks : bool

    Returns
    -------
    generator

    """
    bottom = os.fspath(bottom)
    dirs = []
    nondirs = []

    bottomup = not topdown
    try:
        scandir_it = os.scandir(bottom)
    except OSError or NameError as error:
        if onerror is not None:
            onerror(error)
        return

    with scandir_it:
        while True:
            try:
                try:
                    entry = next(scandir_it)
                except StopIteration:
                    break

            except OSError as error:
                if onerror is not None:
                    onerror(error)
                return

            try:
                is_dir = entry.is_dir()
            except OSError:
                is_dir = False

            if is_dir:
                dirs.append(entry.name)
            else:
                nondirs.append(entry.name)

    new_path = os.path.dirname(bottom)

    if bottomup:
        yield bottom, dirs, nondirs

    # Recurse into parent-directories
    if bottom != new_path:  # Avoid RecursionError when at the root directory
        yield from rwalk(new_path, topdown, onerror, followlinks)

        if followlinks and os.path.islink(new_path):
            yield from rwalk(os.path.abspath(new_path), topdown, onerror, followlinks)

    if not bottomup:
        yield bottom, dirs, nondirs
