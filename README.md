# ClassIn Downloader

用以批量下载 ClassIn 上的课程录像。仅在中国科学技术大学（USTC）的 Blackboard + ClassIn 平台下测试可用。



## 使用

### 下载单个 ClassIn 视频

```shell
python main.py classin "https://www.eeo.cn/live.php?lessonKey=5f--------f1"
python main.py classin "5f--------f1"
```



### 批量下载 Blackboard 网页/txt 文件 里的 ClassIn 视频

先去自己的 `Blackboard - ClassIn 在线研讨室 - 获取历史回放列表 - 全部显示` ，然后 <kbd>Ctrl</kbd>+<kbd>S</kbd> 保存 `网页，仅HTML`。

下面命令里的 `bb.html` 可替换为到 HTML 文件的绝对路径。

```shell
python main.py bb bb.html
python main.py txt bb.txt
```

