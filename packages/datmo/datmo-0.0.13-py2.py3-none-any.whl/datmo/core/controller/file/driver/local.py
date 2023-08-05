import os
import stat
import shutil
import glob
import hashlib
import checksumdir
from io import open
try:
    to_unicode = unicode
except NameError:
    to_unicode = str

from datmo.core.util.i18n import get as __
from datmo.core.util.exceptions import (
    PathDoesNotExist, FileIOError, FileStructureError, FileAlreadyExistsError,
    DirAlreadyExistsError)
from datmo.core.controller.file.driver import FileDriver
from datmo.core.util.misc_functions import get_datmo_temp_path, parse_paths


class LocalFileDriver(FileDriver):
    """
    This FileDriver handles the datmo file tree on the local system
    """

    def __init__(self, root):
        super(LocalFileDriver, self).__init__()
        self.root = root
        # Check if filepath exists
        if not os.path.exists(self.root):
            raise PathDoesNotExist(
                __("error", "controller.file.driver.local.__init__", root))
        self._is_initialized = self.is_initialized
        self.type = "local"

    @staticmethod
    def get_safe_dst_filepath(filepath, dst_dirpath):
        if not os.path.isfile(filepath):
            raise PathDoesNotExist(
                __("error",
                   "controller.file.driver.local.get_safe_dst_filepath.core",
                   filepath))
        if not os.path.isdir(dst_dirpath):
            raise PathDoesNotExist(
                __("error",
                   "controller.file.driver.local.get_safe_dst_filepath.dst",
                   dst_dirpath))
        _, filename = os.path.split(filepath)
        dst_filepath = os.path.join(dst_dirpath, filename)
        number_of_items = glob.glob(dst_filepath)
        if number_of_items:
            filepath_without_ext = os.path.splitext(dst_filepath)[0]
            extension = os.path.splitext(dst_filepath)[1]
            number_of_items = len(glob.glob(filepath_without_ext + '*'))
            new_filepath = filepath_without_ext + "_" + str(
                number_of_items - 1)
            new_filepath_with_ext = new_filepath + extension
            return new_filepath_with_ext
        else:
            return dst_filepath

    @staticmethod
    def copytree(src_dirpath, dst_dirpath, symlinks=False, ignore=None):
        if not os.path.isdir(src_dirpath):
            raise PathDoesNotExist(
                __("error", "controller.file.driver.local.copytree.core",
                   src_dirpath))
        if not os.path.isdir(dst_dirpath):
            raise PathDoesNotExist(
                __("error", "controller.file.driver.local.copytree.dst",
                   dst_dirpath))
        for item in os.listdir(src_dirpath):
            src_filepath = os.path.join(src_dirpath, item)
            dst_filepath = os.path.join(dst_dirpath, item)
            if os.path.isdir(src_filepath):
                if os.path.exists(dst_filepath):
                    shutil.rmtree(dst_filepath)
                shutil.copytree(src_filepath, dst_filepath, symlinks, ignore)
            else:
                if os.path.exists(dst_filepath):
                    os.remove(dst_filepath)
                shutil.copy2(src_filepath, dst_filepath)
        return True

    @staticmethod
    def copyfile(filepath, dst_dirpath):
        if not os.path.isfile(filepath):
            raise PathDoesNotExist(
                __("error", "controller.file.driver.local.copyfile.core",
                   filepath))
        if not os.path.isdir(dst_dirpath):
            raise PathDoesNotExist(
                __("error", "controller.file.driver.local.copyfile.dst",
                   dst_dirpath))
        dst_filepath = LocalFileDriver.get_safe_dst_filepath(
            filepath, dst_dirpath)
        shutil.copy2(filepath, dst_filepath)
        return True

    @property
    def is_initialized(self):
        if self.exists_datmo_file_structure():
            if self.exists_collections_dir():
                if os.path.isdir(
                        os.path.join(self.root, ".datmo", "collections",
                                     "d41d8cd98f00b204e9800998ecf8427e")):
                    self._is_initialized = True
                    return self._is_initialized
        self._is_initialized = False
        return self._is_initialized

    # Implemented functions for all FileDriver objects

    def init(self):
        try:
            # Ensure the Datmo file structure exists
            self.ensure_datmo_file_structure()
            # Ensure the collections directory exists
            self.ensure_collections_dir()
            # Ensure the empty collection exists
            if not os.path.isdir(
                    os.path.join(self.root, ".datmo", "collections",
                                 "d41d8cd98f00b204e9800998ecf8427e")):
                self.create(
                    os.path.join(".datmo", "collections",
                                 "d41d8cd98f00b204e9800998ecf8427e"),
                    directory=True)
        except Exception as e:
            raise FileIOError(
                __("error", "controller.file.driver.local.init", str(e)))
        return True

    def create(self, relative_path, directory=False):
        """
        Create files or directories

        Parameters
        ----------
        relative_path : str
            relative filepath from base filepath
        directory : bool
            True for directory, False for file

        Returns
        -------
        filepath : str
            absolute filepath of created file or directory
        """
        filepath = os.path.join(self.root, relative_path)
        if os.path.exists(filepath):
            os.utime(filepath, None)
        else:
            if directory:
                os.makedirs(filepath)
            else:
                with open(os.path.join(self.root, relative_path), "ab"):
                    os.utime(filepath, None)
        return filepath

    def exists(self, relative_path, directory=False):
        filepath = os.path.join(self.root, relative_path)
        if directory:
            return True if os.path.isdir(filepath) else False
        else:
            return True if os.path.isfile(filepath) else False

    def get(self, relative_path, mode="r", directory=False):
        if not os.path.exists(os.path.join(self.root, relative_path)):
            raise PathDoesNotExist(
                __("error", "controller.file.driver.local.get",
                   os.path.join(self.root, relative_path)))
        if directory:
            dirpath = os.path.join(self.root, relative_path)
            absolute_filepaths = []
            for dirname, _, filenames in os.walk(dirpath):
                # print path to all filenames.
                for filename in filenames:
                    absolute_filepaths.append(os.path.join(dirname, filename))

            # Return a list of file objects
            return [
                open(absolute_filepath, mode)
                for absolute_filepath in absolute_filepaths
            ]
        else:
            filepath = os.path.join(self.root, relative_path)
            return open(filepath, mode)

    def ensure(self, relative_path, directory=False):
        if not self.exists(
                os.path.join(self.root, relative_path), directory=directory):
            self.create(
                os.path.join(os.path.join(self.root, relative_path)),
                directory=directory)
        return True

    def delete(self, relative_path, directory=False):
        if not os.path.exists(os.path.join(self.root, relative_path)):
            raise PathDoesNotExist(
                __("error", "controller.file.driver.local.delete",
                   os.path.join(self.root, relative_path)))
        if directory:
            shutil.rmtree(relative_path)
        else:
            os.remove(os.path.join(self.root, relative_path))
        return True

    def create_collection(self, paths):
        if not self.is_initialized:
            raise FileStructureError(
                __("error",
                   "controller.file.driver.local.create_collection.structure"))

        self.ensure_collections_dir()
        temp_collection_path = get_datmo_temp_path(self.root)

        filehash = self.calculate_hash_paths(paths, temp_collection_path)

        # Move contents to folder with filehash as name and remove temp_collection_path
        collection_path = os.path.join(self.root, ".datmo", "collections",
                                       filehash)
        if os.path.isdir(collection_path):
            return filehash
            # raise FileStructureError("exception.file.create_collection", {
            #     "exception": "File collection with id already exists."
            # })
        os.makedirs(collection_path)
        self.copytree(temp_collection_path, collection_path)

        # Change permissions to read only for collection_path. File collection is immutable
        mode = stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH

        for root, dirs, files in os.walk(collection_path, topdown=False):
            for dir in [os.path.join(root, d) for d in dirs]:
                os.chmod(dir, mode)
            for file in [os.path.join(root, f) for f in files]:
                os.chmod(file, mode)

        return filehash

    def calculate_hash_paths(self, paths, directory):
        try:
            files, dirs = parse_paths(self.root, paths, directory)
        except PathDoesNotExist as e:
            raise PathDoesNotExist(
                __("error",
                   "controller.file.driver.local.create_collection.filepath",
                   str(e)))

        # Populate collection from left to right in lists
        for file_tuple in files:
            src_abs_filepath, dest_abs_filepath = file_tuple
            if os.path.exists(dest_abs_filepath):
                raise FileAlreadyExistsError(
                    __("error",
                       "controller.file.driver.create_collection.file_exists",
                       dest_abs_filepath))
            # File is copied over to the new destination path
            shutil.copy2(src_abs_filepath, dest_abs_filepath)

        for dir_tuple in dirs:
            src_abs_dirpath, dest_abs_dirpath = dir_tuple
            if os.path.exists(dest_abs_dirpath):
                raise DirAlreadyExistsError(
                    __("error",
                       "controller.file.driver.create_collection.dir_exists",
                       dest_abs_dirpath))
            os.makedirs(dest_abs_dirpath)
            # All contents of directory is copied over to the new directory path
            self.copytree(src_abs_dirpath, dest_abs_dirpath)

        # Hash the files to find filehash
        return self.get_dirhash(directory)

    @staticmethod
    def get_filehash(absolute_filepath):
        if not os.path.isfile(absolute_filepath):
            raise PathDoesNotExist(
                __("error", "util.misc_functions.get_filehash",
                   absolute_filepath))
        BUFF_SIZE = 65536
        sha1 = hashlib.md5()
        with open(absolute_filepath, "rb") as f:
            while True:
                data = f.read(BUFF_SIZE)
                if not data:
                    break
                sha1.update(data)
        return sha1.hexdigest()

    @staticmethod
    def get_dirhash(absolute_dirpath):
        return checksumdir.dirhash(absolute_dirpath)

    def get_absolute_collection_path(self, filehash):
        return os.path.join(self.root, ".datmo", "collections", filehash)

    def get_relative_collection_path(self, filehash):
        return os.path.join(".datmo", "collections", filehash)

    def get_collection_path(self, filehash):
        return self.get_absolute_collection_path(filehash)

    def exists_collection(self, filehash):
        collection_path = os.path.join(self.root, ".datmo", "collections",
                                       filehash)
        return self.exists(collection_path, directory=True)

    def get_collection_files(self, filehash, mode="r"):
        relative_collection_path = os.path.join(".datmo", "collections",
                                                filehash)
        # Call get function with the directory=True parameter
        return self.get(relative_collection_path, mode=mode, directory=True)

    def delete_collection(self, filehash):
        collection_path = os.path.join(self.root, ".datmo", "collections",
                                       filehash)
        return self.delete(collection_path, directory=True)

    def transfer_collection(self, filehash, dst_dirpath):
        if not self.exists_collection(filehash):
            raise PathDoesNotExist(
                __("error", "controller.file.driver.local.transfer_collection",
                   filehash))
        if not os.path.isdir(dst_dirpath):
            raise PathDoesNotExist(
                __("error",
                   "controller.file.driver.local.transfer_collection.dst",
                   dst_dirpath))
        collection_path = os.path.join(self.root, ".datmo", "collections",
                                       filehash)
        return self.copytree(collection_path, dst_dirpath)

    # Datmo base directory
    def create_hidden_datmo_dir(self):
        filepath = os.path.join(self.root, ".datmo")
        if not os.path.isdir(filepath):
            os.makedirs(filepath)
        return True

    def exists_hidden_datmo_dir(self):
        filepath = os.path.join(self.root, ".datmo")
        return self.exists(filepath, directory=True)

    def ensure_hidden_datmo_dir(self):
        filepath = os.path.join(self.root, ".datmo")
        return self.ensure(filepath, directory=True)

    def delete_hidden_datmo_dir(self):
        filepath = os.path.join(self.root, ".datmo")
        return self.delete(filepath, directory=True)

    # Overall Datmo file structure
    def create_datmo_file_structure(self):
        return self.create_hidden_datmo_dir()

    def exists_datmo_file_structure(self):
        return self.exists_hidden_datmo_dir()

    def ensure_datmo_file_structure(self):
        return self.ensure_hidden_datmo_dir()

    def delete_datmo_file_structure(self):
        return self.delete_hidden_datmo_dir()

    # Template files handling

    # TODO: Add code to handle and fill in templates from `templates/` folder in document

    # Other functions
    def create_collections_dir(self):
        if not self.is_initialized:
            raise FileStructureError(
                __("error",
                   "controller.file.driver.local.create_collections_dir"))
        collections_path = os.path.join(self.root, ".datmo", "collections")
        if not os.path.isdir(collections_path):
            os.makedirs(collections_path)
        return True

    def exists_collections_dir(self):
        collections_path = os.path.join(self.root, ".datmo", "collections")
        return self.exists(collections_path, directory=True)

    def ensure_collections_dir(self):
        collections_path = os.path.join(self.root, ".datmo", "collections")
        return self.ensure(collections_path, directory=True)

    def delete_collections_dir(self):
        collections_path = os.path.join(self.root, ".datmo", "collections")
        return self.delete(collections_path, directory=True)

    def list_file_collections(self):
        if not self.is_initialized:
            raise FileStructureError(
                __("error",
                   "controller.file.driver.local.list_file_collections"))
        collections_path = os.path.join(self.root, ".datmo", "collections")
        collections_list = os.listdir(collections_path)
        return collections_list
