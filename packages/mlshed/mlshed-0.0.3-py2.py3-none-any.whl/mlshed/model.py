"""Model objects."""

import os
# import re
import shutil

from .cfg import (
    _snail_case,
    # model_dirpath,
    model_filepath,
)
from .exceptions import (
    MissingLocalModelError,
)
from .azure import (
    upload_model,
    download_model,
)


class Model(object):
    """An mlshed model.

    Parameters
    ----------
    name : str
        The name of the model. Used mainly in printing messages.
    task : str, optional
        The data science task this model serves. Optional.
    default_ext : str, optional
        The default extension used for instances of this model. defaults to
        'pkl'.
    fname_base : str, optional
        The base of the file name for the model, without any file extension.
        E.g. 'dog_detect' for 'dog_detect.pkl'. If not given, a snail_cased
        version of the model name is used.
    singleton : bool, default False
        If set, this model is assumed to be composed of a single instance,
        and as such no model-specific sub-directory is created.
    **kwargs : extra keyword arguments
        Extra keyword arguments, representing additional attributes of the
        model. E.g., 'language=en' or 'source=newspaper'.
    """

    EXT_PATTERN = r'\.([a-z]+)'

    def __init__(self, name, task=None, default_ext=None, fname_base=None,
                 singleton=False, **kwargs):
        self.name = name
        self.task = task
        if default_ext is None:
            default_ext = 'pkl'
        self.default_ext = default_ext
        if fname_base is None:
            fname_base = _snail_case(name)
        self.fname_base = fname_base
        self.singleton = singleton
        self.kwargs = kwargs

    @staticmethod
    def _tags_to_str(tags=None):
        return '_'+'_'.join(sorted(tags)) if tags else ''

    @staticmethod
    def _version_to_str(version=None):
        return '_{}'.format(version) if version else ''

    def fname(self, version=None, tags=None, ext=None):
        """Returns the filename appropriate for an instance of this model.

        Parameters
        ----------
        version: str, optional
            The version of the instance of this model.
        tags : list of str, optional
            The tags associated with the instance of this model.
        ext : str, optional
            The file extension to use. If not given, the default extension is
            used.

        Returns
        -------
        str
            The appropariate filename.
        """
        if ext is None:
            ext = self.default_ext
        return '{}{}{}.{}'.format(
            self.fname_base,
            self._tags_to_str(tags=tags),
            self._version_to_str(version=version),
            ext,
        )

    def fpath(self, version=None, tags=None, ext=None):
        """Returns the filepath appropriate for an instance of this model.

        Parameters
        ----------
        version: str, optional
            The version of the instance of this model.
        tags : list of str, optional
            The tags associated with the given instance of this model.
        ext : str, optional
            The file extension to use. If not given, the default extension is
            used.

        Returns
        -------
        str
            The appropariate filepath.
        """
        if self.singleton:
            return model_filepath(
                filename=self.fname(version=version, tags=tags, ext=ext),
                task=self.task,
                **self.kwargs,
            )
        return model_filepath(
            filename=self.fname(version=version, tags=tags, ext=ext),
            model_name=self.name,
            task=self.task,
            **self.kwargs,
        )

    def add_local(self, source_fpath, version=None, tags=None):
        """Copies a given file into local store as an instance of this model.

        Parameters
        ----------
        source_fpath : str
            The full path for the source file to use.
        version: str, optional
            The version of the instance of this model.
        tags : list of str, optional
            The tags associated with the given instance of this model.

        Returns
        -------
        ext : str
            The extension of the added file.
        """
        ext = os.path.splitext(source_fpath)[1]
        ext = ext[1:]  # we dont need the dot
        fpath = self.fpath(version=version, tags=tags, ext=ext)
        shutil.copyfile(src=source_fpath, dst=fpath)
        return ext

    # to add normal extension discovery on azure:
    # https://azure-storage.readthedocs.io/ref/
    # azure.storage.blob.baseblobservice.html
    # look at list_blobs

    # def _fname_patten(self, version=None, tags=None):
    #     return '{}{}{}{}'.format(
    #         self.fname_base,
    #         self._tags_to_str(tags),
    #         self._version_to_str(version),
    #         self.EXT_PATTERN,
    #     )
    #
    # def _find_extension(self, version=None, tags=None):
    #     fpattern = self._fname_patten(version=version, tags=tags)
    #     if self.singleton:
    #         data_dir = model_dirpath(task=self.task, **self.kwargs)
    #     else:
    #         data_dir = model_dirpath(
    #             model_name=self.name, task=self.task, **self.kwargs)
    #     for fname in os.listdir(data_dir):
    #         match = re.match(fpattern, fname)
    #         if match:
    #             return match.group(1)
    #     return None

    def upload(self, version=None, tags=None, ext=None, source_fpath=None,
               **kwargs):
        """Uploads the given instance of this model to model store.

        Parameters
        ----------
        version: str, optional
            The version of the instance of this model.
        tags : list of str, optional
            The tags associated with the given instance of this model.
        ext : str, optional
            The file extension to use. If not given, the default extension is
            used.
        source_fpath : str, optional
            The full path for the source file to use. If given, the file is
            copied from the given path to the local storage path before
            uploading.
        **kwargs : extra keyword arguments
            Extra keyword arguments are forwarded to
            azure.storage.blob.BlockBlobService.create_blob_from_path.
        """
        if source_fpath:
            ext = self.add_local(
                source_fpath=source_fpath, version=version, tags=tags)
        fpath = self.fpath(version=version, tags=tags, ext=ext)
        if not os.path.isfile(fpath):
            attribs = "{}{}ext={}".format(
                "version={} and ".format(version) if version else "",
                "tags={} and ".format(tags) if tags else "",
                ext,
            )
            raise MissingLocalModelError(
                "No model with {} in local store! (path={})".format(
                    attribs, fpath))
        upload_model(
            model_name=self.name,
            file_path=fpath,
            task=self.task,
            model_attributes=self.kwargs,
            **kwargs,
        )

    def download(self, overwrite=False, version=None, tags=None, ext=None,
                 verbose=False, **kwargs):
        """Downloads the given instance of this model from model store.

        Parameters
        ----------
        overwrite : bool, default False
            If set to True, the given instance of the model is downloaded from
            model store even if it exists in the local data directory.
            Otherwise, if a matching model is found localy, download is
            skipped.
        version: str, optional
            The version of the instance of this model.
        tags : list of str, optional
            The tags associated with the given instance of this model.
        ext : str, optional
            The file extension to use. If not given, the default extension is
            used.
        verbose : bool, default False
            If set to True, informative messages are printed.
        **kwargs : extra keyword arguments
            Extra keyword arguments are forwarded to
            azure.storage.blob.BlockBlobService.get_blob_to_path.
        """
        fpath = self.fpath(version=version, tags=tags, ext=ext)
        if os.path.isfile(fpath) and not overwrite:
            if verbose:
                print(
                    "File exists and overwrite set to False, so not "
                    "downloading {} with version={} and tags={}".format(
                        self.name, version, tags))
            return
        download_model(
            model_name=self.name,
            file_path=fpath,
            task=self.task,
            model_attributes=self.kwargs,
            **kwargs,
        )
    #
    # def load(self, tags=None, ext=None, **kwargs):
    #     """Loads an instance of this model into a python object.
    #
    #     Parameters
    #     ----------
    #     tags : list of str, optional
    #         The tags associated with the desired instance of this model.
    #     ext : str, optional
    #         The file extension to use. If not given, the default extension is
    #         used.
    #     **kwargs : extra keyword arguments, optional
    #         Extra keyword arguments are forwarded to the deserialization
    #         method of the SerializationFormat object corresponding to the
    #         extension used.
    #
    #     Returns
    #     -------
    #     pandas.DataFrame
    #         A dataframe containing the desired instance of this model.
    #     """
    #     ext = self._find_extension(tags=tags)
    #     if ext is None:
    #         if tags is None:
    #             raise MissingLocalModelError(
    #                 "No instance of {} model!".format(self.name))
    #         raise MissingLocalModelError(
    #             "No instance of model {} with tags: {}".format(
    #                 self.name, tags))
    #     fpath = self.fpath(tags=tags, ext=ext)
    #     fmt = SerializationFormat.by_name(ext)
    #     return fmt.deserialize(fpath, **kwargs)
    #
    # def dump_df(self, df, tags=None, ext=None, **kwargs):
    #     """Dumps an instance of this model into a file.
    #
    #     Parameters
    #     ----------
    #     df : pandas.DataFrame
    #         The dataframe to dump to file.
    #     tags : list of str, optional
    #         The tags associated with the given instance of this model.
    #     ext : str, optional
    #         The file extension to use. If not given, the default extension is
    #         used.
    #     **kwargs : extra keyword arguments, optional
    #         Extra keyword arguments are forwarded to the serialization method
    #         of the SerializationFormat object corresponding to the extension
    #         used.
    #     """
    #     if ext is None:
    #         ext = self.default_ext
    #     fpath = self.fpath(tags=tags, ext=ext)
    #     fmt = SerializationFormat.by_name(ext)
    #     fmt.serialize(df, fpath, **kwargs)
    #
    # def upload_df(self, df, tags=None, ext=None, **kwargs):
    #     """Dumps an instance of this model into a file and then uploads it
    #     to model store.
    #
    #     Parameters
    #     ----------
    #     df : pandas.DataFrame
    #         The dataframe to dump and upload.
    #     tags : list of str, optional
    #         The tags associated with the given instance of this model.
    #     ext : str, optional
    #         The file extension to use. If not given, the default extension is
    #         used.
    #     **kwargs : extra keyword arguments, optional
    #         Extra keyword arguments are forwarded to the serialization method
    #         of the SerializationFormat object corresponding to the extension
    #         used.
    #     """
    #     self.dump_df(df=df, tags=tags, ext=ext, **kwargs)
    #     self.upload(tags=tags, ext=ext)
