# import pyimgur
# CLIENT_ID = "Your_applications_client_id"
# im = pyimgur.Imgur(CLIENT_ID)
# image = im.get_image('S1jmapR')
# print(image.title) # Cat Ying & Yang
# print(image.link) # http://imgur.com/S1jmapR.jpg

import base64


import os
import pandas as pd
from datetime import datetime

TIMESTAMP = datetime.now().strftime('%Y-%m-%d')
SAVE_ROOT = os.path.join('data')

SAVE_PATH = os.path.join(SAVE_ROOT, TIMESTAMP)
df = pd.read_csv(os.path.join(SAVE_PATH, TIMESTAMP + '_tag_count.csv'))
tag_name_list = df['tag'].head(1).tolist()
for tage_name in tag_name_list:
    image_name = tage_name.strip('').replace('/', '-').replace('\\', '-') + ".png"
    # 讀取本地圖像文件
    with open(os.path.join(SAVE_PATH, image_name), "rb") as image_file:
        image_data = image_file.read()

    # 將圖像數據進行Base64編碼
    image_base64 = base64.b64encode(image_data).decode()
    print(image_base64)

print(tag_name_list)


# # 構建ImageSendMessage對象
# message = ImageSendMessage(
#     original_content_url='data:image/png;base64,' + image_base64,
#     preview_image_url='data:image/png;base64,' + image_base64
# )