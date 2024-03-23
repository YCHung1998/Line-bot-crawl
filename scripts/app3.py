from flask import Flask, request, abort

from linebot.v3 import (
    WebhookHandler
)
from linebot.v3.exceptions import (
    InvalidSignatureError
)
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage
)
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent
)

from linebot.v3.messaging import ApiException, ErrorResponse
from linebot.models import ImageSendMessage

import os
import pandas as pd
import configparser
from datetime import datetime
from runner_crawl import main
from botcode.linebot_notify.google_drive_module import GoogleDrive



app = Flask(__name__)


def get_config():
    config = configparser.ConfigParser()
    config.read('config.ini', encoding='utf-8')
    return config

def get_google_drive_config():
    config = get_config()
    SERVICE_ACCOUNT = config.get('google-drive', 'drive_bot_secret_key')
    SCOPES = config.get('google-drive', 'scopes')
    PARENT_FOLDER_ID = config.get('google-drive', 'parent_folder_id')
    return [SERVICE_ACCOUNT, SCOPES, PARENT_FOLDER_ID]

def get_access_token_and_secret():
    config = get_config()
    access_token = config.get('line-bot', 'channel_access_token')
    secret = config.get('line-bot', 'channel_secret')
    return [access_token, secret]

# Google Drive Config
[SERVICE_ACCOUNT, SCOPES, PARENT_FOLDER_ID] = get_google_drive_config()


# Line Bot Config
[access_token, secret] = get_access_token_and_secret()
configuration = Configuration(access_token=access_token)
handler = WebhookHandler(secret)



#檢查路由，確認資料是否正確
@app.route('/', methods = ['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        # print("what's wrong to here?????????????????????????")
        # app.logger.info("Invalid signature. Please check your channel access token/channel secret.")
        # print("what's wrong to here\n\n\n\n???")
        abort(400)

    return 'OK'

message_kv = {"@傳送類別排序和文章數": "@傳送類別排序和文章數", 
                "@數位時代五日內熱搜類別": "@數位時代五日內熱搜類別", 
                "@傳送圖片": "@傳送圖片", 
                "@回傳我的Uid": "@回傳我的Uid", 
                "@keyword": "@keyword",

                }


#回傳
@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        message = TextMessage(text = ":)")
        TIMESTAMP = datetime.now().strftime('%Y-%m-%d')
        if event.message.text == "@傳送類別排序和文章數":
            # load the local dataset
            SAVE_ROOT = os.path.join('data')
            SAVE_PATH = os.path.join(SAVE_ROOT, TIMESTAMP)
            df = pd.read_csv(os.path.join(SAVE_PATH, TIMESTAMP + '_tag_count.csv'))
            text_list = [f"{row[1]:>3d}則 -> {row[0]:<12s}\t\t\n" for _, row in df.iterrows()]
            text = ''.join(text_list)
            messages = [TextMessage(text = text)]

        elif event.message.text == "@數位時代五日內熱搜類別":
            # message = TextMessage(text = "正在爬取熱搜類別...(30 sec 後跳通知)")
            # main()
            messages = [TextMessage(text = "已爬取完畢，請輸入 @傳送類別排序和文章數")]

        # elif event.message.text == "@傳送圖片":

        #     SAVE_ROOT = os.path.join('data')
        #     SAVE_PATH = os.path.join(SAVE_ROOT, TIMESTAMP)
        #     df = pd.read_csv(os.path.join(SAVE_PATH, TIMESTAMP + '_tag_count.csv'))
        #     # google_drive = GoogleDrive(SERVICE_ACCOUNT,
        #     #                             SCOPES,
        #     #                             PARENT_FOLDER_ID, 
        #     #                             folder_name=TIMESTAMP)
        #     # print("handle_message -------------------0")
        #     # google_drive.get_service()
        #     # fh = google_drive.download_file(file_id="1IUh2JIHaaVofKx6h797NQjQmABColYeK")
        #     # print("handle_message -------------------1")
        #     # print(fh)
        #     import base64
        #     # # print("handle_message -------------------2")
        #     SAVE_PATH = os.path.join(SAVE_ROOT, TIMESTAMP)
        #     df = pd.read_csv(os.path.join(SAVE_PATH, TIMESTAMP + '_tag_count.csv'))
        #     tag_name_list = df['tag'].head(1).tolist()
        #     for tage_name in tag_name_list:
        #         image_name = tage_name.strip('').replace('/', '-').replace('\\', '-') + ".png"
        #         # 讀取本地圖像文件
        #         with open(os.path.join(SAVE_PATH, image_name), "rb") as image_file:
        #             image_data = image_file.read()

        #         # 將圖像數據進行Base64編碼
        #         image_base64 = base64.b64encode(image_data).decode()


        #     text_message = TextMessage(text=f"回傳 {image_name} ")

            # image_message = ImageSendMessage(
            #     original_content_url='data:image/jpeg;base64,' + image_base64,
            #     preview_image_url='data:image/jpeg;base64,' + image_base64
            #     )
            # message_image = ImageSendMessage(
            #     original_content_url='https://example.com/image.jpg',
            #     preview_image_url='https://example.com/image.jpg'
            # ) 

            # 將消息內容分別封裝成字典
            # text_message_dict = {
            #     'type': 'text',
            #     'message': text_message.dict()
            # }
            # image_message_dict = {
            #     'type': 'image',
            #     'original_content_url': image_message.original_content_url,
            #     'preview_image_url': image_message.preview_image_url
            # }

            # messages = [text_message_dict, image_message_dict]
            # messages = [text_message, text_message]

        elif event.message.text == "@回傳我的Uid":
            messages = [TextMessage( text=event.source.user_id)]

        elif event.message.text == "@keyword":
            messages = [TextMessage( text= "@傳送類別排序和文章數\n@數位時代五日內熱搜類別\n@回傳我的Uid")]
        else:
            messages = None

    if messages:
        line_bot_api.reply_message_with_http_info(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=messages
            )
        )
    else:
        pass
        # print("不給予任何回應")



if __name__ == '__main__':
    app.run()
    # TIMESTAMP = datetime.now().strftime('%Y-%m-%d')
    # SAVE_ROOT = os.path.join('data')

    # SAVE_PATH = os.path.join(SAVE_ROOT, TIMESTAMP)
    # df = pd.read_csv(os.path.join(SAVE_PATH, TIMESTAMP + '_tag_count.csv'))
    # tag_name_list = df['tag'].head(3).tolist()
    # for tage_name in tag_name_list:
    #     image_name = {tage_name.strip('').replace('/', '-').replace('\\', '-')} + "".png"

    # print(tag_name_list)