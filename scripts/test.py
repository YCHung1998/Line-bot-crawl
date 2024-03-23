# D:\Desktop\ych\side_project\geturl\linebot\botcode>ngrok http 5000
# ngrok http 5000

from flask import Flask, request

# # 載入 json 標準函式庫，處理回傳的資料格式
import os
import json
import configparser
# # 載入 LINE Message API 相關函式庫
from linebot import LineBotApi
from linebot.v3 import WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, ImageSendMessage  

app = Flask(__name__)

def get_config():
    config = configparser.ConfigParser()
    config.read('config.ini', encoding='utf-8')
    return config

def get_access_token_and_secret():
    config = get_config()
    access_token = config.get('line-bot', 'channel_access_token')
    secret = config.get('line-bot', 'channel_secret')
    return [access_token, secret]

[access_token, secret] = get_access_token_and_secret()

def reply_img(text):
    # 文字對應圖片網址的字典
    img = {
        '皮卡丘':'https://upload.wikimedia.org/wikipedia/en/a/a6/Pok%C3%A9mon_Pikachu_art.png',
        '傑尼龜':'https://upload.wikimedia.org/wikipedia/en/5/59/Pok%C3%A9mon_Squirtle_art.png'
    }
    if text in img:
        return img[text]
    else:
    # 如果找不到對應的圖片，回傳 False
        return False


@app.route("/", methods=['POST'])
def line_bot():
    body = request.get_data(as_text=True)                    # 取得收到的訊息內容
    try:
        json_data = json.loads(body)                         # json 格式化訊息內容
        messaging_api = LineBotApi(access_token)              # 確認 token 是否正確 明明說要deprecated 了
        # messaging_api = MessagingApi(access_token)              # 確認 token 是否正確 不知道為啥這不行
        handler = WebhookHandler(secret)                     # 確認 secret 是否正確
        signature = request.headers['X-Line-Signature']      # 加入回傳的 headers
        handler.handle(body, signature)                      # 綁定訊息回傳的相關資訊
        tk = json_data['events'][0]['replyToken']            # 取得回傳訊息的 Token
        type_ = json_data['events'][0]['message']['type']     # 取得 LINe 收到的訊息類型
        if type_=='text':
            msg = json_data['events'][0]['message']['text']  # 取得 LINE 收到的文字訊息
            print('msg', msg)                                       # 印出內容
            if msg in ['本日前五熱門類', '數位時代']:
                print("1"*20)
                from runner import main
                print("2"*20)
                main()
                print("3"*20)
                dirs = os.listdir('data')
                print("4"*20)
                reply = '-'.join(dirs)
                pass
            else:
                reply = msg
        else:
            reply = '你傳的不是文字呦～'
        print('reply', reply)
        messaging_api.reply_message(tk,TextSendMessage(reply))# 回傳訊息
    except:
        json_data = json.loads(body)
        print(json_data)
        print('error')
    return 'OK'                                              # 驗證 Webhook 使用，不能省略


if __name__ == "__main__":
    app.run()

