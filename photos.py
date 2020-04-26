from __future__ import print_function
from apiclient.http import MediaFileUpload, MediaIoBaseDownload
import os, io
import logging  
from apiclient import discovery 
from httplib2 import Http  
from oauth2client import file, client, tools 
from oauth2client.file import Storage 
from googleapiclient.discovery import build

import config
import telebot
from telebot.types import InputMediaPhoto, InputMediaVideo
from telebot import types
from database import SQL
from users import Seeker

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',level=logging.INFO)  
logger = logging.getLogger(__name__)  
db = SQL()

SCOPES = 'https://www.googleapis.com/auth/drive'
store = file.Storage('storage.json')  
creds = store.get()  
if not creds or creds.invalid:  
    flow = client.flow_from_clientsecrets('client_secrets.json', SCOPES)  
    creds = tools.run_flow(flow, store)  
drive_service = discovery.build('drive', 'v3', http=creds.authorize(Http()),cache_discovery=False) 

def download_photo(file_id):
    request = drive_service.files().get_media(fileId=file_id)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
        print ("Download %d%%." % int(status.progress() * 100))
    return fh.getvalue()
def get_flat_photo(message, flat_id, bot):
    photo_id = db.get_flat_photo_file_id(flat_id)
    # lista = []
    # print(photo_id)
    # for url in photo_id[0]:
    #     lista.append(InputMediaPhoto(media = 'https://drive.google.com/file/d/'+str(url)+'/view?usp=sharing'))
    # files = bot.send_media_group(message.chat.id, lista)
    photo = 'https://drive.google.com/file/d/'+str(photo_id[0][0])+'/view?usp=sharing'
    bot.send_photo(message.chat.id, photo)
# def prof(message, cur_prof):
#     flat_matches = db.get_matches(search)
#     photo_id = db.get_flat_photo_file_id(flat_matches[cur_prof-1][0])
#     lista = []
#     print(photo_id)
#     for url in photo_id[0]:
#         lista.append(InputMediaPhoto(media = 'https://drive.google.com/file/d/'+str(url)+'/view?usp=sharing'))
#     files = bot.send_media_group(message.chat.id, lista)

def document_handler(message, bot):
    folder_id = '1XjIl-IBxYh0frbvxg9HyHsN1ppyNf-nZ'
    file_id = message.photo[-1].file_id
    file = bot.get_file(file_id)
    downloaded_file = bot.download_file(file.file_path)
    with open(file_id, 'wb') as new_file:
        new_file.write(downloaded_file)

    file_metadata = {
    'name': [file_id],
    'parents': [folder_id]
    }
    media = MediaFileUpload(file_id, mimetype='image/jpeg', resumable=True)
    file = drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    return file.get('id')