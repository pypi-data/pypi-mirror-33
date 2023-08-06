"""Docstring for ``decorator``.

========================
Function Decorator
========================
==================== =========================================================
File Transfer
==============================================================================
gdrive_downloader    File downloader from Google Drive.
gdrive_uploader      File uploader to Google Drive.
==================== =========================================================
"""


import os
from glob import glob
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
# from google.colab import auth
from oauth2client.client import GoogleCredentials


__all__ = ['gdrive_downloader',
           'gdrive_uploader']


def gdrive_downloader(gdrive_url_id, pattern='*', download_path='./data'):
    """Download files in Google Drive.

    Download files in Googel Drive to the given path.

    Parameters
    ----------
    gdrive_url_id: str
        An URL ID of an Google Drive directory which contains files to
        download.
        `https://drive.google.com/drive/folders/<google drive URL ID>`.

    pattern: str (default: '*')
        A pattern of regular expression to filter file in the target directory.

    download_path: str (default: './data')
        A target directory to download files in given URL ID.

    Returns
    -------
    None
        Nothing is returned.

    See Also
    --------
    `PyDrive`

    Examples
    --------
    >>> import unipy.util.gdrive import gdrive_downloader
    >>> gdrive_path_id = '1LA5334-SZdizcFqkl4xO8Hty7w1q0e8h'
    >>> up.gdrive_downloader(gdrive_path_id)

    """
    # 1. Authenticate and create the PyDrive client.
    # auth.authenticate_user()
    gauth = GoogleAuth()
    gauth.credentials = GoogleCredentials.get_application_default()
    drive = GoogleDrive(gauth)

    # 2. Create a directory for download.
    try:
        os.makedirs(download_path, exist_ok=False)
        print("Creating a directory: '{path}'".format(path=download_path))
    except FileExistsError:
        print("Directory Exists: '{path}'".format(path=download_path))

    # 3. Get a list of target files.
    file_list = drive.ListFile(
    {'q': "'{url_id}' in parents".format(url_id=gdrive_url_id)}).GetList()

    # 4. Download it.
    for file in file_list:
        # 3. Create & download by id.
        print('title: %s, id: %s' % (file['title'], file['id']))
        fname = os.path.join('data', file['title'])
        print('Downloading {fname} ...'.format(fname=fname))
        f_ = drive.CreateFile({'id': file['id']})
        f_.GetContentFile(fname)

    print('\nDownload Finished.')


def gdrive_uploader(gdrive_url_id, pattern='*', src_dir='./data'):
    """Download files in Google Drive.

    Download files in Googel Drive to the given path.

    Parameters
    ----------
    gdrive_url_id: str
        An URL ID of an Google Drive directory to upload files.
        `https://drive.google.com/drive/folders/<google drive URL ID>`.

    pattern: str (default: '*')
        A pattern of regular expression to filter file in the target directory.

    src_dir: str (default: './data')
        A source directory to upload files in given URL ID.

    Returns
    -------
    None
        Nothing is returned.

    See Also
    --------
    `PyDrive`

    Examples
    --------
    >>> import unipy.util.gdrive import gdrive_uploader
    >>> gdrive_path_id = '1LA5334-SZdizcFqkl4xO8Hty7w1q0e8h'
    >>> up.gdrive_uploader(gdrive_path_id)

    """
    # 1. Authenticate and create the PyDrive client.
    #auth.authenticate_user()
    gauth = GoogleAuth()
    gauth.credentials = GoogleCredentials.get_application_default()
    drive = GoogleDrive(gauth)

    # 2. Get a list of target files.
    print("Uploading: '{path}'".format(path=src_dir))
    file_list = glob(src_dir + '/*')
    gdrive_exist_list = drive.ListFile(
        {'q': "'{url_id}' in parents".format(url_id=gdrive_url_id)}).GetList()
    gdrive_exist_name = [f['title'] for f in gdrive_exist_list]

    for file in file_list:

        fname = file.split('/')[-1]

        if fname in gdrive_exist_name:
            print("'{fname}' File exists. Updating it...".format(fname=fname))
            f_ = [f for f in gdrive_exist_list if f['title'] == fname][0]
        else:
            print("Uploading '{fname}' ...".format(fname=fname))
            f_ = drive.CreateFile({'title': fname,
                                   "parents" : [{"id": gdrive_url_id}]})
        f_.SetContentFile(file)
        f_.Upload()

    print('\nUpload Finished.')
