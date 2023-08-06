#!/usr/bin/env python

"""
    Library of common APIs for Python Applications
"""

__all__ = ['context', 'ntpx', 'parent', 'popd', 'pushd', 'TEMPDIR', 'USER', 'COMPUTER']

TEMPDIR = '/temp'
USER = ''
COMPUTER = ''


class context:
    """
    Provides context to a Python module with several useful methods.

    The context object provides methods to give useful context to a Python module.
    Things like current location, fully qualified script name, an alias and more.

    when you instantiate one of these, you pass in __file__ if defined,
    otherwise sys.argv[0]
    """

    def __init__(self, foo, alias=None):
        from os.path import abspath, split, splitext

        self._whoami = abspath(foo)
        self._whereami,whocares = split(self._whoami)
        
        name,ext = splitext(whocares)

        if alias is None:
            self._alias = name
        else:
            self._alias = alias

    def whoami(self):
        """Returns the fully qualified name of the current module"""
        return self._whoami

    def alias(self):
        """Returns the alias (shortname) of the current module"""
        return self._alias

    def whereami(self):
        """Returns the fully qualified path where the current module is stored"""
        return self._whereami

    def pyVersionStr(self):
        """Returns the version of the Python Interpreter running my script"""
        from sys import version_info

        return "Python Interpreter Version: {}.{}.{}".format(version_info.major,
                                                             version_info.minor,
                                                             version_info.micro)

try:
    me = context(__file__)
except:
    from sys import argv
    me = context(argv[0])
    
def _init():
    from os import name, environ
    from os.path import normcase

    global USER, COMPUTER, TEMPDIR

    if name == 'nt':
        ENVUSERNAME = 'USERNAME'
        ENVTMPDIR = 'TEMP'
    else:   # assume name == 'posix'
        ENVUSERNAME = 'LOGNAME'
        ENVTMPDIR = 'TMPDIR'

    if ( ENVUSERNAME in environ):
        USER = environ[ENVUSERNAME]

    from platform import node
    
    COMPUTER = node()

    if (ENVTMPDIR in environ):
        TEMPDIR = environ[ENVTMPDIR]

    TEMPDIR = normcase(TEMPDIR)


class ntpx:
    """implements the NT-style path manipulation support for arguments.
    
    example:
    
        print ntpx('c:/dir/foo.ext').format('dp')  - prints 'c:/dir/'
        print ntpx('c:/dir/foo.ext').format('nx')  - prints 'foo.ext'"""

    def __init__(self,path,normalize=1):
        """object constructor takes a path, and optionally, whether to normalize the path"""
        from os import sep
        from os.path import abspath, normpath, splitdrive, split, splitext
        from os.path import getsize, getmtime

        if normalize:
            self._full = abspath(normpath(path))
        else:
            self._full = abspath(path)

        self._driv,x = splitdrive(self._full)
        self._path,y = split(x)
        self._path += sep
        self._name,self._ext = splitext(y)

        if os.path.exists(self._full):
            self._size = getsize(self._full)
            self._time = getmtime(self._full)

        else:
            self._size = None
            self._time = None


    def all(self):
        """
        returns a tuple containing all elements of the object
        
        (abs_path, drive_letter, path_only, rootname, extension, filesize, time_in_seconds)
        """

        return (self._full, self._driv, self._path, self._name, self._ext, self._size, self._time)

    def format(self, fmt):
        """
        returns string representing the items specified in the format string

        the format string can contain:
        
            d - drive letter
            p - path
            n - name
            x - extension
            z - file size
            t - file time in seconds
        
        you can string them together, e.g. 'dpnx' returns the fully qualified name.
        
        On platforms like Unix, where drive letter doesn't make sense, it's simply
        ignored when used in a format string, making it easy to construct fully
        qualified path names in an os independent manner.
        """

        val = ''
        for x in fmt:
            if x == 'd':
                val += self._driv

            elif x == 'p':
                val += self._path

            elif x == 'n':
                val += self._name

            elif x == 'x':
                val += self._ext

            elif x == 'z':
                if self._size != None: val += str(self._size)

            elif x == 't':
                if self._time != None: val += str(self._time)

        return val

    def drive(self):
        """returns the drive letter only"""
        return self._driv

    def path(self):
        """returns the path only"""
        return self._path

    def name(self):
        """returns the name only"""
        return self._name

    def ext(self):
        """returns the extension only"""
        return self._ext

    def size(self):
        """returns the size of the file"""
        return self._size

    def datetime(self):
        """returns the time of the file in seconds"""
        return self._time

_pushdstack = []

def parent(pathspec):
    """
    Return the parent directory of pathspec.

    This function calls abspath() on pathspec before splitting it into pieces.
    If you pass in a partial path, it will return the normalized absolute path,
    and not just any relative path that was on the original pathspec.
    """
    from os.path import split, abspath
    path, filename = split(abspath(pathspec))

    return path

def pushd(dir=None, throw_if_dir_invalid=True):
    """
    Push the current working directory (CWD) onto a stack, set CWD to 'dir'
    
    Save the CWD onto a global stack so that we can return to it later. 
    
    If dir is None, the function simply stores the CWD onto the stack and returns.

    If throw_if_dir_invalid is True (default), this method will throw whatever 
    exception is raised by chdir(dir). Otherwise, it returns True or False.

    Use popd() to restore the original directory.
    
    Returns:
        True - Success
        False - Failure
    """
    global _pushdstack
    from os import getcwd, chdir

    if dir is None:
        dir = getcwd()

    if not isinstance(dir,type('')):
        raise TypeError("pushd() expected string object, but got {}".format(type(dir)))

    _pushdstack.append(getcwd())
    
    if not dir:
        return

    try:
        chdir(dir)
        err = 0
    except OSError:
        err = 1

    if err == 1:
        _pushdstack.pop()
        if throw_if_dir_invalid:
            raise

    return True if err == 0 else False

def popd(pop_all=False, throw_if_dir_invalid=True):
    """
    Set the current working directory back to what it was when last pushd() was called.
    
    pushd() creates a stack, so each call to popd() simply sets the CWD back to what it
    was on the prior pushd() call.
    
    If pop_all is True, sets the CWD to the state when pushd() was first called. Does
    NOT call os.getcwd() for intervening paths, only the final path.

    If throw_if_dir_invalid is True (default), this method will throw whatever 
    exception is raised by chdir(dir). Otherwise, it returns True or False.
    """
    global _pushdstack
    from os import chdir

    if len(_pushdstack) == 0:
        raise ValueError("popd() called on an empty stack.")

    if pop_all:
        while( len(_pushdstack) > 1):
            _pushdstack.pop()

    try:
        chdir(_pushdstack.pop())
        err = 0
    except OSError:
        err = 1

    if err == 1 and throw_if_dir_invalid:
        raise

    return err == 0


if (__name__=="__main__"):
    print('PyLib Library Module, not directly callable.')
    from sys import exit
    exit(1)
else:
    _init()
