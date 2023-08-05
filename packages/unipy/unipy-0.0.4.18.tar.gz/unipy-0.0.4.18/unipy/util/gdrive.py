# -*- coding: utf-8 -*-
"""
Created on Tue Jun 16 22:53:52 2018

@author: Young Ju Kim
"""

import os
from glob import glob
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
#from google.colab import auth
from oauth2client.client import GoogleCredentials


__all__ = ['gdrive_downloader',
           'gdrive_uploader']

def gdrive_downloader(gdrive_url_id, download_path='./data'):

    # 1. Authenticate and create the PyDrive client.
    #auth.authenticate_user()
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


def gdrive_uploader(gdrive_url_id, src_dir='./data'):

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


