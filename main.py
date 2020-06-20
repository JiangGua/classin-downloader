import os
import re
import json
import time

import click
import requests

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

@click.group()
def cli():
    pass

def get_classin_video(lessonkey):
    c = Classin(lessonkey)
    path = os.path.join(c.course_name(), c.teacher(), c.md())
    if not os.path.exists(path):
        os.makedirs(path)
    
    vlist = c.videolist()
    for i, v in enumerate(vlist):
        r = requests.get(v, stream=True)
        vfile = os.path.join(path, '{}.mp4'.format(i))
        f = open(vfile, "wb")
        for chunk in r.iter_content(chunk_size=512):
            if chunk:
                f.write(chunk)

def get_bb_videos(html_path):
    with open(html_path, 'r', encoding='utf-8') as f:
        bb_html = f.read()
    b = Blackboard(bb_html)
    lessonkeys = b.lessonkeys()
    for key in lessonkeys:
        get_classin_video(key)

@cli.command()
@click.argument('path')
def bb(path):
    get_bb_videos(path)

@cli.command()
@click.argument('path')
def txt(path):
    get_bb_videos(path)

@cli.command()
@click.argument('url')
def classin(url):
    classin_re = re.compile(r'(?<=https:\/\/www\.eeo\.cn\/live\.php\?lessonKey\=)[0-9a-zA-Z]+')
    keys = classin_re.findall(url)
    if not keys:
        key = url
    else:
        key = keys[0]
    get_classin_video(key)

if __name__ == "__main__":
    cli()