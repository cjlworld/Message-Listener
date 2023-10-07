import requests
from bs4 import BeautifulSoup, Tag
import json
from urllib.parse import urlparse
from dingtalkchatbot.chatbot import DingtalkChatbot
import time
import favicon
from datetime import datetime
import chardet
import os

"""
    传入网页的 url 获得网页上部分信息
"""
class UrlUtils:
    """
        返回编码正确的 response, 使用 chardet 主动猜测编码
    """
    @staticmethod
    def get_response_by_url(url: str) -> requests.Response:
        response = requests.get(url)

        raw_text = response.content
        charset = chardet.detect(raw_text)  # {'confidence': 0.99, 'encoding': 'utf-8'}
        encoding = charset['encoding']

        response.encoding = encoding
        return response
    
    """
        根据 url 获得 <title> 元素
    """
    @staticmethod
    def get_title_by_url(url: str) -> str | None:
        response = UrlUtils.get_response_by_url(url)
        # print(response.encoding)
        soup = BeautifulSoup(response.text, "html.parser")
        title_tag = soup.find("title")

        if type(title_tag) is not Tag:
            return None
            
        title = title_tag.string
        return title

    """
        根据 url 获得 <meta name="description" content=""> 元素
    """
    @staticmethod
    def get_description_by_url(url: str) -> str | None:
        response = UrlUtils.get_response_by_url(url)

        soup = BeautifulSoup(response.text, "html.parser")
        description_tag = soup.find("meta", attrs={"name": "description", "content": True})

        if type(description_tag) is not Tag:
            return None
            
        description = description_tag.get("content")
        return str(description)
    
    """
        根据 url 获得 网站 icon 的 url
    """
    @staticmethod
    def get_icon_by_url(url: str) -> str | None:
        icon_list = favicon.get(url)
        if len(icon_list) == 0:
            pic_url = None
        else:
            pic_url = icon_list[0].url
        
        return pic_url


"""
    对钉钉机器人的封装
"""
class DingWebhookBot:
    # 从 config 文件中获取 钉钉机器人 的 配置
    with open("config.json", "r", encoding="utf-8") as f:
        config = json.load(f)

    DING_WEBHOOK = config["DING_WEBHOOK"]
    DING_SECRET = config["DING_SECRET"]

    """
        发送链接信息，填入 链接，其余通过 UrlUtils 自动补全
    """
    @classmethod
    def send_link_to_ding(cls, link: str) -> None:
        dingbot = DingtalkChatbot(webhook=cls.DING_WEBHOOK, secret=cls.DING_SECRET) 

        title = UrlUtils.get_title_by_url(link)
        if title is None:
            title = "No title"

        content = UrlUtils.get_description_by_url(link)
        if content is None:
            content = f"No description / ({link})"

        pic_url = UrlUtils.get_icon_by_url(link)

        print(f"title={title}, text={content}, message_url={link}, pic_url={pic_url}")
        dingbot.send_link(title=title, text=content, message_url=link, pic_url=pic_url)

    """
        发送 markdown 文本
    """
    @classmethod
    def send_markdown_to_ding(cls, title: str, text: str, is_at_all=False) -> None:
        dingbot = DingtalkChatbot(webhook=cls.DING_WEBHOOK, secret=cls.DING_SECRET) 
        dingbot.send_markdown(title=title, text=text, is_at_all=is_at_all)
    
    """
        发送 plain text
    """
    @classmethod 
    def send_text_to_ding(cls, msg: str) -> None:
        dingbot = DingtalkChatbot(webhook=cls.DING_WEBHOOK, secret=cls.DING_SECRET) 
        dingbot.send_text(msg=msg)


"""
    解析 url 对应网站中 出现的链接，并根据主域名进行链接补全
    返回补全后的链接组成的列表
"""
def parse_links(url: str) -> list[str]:
    IGNORE_LINKS = ['javascript:void(0)', 'javascript:void(0);']

    response = UrlUtils.get_response_by_url(url)

    soup = BeautifulSoup(response.text.encode('utf-8'), "html.parser")

    parsed_url = urlparse(url)
    # 传输协议 parsed_url.scheme
    # 域名 parsed_url.hostname

    results: list[str] = []
    for link_tag in soup.find_all("a", attrs={"href": True}):
        link = link_tag.get("href")

        # 无视一些链接
        if link in IGNORE_LINKS:
            continue

        # 补全 传输协议 和 域名
        if link[0] == '/':
            link = "{:s}://{:s}{:s}".format(parsed_url.scheme, parsed_url.hostname, link)

        results.append(link)

    return results


if __name__ == "__main__":
    print(datetime.now())

    # 初始化 data.json
    if not os.path.exists("data.json"):
        with open("data.json", "w") as f:
            json.dump({}, f, indent=4)

    with open("data.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    
    """
    {
        "https://example.com/": [
            "url1",
            ...
        ]
    }
    """

    # 获取需要监听的网站列表
    with open("config.json", "r", encoding="utf-8") as f:
        urls = json.load(f)["urls"]

    try:
        for url in urls:
            # 一个新的链接
            if data.get(url) is None:
                data[url] = []

            results = parse_links(url)
            for link in results:
                if link not in data[url]:
                    DingWebhookBot.send_link_to_ding(link)
                    data[url].append(link)
                    # 为了避免限流 (最多 20条/min), sleep 10s
                    time.sleep(10)
    finally:
        with open("data.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

        print("--------------------END----------------------\n")
        DingWebhookBot.send_text_to_ding(msg="今日网页订阅推送完毕, 请查收")
