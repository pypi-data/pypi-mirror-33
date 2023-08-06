"""Remote model storage on Azure."""

import os
import ntpath
import warnings

from decore import lazy_property
try:
    from azure.storage.blob import BlockBlobService
except ImportError:
    warnings.warn(
        "Importing azure Python package failed. "
        "Azure-based remote model stores are disabled.")

from .cfg import (
    SHED_CFG,
    _snail_case,
)
from .exceptions import (
    MissingRemoteModelError,
)


@lazy_property
def _blob_service():
    return BlockBlobService(
        account_name=SHED_CFG['azure']['account_name'],
        account_key=SHED_CFG['azure']['account_key'],
        socket_timeout=600,
    )


def _subfolder_name(model_name):
    t = model_name.lower()
    t = t.replace(' ', '_')
    return t


def _blob_name(model_name, file_name, task=None, model_attributes=None):
    path_prefix = 'mlshed'
    if task:
        path_prefix += '/{}'.format(_snail_case(task))
    if model_attributes:
        for k, v in sorted(model_attributes.items()):
            path_prefix += '/{}_{}'.format(_snail_case(k), _snail_case(v))
    subfolder = _subfolder_name(model_name=model_name)
    path_prefix += '/{}'.format(subfolder)
    return '{}/{}'.format(path_prefix, file_name)


def upload_model(
        model_name, file_path, task=None, model_attributes=None, **kwargs):
    """Uploads the given file to model store.

    Parameters
    ----------
    model_name : str
        The name of the model to upload.
    file_path : str
        The full path to the file to upload
    task : str, optional
        The task for which the given model is used for. If not given, a path
        for the corresponding task-agnostic directory is used.
    model_attributes : dict, optional
        Additional attributes of the models. Used to generate additional
        sub-folders on the blob "path". For example, providing 'lang=en' will
        results in a path such as '/lang_en/mymodel.pkl'. Hierarchy always
        matches lexicographical order of keyword argument names, so 'lang=en'
        and 'animal=dog' will result in a path such as
        'task_name/animal_dog/lang_en/svm.pkl'.
    **kwargs : extra keyword arguments
        Extra keyword arguments are forwarded to
        azure.storage.blob.BlockBlobService.create_blob_from_path.

    Returns
    -------
    blob_name : str
        The name of the blob the model was uploaded to.
    """
    fname = ntpath.basename(file_path)
    blob_name = _blob_name(
        model_name=model_name,
        file_name=fname,
        task=task,
        model_attributes=model_attributes,
    )
    _blob_service().create_blob_from_path(
        container_name=SHED_CFG['azure']['container_name'],
        blob_name=blob_name,
        file_path=file_path,
        **kwargs,
    )
    return blob_name


# def extension_by_file_prefix(
#         model_name, file_prefix, task=None, model_attributes=None):
#     """Downloads the given model from model store.
#
#     Parameters
#     ----------
#     model_name : str
#         The name of the model to upload.
#     file_path : str
#         The full path to the file to upload
#     task : str, optional
#         The task for which the given model is used for. If not given, a path
#         for the corresponding task-agnostic directory is used.
#     model_attributes : dict, optional
#         Additional attributes of the models. Used to generate additional
#         sub-folders on the blob "path". For example, providing 'lang=en' will
#         results in a path such as '/lang_en/mymodel.csv'. Hierarchy always
#         matches lexicographical order of keyword argument names, so 'lang=en'
#         and 'animal=dog' will result in a path such as
#         'task_name/animal_dof/lang_en/dset.csv'.
#     **kwargs : extra keyword arguments
#         Extra keyword arguments are forwarded to
#         azure.storage.blob.BlockBlobService.get_blob_to_path.
#     """
#     mock_fname = file_prefix
#     blob_name = _blob_name(
#         model_name=model_name,
#         file_name=fname,
#         task=task,
#         model_attributes=model_attributes,
#     )


def download_model(
        model_name, file_path, task=None, model_attributes=None, **kwargs):
    """Downloads the given model from model store.

    Parameters
    ----------
    model_name : str
        The name of the model to upload.
    file_path : str
        The full path to the file to upload
    task : str, optional
        The task for which the given model is used for. If not given, a path
        for the corresponding task-agnostic directory is used.
    model_attributes : dict, optional
        Additional attributes of the models. Used to generate additional
        sub-folders on the blob "path". For example, providing 'lang=en' will
        results in a path such as '/lang_en/mymodel.csv'. Hierarchy always
        matches lexicographical order of keyword argument names, so 'lang=en'
        and 'animal=dog' will result in a path such as
        'task_name/animal_dof/lang_en/dset.csv'.
    **kwargs : extra keyword arguments
        Extra keyword arguments are forwarded to
        azure.storage.blob.BlockBlobService.get_blob_to_path.
    """
    fname = ntpath.basename(file_path)
    blob_name = _blob_name(
        model_name=model_name,
        file_name=fname,
        task=task,
        model_attributes=model_attributes,
    )
    # print("Downloading blob: {}".format(blob_name))
    try:
        _blob_service().get_blob_to_path(
            container_name=SHED_CFG['azure']['container_name'],
            blob_name=blob_name,
            file_path=file_path,
            **kwargs,
        )
    except Exception as e:
        if os.path.isfile(file_path):
            os.remove(file_path)
        raise MissingRemoteModelError(
            "With blob {}.".format(blob_name)) from e
