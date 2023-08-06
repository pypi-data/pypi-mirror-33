# -*- coding: utf-8 -*-
# *******************************************************
#   ____                     _               _
#  / ___|___  _ __ ___   ___| |_   _ __ ___ | |
# | |   / _ \| '_ ` _ \ / _ \ __| | '_ ` _ \| |
# | |__| (_) | | | | | |  __/ |_ _| | | | | | |
#  \____\___/|_| |_| |_|\___|\__(_)_| |_| |_|_|
#
#  Sign up for free at http://www.comet.ml
#  Copyright (C) 2015-2019 Comet ML INC
#  This file can not be copied and/or distributed without the express
#  permission of Comet ML Inc.
# *******************************************************

""" This module handles syncing git repos with the backend. Used for pull
request features."""

import json
import logging
import os
import shutil
import tempfile
import zipfile
from multiprocessing import Process
from os.path import join, splitext

import requests

from ._reporting import FILE_UPLOADED_FAILED, REPO_UPLOADED, REPO_UPLOADED_FAILED
from .config import CONFIG_PATH, read_config_file
from .connection import Reporting, get_backend_session

LOGGER = logging.getLogger(__name__)


def get_repo_root(endpoint, project_id, experiment_id, file_path):
    """
    Gets the git repo path from server.

    Args:
        endpoint: path to server endpoint
        project_id: unique project identifier (required)
        experiment_id: unique experiment identifier (required)
        file_path: current file path. Could be any file that belongs to the
        repo.

    Returns: path to git repo

    """
    payload = {
        "projectId": project_id, "filePath": file_path, "experimentId": experiment_id
    }
    r = get_backend_session().get(endpoint, params=payload)
    ret_val = json.loads(r.text)

    if "root_path" in ret_val and ret_val["root_path"] is not None:
        return ret_val["root_path"]

    elif "msg" in ret_val:
        raise ValueError(ret_val["msg"])

    return None


def merge_config_file(base_config, repo_root_path):
    """ Try reading the configuration file at the root of the repository and
    return the merged config
    Args:
        base_config: a configuration dictionary, usually a copy of the
        default configuration
        repo_root_path: path of repository root
    """
    config_file_path = join(repo_root_path, CONFIG_PATH)

    return read_config_file(base_config, config_file_path)


def compress_py_files(repo_root_path, extensions):
    """
    Compresses all files ending with given extensions in repo to a single zip
    file
    Args:
        repo_root_path: path of folder to zip
        extensions: list of strings containing extensions of files to zip

    Returns: (path to folder that contains zip file, full path to zip file)

    """
    zip_dir = tempfile.mkdtemp()
    zip_path = join(zip_dir, "repo.zip")

    archive = zipfile.ZipFile(zip_path, "w")

    for root, _, files in os.walk(repo_root_path):
        for afile in files:
            extension = splitext(afile)[-1].lower()
            if extension in extensions:
                arcname = join(root.replace(repo_root_path, ""), afile)
                archive.write(join(root, afile), arcname=arcname)
    archive.close()

    return zip_dir, zip_path


def _send_file(url, files, params):
    r = get_backend_session().post(url, params=params, files=files)

    if r.status_code != 200:
        raise ValueError("POSTing file failed: %s" % r.content)


def send_file(
    post_endpoint, api_key, experiment_id, project_id, file_path, additional_params=None
):
    params = {"experimentId": experiment_id, "projectId": project_id, "apiKey": api_key}

    if additional_params is not None:
        params.update(additional_params)

    with open(file_path, "rb") as _file:

        files = {"file": _file}

        _send_file(post_endpoint, params=params, files=files)


def send_file_contents(
    post_endpoint,
    api_key,
    experiment_id,
    project_id,
    file_contents,
    file_name,
    additional_params=None,
):
    params = {"experimentId": experiment_id, "projectId": project_id, "apiKey": api_key}

    if additional_params is not None:
        params.update(additional_params)

    files = {"file": (file_name, file_contents)}

    _send_file(post_endpoint, params=params, files=files)


def upload_repo(
    project_id,
    experiment_id,
    file_path,
    get_path_endpoint,
    post_zip_endpoint,
    api_key,
    config,
):
    """
    Determines repo path and uploads a subset of it's files to server. Used to
    create pull requests on the frontend.
    Args:
        project_id: unique project id
        experiment_id: unique experiment id
        file_path: path to a python file that is part of the repo
        get_path_endpoint: server endpoint url to get repo path
        post_zip_endpoint: server endpoint url to send zip file
        config: a configuration dictionary, usually a copy of the default
        configuration
        api_key: the user's api_key

    Returns: None

    """
    try:
        repo_root_path = get_repo_root(
            get_path_endpoint, project_id, experiment_id, file_path
        )

        if not repo_root_path:
            return

        config = merge_config_file(config, repo_root_path)

        zip_folder, zip_path = compress_py_files(
            repo_root_path, config["uploaded_extensions"]
        )

        send_file(post_zip_endpoint, api_key, experiment_id, project_id, zip_path)
        Reporting.report(
            event_name=REPO_UPLOADED,
            experiment_key=experiment_id,
            project_id=project_id,
            api_key=api_key,
        )

        # Cleanup temp directory
        shutil.rmtree(zip_folder)
    except ValueError as e:
        LOGGER.error("Repo files would not be synced", exc_info=True)
        Reporting.report(
            event_name=REPO_UPLOADED_FAILED,
            experiment_key=experiment_id,
            project_id=project_id,
            api_key=api_key,
            err_msg=str(e),
        )


def upload_file(
    project_id,
    experiment_id,
    file_path,
    upload_endpoint,
    api_key,
    additional_params=None,
    clean=True,
):
    try:
        send_file(
            upload_endpoint,
            api_key,
            experiment_id,
            project_id,
            file_path,
            additional_params,
        )

        if clean is True:
            # Cleanup file
            try:
                os.remove(file_path)
            except OSError:
                pass
    except Exception as e:
        LOGGER.error("File could not be uploaded", exc_info=True)
        Reporting.report(
            event_name=FILE_UPLOADED_FAILED,
            experiment_key=experiment_id,
            project_id=project_id,
            api_key=api_key,
            err_msg=str(e),
        )


def upload_file_contents(
    project_id,
    experiment_id,
    file_contents,
    file_name,
    upload_endpoint,
    api_key,
    additional_params=None,
):
    try:
        send_file_contents(
            upload_endpoint,
            api_key,
            experiment_id,
            project_id,
            file_contents,
            file_name,
            additional_params,
        )
    except Exception as e:
        LOGGER.error("File could not be uploaded", exc_info=True)
        Reporting.report(
            event_name=FILE_UPLOADED_FAILED,
            experiment_key=experiment_id,
            project_id=project_id,
            api_key=api_key,
            err_msg=str(e),
        )


def upload_repo_start_process(
    project_id,
    experiment_id,
    file_path,
    get_path_endpoint,
    post_zip_endpoint,
    api_key,
    config,
):
    args = (
        project_id,
        experiment_id,
        file_path,
        get_path_endpoint,
        post_zip_endpoint,
        api_key,
        config,
    )
    p = Process(target=upload_repo, args=args)
    p.start()
    return p


def upload_file_process(*args):
    p = Process(target=upload_file, args=args)
    p.start()
    return p


def upload_file_contents_process(*args):
    p = Process(target=upload_file_contents, args=args)
    p.start()
    return p
