"""
Author: ifhsj
Blog: https://blog.ifhsj.top/
"""
 
from xml.etree import ElementTree as ET
from fake_useragent import UserAgent
from os.path import exists
from requests import get
from os import makedirs
from json import loads
from time import sleep
from re import findall
from sys import exit
 
 
# 初始Cookie
originalCookie: str = ""
 
 
# 获取V2Ray代理
def getProxies():
    return {
        'http': "http://127.0.0.1:10809",
        'https': "http://127.0.0.1:10809"
    }
 
 
# 获取用户Cookie
def getCookie():
    cookie: str = input("输入Cookie（使用默认则不填）或 “9” 来结束爬虫：").strip()
 
    return originalCookie if cookie == "" else cookie
 
 
# 获取图片类型
def getImgType():
    imgType = 3
    try:
        imgType: int = int(input("选择类型 —— 1.R18，2.R16，3.未分类  8.重设Cookie： "))
    except ValueError:
        print("只能输入数字，重新输入")
        getImgType()
 
    return imgType
 
 
# 获取图片位次
def getImgIndex():
    imgIndex = 0
    try:
        imgIndex: int = int(input("输入位次（p0为0，p1为1）："))
    except ValueError:
        print("只能输入数字，重新输入")
        getImgIndex()
 
    return imgIndex
 
 
# 生成Headers
def getHeaders(imgId, cookie):
    return {
        "cookie": cookie,
        "user-agent": UserAgent().random,
        "referer": "https://www.pixiv.net/artworks/" + imgId
    }
 
 
# 获取图片存储路径
def getSaveDir(imgType):
    R18Dir: str = "./Pixiv/R18NEW/"
    R16Dir: str = "./Pixiv/R16NEW/"
    NoneTypeDir: str = "./Pixiv/"
 
    if imgType == 1:
        if not exists(R18Dir):
            makedirs(R18Dir)
 
        return R18Dir
    elif imgType == 2:
        if not exists(R16Dir):
            makedirs(R16Dir)
 
        return R16Dir
    else:
        if not exists(NoneTypeDir):
            makedirs(NoneTypeDir)
 
        return NoneTypeDir
 
 
# 下载图片
def downloadImg(url, imgIndex, imgType, cookie):
    imgId = findall("http[s]://www.pixiv.net/artworks/(\d+)", url)[0]
    jsonUrl = "https://www.pixiv.net/ajax/illust/" + str(imgId) + "/pages"
 
    req = get(jsonUrl, headers=getHeaders(imgId, cookie), proxies=getProxies())
    json = req.text
 
    if req.status_code == 401:
        return 401
 
    imgUrl = loads(json)["body"][imgIndex]["urls"]["original"]
    suffix = ".jpg"
    if imgUrl[-4:] == "jpeg":
        suffix = ".jpeg"
 
    req = get(imgUrl, headers=getHeaders(imgId, cookie), proxies=getProxies())
 
    saveDir = getSaveDir(imgType)
    imgName = imgId + "_p" + str(imgIndex) + suffix
    with open(saveDir + imgName, "wb") as f:
        f.write(req.content)
 
    print(imgName, "已完成", "\n")
 
 
# 获取URL
def getUrl():
    method = input("选择模式 —— 1.列表输入，2.字符串解析：")
    urlList = []
    if method == "1":
        while True:
            url = input("持续输入地址，输入 ”9“ 停止输入：").strip()
            if url == "9":
                break
            elif not url.startswith("http"):
                print("只能输入 ”9“ 或URL，重新输入")
                continue
            else:
                urlList.append(url)
                continue
 
        return urlList
 
    elif method == "2":
        url = input("输入包含地址的字符串：").strip()
        urlList = findall("http[s]?://www.pixiv.net/artworks/\d+", url)
 
        if len(urlList) == 0:
            print("解析无结果")
        else:
            print("解析出", len(urlList), "个地址")
            print(urlList, "开始下载")
 
        return urlList
 
    else:
        print("只能输入 “1” 或 “2”，重新输入")
        getUrl()
 
 
# 尝试调用下载
def tryDownload(urlList, imgIndex, imgType, cookie):
    count = len(urlList)
    failedUrl = []
    for i in urlList:
        print("队列剩余：", count, "  正在开始下载......")
        count -= 1
 
        try:
            sCode = downloadImg(i, imgIndex, imgType, cookie)
 
            if sCode == 401:
                print("\n")
                print("------ 原始请求被拒绝，请检查Cookie ------")
                print("====== Pixiv 爬 虫 已 强 制 终 止 ======")
                exit(1)
 
            sleep(1.5)
        except Exception as e:
            failedUrl.append(i)
            print("第", urlList.index(i) + 1, "个地址出错：", end="")
            print(e, "\n")
 
    print("------- 全 部 完 成 -------")
    return failedUrl
 
 
# 尝试重新下载
def retry(failedUrl, imgIndex, imgType, cookie):
    print("出错的地址：", failedUrl)
    print("正在尝试重新下载")
 
    failedUrlCount = len(failedUrl)
    failedAgain = []
    for i in failedUrl:
        print("队列剩余：", failedUrlCount, "  正在开始下载......")
        failedUrlCount -= 1
 
        try:
            downloadImg(i, imgIndex, imgType, cookie)
            sleep(1.5)
        except Exception as e:
            failedAgain.append(i)
            print("第", failedUrl.index(i) + 1, "个地址出错：", end="")
            print(e, "\n")
 
    print("------- 重 试 全 部 完 成 -------")
    return failedAgain
 
 
# 执行下载与重试
def downloadAndRetry(urlList, imgIndex, imgType, cookie, autoRetry):
    failedUrl = tryDownload(urlList, imgIndex, imgType, cookie)
 
    if len(failedUrl) != 0:
        failedAgain = retry(failedUrl, imgIndex, imgType, cookie)
 
        if len(failedAgain) != 0:
            print("再次出错的地址：", failedAgain, "\n")
 
            if autoRetry is False:
                while len(failedAgain) != 0:
                    r = input("是否继续重试 —— Y（默认），N：").lower()
 
                    if r == "" or r == "y":
                        failedAgain = retry(failedAgain, imgIndex, imgType, cookie)
                    elif r == "n":
                        return False
                    else:
                        print("只能输入 “Y” 或 “N” 或不填，重新输入")
                        continue
 
                return True
 
            else:
                print("--- 最后一次重试请求出错的地址 ---")
                failedAgain = retry(failedAgain, imgIndex, imgType, cookie)
                return failedAgain
 
        else:
            print("没有再次出错的地址", "\n")
            return True
 
    else:
        print("\n")
        return True
 
 
# 重写XML错误地址
def autoRewriteXML(failedUrls, imgType, root):
    if len(failedUrls[imgType]) == 0:
        return
 
    for m in failedUrls[imgType]:
        for imgIndex in m:
            urls: str = ""
            for url in m[imgIndex]:
                urls += url
 
            p = root.find(imgType).find(imgIndex)
            p.text = urls
 
 
# XML自动化
def autoRunXML(cookie):
    xml = ET.parse("urls.xml")
    root = xml.getroot()
 
    failedUrls = {"r18": [], "r16": [], "uncategorized": []}
    for typeNode in root:
        imgType = int(typeNode.attrib["type"])
        imgTypeCN = typeNode.tag
 
        for indexNode in typeNode:
            text = indexNode.text.strip()
 
            if text is not None and text != "":
                urlList = findall("http[s]?://www.pixiv.net/artworks/\d+", text)
                imgIndex = int(indexNode.attrib["index"])
                imgIndexCN = indexNode.tag
 
                print("\n--^*_*^----^*_*^----^*_*^--")
                print("正在下载", imgTypeCN, "类", imgIndexCN, "共", len(urlList), "张图片")
 
                failed = downloadAndRetry(urlList, imgIndex, imgType, cookie, True)
 
                if failed is not True:
                    if len(failed) > 0:
                        failedUrls[imgTypeCN].append({imgIndexCN: failed})
 
            # 防止双标签变单标签，需要留一个字符
            indexNode.text = "\n"
 
    print("已将已完成的地址移除\n")
 
    lenR18Failed = len(failedUrls["r18"])
    lenR16Failed = len(failedUrls["r16"])
    lenUncategorizedFailed = len(failedUrls["uncategorized"])
    totalFailed = lenR18Failed + lenR16Failed + lenUncategorizedFailed
 
    if totalFailed == 0:
        print("没有出错的地址")
    else:
        if lenR18Failed != 0:
            print("r18类出错地址：", failedUrls["r18"])
        if lenR16Failed != 0:
            print("r16类出错地址：", failedUrls["r16"])
        if lenUncategorizedFailed != 0:
            print("未分类出错地址：", failedUrls["uncategorized"])
 
        while True:
            autoRewrite = input("是否将错误地址重新写入XML —— Y（默认），N：").lower()
            if autoRewrite == "" or autoRewrite == "y":
                print("\n")
                autoRewriteXML(failedUrls, "r18", root)
                autoRewriteXML(failedUrls, "r16", root)
                autoRewriteXML(failedUrls, "uncategorized", root)
                print("所有错误地址重写完毕")
                break
 
            elif autoRewrite == "n":
                break
 
            else:
                print("只能输入 “Y” 或 “N” 或不填，重新输入")
                continue
 
    xml = ET.ElementTree(root)
    xml.write("urls.xml", encoding="utf-8")
 
    return False
 
 
# 开始接口
def start():
    cookie = getCookie()
    if cookie == "9":
        print("\n")
        return False
 
    openAutoRun = input("是否开启XML自动化爬取功能 —— Y（默认），N：").lower()
    if openAutoRun == "" or openAutoRun == "y":
        f = autoRunXML(cookie)
        return f
 
    elif openAutoRun == "n":
        imgIndex = getImgIndex()
 
        imgType = getImgType()
        if imgType == 8:
            cookie = getCookie()
            imgType = getImgType()
 
        urlList = getUrl()
 
        f = downloadAndRetry(urlList, imgIndex, imgType, cookie, False)
        return f
 
    else:
        print("只能输入 “Y” 或 “N” 或不填，重新输入")
        start()
 
 
if __name__ == '__main__':
    flag = True
    while flag:
        flag = start()
        if not flag:
            print("======= Pixiv 爬 虫 结 束 =======")
 
