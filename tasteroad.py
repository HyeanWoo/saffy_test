# -*- coding: utf-8 -*-
import json
import os
import re
import urllib.request
import multiprocessing as mp
from threading import Thread

from bs4 import BeautifulSoup
from slackclient import SlackClient
from flask import Flask, request, make_response, render_template
from urllib import parse

app = Flask(__name__)

slack_token = "xoxb-508557942135-508907309590-g4hFdp5TDzEnpGsev1uuoKr1"
slack_client_id = "508557942135.507705827765"
slack_client_secret = "b284ae5ad42ebf24af0a2e75739336ee"
slack_verification = "FaGZ4w6h2cvHOxb62Lz9im6y"
sc = SlackClient(slack_token)

def processing_event(queue):
   while True:
       # 큐가 비어있지 않은 경우 로직 실행
       if not queue.empty():
           slack_event = queue.get()

           # Your Processing Code Block gose to here
           channel = slack_event["event"]["channel"]
           text = slack_event["event"]["text"]

           # 챗봇 크롤링 프로세스 로직 함수
           keywords = processing_function(text)

           # 아래에 슬랙 클라이언트 api를 호출하세요
           sc.api_call(
               "chat.postMessage",
               channel=channel,
               text=keywords
           )

# 크롤링 함수 구현하기
def processing_function(text):

    # korean = []
    # text = text[13:]
    # for i in range(0, len(text.split())):
    #     parse_url = parse.urlparse("https://www.diningcode.com/list.php?query={0}".format(text.split()[i]))
    #     query = parse.parse_qs(parse_url.query)
    #     korean.append(parse.urlencode(query, doseq=True).split('=')[1])
    #
    #
    # url = "https://www.diningcode.com/list.php?query={0}+{1}".format(korean[0], korean[1])
    # req = urllib.request.Request(url)
    # sourcecode = urllib.request.urlopen(url).read()
    # soup = BeautifulSoup(sourcecode, "html.parser")
    #
    # list_link = []
    # list_ranking = []
    #
    # title = []
    # category = []
    # ratings = []
    # address = []
    # phoneNum = []
    # menuList = []

    keywords = [':heart:']

    # for links in soup.find_all("li")[5:]:
    #     list_link.append("https://www.diningcode.com" + links.find("a")["href"])
    #     list_ranking.append(links.find("span", class_="btxt").get_text().strip())
    #
    # for i in range(0, len(list_link)):
    #     url = list_link[i]
    #     req = urllib.request.Request(url)
    #     sourcecode = urllib.request.urlopen(url).read()
    #     soup = BeautifulSoup(sourcecode, "html.parser")
    #     for elem in soup.find_all("div", class_="div-cont"):
    #         title.append(elem.find("div", class_="tit-point").get_text().strip())
    #         category.append(elem.find("div", class_="btxt").get_text().strip()[6:])
    #         ratings.append(elem.find("p", class_="grade").get_text().strip()[0:3])
    #         address.append(elem.find("li", class_="locat").get_text().strip())
    #         phoneNum.append(elem.find("li", class_="tel").get_text().strip())
    #         if not elem.find_all("div", class_="menu-info short"):
    #             menuList.append("정보없음")
    #         else:
    #             for j in elem.find_all("div", class_="menu-info short"):
    #                 menuList.append(
    #                     j.get_text().strip().replace('\n', '').replace('\t', '-').replace('더보기', '').replace('원', '원\n')[4:])
    # for i in range(0, len(list_ranking)):
    #     keywords.append(list_ranking[i] + " " + list_link[i])
    #     keywords.append("카테고리: {0}".format(category[i]))
    #     keywords.append("평점: {0}".format(ratings[i]))
    #     keywords.append("주소: {0}".format(address[i]))
    #     keywords.append("전화번호: {0}".format(phoneNum[i]))
    #     keywords.append("주요메뉴: \n{0}".format(menuList[i]))

    return u'\n'.join(keywords)


# 이벤트 핸들하는 함수
def _event_handler(event_type, slack_event):

   if event_type == "app_mention":
       event_queue.put(slack_event)
       return make_response("App mention message has been sent", 200, )


@app.route("/listening", methods=["GET", "POST"])
def hears():
    slack_event = json.loads(request.data)

    if "challenge" in slack_event:
        return make_response(slack_event["challenge"], 200, {"content_type": "application/json"})

    if slack_verification != slack_event.get("token"):
        message = "Invalid Slack verification token: %s" % (slack_event["token"])
        make_response(message, 403, {"X-Slack-No-Retry": 1})

    if "event" in slack_event:
        event_type = slack_event["event"]["type"]
        return _event_handler(event_type, slack_event)

    # If our bot hears things that are not events we've subscribed to,
    # send a quirky but helpful error response
    return make_response("[NO EVENT IN SLACK REQUEST] These are not the droids\
                         you're looking for.", 404, {"X-Slack-No-Retry": 1})


@app.route("/", methods=["GET"])
def index():
    return "<h1>Server is ready.</h1>"


if __name__ == '__main__':
   event_queue = mp.Queue()

   p = Thread(target=processing_event, args=(event_queue,))
   p.start()
   print("subprocess started")

   app.run('127.0.0.1', port=5000)
   p.join()