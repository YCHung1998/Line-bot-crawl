# D:\Desktop\ych\side_project\geturl\linebot\botcode>ngrok http 5000
# ngrok http 5000
import os
import jieba
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt

from io import BytesIO
from sklearn.feature_extraction.text import TfidfVectorizer
from wordcloud import WordCloud
from datetime import datetime

# script use
from .Bnext_module import Bnext_news
# test at this file use
# from Bnext_module import Bnext_news

class Bnext_Notify():
    def __init__(self, filepath, filename):
        self.bnext = Bnext_news()
        self.filepath = filepath
        os.makedirs(filepath, exist_ok=True)
        self.filename = filename
        self.save_path = os.path.join(filepath, filename)

    def update_data(self, page):
        self.bnext.update_url()
        for i in range(1, page+1):
            print(f"==========Page {i}==========")
            self.bnext.get_data()
            self.bnext.next_page(i)
        if 'csv' not in self.filename or 'xlsx' not in self.filename:
            self.bnext.save_to_csv(os.path.join(self.filepath, self.filename + '.csv'))
        else:
            self.bnext.save_to_csv(os.path.join(self.filepath, self.filename))
        self.df = self.bnext.get_df()
        return self.df

    def save_to_csv(self, filename="bnext-news.csv"):
        if ".csv" in filename:
            self.bnext.save_to_csv(filename)
        self.bnext.save_to_csv(filename + ".csv")

    def analyze_data(self):
        # 依照文章類別分析文章數量
        self.df['count'] = 1
        self.tag_cnt = self.df.groupby(['tag'])['count'].count().reset_index().sort_values('count', ascending=False)
        self.tag_cnt.reset_index(drop=True, inplace=True)
        self.tag_cnt

        # self.time_cnt = self.df.groupby(['time'])['count'].count().reset_index().sort_values('time', ascending=True)
        # self.time_cnt.reset_index(drop=True, inplace=True)
        return self.tag_cnt

    def generate_treemap(self):
        # 繪製 Treemap 圖表
        self.treemap = px.treemap(self.tag_cnt, path=['tag'], values='count')
        self.treemap.update_traces(textfont=dict(size=36, family='Arial'))  # 調整字體大小和字體樣式
        self.treemap.update_traces(textfont=dict(size=36, family='Arial', color='black', colorsrc='count'),
                        textposition='middle center',
                        hoverinfo='label+percent entry',
                        hovertemplate='<b>%{label}:</b> %{value}',
                        marker=dict(colorscale='Blues_r')) # 或者是 'Blues_r' 以獲得較暗的色調
        # 顯示圖表
        # self.treemap.show()
        print((self.save_path+'.png'))
        self.treemap.write_image((self.save_path+'.png'), width=1000, height=1000, scale=2)
        # self.save_ByteIO_image(self.treemap, file=self.save_path)

    def chinese_word_segmentation(self, text):
        seg_list = jieba.cut(text)
        return " ".join(seg_list)

    def generate_word_cloud(self, topic, colormap='plasma'):
        # Define your list of Chinese stopwords
        self.stopwords = set(['的', '了', '和', '是', '在', '我', '有', '不',
                '人', '都', '一', '上', '也', '很', '到', '他', '年', '而',
                '能', '會', '這個', '個', '我們', '好', '以', '但', '又', '要', 
                '用', '她', '這', '也', '到', 
                '等', '從', '自己', '可以', '被', '什麼', '哪些', '還有', '為何', '可能性'])
        # 根據tag選擇相關的文本
        selected_topics = self.df[self.df['tag'] == topic]['topic'].tolist()
        text = ' '.join(selected_topics)
        
        # 中文分詞
        text = self.chinese_word_segmentation(text)
        text_without_stopwords = ' '.join(word for word in text.split() if word not in self.stopwords)

        # 使用TF-IDF計算詞頻
        tfidf_vectorizer = TfidfVectorizer()
        tfidf_matrix = tfidf_vectorizer.fit_transform([text_without_stopwords])
        feature_names = tfidf_vectorizer.get_feature_names_out()

        # 將TF-IDF結果轉換為字典
        tfidf_dict = {}
        for i, feature in enumerate(feature_names):
            tfidf_dict[feature] = tfidf_matrix[0, i]
        # 生成文字雲
        wordcloud = WordCloud(background_color='black',
                # font_path='/usr/share/fonts/wqy/wqy-zenhei.ttc',
                    font_path = './linebot_notify/font/Noto_Sans_TC/static/NotoSansTC-Black.ttf', # '肥肥粗體'
                    colormap=colormap)
        wordcloud = wordcloud.generate_from_frequencies(tfidf_dict)
        return wordcloud

    def save_treemap(self, filename="bnext-treemap.png"):
        self.treemap.write_image(filename, width=1000, height=1000, scale=2)

    def reset_df(self, df=None):
        self.df = df

    def load_csv(self, filename):
        self.df = pd.read_csv(filename)

    def send_message_to_linebot_notify(self):
        pass

if __name__ == "__main__":
    SAVE_ROOT = os.path.join('..', 'data')
    TIMESTAMP = datetime.now().strftime('%Y-%m-%d')
    # TIMESTAMP = '2024-03-20'
    SAVE_PATH = os.path.join(SAVE_ROOT, TIMESTAMP)
    os.makedirs(SAVE_PATH, exist_ok=True)

    PAGE = 5 # default 5 and max is 20 (以後讀不出來) 
    bnext_notify = Bnext_Notify(filepath=SAVE_PATH, filename=TIMESTAMP)

    if True:
        #  自動化排成當我做 每日早7.30 以及 19:30 更新分析資料 
        df = bnext_notify.update_data(page=PAGE)
        tag_cnt_df = bnext_notify.analyze_data()
        tag_cnt_df.to_csv(os.path.join(SAVE_PATH, TIMESTAMP + '_tag_count.csv'), index=False, encoding='utf-8')
    else:
        #  Line bot message api 直接觸發此程式生成圖像 更甚至以生成好 調用特定資料夾圖像
        # load data
        df = pd.read_csv(os.path.join(SAVE_PATH, TIMESTAMP + '.csv')) # craawl data
        tag_cnt_df = pd.read_csv(os.path.join(SAVE_PATH, TIMESTAMP + '_tag_count.csv')) # analysis data
        bnext_notify.reset_df(df) # if data has been loaded just update the df and analysis data
    
    tag_cnt_df = bnext_notify.analyze_data()
    # print(tag_cnt_df)
    tag = tag_cnt_df['tag'].head(5)
    for tag_item in tag:
        print("Create word cloud for", tag_item)
        wordcloud = bnext_notify.generate_word_cloud(tag_item)
        filename = tag_item.strip('').replace('/', '-').replace('\\', '-')
        wordcloud.to_file(os.path.join(SAVE_PATH, filename + '.png'))
        print('Save the word cloud image to', filename + '.png')




