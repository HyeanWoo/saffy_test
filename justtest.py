# 쓰레드, 큐를 위한 라이브러리 추가

import multiprocessing as mp
from threading import Thread

from bs4 import BeautifulSoup
from slackclient import SlackClient
from flask import Flask, request, make_response, render_template

app = Flask(__name__)

# slack_token = "xoxb-"
# slack_client_id = ""
# slack_client_secret = ""
# slack_verification = ""
slack_token = "xoxb-508557942135-508907309590-g4hFdp5TDzEnpGsev1uuoKr1"
slack_client_id = "508557942135.507705827765"
slack_client_secret = "b284ae5ad42ebf24af0a2e75739336ee"
slack_verification = "FaGZ4w6h2cvHOxb62Lz9im6y"
sc = SlackClient(slack_token)



# threading function
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


# 크롤링 함수
def processing_function(text):
   # 함수를 구현해 주세요
   keywords = "성공!!~"

   # delay test...

   return keywords


# 이벤트 핸들하는 함수
def _event_handler(event_type, slack_event):

   if event_type == "app_mention":
       event_queue.put(slack_event)
       return make_response("App mention message has been sent", 200, )


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
   event_queue = mp.Queue()

   p = Thread(target=processing_event, args=(event_queue,))
   p.start()
   print("subprocess started")

   app.run('127.0.0.1', port=5000)
   p.join()