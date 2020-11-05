import os
import re
import sys
import json
import time

import requests

import downloader
from config import TEMP_FOLDER

# 爬虫请求头
headers = {
  'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
  'Accept-Language': 'zh-CN,zh;q=0.9,zh-TW;q=0.8,en;q=0.7',
  'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36',
}

class Blackboard():
    def __init__(self, html):
        self.html = html

    def links(self):
        classin_re = re.compile(r'https\:\/\/www\.eeo\.cn\/live\.php\?lessonKey\=[0-9a-zA-Z]+')
        links = classin_re.findall(self.html)
        return links

    def lessonkeys(self):
        classin_re = re.compile(r'(?<=https:\/\/www\.eeo\.cn\/live\.php\?lessonKey\=)[0-9a-zA-Z]+')
        keys = classin_re.findall(self.html)
        return keys

class Classin():
    def __init__(self, lessonkey):
        self.lessonkey = lessonkey
        self.webcastdata = None
        self.classinfo = None
    
    def _webcastdata(self):
        if self.webcastdata:
            return self.webcastdata

        from_data = {
            'lessonKey': self.lessonkey
        }
        r = requests.post('https://www.eeo.cn/saasajax/webcast.ajax.php?action=getLessonWebcastData', data=from_data)
        self.webcastdata = json.loads(r.text)
        return self.webcastdata

    def _classinfo(self):
        if self.classinfo:
            return self.classinfo
        
        from_data = {
            'lessonKey': self.lessonkey
        }
        r = requests.post('https://www.eeo.cn/saasajax/webcast.ajax.php?action=getLessonClassInfo', data=from_data)
        self.classinfo = json.loads(r.text)
        return self.classinfo

    def course_name(self):
        data = self._classinfo()
        return data['data']['courseName']

    def teacher(self):
        data = self._classinfo()
        return data['data']['teacherName']

    def school(self):
        data = self._classinfo()
        return data['data']['schoolName']

    def start_timestamp(self):
        # 秒时间戳
        data = self._classinfo()
        return data['data']['lessonStarttime']

    def end_timestamp(self):
        # 秒时间戳
        data = self._classinfo()
        return data['data']['lessonEndtime']

    def videolist(self):
        data = self._webcastdata()
        vlist = data['data']['lessonData']['vodList']
        result = []
        for i in sorted(vlist):
            result.append(vlist[i])
        return result

    def _md(self, timestamp):
        local_time = time.localtime(int(timestamp))
        md = time.strftime("%m%d", local_time)
        return md

    def md(self):
        return self._md(self.start_timestamp())

    def info(self):
        obj = {
            'course_name': self.course_name(),
            'teacher': self.teacher(),
            'videolist': self.videolist(),
            'start_timestamp': self.start_timestamp(),
            'end_timestamp': self.end_timestamp(),
            'md': self.md()
        }
        return obj

def get_classin_video(lessonkey):
    c = Classin(lessonkey)
    path = os.path.join(c.course_name(), c.teacher(), c.md())
    if not os.path.exists(path):
        os.makedirs(path)
    
    vlist = c.videolist()
    for i, v in enumerate(vlist):
        # r = requests.get(v, stream=True)
        vfile = os.path.join(path, '{}.mp4'.format(i))
        print('正在下载:', c.md())
        try:
            downloader.multithread_download(v, vfile)
        except Exception as e:
            print(vfile, '下载失败\n链接: ', v, '\n错误: ', e)
        # f = open(vfile, "wb")
        # try:
        #     for chunk in r.iter_content(chunk_size=512):
        #         if chunk:
        #             f.write(chunk)
        # except Exception as e:
        #     print(vfile, '下载失败\n链接: ', v, '\n错误: ', e)

def get_bb_videos(html_path):
    with open(html_path, 'r', encoding='utf-8') as f:
        bb_html = f.read()
    b = Blackboard(bb_html)
    lessonkeys = b.lessonkeys()
    for key in lessonkeys:
        get_classin_video(key)

def download_all_videos_from_bb_txt():
    temp_file_path = 'temp.txt'
    open(temp_file_path, 'w', encoding='utf-8').close()     # 创建一个空白的临时文本文件
    input('即将打开文本编辑器. 按回车键继续...')
    os.startfile(temp_file_path)
    input('请将「ClassIn 在线研讨室 - 全部显示」页面的源代码复制粘贴到其中, 保存退出后按回车键开始下载...')
    if not os.path.exists(TEMP_FOLDER):
        os.mkdir(TEMP_FOLDER)
    get_bb_videos(temp_file_path)
    os.remove(temp_file_path)    

if __name__ == "__main__":
    download_all_videos_from_bb_txt()
    