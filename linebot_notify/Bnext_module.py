import time
import bs4
import requests
import pandas as pd

def timer(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        print(f"Function '{func.__name__}' executed in {execution_time:.4f} seconds.")
        return result
    return wrapper



class Bnext():
    def __init__(self):
        self.url_set = {
                "熱門":"https://www.bnext.com.tw/ranking",
                "首頁": "https://www.bnext.com.tw/",
                "專題": "https://www.bnext.com.tw/topics",
                "活動": "https://www.bnext.com.tw/events",
                "新聞": "https://www.bnext.com.tw/articles",
                }
        self.url = "https://www.bnext.com.tw/"
        self.header = {
            'Referer': "https://www.bnext.com.tw/",
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        }
    def get_url(self):
        return self.url
    
    def update_url(self, url=None):
        if url: self.url = url
        self.response = requests.get(self.url, headers=self.header)
        self.content = bs4.BeautifulSoup(self.response.text, "html.parser")
        
    def reset_list(self):
        return None
    
    def get_data(self):
        return None
    
    def save_to_excel(self, file_name):
        dataframe_format = {'k': 'v',
                            'k2': 'v2'}
        df = pd.DataFrame(dataframe_format)
        df.to_excel(file_name, index=False, encoding='utf-8')
        return None
    
    def save_to_csv(self, file_name):
        dataframe_format = {'k': 'v',
                            'k2': 'v2'}
        df = pd.DataFrame(dataframe_format)
        df.to_csv(file_name, index=False, encoding='utf-8')
        return None


class Bnext_topics(Bnext):

    def __init__(self):
        super().__init__()
        self.url = self.url_set["專題"]
        self.header = {
            'Referer': "https://www.bnext.com.tw/",
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        }
        self.topic_list= []
        self.content_list = []
        self.link_list = []

    @timer
    def get_data(self):
        big_title = self.content.find_all("div", class_="grid grid-cols-1 gap-4 relative bg-slate-50 border")
        for index, bt in enumerate(big_title, 1):
            # get the title, text and link
            title = bt.find("div", class_="flex flex-col items-center gap-1").text
            text = bt.find("div", class_="text-xs text-justify font-light text-gray-200 two-line-text tracking-wide")
            link  = bt.find("a", class_="absolute inset-0")['href']
            # tiltle and text cleaning
            title = title.replace(' ', '').replace('\n', '') if title else ''
            text = text.string.replace(' ', '').replace('\n', '') if text else ''

            if title:
                self.topic_list.append(title)
                self.content_list.append(text)
                self.link_list.append(link)

    def save_to_excel(self, file_name):
        dataframe_format = {'topic': self.topic_list,
                'content': self.content_list,
                'link': self.link_list}
        df = pd.DataFrame(dataframe_format)
        df.to_excel(file_name, index=False, encoding='utf-8')

    def save_to_csv(self, file_name):
        dataframe_format = {'topic': self.topic_list,
                'content': self.content_list,
                'link': self.link_list}
        df = pd.DataFrame(dataframe_format)
        df.to_csv(file_name, index=False, encoding='utf-8')

    def reset_list(self):
        self.topic_list= []
        self.content_list = []
        self.link_list = []


class Bnext_news(Bnext):

    def __init__(self):
        super().__init__()
        self.url = self.url_set["新聞"]
        self.url_format = lambda i: f"{self.url_set['新聞']}?page={i}"
        self.header = {
            'Referer': "https://www.bnext.com.tw/",
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        }
        self.topic_list= []
        self.link_list = []
        self.tag_list = []
        self.time_list = []

    @timer
    def get_data(self):
        block_list = self.content.find_all("div", {"data-dl": "gtm",
                                            "data-dl_block": "article_list",
                                            "data-dl_item": "article", 
                                            "data-dl_icon": "content",
                                            "data-dl_text": "文章"})
        for index, blk in enumerate(block_list, 1):
            # get the title, text and link
            try:
                title = blk.find("h2", class_="three-line-text text-lg").text
                link = blk.find("a", class_="absolute inset-0")['href']
                tag = blk.find("a", class_="text-primary").text
                time_unit =  ["分前", "小時前", "天前", "星期前", "月前"]
                # 資料會到4星期前
                # 容易在這邊有問題
                time_span = blk.find("span", string=lambda text: any([unit in text  for unit in time_unit])).string
                if title:
                    self.topic_list.append(title)
                    self.link_list.append(link)
                    self.tag_list.append(tag)
                    self.time_list.append(time_span)
                    
                # print(title, link, tag, time_span, sep='\n')
            except :
                print('Go to except, 因為此網頁結構後面是收集連結的部分，所以會出現錯誤訊息，但不影響結果。')
                break
                

    def get_df(self):
        return self.df

    def save_to_excel(self, file_name):
        self.dataframe_format = {'topic': self.topic_list,
                                'tag': self.tag_list,
                                'time': self.time_list,
                                'link': self.link_list}
        self.df = pd.DataFrame(self.dataframe_format)
        self.df.to_excel(file_name, index=False, encoding='utf-8')

    def save_to_csv(self, file_name):
        self.dataframe_format = {'topic': self.topic_list,
                                'tag': self.tag_list,
                                'time': self.time_list,
                                'link': self.link_list}
        self.df = pd.DataFrame(self.dataframe_format)
        print("\nSave the data to csv file.\n")
        self.df.to_csv(file_name, index=False, encoding='utf-8')

    def reset_list(self):
        self.topic_list= []
        self.tag_list = []
        self.time_list = []
        self.link_list = []

    def next_page(self, i):
        self.url = self.url_format(i)
        self.response = requests.get(self.url, headers=self.header)
        self.content = bs4.BeautifulSoup(self.response.text, "html.parser")
        return self.url

if __name__ == "__main__":
    # run the code here to test the module for Bnext_topics

    # bnext = Bnext_topics()
    # bnext.update_url()
    # bnext.get_data()
    # bnext.save_to_csv("bnext-topics.csv")

    # run the code here to test the module for Bnext_news
    bnext = Bnext_news()
    bnext.update_url()
    for i in range(1, 21):
        print(f"==========Page {i}==========")
        bnext.get_data()
        bnext.next_page(i)

        if i % 10 == 0:
            bnext.save_to_csv(f"bnext-news-{i}.csv")
            bnext.reset_list()