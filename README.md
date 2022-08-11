# FHPixivDownloader2.0
多地址自动下载的Pixiv爬虫2.0

> 详见：[Pixiv Python爬虫2.0](https://blog.ifhsj.top/archives/pixiv-python-pa-chong-20)

## 引言
之前写过Pixiv爬虫，这次对爬虫进行了升级，增加了XML自动爬取功能，修复了一些BUG。之前的爬虫文章地址：[Pixiv Python爬虫](https://blog.ifhsj.top/archives/pixiv-python-pa-chong)。


## XML自动爬取功能
1. 介绍  
该功能依赖urls.xml文件，使用该功能时，爬虫将自动检测该文件内的地址类型、位次，之后对地址进行多重请求，下载Pixiv原图，之后将成功下载的图片地址删除，保留下载或请求失败的地址。爬虫程序文件和urls.xml文件在文章最下方的链接中下载，目前urls.xml中每种类型的位次标签仅有16个，如果觉得不够，用户可根据实际情况，按命名规则自行增加。

2. 用法
	1. 设置好自己的Cookie和getSaveDir函数下的图片保存路径。
	2. 将想下载的图片地址，放到XML中对应的位次里。
	3. 开始爬虫程序，按两下回车。


## 对于 “类型” 和 “位次” 的说明
1. 类型：图片类型分为三种，R18、R16、Uncategorized（不好区分类型的图片），每种类型的选择仅关系到图片保存的目录。
2. 位次：位次即一个artworks下的图片次序。以 ```https://www.pixiv.net/artworks/95254183``` 为例，作者放了五张图片，那这五张图片的位次就是0、1、2、3、4，如果你想要下载第2张图片，就复制这个链接，粘贴到urls.xml中r16标签下的p1标签内即可。


## 开发环境
1. 系统：Windows 10 X64
2. Python版本：3.7.3
3. IDE：Pycharm2020.2


## 需要安装的第三方库
1. fake_useragnet
2. requests

安装代码：
``` Shell
pip install fake_useragent -i https://pypi.doubanio.com/simple
pip install requests -i https://pypi.doubanio.com/simple
```
