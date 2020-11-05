import os
import threading
import time

import requests
import retry

def multi_thread_download(url, path):
    PER_THREAD_MIN = 2000  # 每个线程至少下载量
    MAX_THREAD_COUNT = 50  # 最多线程数
    TEMP_FOLDER = "dow"  # 临时文件夹
    TARGET_FILE_NAME = "mul.mp4"  # 存储目标
    if not os.path.exists(TEMP_FOLDER):
        os.mkdir(TEMP_FOLDER)
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
        with open(TARGET_FILE_NAME, "wb") as f:
            for j, i in enumerate(task):
                with open(i['path'], 'rb') as ff:
                    f.write(ff.read(i['end'] - i['beg']))
        endTime = time.time()
        print(endTime - begTime)

    @retry.retry(tries=100)
    def go(it):
        nonlocal  cnt
        print(it)
        resp = requests.get(url, headers={
            'Range': "bytes=%d-%d" % (it['beg'], it['end'] - 1)
        })
        if resp.status_code not in [200, 206]:
            print(it, resp.status_code, '爬虫失败')
            raise Exception("爬虫失败")
        if len(resp.content) != it['end'] - it['beg']:
            print("长度不对")
            raise Exception("长度不对")
        with open(it['path'], 'wb') as f:
            f.write(resp.content)
        print(it, it['end'] - it['beg'], len(resp.content), 'over', resp.status_code)
        lock.acquire(timeout=0)
        cnt -= 1
        if cnt == 0:
            merge()
        lock.release()

    def start_threading():
        for i in task:
            threading.Thread(target=go, args=(i,)).start()

    start_threading()