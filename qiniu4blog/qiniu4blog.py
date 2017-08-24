#!/usr/bin/env python3

import configparser
import datetime
import hashlib
import os
import platform
import sys
import time
import urllib
from mimetypes import MimeTypes

import pyperclip
import qiniu
from watchdog.events import PatternMatchingEventHandler
from watchdog.observers import Observer

config = configparser.ConfigParser()
config.read(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'qiniu.cfg'))
bucket = config.get('config', 'bucket')
ak = config.get('config', 'accessKey')
sk = config.get('config', 'secretKey')
path_to_watch = config.get('config', 'path_to_watch', fallback='.')
addr = config.get('config', 'addr')
style = config.get('config', 'style', fallback='')  # 图片样式
mime = MimeTypes()
now = datetime.datetime.now()


class MyHandler(PatternMatchingEventHandler):
    patterns = ["*.jpeg", "*.jpg", "*.png", "*.bmp", "*.gif", "*.tiff", "*.tar.gz", "*.zip"]
    ignore_directories = True
    case_sensitive = False
    count = 0

    def on_created(self, event):
        # 不知为何新建文件会触发两次通知事件, 于是偷懒加了计数器, 达到只传一次的目的
        if self.count % 2:
            go(event.src_path)
        self.count += 1


def go(fp):
    # watchdog太过灵敏, 需要设定一点延时, 不然文件还未写入磁盘就开始后续操作会报permission deny的错误
    time.sleep(0.5)
    name, remote_key = generate_key(fp)  # 生成远端存储别名
    upload(fp, remote_key)  # 上传
    src = '![' + name + ']' + '(' + addr + remote_key + style + ')'
    set_clipboard(src)  # 整理md图片链接格式到剪贴板


def set_clipboard(s):
    pyperclip.copy(s)
    pyperclip.paste()
    print(s)


def upload(fp, uploadname):
    auth = qiniu.Auth(ak, sk)
    token = auth.upload_token(bucket, key=None)
    qiniu.put_file(token, uploadname, fp, mime_type=mime.guess_type(fp)[0])


def generate_key(fp):
    name, ext = os.path.splitext(os.path.basename(fp))
    with open(fp, 'rb') as fh:
        md5 = hashlib.md5(fh.read()).hexdigest()
    # remote url: filetype/year/month/md5.filetype
    remote = ext[1:] + '/' + str(now.year) + '/' + str(now.month) + '/' + md5 + ext
    return name, remote


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else path_to_watch
    event_handler = MyHandler()
    observer = Observer()
    observer.schedule(event_handler, path)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    finally:
        print("总共上传了{}个文件".format(event_handler.count // 2))
    observer.join()
