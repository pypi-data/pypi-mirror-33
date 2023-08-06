#!/usr/bin/env python3

"""
Entry point for QBorg.

Execute with
$ python3 -m qborg
"""

if __name__ == '__main__':
    import sys

    if __package__ is None and not hasattr(sys, 'frozen'):
        # Direct call of __main__.py
        import os
        _path = os.path.realpath(os.path.abspath(__file__))
        sys.path.insert(0, os.path.dirname(os.path.dirname(_path)))

    from qborg.qborg import main

    status = None
    try:
        status = main()
    except KeyboardInterrupt:
        pass

    sys.exit(status)
