#!/usr/bin/python
import argparse
import re
import sys
import os, fnmatch
import shutil
import subprocess
import os.path
import config
import json
import io

FROM_PROJECT_ID = config.FROM_PROJECT_ID
TO_PROJECT_ID = config.TO_PROJECT_ID
FROM_PROJECT = config.FROM_PROJECT
TO_PROJECT = config.TO_PROJECT
PREFIX = "_!@#$%_"


def isFileContainString(filename, string):
    try:
        with io.open(filename,"r", encoding="utf-8") as f:
            try:
                s = f.read()
                if string in s:
                    return True
                else:
                    return False
            except:
    #             print("CAN READ FILE::", filename)
                return False
    except IOError:
        return False

def isFilesContainString(dirName, string, targetFilePath):
    for root, dirs, files in os.walk(dirName):
        for file in files:
            fullFilePath = os.path.join(root, file)
            if targetFilePath != fullFilePath and not file.endswith('.DS_Store') and '.git' not in root:
                if not file.endswith('.png') and not file.endswith('.jpg'):
                    if isFileContainString( os.path.join(root, file), string ) :
                        return True
    return False

# Return the png uid
# filePath:                 cc-newgame-1234/Assets/Background/Info_Baccarat.png.meta
# fileName:                 Info_Baccarat.png.meta
# ext:                      .png.meta, .jpg.meta
# content in files:         "uuid": "d8e13355-4287-4f45-a24a-d6c35db8afb0",
def getImageUID(filePath, fileName, ext):
    with open(filePath) as json_file:
        data = json.load(json_file)
        fileName = fileName.replace(ext, '')
        result = ''
        if fileName not in data['subMetas']:
            print("FIND NO UUID FOR FILE ", filePath)
            return None
        else:
            return data['subMetas'][fileName]['uuid']

# Image has outer and inner UID
def getImageOuterUID(filePath, fileName, ext):
    with open(filePath) as json_file:
        data = json.load(json_file)
        fileName = fileName.replace(ext, '')
        return data['uuid']

# ChieuTuong.png.meta ref by ChieuTuong.json.meta
# 1. Check if json.meta file exist
# 2. Check if json.meta file contains outer uid
def isOuterUIDInSpines(filePath, fileName, uid) :
    jsonFileName = fileName.replace('png.meta', 'json.meta')
    jsonFilePath = filePath.replace(fileName, jsonFileName)
    return isFileContainString(jsonFilePath, uid)

def isImageUsedByFnt(metaImgPath, imgMetaName) :
    fntPath = metaImgPath.replace('.png.meta', '.fnt')
    imgName = imgMetaName.replace('.png.meta', '.png')
    return isFileContainString(fntPath, imgName)

def getFontUID(filePath):
    with open(filePath) as json_file:
        data = json.load(json_file)
        if 'uuid' not in data:
            print("FIND NO UUID FOR FILE ", filePath)
            return None
        else:
            return data['uuid']

########
# MAIN #
########



tool_path = os.path.dirname(os.path.realpath(__file__))
root_path = os.path.abspath(os.path.join(tool_path, os.pardir))
from_project_dir = root_path + '/' + FROM_PROJECT
to_project_dir = root_path + '/' + TO_PROJECT

curDir = to_project_dir + '/Assets'
print(curDir)
for root, dirs, files in os.walk(curDir):
    for file in files:
        if file.endswith("font_chat_1.png.meta") :
            metaFilePath = os.path.join(root, file)
            outerUID = getImageOuterUID(metaFilePath, file, 'png.meta')
            isInSpines = isOuterUIDInSpines(metaFilePath, file, outerUID)
            usedByFont = isImageUsedByFnt(metaFilePath, file)
            uuid = getImageUID(metaFilePath, file, ".png.meta")
            if uuid is not None and not isInSpines and not usedByFont:
                result = isFilesContainString(to_project_dir, uuid, metaFilePath)
                print(uuid)
                if not result:
                    #print("isFileContainsString::", result, metaFilePath)
                    #Remove file
                    filePath = metaFilePath.replace('.meta', '')
                    print("REMOVE_FILE::", metaFilePath)
                    print("REMOVE_FILE::", filePath)
                    try:
                        os.remove(metaFilePath)
                        os.remove(filePath)
                    except OSError:
                        pass


curDir = to_project_dir + '/Assets'
for root, dirs, files in os.walk(curDir):
    for file in files:
        if file.endswith(".jpg.meta") and 'fonts' not in root:
            metaFilePath = os.path.join(root, file)
            uuid = getImageUID(metaFilePath, file, ".jpg.meta")
            if uuid is not None:
                result = isFilesContainString(to_project_dir, uuid, metaFilePath)
                if not result:
                    #print("isFileContainsString::", result, metaFilePath)
                    #Remove file
                    filePath = metaFilePath.replace('.meta', '')
                    print("REMOVE_FILE::", metaFilePath)
                    print("REMOVE_FILE::", filePath)
                    try:
                        os.remove(metaFilePath)
                        os.remove(filePath)
                    except OSError:
                        pass

curDir = to_project_dir + '/Assets'
for root, dirs, files in os.walk(curDir):
    for file in files:
        if file.endswith(".fnt.meta"):
            metaFilePath = os.path.join(root, file)
            uuid = getFontUID(metaFilePath)
            if uuid is not None:
                result = isFilesContainString(to_project_dir, uuid, metaFilePath)
                if not result:
                    #print("isFileContainsString::", result, metaFilePath)
                    #Remove file
                    filePath = metaFilePath.replace('.meta', '')
                    print("REMOVE_FILE::", metaFilePath)
                    print("REMOVE_FILE::", filePath)
                    try:
                        os.remove(metaFilePath)
                        os.remove(filePath)
                    except OSError:
                        pass


curDir = to_project_dir + '/Assets'
for root, dirs, files in os.walk(curDir):
    for file in files:
        if file.endswith(".mp3.meta"):
            metaFilePath = os.path.join(root, file)
            uuid = getFontUID(metaFilePath)
            if uuid is not None:
                result = isFilesContainString(to_project_dir, uuid, metaFilePath)
                if not result:
                    #print("isFileContainsString::", result, metaFilePath)
                    #Remove file
                    filePath = metaFilePath.replace('.meta', '')
                    print("REMOVE_FILE::", metaFilePath)
                    print("REMOVE_FILE::", filePath)
                    try:
                        os.remove(metaFilePath)
                        os.remove(filePath)
                    except OSError:
                        pass