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
    # p = re.compile("Your number is <b>(\d+)</b>")
    # m = p.search("xxx Your number is <b>123</b>")
    # print(m.groups()[0])
    # url = re.search(r'(https?://\S+)', text.split('|')[0]).group(0)

    url = "https://search.naver.com/search.naver?where=nexearch&sm=tab_etc&query=%EC%A0%84%EA%B5%AD%EB%AF%B8%EC%84%B8%EB%A8%BC%EC%A7%80"
    req = urllib.request.Request(url)

    sourcecode = urllib.request.urlopen(url).read()
    soup = BeautifulSoup(sourcecode, "html.parser")

    # area_list = []
    keywords = []
    dust_dict = {}
    tr_list = soup.find("div", class_="tb_scroll").find("tbody").find_all("tr")

    for tr in tr_list:
        location = tr.find("th").get_text()
        value = int(tr.find("span").get_text())
        states_morning = []
        states_evening = []
        cnt = 0
        for state in tr.find_all("span", class_=(["lv1", "lv2", "lv3", "lv4", "lv5"])):
            if cnt == 0:
                states_morning.append(state.get_text())
                cnt += 1
            else:
                states_evening.append(state.get_text())
        dust_dict = {location: (value, states_morning, states_evening)}
        keywords.append("{0}지역 미세먼지 수치: {1}, 오전예보: {2} 오후예보: {3}".format(location, value, states_morning, states_evening))
    # .replace('[', '').replace(']', '')
    # music = []
    # music.append("Bugs 실시간 음악 차트 Top 10")
    # music.append("")
    # for i in range(0, 10):
    #     music.append("{0}위: {1} / {2}".format(i+1, titleList[i], artistList[i]))

    return u'\n'.join(keywords)


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
    app.run('127.0.0.1', port=5000)
