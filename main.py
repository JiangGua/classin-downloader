import re
import json
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

    
if __name__ == "__main__":
    # c = Classin('6cf034395ded55e4')
    # print(c.videolist())
    with open('a.html', 'r', encoding='utf-8') as f:
        text = f.read()
    b = Blackboard(text)
    print(b.lessonkeys())
