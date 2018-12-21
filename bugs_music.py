# -*- coding: utf-8 -*-
import json
import os
import re
import urllib.request

from bs4 import BeautifulSoup
from slackclient import SlackClient
from flask import Flask, request, make_response, render_template

app = Flask(__name__)

slack_token = "xoxb-508557942135-508907309590-g4hFdp5TDzEnpGsev1uuoKr1"
slack_client_id = "508557942135.507705827765"
slack_client_secret = "b284ae5ad42ebf24af0a2e75739336ee"
slack_verification = "FaGZ4w6h2cvHOxb62Lz9im6y"
sc = SlackClient(slack_token)


# 크롤링 함수 구현하기
def _crawl_naver_keywords(text):
    # url = re.search(r'(https?://\S+)', text.split('|')[0]).group(0)
    url = "https://music.bugs.co.kr/chart"
    req = urllib.request.Request(url)

    sourcecode = urllib.request.urlopen(url).read()
    soup = BeautifulSoup(sourcecode, "html.parser")

    titleList = []
    artistList = []

    for data in (soup.find_all("p", class_=("title"))):
        if not data.get_text() in titleList:
            if len(titleList) >= 10:
                break
            titleList.append(data.get_text().strip())

    for data in (soup.find_all("p", class_=("artist"))):
        if not data.get_text() in artistList:
            if len(artistList) >= 10:
                break
            artistList.append(data.get_text().strip())

    music = []
    for i in music:
        music.append("{0}위: {1} / {2}".format(i+1, titleList[i], artistList[i]))
    # 한글 지원을 위해 앞에 unicode u를 붙혀준다.
    return u'\n'.join(music)


# 이벤트 핸들하는 함수
def _event_handler(event_type, slack_event):
    print(slack_event["event"])

    if event_type == "app_mention":
        channel = slack_event["event"]["channel"]
        text = slack_event["event"]["text"]

        keywords = _crawl_naver_keywords(text)
        sc.api_call(
            "chat.postMessage",
            channel=channel,
            text=keywords
        )

        return make_response("App mention message has been sent", 200, )

    # ============= Event Type Not Found! ============= #
    # If the event_type does not have a handler
    message = "You have not added an event handler for the %s" % event_type
    # Return a helpful error message
    return make_response(message, 200, {"X-Slack-No-Retry": 1})


@app.route("/listening", methods=["GET", "POST"])
def hears():
    slack_event = json.loads(request.data)

    if "challenge" in slack_event:
        return make_response(slack_event["challenge"], 200, {"content_type":
                                                                 "application/json"
                                                             })

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
    app.run('0.0.0.0', port=8080)
