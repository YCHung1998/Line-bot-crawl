import io
import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import  MediaFileUpload, MediaIoBaseUpload, MediaIoBaseDownload
from datetime import datetime

import configparser

def get_config():
    config = configparser.ConfigParser()
    config.read('config.ini', encoding='utf-8')
    return config

cfg = get_config()
SCOPES = [cfg.get('google-drive', 'scopes')]

# SCOPES = ["https://www.googleapis.com/auth/drive"]
SERVICE_ACCOUNT = "google_auth.json" # doenload form google api service account secret key

# https://drive.google.com/drive/folders/1W2tktT7pAsRghoix_EAW-8Vzzel7J_oN
# folder recognize code : 1W2tktT7pAsRghoix_EAW-8Vzzel7J_oN
# PARENT_FOLDER_ID = "1W2tktT7pAsRghoix_EAW-8Vzzel7J_oN"
PARENT_FOLDER_ID = "1W2tktT7pAsRghoix_EAW-8Vzzel7J_oN" # 父資料夾

# 需要再主動新建資料夾 FOLDER_ID
LOCAL_FOLDER = r"D:\Desktop\ych\side_project\geturl\linebot\botcode\data"
TIMESTAMP = datetime.now().strftime('%Y-%m-%d')


class GoogleDrive():
    def __init__(self, SERVICE_ACCOUNT, scopes, parent_folder_id, folder_name):  
        self.SERVICE_ACCOUNT = SERVICE_ACCOUNT
        self.scopes = scopes
        self.parent_folder_id = parent_folder_id

        # create folder or get exist folder id
        self.folder_name = folder_name
        self.folder_id = None

    # 連上伺服器
    def get_service(self):
        self.creds = service_account.Credentials.from_service_account_file(
            self.SERVICE_ACCOUNT, scopes=self.scopes)
        self.service = build('drive', 'v3', credentials=self.creds)
        return self.service
    
    # 列舉雲端資料夾 (連上的)
    def list_folder(self):
        query = f"name='{self.folder_name}'"
        if self.parent_folder_id:
            query += f" and '{self.parent_folder_id}' in parents"

        response = self.service.files().list(q=query, fields='files(id, name)').execute()
                                                        # fields='files(id, name, createdTime)' 回傳項目
        self.existing_folders = response.get('files', [])
        return self.existing_folders

    def get_folder_id(self):
        if not self.existing_folders:
            print(f'資料夾 "{self.folder_name}" 不存在，創建資料夾中...')
            self.create_folder()
        else:
            print(f'資料夾 "{self.folder_name}" 已存在，無需重複創建')
            self.folder_id = self.existing_folders[0]['id']
        return self.folder_id


    def create_folder(self):
        self.file_metadata = {
            'name': self.folder_name,
            'mimeType': 'application/vnd.google-apps.folder'
        }

        if self.parent_folder_id:
            self.file_metadata['parents'] = [self.parent_folder_id]
        
        file = self.service.files().create(body=self.file_metadata, fields='id').execute()
        self.folder_id = file.get('id')
        print(f'資料夾 "{self.folder_name}" 已創建成功\n\
資料夾id "{file.get("id")}". ')
        return self.folder_id

    def upload_to_drive(self, file_path, filename, folder_id):
        file = {
            "name" : filename,
            "parents" : [folder_id]
        }
        if filename.split('.')[-1] in ['png', 'jpeg', 'jpg']:
            # upload the image file
            file['mimeType'] = 'image/png'
            media = MediaFileUpload(file_path)

        elif filename.split('.')[-1] in ['csv', 'xslx', 'xls']:
            # upload the csv file
            file['mimeType'] = 'text/csv'
            media = MediaFileUpload(file_path, mimetype='text/csv')

        print(f'正在上傳 "{file}" 檔案...')
        # body:檔案資料, media_body:上傳檔物件, 執行
        file_id = self.service.files().create(
            body=file, media_body=media).execute()
        print('雲端檔案ID:' + str(file_id['id']))
        return file_id['id']
    
    def delete_folder(self, folder_id=None):
        if not folder_id:
            raise ValueError("請提供資料夾ID 避免誤刪資料")
        elif folder_id == self.parent_folder_id:
            raise ValueError("無法刪除父資料夾")
        
        try:
            self.service.files().delete(fileId=folder_id).execute()
            print(f'資料夾 "{self.folder_name}" 已刪除')
        except Exception as e:
            print(f'資料夾id "{folder_id}" 不存在 或 有誤\n {e}')

    def download_file(self, file_id):
        print("download_file -------------------1")
        request = self.service.files().get_media(fileId=file_id)
        print("download_file -------------------2")
        fh = io.BytesIO()
        print("download_file -------------------3")
        downloader = MediaIoBaseDownload(fh, request)
        print("download_file -------------------4")
        done = False
        while not done:
            status, done = downloader.next_chunk()
        print("download_file -------------------5")
        return fh.getvalue()


def run(test=False):

    google_drive = GoogleDrive(SERVICE_ACCOUNT,
                            SCOPES,
                            PARENT_FOLDER_ID, 
                            folder_name=TIMESTAMP)
    google_drive.get_service()
    drive_list = google_drive.list_folder()
    print(drive_list)
    google_drive.get_folder_id()
    file_list = os.listdir(os.path.join(LOCAL_FOLDER, TIMESTAMP))
    for file in file_list:
        file_path = os.path.join(LOCAL_FOLDER, TIMESTAMP, file)
        google_drive.upload_to_drive(file_path, file, google_drive.folder_id)
    # if test is true then delete the folder we upload
    if test:
        google_drive.delete_folder(google_drive.folder_id)



if __name__ == "__main__":
    # run(test=False)
    google_drive = GoogleDrive(SERVICE_ACCOUNT,
                            SCOPES,
                            PARENT_FOLDER_ID, 
                            folder_name=TIMESTAMP)
    google_drive.get_service()
    drive_list = google_drive.list_folder()
    print(drive_list)