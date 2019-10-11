import requests
from bs4 import BeautifulSoup
import csv
from fake_useragent import UserAgent
from time import sleep

# 定义请求头
HEADERS = {
    'User-Agent': UserAgent().random,
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
    'Accept-Encoding': 'gzip,deflate,br',
    'Cookie': '',
    'Connection': 'keep-alive',
    'Pragma': 'no-cache',
    'Cache-Control': 'no-cache'
}

# 新建写入的csv
csvfile = open('qunar.csv', 'w', encoding='utf-8', newline='')
writer = csv.writer(csvfile)
# 写入第一行
writer.writerow(["区域", "名称", "景点id", "类型", "级别", "热度", "地址", "特色", "经纬度"])


# 下载景点内容的函数
pageCount = 0
MAX_PAGE_COUNT = 10  # 增加一个最大页数的限制

# 下载页面，如果状态码不为200，等待10s
def download_soup_waitting(url):
    try:
        # verify 传入Charles的根证书，该证书从Keychain中导出，用于抓取https包
        response = requests.get(url, headers=HEADERS, allow_redirects=False, timeout=5, verify='/Users/vinzhou/Documents/CharlesProxyCA.pem')
        if response.status_code == 200:
            html = response.content
            html = html.decode("utf-8")
            soup = BeautifulSoup(html, "html.parser")
            print("下载完成: "+url)
            return soup
        else:
            sleep(10)
            print("等待下载中: "+url)
            return download_soup_waitting(url)
    except:
        return ""


def get_types():
    # 定义热门景点的类型
    types = ["文化古迹", "自然风光", "公园", "古建筑", "寺庙", "遗迹", "古镇", "陵墓陵园", "故居", "宗教"]
    for type in types:
        global pageCount
        pageCount = 0
        # 定义请求的url字符串，%E7%83%AD%E9%97%A8%E6%99%AF%E7%82%B9 为 热门景点 的url encoding值
        url = "https://piao.qunar.com/ticket/list.htm?keyword=%E7%83%AD%E9%97%A8%E6%99%AF%E7%82%B9&from=mpl_search_suggest&subject=" + type + "&page=1"
        get_type(type, url)


def get_type(type, url):
    soup = download_soup_waitting(url)
    if soup == "":
        print("soup is empty")
        return
    search_list = soup.find('div', attrs={'id': 'search-list'})
    sight_items = search_list.findAll('div', attrs={'class': 'sight_item'})
    for sight_item in sight_items:
        name = sight_item['data-sight-name']
        districts = sight_item['data-districts']
        point = sight_item['data-point']
        address = sight_item['data-address']
        data_id = sight_item['data-id']
        level = sight_item.find('span', attrs={'class': 'level'})  # 5A
        if level:
            level = level.text
        else:
            level = ""
        product_star_level = sight_item.find('span', attrs={'class': 'product_star_level'})
        if product_star_level:
            product_star_level = product_star_level.text
        else:
            product_star_level = ""
        intro = sight_item.find('div', attrs={'class': 'intro'})
        if intro:
            intro = intro['title']
        else:
            intro = ""
        writer.writerow(
            [districts.replace("\n", ""), name.replace("\n", ""), data_id.replace("\n", ""), type.replace("\n", ""),
             level.replace("\n", ""), product_star_level.replace("\n", ""), address.replace("\n", ""),
             intro.replace("\n", ""), point.replace("\n", "")])
    # 找到向下翻页的按钮
    next = soup.find('a', attrs={'class': 'next'})
    global pageCount
    if next and pageCount < MAX_PAGE_COUNT:
        pageCount += 1
        next_url = "http://piao.qunar.com" + next['href']
        get_type(type, next_url)


if __name__ == '__main__':
    get_types()
