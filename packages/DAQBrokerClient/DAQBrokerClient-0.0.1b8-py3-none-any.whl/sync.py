import os
import time
import traceback
import platform
import subprocess


def syncDirectory(
        server,
        database,
        instrument,
        meta,
        backupPort,
        backupUser,
        backupPass,
        metaName,
        serverDB):
    scriptPath = os.getcwd()
    if(platform.system() == 'Windows'):  # Running on windows machine
        command1 = os.path.join(scriptPath, 'cygpath')
        command1 = command1 + ' ' + meta["path"]
        CREATE_NO_WINDOW = 0x08000000
        si = subprocess.STARTUPINFO()
        si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        winPath = subprocess.check_output(
            command1,
            universal_newlines=True,
            creationflags=CREATE_NO_WINDOW,
            startupinfo=si).replace(
            '\n',
            '')
        command = os.path.join(scriptPath, 'rsync') + \
            ' -a --no-p --append-verify --bwlimit=500'
        os.environ['RSYNC_PASSWORD'] = backupPass
        if 'getNested' in meta:
            if(meta['getNested'] == "1" or meta['getNested'] == "true" or meta['getNested']):
                comamand = command + ' --include="*/" '
        command = command + ' --include="*' + meta["pattern"] + '*.' + meta["extension"] + '" --exclude="*" --port=' + str(
            backupPort) + ' ' + winPath + '/ ' + backupUser + '@' + server + '::daqbroker/' + serverDB + '/' + database + '/' + instrument + '/' + metaName
        print(command)
        with open(os.devnull, 'w') as devnull:
            output = subprocess.call(
                command + '>out',
                env=os.environ,
                shell=True,
                creationflags=CREATE_NO_WINDOW,
                startupinfo=si,
                stderr=devnull)
    else:
        command = 'rsync -a --append-verify --no-p --bwlimit=500'
        if 'getNested' in meta:
            if(meta['getNested'] == "1" or meta['getNested'] == "true" or meta['getNested']):
                comamand = command + ' --include="*/" '
        command = command + ' --include="*' + meta["pattern"] + '*.' + meta["extension"] + '" --exclude="*" --port=' + str(
            backupPort) + ' ' + meta["path"] + '/ ' + backupUser + '@' + server + '::daqbroker/' + serverDB + '/' + database + '/' + instrument + '/' + metaName
        # print(backupPass)
        # print(command)
        with open(os.devnull, 'w') as devnull:
            output = subprocess.check_output(
                command.split(' '), env={
                    'RSYNC_PASSWORD': backupPass}, stderr=devnull)
