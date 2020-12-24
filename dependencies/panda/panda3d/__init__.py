"Python bindings for the Panda3D libraries"

__version__ = '1.11.0'

if __debug__:
    if 1 / 2 == 0:
        raise ImportError("Python 2 is not supported.")

if '__file__' in locals():
    import os

    bindir = os.path.join(os.path.dirname(__file__), '..', 'bin')
    if os.path.isdir(bindir):
        if hasattr(os, 'add_dll_directory'):
            os.add_dll_directory(bindir)
        elif not os.environ.get('PATH'):
            os.environ['PATH'] = bindir
        else:
            os.environ['PATH'] = bindir + os.pathsep + os.environ['PATH']
    del os, bindir
