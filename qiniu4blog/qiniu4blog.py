#!/usr/bin/env python3

import os, time, datetime, platform, urllib, hashlib
import qiniu
from mimetypes import MimeTypes
import pyperclip
from os.path import expanduser
import configparser

homedir = expanduser("~")
config = configparser.ConfigParser()
config.read(homedir+'/qiniu.cfg')
mime = MimeTypes()
now = datetime.datetime.now()


try:
    bucket = config.get('config', 'bucket')
    accessKey = config.get('config', 'accessKey')
    secretKey = config.get('config', 'secretKey')
    path_to_watch = config.get('config', 'path_to_watch')
    enable = config.get('custom_url','enable')
    if enable == 'false':
        print('custom_url not set')
    else:
        addr = config.get('custom_url','addr')


except ConfigParser.NoSectionError as err:
    print('Error Config File:' + err)


def setcodeingbyos():
    '''获取系统平台,设置编解码'''
    if 'cygwin' in platform.system().lower():
        code = 'GBK'
    elif os.name == 'nt' or platform.system() == 'Windows':
        code = 'GBK'
    elif os.name == 'mac' or platform.system() == 'Darwin':
        code = 'utf-8'
    elif os.name == 'posix' or platform.system() == 'Linux':
        code = 'utf-8'
    return  code


def set_clipboard(url_list):
	for url in url_list:
		pyperclip.copy(url)
	spam = pyperclip.paste()



def parseRet(retData, respInfo):
    '''处理上传结果'''
    if retData != None:
        print("Upload file success!")
        print("Hash: " + retData["hash"])
        print("Key: " + retData["key"])
        for k, v in retData.items():
            if k[:2] == "x:":
                print(k + ":" + v)
        for k, v in retData.items():
            if k[:2] == "x:" or k == "hash" or k == "key":
                continue
            else:
                print(k + ":" + str(v))
    else:
        print("Upload file failed!")
        print("Error: " + respInfo.text_body)


def upload_without_key(bucket, filePath, uploadname):
    '''上传文件'''

    auth = qiniu.Auth(accessKey, secretKey)
    upToken = auth.upload_token(bucket, key=None)
    
    key = uploadname
    retData, respInfo = qiniu.put_file(upToken, key, filePath, mime_type=mime.guess_type(filePath)[0])
    parseRet(retData, respInfo)


def getkey(filename):
    ext = filename[filename.rfind('.'):]
    file_path = path_to_watch + '/' + filename
    md5 = hashlib.md5(open(file_path, 'rb').read()).hexdigest()
    # remote url: filetype/year/month/md5.filetype
    remote = ext[1:] + '/' + str(now.year) + '/' + str(now.month) + '/' + md5 + ext
    return remote


def main():
    print("running ... ...")
    before = dict([(f, None) for f in os.listdir(path_to_watch)])
    while 1:
        time.sleep(1)
        after = dict([(f, None) for f in os.listdir(path_to_watch)])
        added = [f for f in after if not f in before]
        removed = [f for f in before if not f in after]
        if added:
            print("Added Files: " + ", ".join(added))
            # print(added)
            url_list = []

            for i in added:
                filekey = getkey(i)

                upload_without_key(bucket, os.path.join(path_to_watch, i), filekey)
                if enable == 'true':
                    url = addr + urllib.parse.quote(filekey)
                else:
                    url = 'http://' + bucket + '.qiniudn.com/' + urllib.parse.quote(filekey)
                url_list.append(url)

            with open('image_markdown.txt', 'a') as f:
                for url in url_list:
                    image = '![' + added[0] + ']' + '(' + url + ')' + '\n'
                    f.write(image)
            print("image url [markdown] is save in image_markdwon.txt")

            set_clipboard(url_list)
        if removed:
            print("Removed Files: " + ", ".join(removed))
            print(removed)
        before = after

if __name__ == "__main__":
    main()


