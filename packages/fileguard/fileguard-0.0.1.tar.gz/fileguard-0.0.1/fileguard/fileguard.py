import os
import uuid
import shutil
import ntpath
import tempfile
import distutils.dir_util
from functools import wraps
from .utils import path_is_dir
from types import FunctionType

class _guard(object):

    def __init__(self, paths):
        self._backup = {}
        for path in paths:
            self._backup[path] = []
        self._tmp_dir = None

    def __call__(self, func):
        if isinstance(func, type):
            return self.decorate_class(func)
        else:
            return self.decorate_callable(func)

    def __enter__(self):
        """Store original file contents"""
        self._store_backup_content()
        return self

    def __exit__(self, *exc_info):
        """Restore original file contents"""
        self._restore_backup_content()

    def _set_up_tmp_dir_if_needed(self):
        if self._tmp_dir is None:
            self._tmp_dir = tempfile.TemporaryDirectory(prefix='fileguard_')

    def _cleanup_tmp_dir_if_needed(self):
        """
        Remove the temp directory only if all of the fileguarded files have
        been restored, i.e. if there are no remaining backups to restore.
        """
        for path in self._backup:
            if len(self._backup[path]) == 0:
                c = self._backup[path]
            else:
                return

        self._tmp_dir.cleanup()
        self._tmp_dir = None

    def _store_backup_content(self):
        self._set_up_tmp_dir_if_needed()

        for path in self._backup:
            is_dir = path_is_dir(path)

            tmp_file_name = uuid.uuid4().hex
            temp_path = os.path.join(self._tmp_dir.name, tmp_file_name)
            if is_dir:
                # copy directory
                distutils.dir_util.copy_tree(path, temp_path)
            else:
                # copy file
                shutil.copy2(path, temp_path)

            self._backup[path].append((temp_path, is_dir))

    def _restore_backup_content(self):
        for path in self._backup:
            tmp_file_path, is_dir = self._backup[path].pop()
            if is_dir:
                distutils.dir_util.copy_tree(tmp_file_path, path)
            else:
                shutil.copy2(tmp_file_path, path)

            if len(self._backup[path]) == 0:
                # a little optimization: only try to clean the directory up
                # if there is a gurantee that at lest one file backup list
                # is empty.
                self._cleanup_tmp_dir_if_needed()

    def decorate_callable(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            self.__enter__()
            try:
                return func(*args, **kwargs)
            finally:
                self.__exit__()
        return wrapper

    def decorate_class(self, klass):
        """File Guard every user-defined function in the specified class

        Arguments:
            * klass (class): The class to be file-guarded
        """
        # NOTE: if decorating the __new__ method, keep in mind the following:
        #   * https://stackoverflow.com/questions/34777773/typeerror-object-takes-no-parameters-after-defining-new
        #   * https://github.com/python/cpython/blob/5a4bbcd479ce86f68bbe12bc8c16e3447f32e13a/Objects/typeobject.c#L3538

        for attr in dir(klass):

            attr_value = getattr(klass, attr)
            if not isinstance(attr_value, FunctionType):
                            continue

            wrapped = self.decorate_callable(attr_value)
            setattr(klass, attr, wrapped)
        return klass

def guard(*paths):
    """Preserve the contents of a file.

    Can be used as a function decorator, a context manager or a class decorator.
    If used as a class decorator, all user-defined functions will be decorated,
    i.e. all user functions will be file-guarded. You can pass multiple files
    to this function: all of the specified files and/or directories will
    be guarded.

    Args:
        paths ([path-like [path-like ...]]): The path (or list of paths) of
        the file to be guarded. It must be path-like, such as a string.
        In general, any object accepted by `pathlib.Path` can be used.
    """
    return _guard(paths)
