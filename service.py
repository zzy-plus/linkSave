import os
import shutil
from ftplib import FTP
import zipfile
import json
import winreg
import subprocess
from tkinter import filedialog, messagebox
import requests

#打开教程页面
def openPage(url):
    cmd = f"start {url}"
    try:
        subprocess.run(cmd, shell=True)
    except Exception as e:
        print(e)

#解压zip
def unzip(zip_file_path, extract_folder):
    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
        file_names = zip_ref.namelist()
        filename = file_names[0].split('/')[0]
        zip_ref.extractall(extract_folder)
        return filename



#使用py访问ftp服务
def ftpDownload(host, username, passwd, remoteFilePath, localFilePath):
    ftp = None
    try:
        # 连接到FTP服务器
        ftp = FTP()
        ftp.connect(host)
        ftp.login(username, passwd)
        # 打开本地文件以写入下载的数据
        with open(localFilePath, 'wb') as local_file_obj:
            # 下载文件
            print(remoteFilePath)
            ftp.retrbinary('RETR ' + remoteFilePath, local_file_obj.write)
        print(f"文件 '{remoteFilePath}' 下载成功到 '{localFilePath}'")
    except Exception as e:
        print(f"下载文件时发生错误: {str(e)}")
    finally:
        # 关闭FTP连接
        ftp.quit()


def pyExec(cmd):
    return os.popen(cmd).readlines()
def getUserDoc():
    subkey = r"Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders"
    # 打开注册表键
    registry_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, subkey)
    # 读取注册表值
    value, _ = winreg.QueryValueEx(registry_key, "Personal")
    # 关闭注册表键
    winreg.CloseKey(registry_key)
    print(value)
    return value

def copyFile(source,target):
    cmd = "Xcopy " + source + " " + target + " /E /Y /I"
    ret = pyExec(cmd)
    print(ret)

def readData():
    saveDataPath = getUserDoc() + r'\Euro Truck Simulator 2\save_dat.json'
    with open(saveDataPath,'r') as f:
        saveData = json.load(f)
        return saveData['fileList']

def writeData(filename):
    files = os.listdir(getUserDoc() + r'\Euro Truck Simulator 2')
    if 'save_dat.json' in files:
        file_list = readData()
    else:
        file_list = []
    if filename in file_list:
        return
    file_list.append(filename)

    saveDataPath = getUserDoc() + r'\Euro Truck Simulator 2\save_dat.json'
    content = {'fileList': file_list}
    with open(saveDataPath,'w') as f:
        json.dump(content, f)

def clearData():
    saveDataPath = getUserDoc() + r'\Euro Truck Simulator 2\save_dat.json'
    with open(saveDataPath,'w') as f:
        json.dump({'fileList':[]}, f)

def removeFiles(filenames):
    folder_path = getUserDoc() + '\\Euro Truck Simulator 2\\profiles\\'
    for filename in filenames:
        try:
            shutil.rmtree(folder_path + filename)
            print(f"The folder '{folder_path}' has been successfully removed.")
        except OSError as e:
            print(f"Error: {e}")
    clearData()

def renameFiles(path,mode):
    # mode=0,移除
    # mode=1,添加
    files = os.listdir(path)
    print(files)
    if mode == 0:
        print(0)
        for file in files:
            if file.startswith('dlc_') and file not in \
                    ['dlc_rocket_league.scs',
                     'dlc_man_tgx_2020.scs',
                     'dlc_daf_2021.scs',
                     'dlc_daf_tuning_pack.scs',
                     'dlc_daf_xd.scs']:
                os.rename(path + '\\' + file, path + '\\1' + file)

    elif mode == 1:
        print(1)
        for file in files:
            if file.startswith('1dlc_'):
                os.rename(path + '\\' + file, path + '\\' + file[1:])


def setConfigFilesPath():
    dirPath = filedialog.askdirectory() # 选择路径
    if dirPath:
        print(dirPath)
        userHome = os.path.expanduser("~")
        tempPath = userHome + '\\AppData\\Roaming\\linkSave'
        if not os.path.exists(tempPath):
            os.makedirs(tempPath)
        # 保存路径
        with open(tempPath + '\\config.cfg', 'w', encoding='utf-8') as f:
            f.write(dirPath.strip())
        messagebox.showinfo('提示', '设置成功！\n注意：这个路径仅需设置一次，直到你想更改配置文件')


def copyConfigFiles(savePath):
    # 检测配置文件路径是否设置
    filePath = os.path.expanduser("~") + '\\AppData\\Roaming\\linkSave\\config.cfg'
    if not os.path.exists(filePath):
        return
    with open(filePath, 'r', encoding='utf-8') as f:
        configFilesPath = f.readline()

    copyList = []
    if os.path.exists(configFilesPath + '\\config.cfg'):
        try:
            shutil.copy(configFilesPath + '\\config.cfg', savePath + '\\config.cfg')
            copyList.append('config.cfg')
        except Exception as e:
            pass

    if os.path.exists(configFilesPath + '\\config_local.cfg'):
        try:
            shutil.copy(configFilesPath + '\\config_local.cfg', savePath + '\\config_local.cfg')
            copyList.append('config_local.cfg')
        except Exception as e:
            pass

    if os.path.exists(configFilesPath + '\\controls.sii'):
        try:
            shutil.copy(configFilesPath + '\\controls.sii', savePath + '\\controls.sii')
            copyList.append('controls.sii')
        except Exception as e:
            pass

    return copyList


def getUpdateInfo():
    resp = requests.get('http://121.37.222.191:8020/update')
    if resp.status_code != 200:
        return
    return resp.json()


if __name__ == '__main__':
    pass


