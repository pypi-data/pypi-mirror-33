#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jun 11 01:42:23 2017

@author: pydemia
"""


import os
import sys
import getpass
import paramiko
import re


"""
Key Stroke Code
http://academic.evergreen.edu/projects/biophysics/technotes/program/ascii_ctrl.htm
"""

# %%

if __name__ == '__main__':

    try:
        kwargsDict = dict(x.split('=', 1) for x in sys.argv[1:])

        host = kwargsDict['-host']
        user = kwargsDict['-user']
        pswd = kwargsDict['-passwd']
        path = kwargsDict['-pythonpath']

    except KeyError:
        host = input('Enter the host address: ')
        user = input('Enter the username: ')
        pswd = getpass.getpass('Enter your password: ')
        path = input('Enter the Python PATH (default: ~/anaconda3/bin): ')

        if path == '':
            path = '~/anaconda3/bin'

    # %%

    with paramiko.SSHClient() as ssh:

        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(host,
                    username=user, password=pswd)

        python_path = path

        dir_command = 'jupyter --runtime-dir'
        exe_command = 'ipython kernel'

        kernel_start_cmd = '/'.join([python_path, exe_command])
        stdin, stdout, stderr = ssh.exec_command(kernel_start_cmd)
        kmsg = stdout.channel.recv(1024)

        comp = re.compile(r'--existing (kernel-\d+.json)')
        kernel_name = comp.findall(str(kmsg))[0]

        get_ipydir_cmd = '/'.join([python_path, dir_command])
        stdin, stdout, stderr = ssh.exec_command(get_ipydir_cmd)
        ipydir = stdout.readlines()[0][:-1]

        json_path = '{kdir}/{kjson}'.format(kdir=ipydir, kjson=kernel_name)
        client_cmd = 'scp -r {user}@{host}:{kpath} ~/'
        cl_cmd = client_cmd.format(user=user, host=host, kpath=json_path)
        os.system(cl_cmd)

        print('json : ~/' + kernel_name)

        while True:
            end_cmd = input("Enter 'exit' to close: ")
            if end_cmd == 'exit':
                channel = ssh.invoke_shell()
                channel.send('\1C')  # 'Ctrl + \' to exit in remote
                stdin, stdout, stderr = ssh.exec_command('rm ' + json_path)
                break

        # while True:
        #     time.sleep(1)
