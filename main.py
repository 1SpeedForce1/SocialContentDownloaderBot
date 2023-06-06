import json
import math
import pathlib
import shutil
import time
from bs4 import BeautifulSoup
import telebot
from telebot import types
from telebot.types import InputMediaPhoto, InputMediaVideo
import sqlite3
import re
from pytube import YouTube
import tldextract
from flask import Flask
from typing import Optional, Tuple
import requests
from moviepy.editor import *
from pathlib import Path
from PIL import Image
from urllib.parse import quote
import os
from ast import literal_eval


server = Flask(__name__)

token = ""
bot = telebot.TeleBot(token)
tg1 =  #
tg2 =  #

api_key_lamadava = '' #api key lamadava services

conn = sqlite3.connect('db2.db', check_same_thread=False)#текущая бд
cursor = conn.cursor()

conn1 = sqlite3.connect('db.db', check_same_thread=False)#squanch бд
cursor1 = conn1.cursor()

name_pablik = "Подписывайся на @squanch.tv" #дефолтное описание для контента



def check_subscribe(chat_member):
    if chat_member != "left":
        return True
    else:
        return False

def set_active_content(id, content):
    cursor.execute('UPDATE users SET active_content = ? WHERE user_id = ?',(str(content), id,))
    conn.commit()

def get_active_content(id):
    cursor.execute("SELECT active_content FROM users WHERE user_id = {}".format(id))
    return cursor.fetchone()[0]

def get_from_bd(id, column):
    cursor.execute("SELECT {} FROM users WHERE user_id = {}".format(column,id))
    return cursor.fetchone()[0]

def set_to_bd(id, column, value):
    cursor.execute('UPDATE users SET {} = ? WHERE user_id = ?'.format(column), (str(value), id,))
    conn.commit()

def get_all_id(user_id):
    cursor.execute("SELECT user_id FROM users")
    rows = cursor.fetchall()
    for row in rows:
        if user_id in row:
            return True
    return False

def db_add_user(user_id: int, user_name: str, user_surname: str, username: str):
    cursor.execute('INSERT INTO users (user_id, user_name, user_surname, username) VALUES (?, ?, ?, ?)',
                   (user_id, user_name, user_surname, username))
    conn.commit()

def db_add_content(user_id: int, link_content: str, content_description: str):
    cursor.execute('INSERT INTO contents (user_id, link_content, content_description) VALUES (?, ?, ?)',
                   (user_id, link_content, content_description))
    conn.commit()

def db_get_content(file):
    caption = ""
    content_id = str(os.path.splitext(os.path.basename(file))[0])
    cursor.execute(f"SELECT content_description FROM contents WHERE link_content = '{content_id}'")
    desc = cursor.fetchone()
    if desc != None:
        desc = "\n\n*Описание:*\n`{}`".format(desc[0])
    else:
        desc = "\n\n_Описание отсутствует!_"
    path = pathlib.WindowsPath(file)
    dlina = len(list(path.parents))
    no_need1 = str(list(path.parents)[-dlina])
    no_need2 = str(list(path.parents)[-dlina + 1])
    content_type = no_need1.replace(no_need2 + "\\", "")
    if (content_type == 'photo') or (content_type == 'video'):
        caption = '*Тип контента:* _сторис_'
    if content_type == 'clips':
        caption = '*Тип контента:* _клип_'
    if content_type == 'igtv':
        caption = '*Тип контента:* _IGTV_'
    if (content_type == 'photo_posts') or (content_type == 'video_posts'):
        caption = '*Тип контента:* _обычный пост_'
    if content_type == 'albums_posts':
        caption = '*Тип контента:* _альбомный пост_'
    return desc, caption

def db_table_val(media_pk: str, media_description: str):#загрузить в сквонча
    cursor1.execute('INSERT INTO media_descriptions (media_pk, media_description) VALUES (?, ?)',
                   (media_pk, media_description,))
    conn1.commit()

subscribe = types.InlineKeyboardMarkup()
subscribe.row_width = 1
admin_menu = types.InlineKeyboardMarkup()
admin_menu.row_width = 1
rate_content = types.InlineKeyboardMarkup()
rate_content.row_width = 1
tinder = types.InlineKeyboardMarkup()
tinder.row_width = 2
tinder_reels = types.InlineKeyboardMarkup()
tinder_reels.row_width = 2
admin_back_mark = types.InlineKeyboardMarkup()
admin_back_mark.row_width = 1
statistics_menu = types.InlineKeyboardMarkup()
statistics_menu.row_width = 1
back_to_list = types.InlineKeyboardMarkup()
back_to_list.row_width = 1

subscribe_button = types.InlineKeyboardButton("Подписаться!", url = 'https://t.me/squanch_tv')
subscribed_button = types.InlineKeyboardButton("Подписался!", callback_data='subscribed')

content_view = types.InlineKeyboardButton("Оценивать контент!", callback_data='content_rate')
story_view = types.InlineKeyboardButton("Смотреть истории!", callback_data='story_view')
reels_view = types.InlineKeyboardButton("Смотреть клипы!", callback_data='reels_view')
igtv_view = types.InlineKeyboardButton("Смотреть IGTV", callback_data='igtv_view')
albums_posts_view = types.InlineKeyboardButton("Смотреть альбомные посты!", callback_data='albums_posts_view')
other_posts_view = types.InlineKeyboardButton("Смотреть обычные посты!", callback_data='other_posts_view')
all_view = types.InlineKeyboardButton("Смотреть все подряд!", callback_data='all_view')
yes = types.InlineKeyboardButton("✅", callback_data='yes')
no = types.InlineKeyboardButton("❌", callback_data='no')
yes_story = types.InlineKeyboardButton("В сторис", callback_data = 'yes_story')
back_admin = types.InlineKeyboardButton("Вернуться в меню!",callback_data='back_admin')
back_to_users = types.InlineKeyboardButton("Вернуться в список", callback_data='back_to_list_users')


statistics = types.InlineKeyboardButton("Статистика", callback_data='statistics')
users_stat_list = types.InlineKeyboardButton("Статистика каждого пользователя", callback_data='users_stat_list')
full_statistic = types.InlineKeyboardButton("Полная статистика!", callback_data='full_statistic')

subscribe.add(subscribe_button, subscribed_button)
admin_menu.add(content_view, statistics)
rate_content.add(story_view, reels_view, igtv_view, other_posts_view, albums_posts_view, all_view, back_admin)
tinder.add(yes, no, back_admin)
tinder_reels.add(yes, no)
tinder_reels.row_width = 1
tinder_reels.add(yes_story, back_admin)
admin_back_mark.add(back_admin)
statistics_menu.add(users_stat_list, full_statistic, back_admin)
back_to_list.add(back_to_users)

# скачивание видоса из тиктока без водянного знака(ГОТОВО)
def get_id(original_url):
    headers = {
            'user-agent': 'Mozilla/5.0 (Linux; Android 8.0; Pixel 2 Build/OPD3.170816.012) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Mobile Safari/537.36 Edg/87.0.664.66'
        }
    if '@' in original_url:
        original_url = original_url
        video_id = re.findall('/video/(\d+)?', original_url)[0]
        return video_id
    else:
        response = requests.get(url=original_url, headers=headers, allow_redirects=False)
        true_link = response.headers['Location'].split("?")[0]
        original_url = true_link
        # TikTok请求头返回的第二种链接类型
        if '.html' in true_link:
            response = requests.get(url=true_link, headers=headers, allow_redirects=False)
            original_url = response.headers['Location'].split("?")[0]
            print("目标链接: ", original_url)
        video_id = re.findall('/video/(\d+)?', original_url)[0]
        return video_id

def tiktok_download(url, message):
    try:
        mess = bot.send_message(message.chat.id, text='Скачиваю...')
        try:
            Path(f'users_content/{message.chat.id}/tiktok/storys/video').mkdir(parents=True, exist_ok=True)
            Path(f'users_content/{message.chat.id}/tiktok/video_posts/clips').mkdir(parents=True, exist_ok=True)
            Path(f'users_content/{message.chat.id}/tiktok/video_posts/igtv').mkdir(parents=True, exist_ok=True)
            headers = {
                'user-agent': 'Mozilla/5.0 (Linux; Android 8.0; Pixel 2 Build/OPD3.170816.012) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Mobile Safari/537.36 Edg/87.0.664.66'
            }
            video_id = get_id(url)
            tiktok_api_link = 'https://api.douyin.wtf/api?url={}'.format(
                        url)
            res = requests.get(tiktok_api_link, headers=headers).text
            result = json.loads(res)
            nowm = result["video_data"]["nwm_video_url_HQ"]
            author = result["author"]["unique_id"]
            desc = result["desc"]
            if desc == "":
                desc = name_pablik + "\n\n" + "Автор(ТТ): " + author
            else:
                desc = desc + "\n\n" + "Автор(ТТ): " + author
            if os.path.exists(f'users_content/{message.chat.id}/tiktok/storys/video/' + f'{video_id}.mp4'):
                video_1 = open(video_id + ".mp4", 'rb')
                bot.delete_message(mess.chat.id, mess.message_id)
                bot.send_video(message.chat.id, video_1, caption=desc)
                video_1.close()
                return
            elif os.path.exists(f'users_content/{message.chat.id}/tiktok/video_posts/clips/' + f'{video_id}.mp4'):
                video_1 = open(video_id + ".mp4", 'rb')
                bot.delete_message(mess.chat.id, mess.message_id)
                bot.send_video(message.chat.id, video_1, caption=desc)
                video_1.close()
                return
            elif os.path.exists(f'users_content/{message.chat.id}/tiktok/video_posts/igtv/' + f'{video_id}.mp4'):
                video_1 = open(video_id + ".mp4", 'rb')
                bot.delete_message(mess.chat.id, mess.message_id)
                bot.send_video(message.chat.id, video_1, caption=desc)
                video_1.close()
                return
            else:
                resp = requests.get(nowm, stream=True)
                video = open(r'{}.mp4'.format(video_id), "wb")
                video.write(resp.content)
                video.close()
                video_1 = open(r'{}.mp4'.format(video_id), 'rb')
                bot.delete_message(mess.chat.id, mess.message_id)
                bot.send_video(message.chat.id, video_1, caption=desc)
                video_1.close()
                clip = VideoFileClip("{}.mp4".format(video_id))
                video_duration = clip.duration
                clip.close()
                if video_duration < 15:
                    shutil.move("{}.mp4".format(video_id), f'users_content/{message.chat.id}/tiktok/storys/video/')
                if video_duration > 15 and video_duration < 60:
                    shutil.move("{}.mp4".format(video_id), f'users_content/{message.chat.id}/tiktok/video_posts/clips/')
                if video_duration > 60:
                    shutil.move("{}.mp4".format(video_id), f'users_content/{message.chat.id}/tiktok/video_posts/igtv/')
                try:
                    db_add_content(user_id=message.chat.id, link_content=video_id, content_description=desc)
                    old_value = get_from_bd(message.chat.id, "tiktok_loaded")
                    old_value = int(old_value) + 1
                    set_to_bd(message.chat.id, "tiktok_loaded", old_value)
                except sqlite3.IntegrityError:
                    if get_from_bd(message.chat.id, 'worker'):
                        bot.send_message(message.chat.id, text='Такой контент уже был загружен!')
                print("Скачал тикток видос: "+str(url))
        except Exception as e:
            print(str(e))
            Path(f'users_content/{message.chat.id}/tiktok/storys/video').mkdir(parents=True, exist_ok=True)
            Path(f'users_content/{message.chat.id}/tiktok/video_posts/clips').mkdir(parents=True, exist_ok=True)
            Path(f'users_content/{message.chat.id}/tiktok/video_posts/igtv').mkdir(parents=True, exist_ok=True)
            headers = {
                'user-agent': 'Mozilla/5.0 (Linux; Android 8.0; Pixel 2 Build/OPD3.170816.012) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Mobile Safari/537.36 Edg/87.0.664.66'
            }
            video_id = get_id(url)
            tiktok_api_link = 'http://185.250.205.21:8000/api?url={}'.format(url)
            res = requests.get(tiktok_api_link, headers=headers).text
            result = json.loads(res)
            nowm = result["video_data"]["nwm_video_url_HQ"]
            author = result["author"]["unique_id"]
            desc = result["desc"]
            if desc == "":
                desc = name_pablik + "\n\n" + "Автор(ТТ): " + author
            else:
                desc = desc + "\n\n" + "Автор(ТТ): " + author
            if os.path.exists(f'users_content/{message.chat.id}/tiktok/storys/video/' + f'{video_id}.mp4'):
                video_1 = open(video_id + ".mp4", 'rb')
                bot.delete_message(mess.chat.id, mess.message_id)
                bot.send_video(message.chat.id, video_1, caption=desc)
                video_1.close()
                return
            elif os.path.exists(f'users_content/{message.chat.id}/tiktok/video_posts/clips/' + f'{video_id}.mp4'):
                video_1 = open(video_id + ".mp4", 'rb')
                bot.delete_message(mess.chat.id, mess.message_id)
                bot.send_video(message.chat.id, video_1, caption=desc)
                video_1.close()
                return
            elif os.path.exists(f'users_content/{message.chat.id}/tiktok/video_posts/igtv/' + f'{video_id}.mp4'):
                video_1 = open(video_id + ".mp4", 'rb')
                bot.delete_message(mess.chat.id, mess.message_id)
                bot.send_video(message.chat.id, video_1, caption=desc)
                video_1.close()
                return
            else:
                resp = requests.get(nowm, stream=True)
                video = open(r'{}.mp4'.format(video_id), "wb")
                video.write(resp.content)
                video.close()
                video_1 = open(r'{}.mp4'.format(video_id), 'rb')
                bot.delete_message(mess.chat.id, mess.message_id)
                bot.send_video(message.chat.id, video_1, caption=desc)
                video_1.close()
                clip = VideoFileClip("{}.mp4".format(video_id))
                video_duration = clip.duration
                clip.close()
                if video_duration < 15:
                    shutil.move("{}.mp4".format(video_id), f'users_content/{message.chat.id}/tiktok/storys/video/')
                if video_duration > 15 and video_duration < 60:
                    shutil.move("{}.mp4".format(video_id), f'users_content/{message.chat.id}/tiktok/video_posts/clips/')
                if video_duration > 60:
                    shutil.move("{}.mp4".format(video_id), f'users_content/{message.chat.id}/tiktok/video_posts/igtv/')
                try:
                    db_add_content(user_id=message.chat.id, link_content=video_id, content_description=desc)
                    old_value = get_from_bd(message.chat.id, "tiktok_loaded")
                    old_value = int(old_value) + 1
                    set_to_bd(message.chat.id, "tiktok_loaded", old_value)
                except sqlite3.IntegrityError:
                    if get_from_bd(message.chat.id, 'worker'):
                        bot.send_message(message.chat.id, text='Такой контент уже был загружен!')
                print("Скачал тикток видос: " + str(url))
    except Exception as e:
        print("Ошибка при скачивании ТТ видео: " + str(e))
        bot.send_message(message.chat.id, text="Произошла ошибка при скачивании! Попробуйте позже...")

def youtube_download(url, message):
    try:
        Path(f'users_content/{message.chat.id}/yt/storys/video').mkdir(parents=True, exist_ok=True)
        Path(f'users_content/{message.chat.id}/yt/video_posts/clips').mkdir(parents=True, exist_ok=True)
        Path(f'users_content/{message.chat.id}/yt/video_posts/igtv').mkdir(parents=True, exist_ok=True)
        mess = bot.send_message(message.chat.id, text='Скачиваю...')
        yt = YouTube(url)
        title = yt.title
        author = yt.author
        if title == "":
            title = name_pablik+ "\n\n"+"Автор(YТ): " + author
        else:
            title = title + "\n\n" + "Автор(YТ): " + author
        video_id = yt.video_id
        if os.path.exists(f'users_content/{message.chat.id}/yt/storys/video/'+f'{video_id}.mp4'):
            video_1 = open(video_id + ".mp4", 'rb')
            bot.delete_message(mess.chat.id, mess.message_id)
            bot.send_video(message.chat.id, video_1, caption=title)
            video_1.close()
            return
        elif os.path.exists(f'users_content/{message.chat.id}/yt/video_posts/clips/'+f'{video_id}.mp4'):
            video_1 = open(video_id + ".mp4", 'rb')
            bot.delete_message(mess.chat.id, mess.message_id)
            bot.send_video(message.chat.id, video_1, caption=title)
            video_1.close()
            return
        elif os.path.exists(f'users_content/{message.chat.id}/yt/video_posts/igtv/'+f'{video_id}.mp4'):
            video_1 = open(video_id + ".mp4", 'rb')
            bot.delete_message(mess.chat.id, mess.message_id)
            bot.send_video(message.chat.id, video_1, caption=title)
            video_1.close()
            return
        else:
            stream = yt.streams.get_highest_resolution()
            stream.download("", video_id+".mp4")
            clip = VideoFileClip("{}.mp4".format(video_id))
            video_duration = clip.duration
            clip.close()
            video_1 = open(video_id + ".mp4", 'rb')
            bot.delete_message(mess.chat.id, mess.message_id)
            if video_duration > 0 and video_duration < 240:
                bot.send_video(message.chat.id, video_1, caption=title)
            else:
                bot.send_message(message.chat.id, text = "Не удалось скачать, видео слишком длинное!")
            video_1.close()
            if video_duration < 15:
                shutil.move("{}.mp4".format(video_id), f'users_content/{message.chat.id}/yt/storys/video/')
            if video_duration > 15 and video_duration < 60:
                shutil.move("{}.mp4".format(video_id), f'users_content/{message.chat.id}/yt/video_posts/clips/')
            if video_duration > 60 and video_duration < 240:
                shutil.move("{}.mp4".format(video_id), f'users_content/{message.chat.id}/yt/video_posts/igtv/')
            if video_duration > 240:
                os.remove("{}.mp4".format(video_id))
            try:
                db_add_content(user_id=message.chat.id, link_content=video_id, content_description=title)
                old_value = get_from_bd(message.chat.id, "yt_loaded")
                old_value = int(old_value) + 1
                set_to_bd(message.chat.id, "yt_loaded", old_value)
            except sqlite3.IntegrityError:
                if get_from_bd(message.chat.id, 'worker'):
                    bot.send_message(message.chat.id, text='Такой контент уже был загружен!')
            print("Скачал YT видос: " + str(url))
    except Exception as e:
        print("Ошибка при скачивании YТ видео: " + str(e))
        bot.send_message(message.chat.id, text="Произошла ошибка при скачивании! Попробуйте позже...")

def create_album_media(path):
    media_group = []
    for file in os.listdir(path):
        if file.endswith('.mp4'):
            media_group.append(InputMediaVideo(open(str(path)+"/"+file,
                       'rb')))
        if file.endswith('.jpeg'):
            media_group.append(InputMediaPhoto(open(str(path)+"/"+file,
                       'rb')))
    return media_group

def instagram_download(url, message):
    try:
        Path(f'users_content/{message.chat.id}/instagram/storys/video').mkdir(parents=True, exist_ok=True)
        Path(f'users_content/{message.chat.id}/instagram/storys/photo').mkdir(parents=True, exist_ok=True)
        Path(f'users_content/{message.chat.id}/instagram/video_posts/igtv').mkdir(parents=True, exist_ok=True)
        Path(f'users_content/{message.chat.id}/instagram/video_posts/clips').mkdir(parents=True, exist_ok=True)
        Path(f'users_content/{message.chat.id}/instagram/photo_posts').mkdir(parents=True, exist_ok=True)
        Path(f'users_content/{message.chat.id}/instagram/albums_posts').mkdir(parents=True, exist_ok=True)
        mess = bot.send_message(message.chat.id, text='Скачиваю...')
        if "stories" in url:
            a = "https://api.lamadava.com/v1/story/by/url?url={}&access_key={}".format(
                quote(url), api_key_lamadava)
            response = requests.get(url=a)
            result = json.loads(response.text)
            media_type = result["media_type"]
            pk = result["pk"]
            if media_type == 2:
                if os.path.exists(f'users_content/{message.chat.id}/instagram/storys/video/' + r'{}.mp4'.format(pk)):
                    video_1 = open(f'users_content/{message.chat.id}/instagram/storys/video/' + r'{}.mp4'.format(pk),
                                   'rb')
                    bot.delete_message(mess.chat.id, mess.message_id)
                    bot.send_video(message.chat.id, video_1)
                    video_1.close()
                    return
                else:
                    b = "https://api.lamadava.com/v1/story/download?id={}&access_key={}".format(
                        result["id"], api_key_lamadava)
                    response = requests.get(url=b)
                    video = open(f'users_content/{message.chat.id}/instagram/storys/video/'+r'{}.mp4'.format(pk), "wb")
                    video.write(response.content)
                    video.close()
                    video_1 = open(f'users_content/{message.chat.id}/instagram/storys/video/' + r'{}.mp4'.format(pk), 'rb')
                    bot.delete_message(mess.chat.id, mess.message_id)
                    bot.send_video(message.chat.id, video_1)
                    video_1.close()
                    caption = name_pablik
            if media_type == 1:
                if os.path.exists(f'users_content/{message.chat.id}/instagram/storys/photo/' + r'{}.jpeg'.format(pk)):
                    photo_1 = open(f'users_content/{message.chat.id}/instagram/storys/photo/' + r'{}.jpeg'.format(pk),
                                   'rb')
                    bot.delete_message(mess.chat.id, mess.message_id)
                    bot.send_photo(message.chat.id, photo_1)
                    photo_1.close()
                    return
                else:
                    b = "https://api.lamadava.com/v1/story/download?id={}&access_key={}".format(
                        result["id"], api_key_lamadava)
                    response = requests.get(url=b)
                    photo = open(f'users_content/{message.chat.id}/instagram/storys/photo/' + r'{}.jpeg'.format(pk), "wb")
                    photo.write(response.content)
                    photo.close()
                    photo_1 = open(f'users_content/{message.chat.id}/instagram/storys/photo/'+r'{}.jpeg'.format(pk), 'rb')
                    bot.delete_message(mess.chat.id, mess.message_id)
                    bot.send_photo(message.chat.id, photo_1)
                    photo_1.close()
                    caption = name_pablik
            print("Скачал инста-сторис: " + str(url))
        else:
            a = "https://api.lamadava.com/v1/media/by/url?url={}&access_key={}".format(
                quote(url), api_key_lamadava)
            response = requests.get(url=a)
            result = json.loads(response.text)
            media_type = result["media_type"]
            product_type = result["product_type"]
            pk = result["pk"]
            caption = result["caption_text"]
            if caption == "":
                caption = name_pablik
            if media_type == 2:
                video_url = result["video_url"]
                if product_type == "feed":  # скачивание постов с обычным видео
                    if os.path.exists(f'users_content/{message.chat.id}/instagram/video_posts/' + r'{}.mp4'.format(pk)):
                        video_1 = open(f'users_content/{message.chat.id}/instagram/video_posts/' + r'{}.mp4'.format(pk),
                                       'rb')
                        bot.delete_message(mess.chat.id, mess.message_id)
                        bot.send_video(message.chat.id, video_1, caption=caption)
                        video_1.close()
                        return
                    else:
                        response = requests.get(url=video_url)
                        video = open(f'users_content/{message.chat.id}/instagram/video_posts/' + r'{}.mp4'.format(pk),
                                     "wb")
                        video.write(response.content)
                        video.close()
                        video_1 = open(f'users_content/{message.chat.id}/instagram/video_posts/'+r'{}.mp4'.format(pk), 'rb')
                        bot.delete_message(mess.chat.id, mess.message_id)
                        bot.send_video(message.chat.id, video_1, caption=caption)
                        video_1.close()
                if product_type == "igtv":  # скачивание постов с видео igtv
                    if os.path.exists(f'users_content/{message.chat.id}/instagram/video_posts/igtv/' + r'{}.mp4'.format(pk)):
                        video_1 = open(
                            f'users_content/{message.chat.id}/instagram/video_posts/igtv/' + r'{}.mp4'.format(pk),
                            'rb')
                        bot.delete_message(mess.chat.id, mess.message_id)
                        bot.send_video(message.chat.id, video_1, caption=caption)
                        video_1.close()
                        return
                    else:
                        response = requests.get(url=video_url)
                        video = open(f'users_content/{message.chat.id}/instagram/video_posts/igtv/' + r'{}.mp4'.format(pk),
                                     "wb")
                        video.write(response.content)
                        video.close()
                        video_1 = open(f'users_content/{message.chat.id}/instagram/video_posts/igtv/' + r'{}.mp4'.format(pk),
                                       'rb')
                        bot.delete_message(mess.chat.id, mess.message_id)
                        bot.send_video(message.chat.id, video_1, caption=caption)
                        video_1.close()
                if product_type == "clips":  # скачивание клипов
                    if os.path.exists(f'users_content/{message.chat.id}/instagram/video_posts/clips/' + r'{}.mp4'.format(pk)):
                        video_1 = open(
                            f'users_content/{message.chat.id}/instagram/video_posts/clips/' + r'{}.mp4'.format(pk),
                            'rb')
                        bot.delete_message(mess.chat.id, mess.message_id)
                        bot.send_video(message.chat.id, video_1, caption=caption)
                        video_1.close()
                        return
                    else:
                        response = requests.get(url=video_url)
                        video = open(f'users_content/{message.chat.id}/instagram/video_posts/clips/' + r'{}.mp4'.format(pk),
                                     "wb")
                        video.write(response.content)
                        video.close()
                        video_1 = open(f'users_content/{message.chat.id}/instagram/video_posts/clips/' + r'{}.mp4'.format(pk),
                                       'rb')
                        bot.delete_message(mess.chat.id, mess.message_id)
                        bot.send_video(message.chat.id, video_1, caption=caption)
                        video_1.close()
            if media_type == 1:  # скачивание постов с фоткой
                if os.path.exists(f'users_content/{message.chat.id}/instagram/photo_posts/' + r'{}.jpeg'.format(pk)):
                    photo_1 = open(f'users_content/{message.chat.id}/instagram/photo_posts/' + r'{}.jpeg'.format(pk),
                                   'rb')
                    bot.delete_message(mess.chat.id, mess.message_id)
                    bot.send_photo(message.chat.id, photo_1, caption=caption)
                    photo_1.close()
                    return
                else:
                    image_url = result["thumbnail_url"]
                    response = requests.get(url=image_url)
                    photo = open(f'users_content/{message.chat.id}/instagram/photo_posts/' + r'{}.jpeg'.format(pk), "wb")
                    photo.write(response.content)
                    photo.close()
                    photo_1 = open(f'users_content/{message.chat.id}/instagram/photo_posts/' + r'{}.jpeg'.format(pk), 'rb')
                    bot.delete_message(mess.chat.id, mess.message_id)
                    bot.send_photo(message.chat.id, photo_1, caption=caption)
                    photo_1.close()
            if media_type == 8:  # скачивание постов с нескольками фото
                if os.path.exists(f'users_content/{message.chat.id}/instagram/albums_posts/' + str(pk)):
                    media = create_album_media(f'users_content/{message.chat.id}/instagram/albums_posts/{pk}/')
                    bot.delete_message(mess.chat.id, mess.message_id)
                    bot.send_media_group(message.chat.id, media=media)
                    return
                else:
                    Path(f'users_content/{message.chat.id}/instagram/albums_posts/' + str(pk)).mkdir(parents=True, exist_ok=True)
                    resources = result["resources"]
                    for index, source in enumerate(resources):
                        pk_post = index
                        video_url = source["video_url"]
                        photo_url = source["thumbnail_url"]
                        media_type_i = source["media_type"]
                        if media_type_i == 2:
                            response = requests.get(url=video_url)
                            video = open(f'users_content/{message.chat.id}/instagram/albums_posts/{pk}/' + r'{}.mp4'.format(pk_post),
                                         "wb")
                            video.write(response.content)
                            video.close()
                        if media_type_i == 1:
                            response = requests.get(url=photo_url)
                            photo = open(f'users_content/{message.chat.id}/instagram/albums_posts/{pk}/' + r'{}.jpeg'.format(pk_post),
                                         "wb")
                            photo.write(response.content)
                            photo.close()
                    media = create_album_media(f'users_content/{message.chat.id}/instagram/albums_posts/{pk}/')
                    bot.delete_message(mess.chat.id, mess.message_id)
                    bot.send_media_group(message.chat.id, media = media)
            print("Скачал инста-пост: " + str(url))
        try:
            db_add_content(user_id=message.chat.id, link_content=str(pk), content_description=caption)
            old_value = get_from_bd(message.chat.id, "instagram_loaded")
            old_value = int(old_value) + 1
            set_to_bd(message.chat.id, "instagram_loaded", old_value)
        except sqlite3.IntegrityError:
            if get_from_bd(message.chat.id, 'worker'):
                bot.send_message(message.chat.id, text='Такой контент уже был загружен!')
    except Exception as e:
        print("Ошибка при скачивании Инстаграм контента: " + str(e))
        bot.send_message(message.chat.id, text="Произошла ошибка при скачивании! Попробуйте позже...")

def scrap_url(_url: str) -> BeautifulSoup:
    """Crawls the given URL.
    Parameters
    ----------
    _url : str
        URL to crawl.
    Returns
    -------
    BeautifulSoup
        Returns crawled webpage as a BeautifulSoup object.
    Raises
    ------
    InvalidPinterestUrlError
        If the given url is not a pinterest url.
    InvalidUrlError
        If the given url is not a valid/active url.
    """
    headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36"
    }
    r = requests.get(_url, headers=headers, allow_redirects=True)
    if tldextract.extract(r.url).domain != "pinterest":
        print(f"'{_url}' not a valid Pinterest url")
    resp = requests.get(
        r.url.split("/sent")[0],
        headers=headers,
        allow_redirects=True,
    )
    soup_data = BeautifulSoup(resp.text, features="html.parser")
    json_load = json.loads(
        str(soup_data.find("script", {"id": "__PWS_DATA__"})).strip(
            """<script id="__PWS_DATA__" type="application/json">"""
        )
    )["props"]["initialReduxState"]
    og_image_url = soup_data.find("meta", {"name": "og:image"})["content"]
    return json_load, og_image_url

def extract_story(json_load: dict) -> Optional[str]:
    """Extracts video url from story block in dict
    Parameters
    ----------
    json_load : dict
        Json load from crawled webpage.
    Returns
    -------
    Optional[str]
        if present video url
    """
    try:
        pin_id: str = next(iter(json_load["pins"]))
        video_url: str = (
            json_load.get("pins", {})
            .get(pin_id, {})
            .get("story_pin_data", {})
            .get("pages", [[]])[0]
            .get("blocks", [{}])[0]
            .get("video", {})
            .get("video_list", {})
            .get("V_EXP7", {})
            .get("url", None)
        )
    except Exception as excp:
        video_url = None
    return video_url

def extract_video(json_load: dict) -> Optional[str]:
    """Extracts video url from dict
    Parameters
    ----------
    json_load : dict
        Json load from crawled webpage.
    Returns
    -------
    Optional[str]
        If present Video url
    """
    try:
        pin_id: str = next(iter(json_load["pins"]))
        video_url: str = (
            json_load.get("pins", {})
            .get(pin_id, {})
            .get("videos", {})
            .get("video_list", {})
            .get("V_720P", {})
            .get("url", None)
        )
    except Exception as excp:
        video_url = None
    if not video_url:
        video_url = extract_story(json_load)
    return video_url

def extract_image(json_load: dict) -> Optional[str]:
    """Extracts image url from dictionary.
    Parameters
    ----------
    json_load : dict
        Json load from crawled webpage.
    Returns
    -------
    Optional[str]
        Image url if present.
    """
    try:
        pin_id: str = next(iter(json_load["pins"]))
        img_url: str = (
            json_load.get("pins", {})
            .get(pin_id, {})
            .get("images", {})
            .get("orig", {})
            .get("url", None)
        )
    except Exception as excp:
        img_url = None
    return img_url

def get_url(url: str) -> Tuple[str, Optional[str]]:
    """Extracts image and video url
    Parameters
    ----------
    url : str
        url to be crawled
    Returns
    -------
    Tuple[str, Optional[str]]
        A tuple containing image url and video url if present.
    """
    json_load, og_image_url = scrap_url(url)
    image_url = extract_image(json_load) or og_image_url
    video_url = extract_video(json_load)
    return image_url, video_url

def pinterest_download(url, message):
    try:
        Path(f'users_content/{message.chat.id}/pinterest/storys/photo').mkdir(parents=True, exist_ok=True)
        Path(f'users_content/{message.chat.id}/pinterest/video_posts/clips').mkdir(parents=True, exist_ok=True)
        Path(f'users_content/{message.chat.id}/pinterest/video_posts/igtv').mkdir(parents=True, exist_ok=True)
        Path(f'users_content/{message.chat.id}/pinterest/storys/video').mkdir(parents=True, exist_ok=True)
        mess = bot.send_message(message.chat.id, text='Скачиваю...')
        image, video = get_url(url)
        if video == None:
            name = os.path.splitext(os.path.basename(r'{}'.format(image)))[0]
            if os.path.exists(f"users_content/{message.chat.id}/pinterest/storys/photo/"+r'{}.jpeg'.format(name)):
                photo_1 = open(f"users_content/{message.chat.id}/pinterest/storys/photo/" + r'{}.jpeg'.format(name),
                               'rb')
                bot.delete_message(mess.chat.id, mess.message_id)
                bot.send_photo(message.chat.id, photo_1)
                photo_1.close()
                return
            else:
                resp = requests.get(image, stream=True)
                f = open(f"users_content/{message.chat.id}/pinterest/storys/photo/"+r'{}.jpeg'.format(name), "wb")
                f.write(resp.content)
                f.close()
                photo_1 = open(f"users_content/{message.chat.id}/pinterest/storys/photo/" + r'{}.jpeg'.format(name),
                               'rb')
                bot.delete_message(mess.chat.id, mess.message_id)
                bot.send_photo(message.chat.id, photo_1)
                photo_1.close()
        else:
            name = os.path.splitext(os.path.basename(r'{}'.format(video)))[0]
            if os.path.exists(f"users_content/{message.chat.id}/pinterest/storys/video/" + r'{}.mp4'.format(name)):
                video_1 = open(f"users_content/{message.chat.id}/pinterest/storys/video/" + r'{}.mp4'.format(name), 'rb')
                bot.delete_message(mess.chat.id, mess.message_id)
                bot.send_video(message.chat.id, video_1)
                video_1.close()
                return
            elif os.path.exists(f"users_content/{message.chat.id}/pinterest/video_posts/clips/" + r'{}.mp4'.format(name)):
                video_1 = open(f"users_content/{message.chat.id}/pinterest/video_posts/clips/" + r'{}.mp4'.format(name), 'rb')
                bot.delete_message(mess.chat.id, mess.message_id)
                bot.send_video(message.chat.id, video_1)
                video_1.close()
                return
            elif os.path.exists(f"users_content/{message.chat.id}/pinterest/video_posts/igtv/" + r'{}.mp4'.format(name)):
                video_1 = open(f"users_content/{message.chat.id}/pinterest/video_posts/igtv/" + r'{}.mp4'.format(name), 'rb')
                bot.delete_message(mess.chat.id, mess.message_id)
                bot.send_video(message.chat.id, video_1)
                video_1.close()
                return
            else:
                resp = requests.get(video, stream=True)
                f = open(r'{}.mp4'.format(name), "wb")
                f.write(resp.content)
                f.close()
                video_1 = open(r'{}.mp4'.format(name), 'rb')
                bot.delete_message(mess.chat.id, mess.message_id)
                bot.send_video(message.chat.id, video_1)
                video_1.close()
                clip = VideoFileClip("{}.mp4".format(name))
                video_duration = clip.duration
                clip.close()
                if video_duration < 15:
                    shutil.move("{}.mp4".format(name), f"users_content/{message.chat.id}/pinterest/storys/video/")
                if video_duration > 15 and video_duration < 60:
                    shutil.move("{}.mp4".format(name), f"users_content/{message.chat.id}/pinterest/video_posts/clips/")
                if video_duration > 60:
                    shutil.move("{}.mp4".format(name), f"users_content/{message.chat.id}/pinterest/video_posts/igtv/")
        try:
            db_add_content(user_id=message.chat.id, link_content=name, content_description=name_pablik)
            old_value = get_from_bd(message.chat.id, "pinterest_loaded")
            old_value = int(old_value) + 1
            set_to_bd(message.chat.id, "pinterest_loaded", old_value)
        except sqlite3.IntegrityError:
            if get_from_bd(message.chat.id, 'worker'):
                bot.send_message(message.chat.id, text='Такой контент уже был загружен!')

    except Exception as e:
        print("Ошибка при скачивании pinterest: " + str(e))
        bot.send_message(message.chat.id, text="Произошла ошибка при скачивании! Попробуйте позже...")


hello = "👋Привет!\n🤖Я умею скачивать контент из соц сетей:\n✅Instagram\n✅TikTok(без водянного знака)\n✅Pinterest\n✅YouTube Shorts\n\n❓Для получения подробной инструкции введите: /help\n\n🔗Ты можешь отправить мне ссылку с желаемым контентом, который ты хочешь скачать!"
podpiska = "❗Чтобы воспользоваться ботом, подпишитесь на телеграм-канал @squanch_tv❗"
help_msg = 'ℹ*Инструкция:*\n❗_Бот позволяет скачивать контент перечисленных в стартовом сообщении соц сетей_\n❗_Важно знать, что бот может скачивать только из открытых аккаунтов_\n\n*Сейчас я перечислю поддерживаемые ссылки:*\n\n✅*TikTok:*\n`https://vt.tiktok.com/...../`\n`https://vm.tiktok.com/...../`\n`https://www.tiktok.com/...../video/...../`\n\n✅*Pinterest:*\n`https://pin.it/...../`\n`https://www.pinterest.com/pin/...../`\n\n✅*YouTube:*\n`https://youtube.com/shorts/...../`\n\n✅*Instagram:*\n▫_Reels:_\n`https://www.instagram.com/reel/...../`\n▫_Photo/Video/Albums Post:_\n`https://www.instagram.com/p/...../`\n▫_IGTV:_\n`https://www.instagram.com/tv/...../`\n▫_Storys:_\n`https://www.instagram.com/storys/...../`\n\n*Так же бот может скачивать сторисы по юзернейму*\n_Пример:_\n*@username-all* ⬅_скачать все истории данного пользователя_\n*@username-1* ⬅_скачать первую по порядку сторис данного пользователя_'


def change_desc(message, old_message):
    active_menu = get_from_bd(message.chat.id, 'active_menu')
    active_content = get_active_content(message.chat.id)
    if ('albums_posts' in active_menu) or ('albums_posts' in active_content):
        messages = literal_eval(get_from_bd(message.chat.id, 'album_messages'))
        if len(messages) >= 1:
            for id in messages:
                bot.delete_message(chat_id=message.chat.id, message_id=id)
    bot.delete_message(chat_id=message.chat.id, message_id=old_message)
    content_id = str(os.path.splitext(os.path.basename(get_active_content(message.chat.id)))[0])
    cursor.execute(f"UPDATE contents SET content_description = '{message.text}' WHERE link_content = '{content_id}'")
    conn.commit()
    send_anket(message, active_menu)

def construct(content):
    folders_workers = os.listdir("users_content")
    if content == 'storys':
        arr_content = []
        for folder in folders_workers:
            currentDirectory1 = pathlib.Path(f"users_content/{folder}/instagram/storys/photo")
            currentDirectory6 = pathlib.Path(f"users_content/{folder}/instagram/storys/video")
            currentDirectory2 = pathlib.Path(f"users_content/{folder}/pinterest/storys/video")
            currentDirectory3 = pathlib.Path(f"users_content/{folder}/pinterest/storys/photo")
            currentDirectory4 = pathlib.Path(f"users_content/{folder}/tiktok/storys/video")
            currentDirectory5 = pathlib.Path(f"users_content/{folder}/yt/storys/video")
            currentPattern = "*.*"
            for currentFile1 in currentDirectory1.glob(currentPattern):
                arr_content.append(currentFile1)
            for currentFile2 in currentDirectory2.glob(currentPattern):
                arr_content.append(currentFile2)
            for currentFile3 in currentDirectory3.glob(currentPattern):
                arr_content.append(currentFile3)
            for currentFile4 in currentDirectory4.glob(currentPattern):
                arr_content.append(currentFile4)
            for currentFile5 in currentDirectory5.glob(currentPattern):
                arr_content.append(currentFile5)
            for currentFile6 in currentDirectory6.glob(currentPattern):
                arr_content.append(currentFile6)
        return arr_content
    if content == 'clips':
        arr_content = []
        for folder in folders_workers:
            currentDirectory1 = pathlib.Path(f"users_content/{folder}/instagram/video_posts/clips")
            currentDirectory2 = pathlib.Path(f"users_content/{folder}/pinterest/video_posts/clips")
            currentDirectory4 = pathlib.Path(f"users_content/{folder}/tiktok/video_posts/clips")
            currentDirectory5 = pathlib.Path(f"users_content/{folder}/yt/video_posts/clips")
            currentPattern = "*.mp4"
            for currentFile1 in currentDirectory1.glob(currentPattern):
                arr_content.append(currentFile1)
            for currentFile2 in currentDirectory2.glob(currentPattern):
                arr_content.append(currentFile2)
            for currentFile4 in currentDirectory4.glob(currentPattern):
                arr_content.append(currentFile4)
            for currentFile5 in currentDirectory5.glob(currentPattern):
                arr_content.append(currentFile5)
        return arr_content
    if content == 'igtv':
        arr_content = []
        for folder in folders_workers:
            currentDirectory1 = pathlib.Path(f"users_content/{folder}/instagram/video_posts/igtv")
            currentDirectory2 = pathlib.Path(f"users_content/{folder}/pinterest/video_posts/igtv")
            currentDirectory4 = pathlib.Path(f"users_content/{folder}/tiktok/video_posts/igtv")
            currentDirectory5 = pathlib.Path(f"users_content/{folder}/yt/video_posts/igtv")
            currentPattern = "*.mp4"
            for currentFile1 in currentDirectory1.glob(currentPattern):
                arr_content.append(currentFile1)
            for currentFile2 in currentDirectory2.glob(currentPattern):
                arr_content.append(currentFile2)
            for currentFile4 in currentDirectory4.glob(currentPattern):
                arr_content.append(currentFile4)
            for currentFile5 in currentDirectory5.glob(currentPattern):
                arr_content.append(currentFile5)
        return arr_content
    if content == 'other_posts':
        arr_content = []
        for folder in folders_workers:
            currentDirectory1 = pathlib.Path(f"users_content/{folder}/instagram/photo_posts")
            currentDirectory2 = pathlib.Path(f"users_content/{folder}/instagram/video_posts")
            currentPattern = "*.*"
            for currentFile1 in currentDirectory1.glob(currentPattern):
                arr_content.append(currentFile1)
            for currentFile2 in currentDirectory2.glob(currentPattern):
                arr_content.append(currentFile2)
        return arr_content
    if content == 'albums_posts':
        arr_content = []
        for folder in folders_workers:
            currentDirectory1 = pathlib.Path(f"users_content/{folder}/instagram/albums_posts")
            if os.path.exists(currentDirectory1):
                for folder1 in os.listdir(currentDirectory1):
                    if os.path.exists(f'users_content/{folder}/instagram/albums_posts/' + folder1):
                        arr_content.append(pathlib.Path(f'users_content/{folder}/instagram/albums_posts/' + folder1))
        return arr_content
    if content == 'all':
        albums = []
        arr_content = []
        for folder in folders_workers:
            currentDirectory1 = pathlib.Path(f"users_content/{folder}/instagram/albums_posts")
            if os.path.exists(currentDirectory1):
                for folder1 in os.listdir(currentDirectory1):
                    if os.path.exists(f'users_content/{folder}/instagram/albums_posts/' + folder1):
                        arr_content.append(pathlib.Path(f'users_content/{folder}/instagram/albums_posts/' + folder1))

        for folder in folders_workers:
            currentDirectory1 = pathlib.Path(f"users_content/{folder}/instagram/photo_posts")
            currentDirectory2 = pathlib.Path(f"users_content/{folder}/instagram/video_posts")
            currentPattern = "*.*"
            for currentFile1 in currentDirectory1.glob(currentPattern):
                arr_content.append(currentFile1)
            for currentFile2 in currentDirectory2.glob(currentPattern):
                arr_content.append(currentFile2)

        for folder in folders_workers:
            currentDirectory1 = pathlib.Path(f"users_content/{folder}/instagram/video_posts/igtv")
            currentDirectory2 = pathlib.Path(f"users_content/{folder}/pinterest/video_posts/igtv")
            currentDirectory4 = pathlib.Path(f"users_content/{folder}/tiktok/video_posts/igtv")
            currentDirectory5 = pathlib.Path(f"users_content/{folder}/yt/video_posts/igtv")
            currentPattern = "*.mp4"
            for currentFile1 in currentDirectory1.glob(currentPattern):
                arr_content.append(currentFile1)
            for currentFile2 in currentDirectory2.glob(currentPattern):
                arr_content.append(currentFile2)
            for currentFile4 in currentDirectory4.glob(currentPattern):
                arr_content.append(currentFile4)
            for currentFile5 in currentDirectory5.glob(currentPattern):
                arr_content.append(currentFile5)

        for folder in folders_workers:
            currentDirectory1 = pathlib.Path(f"users_content/{folder}/instagram/video_posts/clips")
            currentDirectory2 = pathlib.Path(f"users_content/{folder}/pinterest/video_posts/clips")
            currentDirectory4 = pathlib.Path(f"users_content/{folder}/tiktok/video_posts/clips")
            currentDirectory5 = pathlib.Path(f"users_content/{folder}/yt/video_posts/clips")
            currentPattern = "*.mp4"
            for currentFile1 in currentDirectory1.glob(currentPattern):
                arr_content.append(currentFile1)
            for currentFile2 in currentDirectory2.glob(currentPattern):
                arr_content.append(currentFile2)
            for currentFile4 in currentDirectory4.glob(currentPattern):
                arr_content.append(currentFile4)
            for currentFile5 in currentDirectory5.glob(currentPattern):
                arr_content.append(currentFile5)

        for folder in folders_workers:
            currentDirectory1 = pathlib.Path(f"users_content/{folder}/instagram/storys/video")
            currentDirectory6 = pathlib.Path(f"users_content/{folder}/instagram/storys/photo")
            currentDirectory2 = pathlib.Path(f"users_content/{folder}/pinterest/storys/video")
            currentDirectory3 = pathlib.Path(f"users_content/{folder}/pinterest/storys/photo")
            currentDirectory4 = pathlib.Path(f"users_content/{folder}/tiktok/storys/video")
            currentDirectory5 = pathlib.Path(f"users_content/{folder}/yt/storys/video")
            currentPattern = "*.*"
            for currentFile1 in currentDirectory1.glob(currentPattern):
                arr_content.append(currentFile1)
            for currentFile2 in currentDirectory2.glob(currentPattern):
                arr_content.append(currentFile2)
            for currentFile3 in currentDirectory3.glob(currentPattern):
                arr_content.append(currentFile3)
            for currentFile4 in currentDirectory4.glob(currentPattern):
                arr_content.append(currentFile4)
            for currentFile5 in currentDirectory5.glob(currentPattern):
                arr_content.append(currentFile5)
            for currentFile6 in currentDirectory6.glob(currentPattern):
                arr_content.append(currentFile6)

        return albums, arr_content

def send_anket(message, content_type):
    if (content_type == 'storys'):
        content_list = construct(content_type)
        if len(content_list) != 0:
            content = content_list[0]
            desc, caption = db_get_content(content)
            bot.delete_message(message.chat.id, message.message_id)
            set_active_content(message.chat.id, content)
            if content.suffix == ".mp4":
                video = open(content, 'rb')
                bot.send_video(message.chat.id, video, caption=caption+desc, parse_mode= 'Markdown', reply_markup=tinder)
                video.close()
            else:
                photo = open(content, 'rb')
                bot.send_photo(message.chat.id, photo, caption=caption+desc, parse_mode= 'Markdown', reply_markup=tinder)
                photo.close()
        else:
            set_active_content(message.chat.id, "NO")
            bot.delete_message(message.chat.id, message.message_id)
            bot.send_message(chat_id=message.chat.id, text='Контент в данной категории отсутствует!', reply_markup=admin_back_mark)
    if (content_type == 'clips'):
        content_list = construct(content_type)
        if len(content_list) != 0:
            content = content_list[0]
            desc, caption = db_get_content(content)
            bot.delete_message(message.chat.id, message.message_id)
            set_active_content(message.chat.id, content)
            if content.suffix == ".mp4":
                video = open(content, 'rb')
                msg = bot.send_video(message.chat.id, video, caption=caption + desc, parse_mode='Markdown',
                               reply_markup=tinder_reels)
                video.close()
                bot.register_next_step_handler(msg, change_desc, msg.id)
            else:
                photo = open(content, 'rb')
                msg = bot.send_photo(message.chat.id, photo, caption=caption + desc, parse_mode='Markdown',
                               reply_markup=tinder_reels)
                photo.close()
                bot.register_next_step_handler(msg, change_desc, msg.id)
        else:
            set_active_content(message.chat.id, "NO")
            bot.delete_message(message.chat.id, message.message_id)
            bot.send_message(chat_id=message.chat.id, text='Контент в данной категории отсутствует!',
                             reply_markup=admin_back_mark)

    if (content_type == 'igtv') or (content_type == 'other_posts'):
        content_list = construct(content_type)
        if len(content_list) != 0:
            content = content_list[0]
            desc, caption = db_get_content(content)
            bot.delete_message(message.chat.id, message.message_id)
            set_active_content(message.chat.id, content)
            if content.suffix == ".mp4":
                video = open(content, 'rb')
                msg = bot.send_video(message.chat.id, video, caption=caption + desc, parse_mode='Markdown',
                               reply_markup=tinder)
                video.close()
                bot.register_next_step_handler(msg, change_desc, msg.id)
            else:
                photo = open(content, 'rb')
                msg = bot.send_photo(message.chat.id, photo, caption=caption + desc, parse_mode='Markdown',
                               reply_markup=tinder)
                photo.close()
                bot.register_next_step_handler(msg, change_desc, msg.id)
        else:
            set_active_content(message.chat.id, "NO")
            bot.delete_message(message.chat.id, message.message_id)
            bot.send_message(chat_id=message.chat.id, text='Контент в данной категории отсутствует!',
                             reply_markup=admin_back_mark)

    if content_type == 'albums_posts':
        albums_id = []
        albums_list = construct(content_type)
        if (len(albums_list) != 0):
            album = albums_list[0]
            desc, caption = db_get_content(album)
            media = create_album_media(album)
            bot.delete_message(message.chat.id, message.message_id)
            album_message = bot.send_media_group(message.chat.id, media=media)
            for message in album_message:
                albums_id.append(message.id)
            set_to_bd(message.chat.id, 'album_messages', albums_id)
            msg = bot.send_message(message.chat.id, text=caption+desc, parse_mode= 'Markdown', reply_markup=tinder)
            set_active_content(message.chat.id, album)
            bot.register_next_step_handler(msg, change_desc, msg.id)
        else:
            set_active_content(message.chat.id, "NO")
            bot.delete_message(message.chat.id, message.message_id)
            bot.send_message(chat_id=message.chat.id, text='Контент в данной категории отсутствует!',
                             reply_markup=admin_back_mark)

    if content_type == 'all':
        albums_list, content_list = construct(content_type)
        if (len(content_list) != 0):
            content = content_list[0]
            desc, caption = db_get_content(content)
            bot.delete_message(message.chat.id, message.message_id)
            set_active_content(message.chat.id, content)
            if content.suffix == ".mp4":
                video = open(content, 'rb')
                msg = bot.send_video(message.chat.id, video, caption = caption+desc, parse_mode= 'Markdown', reply_markup=tinder)
                video.close()
                if "сторис" in caption:
                    pass
                else:
                    bot.register_next_step_handler(msg, change_desc, msg.id)
            else:
                photo = open(content, 'rb')
                msg = bot.send_photo(message.chat.id, photo, caption = caption+desc, parse_mode= 'Markdown', reply_markup=tinder)
                photo.close()
                if "сторис" in caption:
                    pass
                else:
                    bot.register_next_step_handler(msg, change_desc, msg.id)
            return
        if (len(albums_list) != 0):
            albums_id = []
            album = albums_list[0]
            desc, caption = db_get_content(album)
            media = create_album_media(album)
            bot.delete_message(message.chat.id, message.message_id)
            album_message = bot.send_media_group(message.chat.id, media=media)
            for message in album_message:
                albums_id.append(message.id)
            set_to_bd(message.chat.id, 'album_messages', albums_id)
            msg = bot.send_message(message.chat.id, text=caption+desc, parse_mode= 'Markdown', reply_markup=tinder)
            set_active_content(message.chat.id, album)
            bot.register_next_step_handler(msg, change_desc, msg.id)
            return
        else:
            set_active_content(message.chat.id, "NO")
            bot.delete_message(message.chat.id, message.message_id)
            bot.send_message(chat_id=message.chat.id, text='Контент в данной категории отсутствует!',
                             reply_markup=admin_back_mark)

def move(rate):
    path = pathlib.WindowsPath(rate)
    no_need = str(list(path.parents)[-4])
    no_need = no_need + '\\'
    path = str(path)
    path = path.replace(no_need, '')
    path2 = os.path.dirname(path) + '\\'
    shutil.move(rate, path2)

def move2(rate):
    shutil.move(rate, "storys\\video")

def get_active_id(rate):
    path = pathlib.WindowsPath(rate)
    no_need = str(list(path.parents)[-3])
    active_id = no_need.replace("users_content\\", "")
    return active_id

def get_count_content():
    count_storys = len(construct('storys'))
    count_clips = len(construct('clips'))
    count_igtv = len(construct('igtv'))
    count_albums = len(construct('albums_posts'))
    count_other_posts = len(construct('other_posts'))
    total_count = count_storys+count_clips+count_igtv+count_albums+count_other_posts
    info = f"📁*Количество непроверенного контента:*\n📙_Сторис: {count_storys}\n📘Клипы: {count_clips}\n📗IGTV: {count_igtv}\n📕Обычные посты:_ {count_other_posts}\n📚Альбомные посты: {count_albums}\n*💾Всего:* {total_count}\n\nВыбери категорию:"
    return info

def download_ig_storys(message, username, story_id):
    Path(f'users_content/{message.chat.id}/instagram/storys/video').mkdir(parents=True, exist_ok=True)
    Path(f'users_content/{message.chat.id}/instagram/storys/photo').mkdir(parents=True, exist_ok=True)
    mess = bot.send_message(message.chat.id, text='Скачиваю...')
    try:
        a = "https://api.lamadava.com/v1/user/stories/by/username?username={}&amount=0&access_key=".format(
            quote(username))
        response = requests.get(url=a)
        result = json.loads(response.text)
        try:
            is_private = result[0]['user']['is_private']
            if is_private:
                return False
        except:
            return False
        if story_id.isdigit():
            if int(story_id) > len(result):
                return False
            else:#Скачиваем определенную сторис по юзернейму!
                story_id = int(story_id) - 1
                media_type = result[story_id]["media_type"]
                pk = result[story_id]["pk"]
                if media_type == 2:
                    url = result[story_id]['video_url']
                    if os.path.exists(f'users_content/{message.chat.id}/instagram/storys/video/' + r'{}.mp4'.format(pk)):
                        video_1 = open(f'users_content/{message.chat.id}/instagram/storys/video/' + r'{}.mp4'.format(pk),
                                       'rb')
                        bot.delete_message(mess.chat.id, mess.message_id)
                        bot.send_video(message.chat.id, video_1)
                        video_1.close()
                    else:
                        response = requests.get(url=url)
                        video = open(f'users_content/{message.chat.id}/instagram/storys/video/' + r'{}.mp4'.format(pk),
                                     "wb")
                        video.write(response.content)
                        video.close()
                        video_1 = open(f'users_content/{message.chat.id}/instagram/storys/video/' + r'{}.mp4'.format(pk),
                                       'rb')
                        bot.delete_message(mess.chat.id, mess.message_id)
                        bot.send_video(message.chat.id, video_1)
                        video_1.close()
                if media_type == 1:
                    url = result[story_id]['thumbnail_url']
                    if os.path.exists(f'users_content/{message.chat.id}/instagram/storys/photo/' + r'{}.jpeg'.format(pk)):
                        photo_1 = open(f'users_content/{message.chat.id}/instagram/storys/photo/' + r'{}.jpeg'.format(pk),
                                       'rb')
                        bot.delete_message(mess.chat.id, mess.message_id)
                        bot.send_photo(message.chat.id, photo_1)
                        photo_1.close()
                    else:
                        response = requests.get(url=url)
                        photo = open(f'users_content/{message.chat.id}/instagram/storys/photo/' + r'{}.jpeg'.format(pk),
                                     "wb")
                        photo.write(response.content)
                        photo.close()
                        photo_1 = open(f'users_content/{message.chat.id}/instagram/storys/photo/' + r'{}.jpeg'.format(pk),
                                       'rb')
                        bot.delete_message(mess.chat.id, mess.message_id)
                        bot.send_photo(message.chat.id, photo_1)
                        photo_1.close()
                try:
                    db_add_content(user_id=message.chat.id, link_content=str(pk), content_description=name_pablik)
                    old_value = get_from_bd(message.chat.id, "instagram_loaded")
                    old_value = int(old_value) + 1
                    set_to_bd(message.chat.id, "instagram_loaded", old_value)
                except sqlite3.IntegrityError:
                    if get_from_bd(message.chat.id, 'worker'):
                        bot.send_message(message.chat.id, text='Такой контент уже был загружен!')
        else:#Скачиваем все сторисы по юзернейму
            bot.delete_message(mess.chat.id, mess.message_id)
            for res in result:
                media_type = res["media_type"]
                pk = res["pk"]
                if media_type == 2:
                    url = res['video_url']
                    if os.path.exists(f'users_content/{message.chat.id}/instagram/storys/video/' + r'{}.mp4'.format(pk)):
                        video_1 = open(f'users_content/{message.chat.id}/instagram/storys/video/' + r'{}.mp4'.format(pk),
                                       'rb')
                        bot.send_video(message.chat.id, video_1)
                        video_1.close()
                    else:
                        response = requests.get(url=url)
                        video = open(f'users_content/{message.chat.id}/instagram/storys/video/' + r'{}.mp4'.format(pk),
                                     "wb")
                        video.write(response.content)
                        video.close()
                        video_1 = open(f'users_content/{message.chat.id}/instagram/storys/video/' + r'{}.mp4'.format(pk),
                                       'rb')
                        bot.send_video(message.chat.id, video_1)
                        video_1.close()
                        try:
                            db_add_content(user_id=message.chat.id, link_content=str(pk), content_description=name_pablik)
                            old_value = get_from_bd(message.chat.id, "instagram_loaded")
                            old_value = int(old_value) + 1
                            set_to_bd(message.chat.id, "instagram_loaded", old_value)
                        except sqlite3.IntegrityError:
                            if get_from_bd(message.chat.id, 'worker'):
                                bot.send_message(message.chat.id, text='Такой контент уже был загружен!')
                if media_type == 1:
                    url = res['thumbnail_url']
                    if os.path.exists(f'users_content/{message.chat.id}/instagram/storys/photo/' + r'{}.jpeg'.format(pk)):
                        photo_1 = open(f'users_content/{message.chat.id}/instagram/storys/photo/' + r'{}.jpeg'.format(pk),
                                       'rb')
                        bot.send_photo(message.chat.id, photo_1)
                        photo_1.close()
                    else:
                        response = requests.get(url=url)
                        photo = open(f'users_content/{message.chat.id}/instagram/storys/photo/' + r'{}.jpeg'.format(pk),
                                     "wb")
                        photo.write(response.content)
                        photo.close()
                        photo_1 = open(f'users_content/{message.chat.id}/instagram/storys/photo/' + r'{}.jpeg'.format(pk),
                                       'rb')
                        bot.send_photo(message.chat.id, photo_1)
                        photo_1.close()
                        try:
                            db_add_content(user_id=message.chat.id, link_content=str(pk), content_description=name_pablik)
                            old_value = get_from_bd(message.chat.id, "instagram_loaded")
                            old_value = int(old_value) + 1
                            set_to_bd(message.chat.id, "instagram_loaded", old_value)
                        except sqlite3.IntegrityError:
                            if get_from_bd(message.chat.id, 'worker'):
                                bot.send_message(message.chat.id, text='Такой контент уже был загружен!')
    except Exception as e:
        print("Ошибка при скачивании инста сторис по запросу: " + str(e))
        bot.send_message(message.chat.id,
                         text="Произошла ошибка при скачивании! Попробуйте позже...")

def create_users_list(message, page_number, edit):
    cursor.execute("SELECT user_id, user_name FROM users")
    users_list = cursor.fetchall()
    users_buttons = types.InlineKeyboardMarkup()
    users_buttons.row_width = 1
    count_users = len(users_list)
    count_page = math.ceil(count_users/10)
    end = page_number*10
    start = end - 10
    end = end-1
    for (index, elem) in enumerate(users_list):
        if (index >= start) and (index <= end):
            name = elem
            users_buttons.add(types.InlineKeyboardButton(text= str(name[1]), callback_data=str(name[0])))
    next_page = types.InlineKeyboardButton(text= "➡", callback_data="next_page_users")
    left_page = types.InlineKeyboardButton(text= "⬅", callback_data="left_page_users")
    if page_number == 1:
        users_buttons.row_width = 1
        users_buttons.add(next_page, back_admin)
    elif page_number == count_page:
        users_buttons.row_width = 1
        users_buttons.add(left_page, back_admin)
    else:
        users_buttons.row_width = 2
        users_buttons.add(left_page, next_page)
        users_buttons.row_width = 1
        users_buttons.add(back_admin)
    if edit == True:
        bot.edit_message_text(chat_id = message.chat.id, message_id = message.message_id, text = "Страница: {}\{}".format(page_number, count_page), reply_markup=users_buttons)
    else:
        bot.delete_message(message.chat.id, message.message_id)
        bot.send_message(message.chat.id, text = "Страница: {}\{}".format(page_number, count_page), reply_markup=users_buttons)

def get_stat_info(id):
    cursor.execute("SELECT user_name, user_surname, username, worker, approved_content, yt_loaded, tiktok_loaded, instagram_loaded, pinterest_loaded FROM users WHERE user_id = {}".format(id))
    user_info = cursor.fetchone()
    name = user_info[0]
    surname = user_info[1]
    username = user_info[2]
    worker = user_info[3]
    if worker:
        worker = 'рабочий'
    else:
        worker = 'обычный пользователь'
    if surname == None:
        surname = 'информация отсутствует!'
    if username == None:
        username = 'информация отсутствует!'
    else:
        username = '@'+username
    total_loaded = int(user_info[5])+int(user_info[6])+int(user_info[7])+int(user_info[8])
    if (int(user_info[4]) != 0) and (int(total_loaded) != 0):
        sootnohenie = int(user_info[4]) / int(total_loaded)
        procent = round(sootnohenie * 100, 2)
    else:
        procent = 0
    info = "🆔: {}\n▫*Имя:* *{}*\n▫*Фамилия:* *{}*\n▫*Юзернейм:* *{}*\n▫*Статус:* _{}_\n\n⬇*Загруженный контент:* \n🔴YouTube: {}\n🟣TikTok: {}\n🟢Instagram: {}\n🟡Pinterest: {}\n\n✅Одобрено: {}/{}\n🔣*Процент совпадения вкуса:* {}%".format(id,
                        name, surname, username, worker, user_info[5], user_info[6], user_info[7],
                                            user_info[8], user_info[4], total_loaded, str(procent))
    return info


@bot.message_handler(commands=['start'])
def start(message):
    if check_subscribe(bot.get_chat_member(chat_id='@squanch_tv', user_id=message.from_user.id).status):
        if get_all_id(message.from_user.id):
            bot.send_video(message.chat.id,video=open('welcome.mp4', 'rb'), caption =hello)
        else:
            db_add_user(user_id=message.from_user.id, user_name=message.from_user.first_name,
                        user_surname=message.from_user.last_name,
                        username=message.from_user.username)
            bot.send_video(message.chat.id,video=open('welcome.mp4', 'rb'), caption =hello)
    else:
        bot.send_message(message.chat.id, text=podpiska, reply_markup=subscribe)

@bot.message_handler(commands=['help'])
def help(message):
    bot.send_video(message.chat.id,video=open('help.mp4', 'rb'), caption = help_msg, parse_mode='Markdown')

@bot.message_handler(content_types=['text'])
def link(message):
    if check_subscribe(bot.get_chat_member(chat_id='@squanch_tv', user_id=message.from_user.id).status):
        if get_all_id(message.from_user.id):
            if 'tiktok.com' in message.text:
                tiktok_download(message.text, message)
            elif message.text.startswith('https://youtube.com/'):
                youtube_download(message.text, message)
            elif 'instagram.com' in message.text:
                instagram_download(message.text, message)
            elif 'https://pin.it/' in message.text:
                pinterest_download(re.findall(r'(https?://\S+)', message.text)[0], message)
            elif (message.text).startswith('@'):
                info = (message.text).split('-')
                if len(info) == 2:
                    result = download_ig_storys(message, info[0].replace("@", ""), info[1])
                    print(result)
                    if result == False:
                        bot.send_message(message.chat.id, text = "Произошла ошибка, возможные  причины:\nВы неверно указали номер истории, её не существует!\nАккаунт закрыт!\nАккаунт не имеет активных историй!")
                else:
                    bot.send_message(message.chat.id, text="❌Неверно указан запрос!\nВведите /help и прочитайте инструкцию!")
            elif ('nikiska' in (message.text).lower()) and (message.chat.id == tg1 or tg2):
                bot.send_message(message.chat.id, text="Админ-панель:", reply_markup=admin_menu)
            else:
                bot.send_message(message.chat.id, text="❌Неверная ссылка!")
        else:
            db_add_user(user_id=message.from_user.id, user_name=message.from_user.first_name,
                        user_surname=message.from_user.last_name,
                        username=message.from_user.username)
            bot.send_video(message.chat.id, video=open('welcome.mp4', 'rb'), caption=hello)
    else:
        bot.send_message(message.chat.id, text=podpiska, reply_markup=subscribe)


@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    if call.message:
        if call.data == "subscribed":
            if check_subscribe(bot.get_chat_member(chat_id='@squanch_tv', user_id=call.message.chat.id).status):
                if get_all_id(call.message.from_user.id):
                    bot.send_video(call.message.chat.id, video=open('welcome.mp4', 'rb'), caption=hello)
                else:
                    db_add_user(user_id=call.message.chat.id, user_name=call.from_user.first_name,
                                user_surname=call.from_user.last_name,
                                username=call.from_user.username)
                    bot.send_video(call.message.chat.id, video=open('welcome.mp4', 'rb'), caption=hello)
            else:
                bot.send_message(call.message.chat.id, text=podpiska, reply_markup=subscribe)
            return
        if call.data == "back_admin":
            bot.clear_step_handler_by_chat_id(chat_id=call.message.chat.id)
            if "album" in str(get_active_content(call.message.chat.id)):
                messages = literal_eval(get_from_bd(call.message.chat.id, 'album_messages'))
                if len(messages) > 1:
                    for message in messages:
                        bot.delete_message(chat_id=call.message.chat.id, message_id=message)
            bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.id)
            bot.send_message(chat_id=call.message.chat.id, text="Админ-панель:", reply_markup=admin_menu)
            set_active_content(call.message.chat.id, "NO")
            set_to_bd(call.message.chat.id, 'active_menu', 'menu')
            return
        if call.data == "content_rate":
            count = get_count_content()
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text=count, parse_mode='Markdown', reply_markup=rate_content)
            return
        if call.data == "story_view":
            send_anket(call.message, 'storys')
            set_to_bd(call.message.chat.id, 'active_menu', 'storys')
            return
        if call.data == "reels_view":
            send_anket(call.message, 'clips')
            set_to_bd(call.message.chat.id, 'active_menu', 'clips')
            return
        if call.data == 'igtv_view':
            send_anket(call.message, 'igtv')
            set_to_bd(call.message.chat.id, 'active_menu', 'igtv')
            return
        if call.data == 'other_posts_view':
            send_anket(call.message, 'other_posts')
            set_to_bd(call.message.chat.id, 'active_menu', 'other_posts')
            return
        if call.data == 'albums_posts_view':
            send_anket(call.message, 'albums_posts')
            set_to_bd(call.message.chat.id, 'active_menu', 'albums_posts')
            return
        if call.data == 'all_view':
            send_anket(call.message, 'all')
            set_to_bd(call.message.chat.id, 'active_menu', 'all')
            return
        if call.data == "yes":
            bot.clear_step_handler_by_chat_id(chat_id=call.message.chat.id)
            bot.answer_callback_query(callback_query_id=call.id, text='Принято')
            rate = str(get_active_content(call.message.chat.id))
            active_menu = get_from_bd(call.message.chat.id, 'active_menu')
            active_id = get_active_id(rate)
            id_media = str(os.path.splitext(os.path.basename(rate))[0])
            cursor.execute(f"SELECT content_description FROM contents WHERE link_content = '{id_media}'")
            desc_db = cursor.fetchone()
            if desc_db != None:
                desc_db = desc_db[0]
            else:
                desc_db = name_pablik
            if "album" in rate:
                messages = literal_eval(get_from_bd(call.message.chat.id, 'album_messages'))
                if len(messages) >= 1:
                    for message in messages:
                        bot.delete_message(chat_id=call.message.chat.id, message_id=message)
                move(rate)
                old_value = get_from_bd(active_id, "approved_content")
                old_value = int(old_value) + 1
                set_to_bd(active_id, "approved_content", old_value)
                send_anket(call.message, active_menu)
            else:
                move(rate)
                old_value = get_from_bd(active_id, "approved_content")
                old_value = int(old_value) + 1
                set_to_bd(active_id, "approved_content", old_value)
                send_anket(call.message, active_menu)
            db_table_val(media_pk=str(id_media), media_description=str(desc_db))
            return
        if call.data == 'yes_story':
            bot.clear_step_handler_by_chat_id(chat_id=call.message.chat.id)
            bot.answer_callback_query(callback_query_id=call.id, text='Принято')
            rate = str(get_active_content(call.message.chat.id))
            active_menu = get_from_bd(call.message.chat.id, 'active_menu')
            active_id = get_active_id(rate)
            id_media = str(os.path.splitext(os.path.basename(rate))[0])
            cursor.execute(f"SELECT content_description FROM contents WHERE link_content = '{id_media}'")
            desc_db = cursor.fetchone()
            if desc_db != None:
                desc_db = desc_db[0]
            else:
                desc_db = name_pablik
            move2(rate)
            old_value = get_from_bd(active_id, "approved_content")
            old_value = int(old_value) + 1
            set_to_bd(active_id, "approved_content", old_value)
            send_anket(call.message, active_menu)
            db_table_val(media_pk=str(id_media), media_description=str(desc_db))
            return
        if call.data == 'no':
            bot.clear_step_handler_by_chat_id(chat_id=call.message.chat.id)
            bot.answer_callback_query(callback_query_id=call.id, text='Удалено!')
            rate = str(get_active_content(call.message.chat.id))
            active_menu = get_from_bd(call.message.chat.id, 'active_menu')
            if "album" in rate:
                messages = literal_eval(get_from_bd(call.message.chat.id, 'album_messages'))
                if len(messages) >= 1:
                    for message in messages:
                        bot.delete_message(chat_id=call.message.chat.id, message_id=message)
                shutil.rmtree(rate)
            else:
                os.remove(rate)
            send_anket(call.message, active_menu)
            return
        if call.data == 'statistics':
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text='Выбери тип статистики:', reply_markup=statistics_menu)
            return
        if call.data == 'users_stat_list':
            create_users_list(call.message, 1, False)
            set_to_bd(call.message.chat.id, 'active_menu', 1)
            return
        if call.data == 'next_page_users':
            page = int(get_from_bd(call.message.chat.id, "active_menu"))
            page += 1
            create_users_list(call.message, page, True)
            set_to_bd(call.message.chat.id, 'active_menu', int(page))
            return
        if call.data == 'left_page_users':
            page = int(get_from_bd(call.message.chat.id, "active_menu"))
            page -= 1
            create_users_list(call.message, page, True)
            set_to_bd(call.message.chat.id, 'active_menu', int(page))
            return
        if call.data == "back_to_list_users":
            create_users_list(call.message, int(get_from_bd(call.message.chat.id, "active_menu")), False)
            return
        if call.data == 'full_statistic':
            cursor.execute("SELECT COUNT(user_id), SUM(yt_loaded), SUM(tiktok_loaded), SUM(instagram_loaded), SUM(pinterest_loaded), SUM(approved_content) FROM users")
            stat_info = cursor.fetchone()
            cursor.execute("SELECT COUNT(worker) FROM users WHERE worker = 1")
            workers = cursor.fetchone()[0]
            info = f"📊*Статистика:*\n👥_Всего пользователей: {stat_info[0]}\n🕵️‍Работники: {workers}_\n\n⬇*Всего загружено:*\n🟣_TikTok: {stat_info[2]}\n🟢Instagram: {stat_info[3]}\n🔴YouTube: {stat_info[1]}\n🟡Pinterest: {stat_info[4]}_\n\n✅*Одобрено:* {stat_info[5]}"
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
                                  text=info, parse_mode='Markdown', reply_markup=admin_back_mark)
            return
        else:
            cursor.execute("SELECT user_id FROM users")
            users_list = cursor.fetchall()
            if call.data in str(users_list):
                info = get_stat_info(call.data)
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text = info, parse_mode='Markdown', reply_markup=back_to_list)


if __name__ == '__main__':
    while True:
        try:
            bot.infinity_polling()
        except:
            time.sleep(5)