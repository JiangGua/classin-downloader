import os
import time
import shutil
import threading
from tempfile import TemporaryDirectory

import requests
import retry

TEMP_FOLDER = "download_cache"  # 临时文件夹
if not os.path.exists(TEMP_FOLDER):
    os.mkdir(TEMP_FOLDER)

# 多线程下载
# 来自 https://www.cnblogs.com/weiyinfu/p/8126063.html
# @JiangGua 进行了一些修改
def multithread_download(url, path, debug=False):
    PER_THREAD_MIN = 2000  # 每个线程至少下载量
    MAX_THREAD_COUNT = 50  # 最多线程数
    begTime = time.time()
    resp = requests.get(url, stream=True)
    sz = int(resp.headers['Content-Length'])
    block_sz = max(sz // MAX_THREAD_COUNT, PER_THREAD_MIN)
    task = []
    cnt = 0
    for i in range(0, sz, block_sz):
        now_sz = sz - i if sz - i - block_sz < PER_THREAD_MIN else block_sz
        it = {
            'beg': i,
            'end': i + now_sz,
            'path': os.path.join(TEMP_FOLDER, str(cnt)),
            'last': i + now_sz == sz
        }
        task.append(it)
        cnt += 1
        if it['last']:
            break
    lock = threading.Lock()

    def merge():
        with open(path, "wb") as f:
            for j, i in enumerate(task):
                with open(i['path'], 'rb') as ff:
                    f.write(ff.read(i['end'] - i['beg']))
        endTime = time.time()
        if debug:
            print(endTime - begTime)

    @retry.retry(tries=100)
    def go(it):
        nonlocal cnt
        if debug:
            print(it)
        resp = requests.get(url, headers={
            'Range': "bytes=%d-%d" % (it['beg'], it['end'] - 1)
        })
        if resp.status_code not in [200, 206]:
            if debug:
                print(it, resp.status_code, '服务器响应异常')
            raise Exception("服务器响应异常")
        if len(resp.content) != it['end'] - it['beg']:
            if debug:
                print("文件切片长度不正确")
            raise Exception("文件切片长度不正确")
        with open(it['path'], 'wb') as f:
            f.write(resp.content)
        if debug:
            print(it, it['end'] - it['beg'], len(resp.content), 'over', resp.status_code)
        lock.acquire(timeout=0)
        cnt -= 1
        if cnt == 0:
            merge()
        lock.release()

    def start_threading():
        threads = []
        for i in task:
            threads.append(threading.Thread(target=go, args=(i,)))
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

    start_threading()
    shutil.rmtree(TEMP_FOLDER)

if __name__ == "__main__":
    multithread_download('https://csdnimg.cn/public/common/toolbar/images/csdnqr@2x.png', '下载/a.png', debug=True)
    # shutil.rmtree(TEMP_FOLDER)