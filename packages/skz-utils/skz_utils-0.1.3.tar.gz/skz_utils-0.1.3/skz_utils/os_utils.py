# -*- coding: utf-8 -*-
import os
import glob
import random
import shutil
import pickle
from datetime import datetime

# path operation
def create_file_path(dir_path, file_name):
    return os.path.join(dir_path, file_name)

def create_dir_path(dir_path, dir_name):
    return os.path.join(dir_path, dir_name)

def give_me_dir_path(parent_dir_path, pre_dir_name=""):
    dir_name = pre_dir_name + "_" + get_dateTime_str()
    return os.path.join(parent_dir_path, dir_name)

# diretory operation
def createDir (dirPath):
    if not os.path.exists(dirPath):
        os.makedirs(dirPath)

def removeDir (dirPath):
    if os.path.exists(dirPath):
        shutil.rmtree(dirPath, ignore_errors=True)

def renameDir (dirPath):
    if os.path.exists(dirPath):
        dt = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        os.rename(dirPath, dirPath + "_bk_" + dt)

def get_dateTime_str():
    dt_str = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    return dt_str

def remove_and_create_Dir(dirPath):
    removeDir(dirPath)
    createDir(dirPath)

def rename_and_create_Dir(dirPath):
    renameDir(dirPath)
    createDir(dirPath)

def get_parent_dirPath(filePath):
    return os.path.split(filePath)[0]

def get_parent_dirName(filePath):
    dirPath = os.path.split(filePath)[0]
    return os.path.split(dirPath)[1]

def get_dir_name(dirPath):
    return os.path.split(dirPath)[1]

def get_dir_name_list(dir_root_path):
    '''get dir_name list under root_dir
    '''
    dir_name_list = []
    for x in os.listdir(dir_root_path):
        xPath = dir_root_path + "/" + x
        if os.path.isdir(xPath):
            dir_name_list.append(x)
    return dir_name_list

def get_sub_dir_path_list(dir_root_path):
    '''get sub_dir_path list under root_dir
    '''
    dir_path_list = []
    for x in os.listdir(dir_root_path):
        xPath = dir_root_path + "/" + x
        if os.path.isdir(xPath):
            dir_path_list.append(xPath)
    return dir_path_list

# file operation
def copy_file(src_filePath, dst_filePath):
    if not os.path.exists(src_filePath):
        return False
    shutil.copyfile(src_filePath, dst_filePath)
    return True

def get_fileName_ext(filePath):
    return os.path.split(filePath)[1]

def get_fileName_no_ext(filePath):
    fileName_ext = os.path.basename(filePath)
    fileName_no_ext = os.path.splitext(fileName_ext)[0]
    return fileName_no_ext

def is_path_exists(path):
    return os.path.exists(path)

def get_all_files_pathList(dirPath, ext):
    file_pathList = []
    for path, subdirs, files in os.walk(dirPath):
        for name in files:
            if name.endswith('.' + ext) and not name.startswith('.'):
                filePath = os.path.join(path, name)
                file_pathList.append(filePath)
    return file_pathList

def get_file_name_list(dirPath, ext):
    file_name_list = []
    for x in os.listdir(dirPath):
        if x.endswith('.' + ext) and not x.startswith('.'):
            file_name_list.append(x)
    return file_name_list

def get_file_path_list(dirPath, ext):
    file_path_list = []
    for x in os.listdir(dirPath):
        if x.endswith('.' + ext) and not x.startswith('.'):
            file_path_list.append(dirPath + "/" + x)
    return file_path_list

def sum_files(dirpath, ext):
    return len(get_file_name_list(dirpath, ext))

def sum_sub_dir_files(dir_path, ext):
    sub_dir_path_list = sorted(get_sub_dir_path_list(dir_path))
    sub_dir_name_list = []
    sub_dir_sum_list = []
    for sub_dir_path in sub_dir_path_list:
        sub_dir_name_list.append(get_dir_name(sub_dir_path))
        sub_dir_sum_list.append(sum_files(sub_dir_path, ext))
    
    return sub_dir_sum_list, sub_dir_name_list

#want to remove functions ####################################################################
def getSubDirListOf(dirPath):
    dirList = []
    for x in os.listdir(dirPath):
        xPath = dirPath + "/" + x
        """
        if not os.path.isabs(xPath):
            xPath = os.path.dirname(os.path.abspath(__file__)) + "/" + xPath
        """
        if os.path.isdir(xPath):
            dirList.append(x)
        """
        else:
            print(x + " is not dir")
        """
    return dirList

def getFileListOf(dirPath, ext):
    fileList = []
    for x in os.listdir(dirPath):
        if x.endswith('.' + ext) and not x.startswith('.'):
            fileList.append(x)
    return fileList

def getPathListOf(dirPath, ext):
    fileList = []
    for x in os.listdir(dirPath):
        if x.endswith('.' + ext) and not x.startswith('.'):
            fileList.append(dirPath + "/" + x)
    return fileList

def countFilesOf(rootDirPath, ext):
    dirList = getSubDirListOf(rootDirPath)
    count = 0
    for i in range(len(dirList)):
        if not dirList[i].startswith('.'):
            dirPath = rootDirPath + "/" + dirList[i]
            # get files
            fileList = getFileListOf(dirPath, ext)
            count += len(fileList)
    return count

def exportStrList2File(strList, otFilePath):
    '''export string list to file
    '''
    f = open(otFilePath, "w")
    for line in strList:
        line = line + "\n"
        try:
            f.write(line.encode('utf_8'))
        except Exception as ex:
            print(ex)
    f.close()

def loadLineListFromFile(filePath):
    f = open(filePath)
    lines = f.readlines()
    f.close()
    lineList = []
    for line in lines:
        line = line.replace('\n', '')
        line = line.replace('\r', '')
        lineList.append(line)
    return lineList

def dumpStrList2File(strList, otFilePath):
    with open(otFilePath, 'wb') as f:
        pickle.dump(strList, f)

def loadFile2StrList(itFilePath):
    with open(itFilePath, 'rb') as f:
        strList = pickle.load(f)
    return strList