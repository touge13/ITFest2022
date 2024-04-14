# -*- coding:utf-8-*-

from email import message
import requests 
import time
import datetime
import psycopg2
import urllib.parse as up
from config import password, token_api

up.uses_netloc.append("postgres")
db = psycopg2.connect(f"dbname='cohgnoux' user='cohgnoux' host='ruby.db.elephantsql.com' password={password}")
cursor = db.cursor()


while True:
    domain_list = []
    cursor.execute(f"SELECT name FROM news")
    result = cursor.fetchall()
    for row in result:
        for x in row:    
            result = x
            test = []
            for letters in x:
                test.append(letters) 
            if test[0] != '#':
                domain_list.append(x)
    print(domain_list)
    for domain in domain_list:

        request = requests.get(f'https://vk.com/{domain}')
        if request.status_code == 200:
            print('Web site exists')
        
            def take_posts():
                token = token_api
                version = 5.92
                count = 1
                offset = 0
                all_posts = []
                response = requests.get('https://api.vk.com/method/wall.get?', 
                                        params = {
                                            'domain':domain,
                                            'count':count,
                                            'access_token':token,
                                            'v':version,
                                            'offset':offset
                                        }
                                        )
                data = response.json()['response']['items']
                all_posts.extend([data])
                return all_posts

            def file_writer(all_posts):
                for post in all_posts:
                    try:
                        id_news = post[0]['id']
                        false = 0

                        try: #автор прикрепил медиа
                            print('check', len(post[0]['attachments']))
                            i = 0
                            url = []
                            while i < len(post[0]['attachments']):
                                if post[0]['attachments'][i]['type'] == 'video':
                                    #формируем данные для составления запроса на получение ссылки на видео
                                    video_access_key = post[0]['attachments'][i]["video"]["access_key"]
                                    video_post_id = post[0]['attachments'][i]["video"]["id"]
                                    video_owner_id = post[0]['attachments'][i]["video"]["owner_id"]
                                    token = '506a29dc0671cdfd104a1aec51ecdf8aa714f24b556090d77578409d0b4c0c45257fb2bbc1e12f13bbe1a'
                                    video_get_url = f"https://api.vk.com/method/video.get?videos={video_owner_id}_{video_post_id}_{video_access_key}&access_token={token}&v=5.92"
                                    req = requests.get(video_get_url)
                                    res = req.json()
                                    result = res["response"]["items"][0]["player"]
                                    url.append(result)
                                elif post[0]['attachments'][i]['type'] == 'photo':
                                    photo_extension = []
                                    for extension_vocabulary in post[0]['attachments'][i]['photo']['sizes']:
                                        photo_extension.append(extension_vocabulary['height'])
                                    max_extension = photo_extension.index(max(photo_extension))
                                    result = post[0]['attachments'][i]['photo']['sizes'][max_extension]['url']
                                    url.append(result)
                                else:
                                    print("Other media format")
                                i = i + 1
                        except:
                            #автор не прикреплял медиа
                            false = false + 1

                        try: #есть медиа в репосте
                            print('check', len(post[0]['copy_history'][0]['attachments']))
                            i = 0
                            url = []
                            #на случай если в новости больше одной фотографии
                            while i < len(post[0]['copy_history'][0]['attachments']):
                                if post[0]['copy_history'][0]['attachments'][i]['type'] == 'video':
                                    #формируем данные для составления запроса на получение ссылки на видео
                                    video_access_key = post[0]['copy_history'][0]['attachments'][i]["video"]["access_key"]
                                    video_post_id = post[0]['copy_history'][0]['attachments'][i]["video"]["id"]
                                    video_owner_id = post[0]['copy_history'][0]['attachments'][i]["video"]["owner_id"]
                                    token = '506a29dc0671cdfd104a1aec51ecdf8aa714f24b556090d77578409d0b4c0c45257fb2bbc1e12f13bbe1a'
                                    video_get_url = f"https://api.vk.com/method/video.get?videos={video_owner_id}_{video_post_id}_{video_access_key}&access_token={token}&v=5.92"
                                    req = requests.get(video_get_url)
                                    res = req.json()
                                    result = res["response"]["items"][0]["player"]
                                    url.append(result)
                                elif post[0]['copy_history'][0]['attachments'][i]['type'] == 'photo':
                                    photo_extension = []
                                    for extension_vocabulary in post[0]['attachments'][i]['photo']['sizes']:
                                        photo_extension.append(extension_vocabulary['height'])
                                    max_extension = photo_extension.index(max(photo_extension))
                                    result = post[0]['attachments'][i]['photo']['sizes'][max_extension]['url']
                                    url.append(result)
                                else:
                                    print("Other media format")
                                i = i + 1
                        except:
                           #в репосте нет прикрепленного медиа
                            false = false + 1

                        if false == 2:
                            url = 'None'
                            #вообще нет прикрепленного медиа

                        if post[0]["text"] == 'None':
                            if post[0]['copy_history'][0]['text'] == 'None':
                                body = 'None'
                            else:
                                body = str(post[0]['copy_history'][0]['text'])

                        else:
                            body = post[0]['text']
                            try:
                                if post[0]['copy_history'][0]['text'] == 'None':
                                    body = str(post[0]['text'])
                                else:
                                    #в репосте есть текст
                                    body = str(post[0]['text']) + '\n' + str(post[0]['copy_history'][0]['text'])

                            except KeyError:
                                pass
                                #в репосте нет текста

                        hashtags = []
                        cursor.execute(f"SELECT name FROM news")
                        result = cursor.fetchall()
                        for row in result:
                            for x in row:    
                                result = x
                                test = []
                                for letters in x:
                                    test.append(letters) 
                                if test[0] == '#':
                                    hashtags.append(x)

                        print(hashtags)
                        for hashtag in hashtags:
                            if hashtag in body:
                                cursor.execute(f"SELECT id_news FROM news WHERE name = '{hashtag}'")
                                result = cursor.fetchall()
                                for row in result:
                                    for x in row:    
                                        result = x

                                if id_news == result:
                                    pass
                                else:
                                    #дата публикации новости
                                    today = datetime.datetime.today()
                                    data_reg = today.strftime("%d.%m.%Y")

                                    sql = "UPDATE news SET id_news = %s, body = %s, url = %s, date = %s WHERE name = %s"
                                    val = (id_news, body, url, data_reg, hashtag)
                                    cursor.execute(sql, val)
                                    db.commit()  

                                    result = []
                                    letters = []
                                    for letter in hashtag:
                                        letters.append(letter)
                                    try:
                                        letters.remove('#')
                                    except:
                                        pass
                                    try:
                                        letters.remove('.')
                                    except:
                                        pass
                                    try:
                                        letters.remove('_')
                                    except:
                                        pass
                                    try:
                                        letters.remove('-')
                                    except:
                                        pass
                                    calldata =  "".join(letters)
                                    result.append(calldata.lower())

                                    letters = []
                                    for letter in hashtag:
                                        letters.append(letter)
                                    if letters[0] == '#':
                                        sel = result[0] + '_h'
                                    else:
                                        sel = result[0] + '_d'

                                    cursor.execute(f'SELECT id_news FROM {sel}')
                                    res1 = cursor.fetchall()
                                    res = []
                                    for row in res1:
                                        for x in row:
                                            res.append(x)
                                    if len(res) > 0:
                                        if len(res1) > 4:
                                            cursor.execute(f"DELETE FROM {sel} WHERE id_news = {res[0]}")
                                            db.commit()
                                            sql = f"INSERT INTO {sel} (id_news, body, url, date) VALUES (%s, %s, %s, %s)"
                                            val = (id_news, body, url, data_reg)
                                            cursor.execute(sql, val)
                                            db.commit()
                                        else:
                                            sql = f"INSERT INTO {sel} (id_news, body, url, date) VALUES (%s, %s, %s, %s)"
                                            val = (id_news, body, url, data_reg)
                                            cursor.execute(sql, val)
                                            db.commit()  
                                    else:
                                        sql = f"INSERT INTO {sel} (id_news, body, url, date) VALUES (%s, %s, %s, %s)"
                                        val = (id_news, body, url, data_reg)
                                        cursor.execute(sql, val)
                                        db.commit()

                            else:
                                cursor.execute(f"SELECT id_news FROM news WHERE name = '{domain}'")
                                result = cursor.fetchall()
                                for row in result:
                                        for x in row:    
                                            result = x

                                if id_news == result:
                                    pass
                                else:
                                    #дата публикации новости
                                    today = datetime.datetime.today()
                                    data_reg = today.strftime("%d.%m.%Y")

                                    sql = "UPDATE news SET id_news = %s, body = %s, url = %s, date = %s WHERE name = %s"
                                    val = (id_news, body, url, data_reg, domain)
                                    cursor.execute(sql, val)
                                    db.commit()   

                                    result_d = []
                                    letters = []
                                    for letter in domain:
                                        letters.append(letter)
                                    try:
                                        letters.remove('#')
                                    except:
                                        pass
                                    try:
                                        letters.remove('.')
                                    except:
                                        pass
                                    try:
                                        letters.remove('_')
                                    except:
                                        pass
                                    try:
                                        letters.remove('-')
                                    except:
                                        pass
                                    calldata =  "".join(letters)
                                    result_d.append(calldata.lower())

                                    letters = []
                                    for letter in domain:
                                        letters.append(letter)
                                    if letters[0] == '#':
                                        sel = result_d[0] + '_h'
                                    else:
                                        sel = result_d[0] + '_d'

                                    cursor.execute(f'SELECT id_news FROM {sel}')
                                    res1 = cursor.fetchall()
                                    res = []
                                    for row in res1:
                                        for x in row:
                                            res.append(x)
                                    if len(res) > 0: 
                                        if len(res1) > 4:
                                            cursor.execute(f"DELETE FROM {sel} WHERE id_news = {res[0]}")
                                            db.commit()
                                            sql = f"INSERT INTO {sel} (id_news, body, url, date) VALUES (%s, %s, %s, %s)"
                                            val = (id_news, body, url, data_reg)
                                            cursor.execute(sql, val)
                                            db.commit()
                                        else:
                                            sql = f"INSERT INTO {sel} (id_news, body, url, date) VALUES (%s, %s, %s, %s)"
                                            val = (id_news, body, url, data_reg)
                                            cursor.execute(sql, val)
                                            db.commit()
                                    else:
                                        sql = f"INSERT INTO {sel} (id_news, body, url, date) VALUES (%s, %s, %s, %s)"
                                        val = (id_news, body, url, data_reg)
                                        cursor.execute(sql, val)
                                        db.commit()

                        print(id_news)
                        print(url)
                        print(body) 
                        print('===========================================================================================================')

                    except IndexError:
                        print('There is no news in the group')
                        print('===========================================================================================================')

            all_posts = take_posts()
            file_writer(all_posts)

        else:
            print('Web site does not exist')
    
    time.sleep(100)