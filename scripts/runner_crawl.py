# 匯入必要的函式庫
import os
import requests
import configparser
import pandas as pd
from botcode.linebot_notify.Bnext_notify import Bnext_Notify
from datetime import datetime

def get_config():
    config = configparser.ConfigParser()
    config.read('config.ini', encoding='utf-8')
    return config

def get_access_token_and_secret():
    config = get_config()
    access_token = config.get('line-bot', 'channel_access_token')
    secret = config.get('line-bot', 'channel_secret')
    line_notify_token = config.get('line-bot', 'line_notify_token')
    return [access_token, secret, line_notify_token]

[access_token, secret, line_notify_token] = get_access_token_and_secret()
# 定義 LINE Bot Notify 存取權杖和目標使用者或群組 ID
ACCESS_TOKEN = line_notify_token # "您的 LINE Bot Notify 存取權杖"
TARGET_ID = "U2f47f6dc319c756794ad75227a2ad33c" # "您的目標使用者或群組 ID"  My uid



# 發送訊息至 LINE Bot Notify
def send_message_to_linebot_notify(image_bytes):
    url = "https://notify-api.line.me/api/notify"
    headers = {"Authorization": "Bearer " + ACCESS_TOKEN}
    files = {"imageFile": image_bytes}
    message = {"message": "您的文字雲影像"}
    requests.post(url, headers=headers, files=files, data=message)

# 主程式
def main():
    SAVE_ROOT = 'data'
    TIMESTAMP = datetime.now().strftime('%Y-%m-%d')
    SAVE_PATH = os.path.join(SAVE_ROOT, TIMESTAMP)
    os.makedirs(SAVE_PATH, exist_ok=True)
    PAGE = 5 # default 5 and max is 20 (以後讀不出來) 
    bnext_notify = Bnext_Notify(filepath=SAVE_PATH, filename=TIMESTAMP)

    if os.path.exists(os.path.join(SAVE_PATH, TIMESTAMP + '_tag_count.csv')):
        print("The data has been updated today.")
        #  Line bot message api 直接觸發此程式生成圖像 更甚至以生成好 調用特定資料夾圖像
        # load data
        df = pd.read_csv(os.path.join(SAVE_PATH, TIMESTAMP + '.csv')) # crawl data
        tag_cnt_df = pd.read_csv(os.path.join(SAVE_PATH, TIMESTAMP + '_tag_count.csv')) # analysis data
        bnext_notify.reset_df(df) # if data has been loaded just update the df and analysis data
    else:
        print("The data has not been updated today.")
        #  自動化排成當我做 每日早7.30 以及 19:30 更新分析資料
        df = bnext_notify.update_data(page=PAGE)
        tag_cnt_df = bnext_notify.analyze_data()
        tag_cnt_df.to_csv(os.path.join(SAVE_PATH, TIMESTAMP + '_tag_count.csv'), index=False, encoding='utf-8')
    
        print("Start to create word cloud images.")
        tag_cnt_df = bnext_notify.analyze_data()
        # print(tag_cnt_df)
        tag = tag_cnt_df['tag'].head(5)
        for tag_item in tag:
            print("Create word cloud for", tag_item)
            wordcloud = bnext_notify.generate_word_cloud(tag_item)
            filename = tag_item.strip('').replace('/', '-').replace('\\', '-')
            wordcloud.to_file(os.path.join(SAVE_PATH, filename + '.png'))
            print('Save the word cloud image to', filename + '.png')


# 執行主程式
if __name__ == "__main__":
    main()