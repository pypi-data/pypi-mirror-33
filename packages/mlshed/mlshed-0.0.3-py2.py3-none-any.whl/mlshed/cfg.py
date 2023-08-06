"""Barn configuration."""

import os

from birch import Birch


SHED_CFG = Birch('mlshed')


def _base_dir():
    dpath = SHED_CFG['base_dir']
    if '~' in dpath:
        dpath = os.path.expanduser(dpath)
    return dpath


def _snail_case(s):
    s = s.lower()
    return s.replace(' ', '_')


def resource_dirpath(task=None, **kwargs):
    """Get the path of the corresponding resource directory.

    Parameters
    ----------
    task : str, optional
        The task for which resources in the desired directory are used for. If
        not given, a path for the corresponding task-agnostic directory is
        returned.
    **kwargs : extra keyword arguments
        Extra keyword arguments, representing additional attributes of the
        resources, are used to generate additional sub-folders on the path.
        For example, providing 'lang=en' will results in a path such as
        '/mlshed_base_dir/regression/lang_en/logreg.pickle'. Hierarchy always
        matches lexicographical order of keyword argument names, so 'lang=en'
        and 'animal=dog' will result in a path such as
        'mlshed_base_dir/task_name/animal_dog/lang_en/svm.pickle'.

    Returns
    -------
    str
        The path to the desired dir.
    """
    path = _base_dir()
    if task:
        path = os.path.join(path, _snail_case(task))
    for k, v in sorted(kwargs.items()):
        subdir_name = '{}_{}'.format(_snail_case(k), _snail_case(v))
        path = os.path.join(path, subdir_name)
    os.makedirs(path, exist_ok=True)
    return path


def model_dirpath(model_name=None, task=None, **kwargs):
    """Get the path of the corresponding model directory.

    Parameters
    ----------
    model_name : str, optional
        The name of the model. Used to define a sub-directory to contain all
        versions of the model and all related resources. If not given, a
        model-agnostic directory path is returned.
    task : str, optional
        The task for which model in the desired directory are used for. If not
        given, a path for the corresponding task-agnostic directory is
        returned.
    **kwargs : extra keyword arguments
        Extra keyword arguments, representing additional attributes of the
        resources, are used to generate additional sub-folders on the path.
        For example, providing 'lang=en' will results in a path such as
        '/mlshed_base_dir/regression/lang_en/logreg.pickle'. Hierarchy always
        matches lexicographical order of keyword argument names, so 'lang=en'
        and 'animal=dog' will result in a path such as
        'mlshed_base_dir/task_name/animal_dog/lang_en/svm.pickle'.

    Returns
    -------
    str
        The path to the desired model directory.
    """
    model_dir_path = resource_dirpath(task=task, **kwargs)
    if model_name:
        model_dir_name = _snail_case(model_name)
        model_dir_path = os.path.join(model_dir_path, model_dir_name)
    os.makedirs(model_dir_path, exist_ok=True)
    return model_dir_path


def model_filepath(filename, model_name=None, task=None, **kwargs):
    """Get the path of the corresponding model file.

    Parameters
    ----------
    filename : str
        The name of the file.
    model_name : str, optional
        The name of the model. Used to define a sub-directory to contain all
        instances of the model. If not given, a model-specific directory is
        not created.
    task : str, optional
        The task for which the model in the desired path is used for. If not
        given, a path for the corresponding task-agnostic directory is
        returned.
    **kwargs : extra keyword arguments
        Extra keyword arguments, representing additional attributes of the
        resources, are used to generate additional sub-folders on the path.
        For example, providing 'lang=en' will results in a path such as
        '/mlshed_base_dir/regression/lang_en/logreg.pickle'. Hierarchy always
        matches lexicographical order of keyword argument names, so 'lang=en'
        and 'animal=dog' will result in a path such as
        'mlshed_base_dir/task_name/animal_dog/lang_en/svm.pickle'.

    Returns
    -------
    str
        The path to the desired model file.
    """
    model_dir_path = model_dirpath(
        model_name=model_name, task=task, **kwargs)
    return os.path.join(model_dir_path, filename)
