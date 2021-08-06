#!/usr/bin/python
import argparse
import re
import sys
import os
import shutil
import subprocess
import os.path
import config
from zipfile import ZipFile
import os, fnmatch
import json

FROM_PROJECT_ID = config.FROM_PROJECT_ID
TO_PROJECT_ID = config.TO_PROJECT_ID
FROM_PROJECT = config.FROM_PROJECT
TO_PROJECT = config.TO_PROJECT
PREFIX = "_PREFIX_"

def replaceFileContent(filename, old_string, new_string):
    # Safely read the input filename using 'with'
    with open(filename) as f:
        s = f.read()
        if old_string not in s:
            return

    # Safely write the changed content, if found in the file
    with open(filename, 'w') as f:
        print('Changing "{old_string}" to "{new_string}" in {filename}'.format(**locals()))
        s = s.replace(old_string, new_string)
        f.write(s)

def _textureToSpriteFrame(filePath, fileName, ext):
    print('==>> file name', filePath)
    with open(filePath, 'r+') as json_file:
        data = json.load(json_file)
        fileName = fileName.replace(ext, '')
        if "type" not in data['userData']:
            print("CAN NOT change texture to sprite-frame ", filePath)
            return None
        else:
            print('==>> type before', data['userData']['type'])
            data['userData']['type'] = "sprite-frame"
            print('==>> type after', data['userData']['type'])

def textureToSpriteFrame(root_path, by_file_name, ext) :
    by_file_path = os.path.join(root_path, by_file_name)
    replaceFileContent(by_file_path, '"type": "texture",' ,'"type": "sprite-frame",')
#     _textureToSpriteFrame(by_file_path, by_file_name, ext)
########
# MAIN #
########
# # # 0.Copy to new folder, ignore .git
tool_path = os.path.dirname(os.path.realpath(__file__))
root_path = os.path.abspath(os.path.join(tool_path, os.pardir))
from_project_dir = root_path + '/' + FROM_PROJECT
to_project_dir = root_path + '/' + TO_PROJECT

# os.popen('killall CocosCreator')
# texture to sprite-frame
print('')
print("############ Texture to Sprite-frame ############")
curDir = to_project_dir
for root, dirs, files in os.walk(curDir):
    for file in files:
        if PREFIX in root:
            if file.endswith(".png.meta"):
                textureToSpriteFrame(root, file, ".png.meta")
            if file.endswith(".jpg.meta"):
                textureToSpriteFrame(root, file, ".jpg.meta")

shutil.rmtree(from_project_dir, ignore_errors=True)
# os.popen('open -a CocosCreator')