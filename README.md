# ClassIn Downloader

用以批量下载 ClassIn 上的课程录像。仅在中国科学技术大学（USTC）的 Blackboard + ClassIn 平台下测试可用。



## 使用方法

### 可执行文件（.exe）

从 [Releases](https://github.com/JiangGua/classin-downloader/releases/latest) 中下载打包好的 exe 文件，双击运行，耐心等待屏幕提示显示后按照提示操作。其中，「ClassIn 在线研讨室 - 全部显示」页面的源代码的获取方式如下：

![ClassIn 在线研讨室](https://cdn.jsdelivr.net/gh/JiangGua/classin-downloader/assets/all-classin-links.png)

然后在空白处右键，「查看网页源代码」，在新弹出的页面按 <kbd>Ctrl</kbd>+<kbd>A</kbd> 全选， <kbd>Ctrl</kbd>+<kbd>C</kbd> 复制，再粘贴到弹出的文本编辑器中保存即可。



### Python 脚本

#### 下载单个 ClassIn 视频

```shell
python main.py classin "https://www.eeo.cn/live.php?lessonKey=5f--------f1"
python main.py classin "5f--------f1"
```

#### 批量下载 Blackboard 网页/txt 文件 里的 ClassIn 视频

先去自己的 `Blackboard - ClassIn 在线研讨室 - 获取历史回放列表 - 全部显示` ，然后 <kbd>Ctrl</kbd>+<kbd>S</kbd> 保存 `网页，仅HTML`。

下面命令里的 `bb.html` 可替换为到 HTML 文件的绝对路径。

```shell
python src/cli.py txt bb.txt
```



## 参考

下载：

- [高级用法: 流式请求 - Requests 中文文档](https://requests.readthedocs.io/zh_CN/latest/user/advanced.html#streaming-requests)
- [使用 requests 库实现多线程下载 - cnblogs](https://www.cnblogs.com/weiyinfu/p/8126063.html)

打包：

- [用 PyInstaller 打包一个 exe 程序 - CSDN](https://blog.csdn.net/huilan_same/article/details/54377919)

图标：

- [Gauger.io - 从 Font Awesome 生成图标](https://gauger.io/fonticon/)