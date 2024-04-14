from hashlib import new
from operator import ne
from types import new_class
from flask import Flask, flash, redirect, render_template, request, url_for
import secrets
import psycopg2
import urllib.parse as up
import requests

password = 'your_password'

#подключаемся к бд
up.uses_netloc.append("postgres")
db = psycopg2.connect(f"dbname='cohgnoux' user='cohgnoux' host='ruby.db.elephantsql.com' password={password}")
cursor = db.cursor()

app = Flask(__name__)
secret = secrets.token_urlsafe(32)
app.secret_key = secret


log_lst = []
cursor.execute(f"SELECT login FROM webinfo")
result = cursor.fetchone()
for login_bd in result:
    log_lst.append(login_bd)

psw_lst = []
cursor.execute(f"SELECT password FROM webinfo")
result = cursor.fetchone()
for password_bd in result:
    psw_lst.append(password_bd)


login_page = log_lst[0]
password_page = psw_lst[0]

authorization = 0

@app.route('/')
def index():
    return render_template('index.html')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.route("/login/", methods=['GET', 'POST'])
def login():
    global authorization
    error = None
    if request.method == 'POST':
        if request.form['username'] != login_page or request.form['password'] != password_page:
            error = 'Неверные учетные данные'
        else:
            authorization = 1
            return redirect(url_for('settings'))
    return render_template('login.html', error=error)


@app.route("/settings/", methods=['GET', 'POST'])
def settings():
    global authorization
    if authorization == 1:
        return render_template('settings.html')
    else:
        return redirect(url_for('login'))

@app.route("/domain/", methods=['GET', 'POST'])
def domain():
    global authorization
    if authorization == 1:
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

        error = None
        if request.method == 'POST':
            addbutton = request.form.get("add")
            deletebutton = request.form.get("delete")
            domain = request.form['add_domain']
            if domain == '':
                pass
            else:
                letters = []
                for letter in domain:
                    letters.append(letter)
                if letters[0] != '#':
                    if addbutton is not None:
                        if len(domain_list) > 20:
                            error = 'Групп не может быть больше 20'
                        else:
                            request_check = requests.get(f'https://vk.com/{domain}')
                            if domain in domain_list:
                                error = 'Такой домен уже существует'
                            elif request_check.status_code == 200:
                                print('Web site exists')
                                sel = domain + '_d'
                                cursor.execute(f"ALTER TABLE ONLY users ADD COLUMN {sel} varchar(30) DEFAULT '0'")
                                cursor.execute(f'''CREATE TABLE {sel} (id_news INT, body VARCHAR, url VARCHAR, date VARCHAR); ''')
                                sql = "INSERT INTO news (id_news, body, url, name, date) VALUES (%s, %s, %s, %s, %s)"
                                val = (0, '', '', domain, '')
                                cursor.execute(sql, val)
                                db.commit()
                            else:
                                print('Web site does not exist')
                                error = 'Группы с таким доменом не существует'
                    elif deletebutton is not None:
                        if len(domain_list) > 0:
                            if domain in domain_list:
                                res = []
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
                                res.append(calldata.lower())

                                sel = res[0] + '_d'
                                cursor.execute(f"ALTER TABLE users DROP COLUMN {sel}")
                                cursor.execute(f''' DROP TABLE {sel}; ''')
                                cursor.execute(f"DELETE FROM news WHERE name='{domain}'")
                                db.commit()
                            else:
                                error = 'Такого домена итак не существует'
                        else:
                            error = 'В базе и так нет ни одного домена'
                else:
                    error = 'Домен не начинается с "#"'

            for opt in domain_list:
                deletebutton = request.form.get(opt)
                if deletebutton is not None:
                    res = []
                    letters = []
                    for letter in opt:
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
                    res.append(calldata.lower())

                    drp = res[0] + '_d'
                    cursor.execute(f"ALTER TABLE users DROP COLUMN {drp}")
                    cursor.execute(f''' DROP TABLE {drp} ''')
                    cursor.execute(f"DELETE FROM news WHERE name='{res[0]}'")
                    db.commit()
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
        return render_template('domain.html', option_domains = domain_list, error = error)
    else:
        return redirect(url_for('login'))

@app.route("/hashtag/", methods=['GET', 'POST'])
def hashtag():
    global authorization
    if authorization == 1:
        hashtags_list = []
        cursor.execute(f"SELECT name FROM news")
        result = cursor.fetchall()
        for row in result:
            for x in row:    
                result = x
                test = []
                for letters in x:
                    test.append(letters) 
                if test[0] == '#':
                    hashtags_list.append(x)

        error = None
        if request.method == 'POST':
            addbutton = request.form.get("add")
            deletebutton = request.form.get("delete")
            hashtag = request.form['add_hashtag']
            if hashtag == '':
                pass
            else:
                letters = []
                for letter in hashtag:
                    letters.append(letter)
                if letters[0] == '#':
                    if addbutton is not None:
                        if len(hashtags_list) > 20:
                            error = 'Хэштэгов не может быть больше 20'
                        else:
                            if hashtag in hashtags_list:
                                error = 'Такой хэштэг уже существует'
                            else:
                                hashtagnew = []
                                for hashtagtable in hashtag:
                                    hashtagnew.append(hashtagtable)
                                hashtagnew.remove('#')
                                res = "".join(hashtagnew)

                                sel = res + '_h'
                                cursor.execute(f"ALTER TABLE ONLY users ADD COLUMN {sel} varchar(30) DEFAULT '0'")
                                cursor.execute(f'''CREATE TABLE {sel} (id_news INT, body VARCHAR, url VARCHAR, date VARCHAR); ''')
                                sql = "INSERT INTO news (id_news, body, url, name, date) VALUES (%s, %s, %s, %s, %s)"
                                val = (0, '', '', hashtag, '')
                                cursor.execute(sql, val)
                                db.commit()

                    elif deletebutton is not None:
                        if len(hashtags_list) > 0:
                            if hashtag in hashtags_list:
                                res = []
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
                                res.append(calldata.lower())

                                sel = res[0] + '_h'
                                cursor.execute(f"ALTER TABLE users DROP COLUMN {sel}")
                                cursor.execute(f''' DROP TABLE {sel}; ''')
                                cursor.execute(f"DELETE FROM news WHERE name='{hashtag}'")
                                db.commit()
                            else:
                                error = 'Такого хэштэга итак не существует'
                        else:
                            error = 'В базе и так нет ни одного хэштэга'
                else:
                    error = 'Хэштэг начинается с "#"'

            for opt in hashtags_list:
                deletebutton = request.form.get(opt)
                if deletebutton is not None:
                    res = []
                    letters = []
                    for letter in opt:
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
                    res.append(calldata.lower())

                    drp = res[0] + '_h'
                    cursor.execute(f"ALTER TABLE users DROP COLUMN {drp}")
                    cursor.execute(f''' DROP TABLE {drp} ''')
                    cursor.execute(f"DELETE FROM news WHERE name='{opt}'")
                    db.commit()
        hashtags_list = []
        cursor.execute(f"SELECT name FROM news")
        result = cursor.fetchall()
        for row in result:
            for x in row:    
                result = x
                test = []
                for letters in x:
                    test.append(letters) 
                if test[0] == '#':
                    hashtags_list.append(x)
        return render_template('hashtag.html', option_hashtags = hashtags_list, error = error)
    else:
        return redirect(url_for('login'))

page = 1
@app.route('/setuser/p=<slug>', methods=['GET', 'POST'])
def page(slug):
    global authorization
    global page
    try:
        page = int(slug)
    except:
        pass

    if authorization == 1:
        users_list = []
        cursor.execute(f"SELECT id FROM users")
        result = cursor.fetchall()
        for row in result:
            for x in row:    
                users_list.append(x)

        users_in_one_page = 10
        pages = len([users_list[i:i+users_in_one_page] for i in range(0,len(users_list),users_in_one_page)])
        if len(users_list) == 0:
            pages = 1
        if page+1 in range(2,pages+2):   
            if len(users_list) != 0:    
                list_lists = [users_list[i:i+users_in_one_page] for i in range(0,len(users_list),users_in_one_page)]
                try:
                    option_users = list_lists[page-1]  
                except IndexError:
                    option_users = list_lists[0]       
            if request.method == 'POST':
                addbutton = request.form.get("add")
                deletebutton = request.form.get("delete")
                user_id = request.form['add_user']
                if user_id == '':
                    pass
                else:             
                    if addbutton is not None:
                        cursor.execute(f"SELECT id FROM users WHERE id = {user_id}")
                        result = cursor.fetchone()
                        if result is None:
                            sql = f"INSERT INTO users (id, nauchimonline_d) VALUES (%s, %s)"
                            val = (user_id, '1')
                            cursor.execute(sql, val)
                            db.commit()
                    elif deletebutton is not None:
                        cursor.execute(f"SELECT id FROM users WHERE id = {user_id}")
                        result = cursor.fetchone()
                        if result is not None:
                            user_id = int(user_id)
                            cursor.execute(f"DELETE FROM users WHERE id = {user_id}")
                            db.commit()     
                for opt in users_list:
                    opt = str(opt)
                    deletebutton = request.form.get(opt)
                    if deletebutton is not None:
                        opt = int(opt)
                        cursor.execute(f"DELETE FROM users WHERE id = {opt}")
                        db.commit()

            users_list = []
            cursor.execute(f"SELECT id FROM users")
            result = cursor.fetchall()
            for row in result:
                for x in row:    
                    users_list.append(x)        

            if len(users_list) != 0:
                list_lists = [users_list[i:i+users_in_one_page] for i in range(0,len(users_list),users_in_one_page)]
                try:
                    option_users = list_lists[page-1]  
                except IndexError:
                    option_users = list_lists[0]    
                rt = []
                cursor.execute(f"SELECT id FROM users WHERE rights = '1'")
                result = cursor.fetchall()
                for row in result:
                    for x in row:    
                        rt.append(x)   
            pages = len([users_list[i:i+users_in_one_page] for i in range(0,len(users_list),users_in_one_page)])
            
            try:
                page = int(slug)  
            except:
                page = 1 

            if len(users_list) == 0:
                pages = 1
                page = 1
                option_users = [0]
                rt = [0]
            return render_template('setuser.html', option_users = option_users, pages = pages, page = page, rt=rt, len = len(users_list), opt_len = len(option_users))
        else:
            return render_template('404.html')
    else:
        return redirect(url_for('login'))

@app.route('/setuser/<slug>', methods=['GET', 'POST'])
def post(slug):
    global authorization
    users_list = []
    cursor.execute(f"SELECT id FROM users")
    result = cursor.fetchall()
    for row in result:
        for x in row:    
            users_list.append(x)

    new_users_list = []
    for i in users_list:
        new_users_list.append(str(i))

    process_for_refresh = '0'

    admin = ''
    
    if slug in new_users_list:
        if authorization == 1:
            cursor.execute(f"SELECT rights FROM users WHERE id = '{slug}'")
            result = cursor.fetchone()

            for right in result:
                if right == "0":
                    admin = '0'
                elif right == "1":
                    admin = '1'

            update_id = request.form.get("update_id_html", False)
            save_button = request.form.get("save")
            adminbutton = request.form.get("admin")
            notadminbutton = request.form.get("notadmin")

            if save_button is not None:
                cursor.execute(f"UPDATE users SET id = '{update_id}' WHERE id = '{int(slug)}'")
                db.commit()
                option_id = str(update_id)
                process_for_refresh = '1'
            else:
                option_id = str(slug)

            if adminbutton is not None:
                cursor.execute(f"UPDATE users SET rights = '1' WHERE id = '{option_id}'")
                db.commit()
                process_for_refresh = '1'
            elif notadminbutton is not None:
                cursor.execute(f"UPDATE users SET rights = '0' WHERE id = '{option_id}'")
                db.commit()
                process_for_refresh = '1'

            domain_list = []
            cursor.execute(f"SELECT name FROM news ORDER BY num")
            result = cursor.fetchall()
            for row in result:
                for x in row:    
                    domain_list.append(x)
            buttons = []
            i=0
            while i < len(domain_list): 
                calldata_list = []
                for domain in domain_list:
                    letters = []
                    for letter in domain:
                        letters.append(letter)
                    h = ''
                    if letters[0] == '#':
                        h = 1
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

                    if h == 1:
                        calldata_list.append(calldata.lower()+'_h')
                    else:
                        calldata_list.append(calldata.lower()+'_d')

                cursor.execute(f"SELECT {calldata_list[i]} FROM users WHERE id = {option_id}")
                user_sub_status = []
                all_sub_status = cursor.fetchone()
                for status in all_sub_status:
                    user_sub_status.append(status)

                if user_sub_status[0] == '0':
                    buttons.append('0')

                elif user_sub_status[0] == '1':
                    buttons.append('1')

                i+=1

            calldata = []
            for domain in domain_list:
                letters = []
                for letter in domain:
                    letters.append(letter)
                h = ''
                if letters[0] == '#':
                    h = 1
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
                calldata_str =  "".join(letters)

                if h == 1:
                    calldata.append(calldata_str.lower()+'_h')
                else:
                    calldata.append(calldata_str.lower()+'_d')

            for opt in calldata:
                subbutton = request.form.get(opt+'sub')
                unsubbutton = request.form.get(opt+'unsub')
                if subbutton is not None:
                    cursor.execute(f"UPDATE users SET {opt} = '1' WHERE id = '{option_id}'")
                    db.commit()
                    process_for_refresh = '1'
                elif unsubbutton is not None:
                    cursor.execute(f"UPDATE users SET {opt} = '0' WHERE id = '{option_id}'")
                    db.commit()
                    process_for_refresh = '1'

            return render_template('usersettings.html', option_id = option_id, process = process_for_refresh, admin = admin, domain_list = domain_list, len = len(domain_list), option_buttons = buttons, calldata = calldata, page = page)
        else:
            return redirect(url_for('login'))
    else:
        return render_template('404.html')

@app.route("/lastfive/", methods=['GET', 'POST'])
def lastfivemenu():  
    domain_list = []
    cursor.execute(f"SELECT name FROM news ORDER BY num")
    result = cursor.fetchall()
    for row in result:
        for x in row:    
            domain_list.append(x)

    calldata = []
    for domain in domain_list:
        letters = []
        for letter in domain:
            letters.append(letter)
        h = ''
        if letters[0] == '#':
            h = 1
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
        calldata_str =  "".join(letters)

        if h == 1:
            calldata.append(calldata_str.lower()+'_h')
        else:
            calldata.append(calldata_str.lower()+'_d')

    return render_template('lastfivemenu.html', calldata = calldata, domain_list = domain_list, len = len(domain_list))

@app.route('/lastfive/<slug>', methods=['GET', 'POST'])
def lastfivepage(slug):
    domain_list = []
    cursor.execute(f"SELECT name FROM news ORDER BY num")
    result = cursor.fetchall()
    for row in result:
        for x in row:    
            domain_list.append(x)

    calldata = []
    for domain in domain_list:
        letters = []
        for letter in domain:
            letters.append(letter)
        h = ''
        if letters[0] == '#':
            h = 1
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
        calldata_str =  "".join(letters)

        if h == 1:
            calldata.append(calldata_str.lower()+'_h')
        else:
            calldata.append(calldata_str.lower()+'_d')

    if slug in calldata:
        error = None
        cursor.execute(f"SELECT * FROM {slug}")
        all_news_check = cursor.fetchall()
        if len(all_news_check) != 0:
            lastfivenews_list = []
            cursor.execute(f"SELECT body FROM {slug}")
            body = cursor.fetchall()
            for body1 in body:
                for body2 in body1:
                    if body2 is not None:
                        if body2 != '':
                            lastfivenews_list.append(body2)
                        else:
                            lastfivenews_list.append('В посте не было текста 😕')
                    else:
                        lastfivenews_list.append('В посте не было текста 😕')

            i = 0 
            while i < len(lastfivenews_list):
                cursor.execute(f"SELECT date FROM {slug}")
                date = cursor.fetchall()
                for date1 in date[i]:
                    if date1 is not None:    
                        if date1 != '':    
                            lastfivenews_list[i] = lastfivenews_list[i] + '\n' + '(' + date1 + ')'

                i+=1        

            i = 0

            while i < len(lastfivenews_list):
                lastfivenews_urls = []
                cursor.execute(f"SELECT url FROM {slug}")
                url = cursor.fetchall()
                type1 = []
                for url2 in url:
                    for url1 in url2:
                        list1 = list(url1)
                        if len(list1) == 2 and list1[0] == '{' and list1[1] == '}':
                            type1.append('')
                            lastfivenews_urls.append('')
                        else:
                            try:
                                if list1[1] == '"' and list1[-2] == '"':
                                    list1.remove('{')
                                    list1.remove('}')
                                    list1.remove('"')
                                    list1.remove('"')
                                    url_str = "".join(list1)
                                    pic = url_str
                                    lastfivenews_urls.append(pic)
                                else:
                                    list1.remove('{')
                                    list1.remove('}')
                                    url_str = "".join(list1)
                                    pic = url_str
                                    if 'vk.com/video' in pic or 'youtube.com/' in pic:
                                        type1.append('video')
                                    else:
                                        type1.append('photo')
                                    lastfivenews_urls.append(pic)

                            except:
                                type1.append('')
                                lastfivenews_urls.append('')
                i+=1

            res = []
            for word in lastfivenews_urls:
                if word.count(',') > 0:
                    res.append(word.split(','))
                else:
                    res.append('')

            type_lst = []
            for k in res:
                if type(k) == list:
                    type_lst.append('list')
                else:
                    type_lst.append('notlist')
        else:
            error = 'По данной подписке не найдено ни одной новости'
            return render_template('lastfivemenu.html', error = error, calldata = calldata, domain_list = domain_list, len = len(domain_list))
        return render_template('lastfivepage.html', option_lastfivenews = lastfivenews_list, len = len(lastfivenews_list), option_urls = lastfivenews_urls, type1 = type1, res = res, type_lst = type_lst, slug = slug, error = error)
    else:
        return render_template('404.html')

@app.route("/lastnews/", methods=['GET', 'POST'])
def lastnews():  
    lastnews_list = []
    cursor.execute(f"SELECT body FROM news ORDER BY num")
    body = cursor.fetchall()
    for body1 in body:
        for body2 in body1:
            if body2 is not None:
                if body2 != '':
                    lastnews_list.append(body2)
                else:
                    lastnews_list.append('В посте не было текста 😕')
            else:
                lastnews_list.append('В посте не было текста 😕')
        
    i = 0 
    while i < len(lastnews_list):
        cursor.execute(f"SELECT name FROM news ORDER BY num")
        name = cursor.fetchall()
        for name1 in name[i]:
                if name1 is not None:    
                    lastnews_list[i] = name1 + '\n' + ':' + '\n' + lastnews_list[i]
        i+=1

    i = 0 
    while i < len(lastnews_list):
        cursor.execute(f"SELECT date FROM news ORDER BY num")
        date = cursor.fetchall()
        for date1 in date[i]:
            if date1 is not None:    
                if date1 != '':    
                    lastnews_list[i] = lastnews_list[i] + '\n' + '(' + date1 + ')'
                
        i+=1        
    
    i = 0
    
    while i < len(lastnews_list):
        lastnews_urls = []
        cursor.execute(f"SELECT url FROM news ORDER BY num")
        url = cursor.fetchall()
        type1 = []
        for url2 in url:
            for url1 in url2:
                list1 = list(url1)
                if len(list1) == 2 and list1[0] == '{' and list1[1] == '}':
                    type1.append('')
                    lastnews_urls.append('')
                else:
                    try:
                        if list1[1] == '"' and list1[-2] == '"':
                            list1.remove('{')
                            list1.remove('}')
                            list1.remove('"')
                            list1.remove('"')
                            url_str = "".join(list1)
                            pic = url_str
                            lastnews_urls.append(pic)
                        else:
                            list1.remove('{')
                            list1.remove('}')
                            url_str = "".join(list1)
                            pic = url_str
                            if 'vk.com/video' in pic or 'youtube.com/' in pic:
                                type1.append('video')
                            else:
                                type1.append('photo')
                            lastnews_urls.append(pic)
                            
                    except:
                        type1.append('')
                        lastnews_urls.append('')
        i+=1

    res = []
    for word in lastnews_urls:
        if word.count(',') > 0:
            res.append(word.split(','))
        else:
            res.append('')

    type_lst = []
    for k in res:
        if type(k) == list:
            type_lst.append('list')
        else:
            type_lst.append('notlist')

    return render_template('lastnews.html', option_lastnews = lastnews_list, len = len(lastnews_list), option_urls = lastnews_urls, type1 = type1, res = res, type_lst = type_lst)




page_survey = 1
@app.route('/survey/p=<slug>', methods=['GET', 'POST'])
def survey(slug):

    global page_survey
    try:
        page_survey = int(slug)
    except:
        pass


    users_list = []
    cursor.execute(f"SELECT id FROM survey")
    result = cursor.fetchall()
    for row in result:
        for x in row:    
            users_list.append(x)

    comment_list = []
    cursor.execute(f"SELECT comment FROM survey")
    result = cursor.fetchall()
    for row in result:
        for x in row:    
            comment_list.append(x)

    users_in_one_page = 10
    pages = len([users_list[i:i+users_in_one_page] for i in range(0,len(users_list),users_in_one_page)])
    if len(users_list) == 0:
        pages = 1
    if page_survey+1 in range(2,pages+2):   
        if len(users_list) != 0:    
            list_lists = [users_list[i:i+users_in_one_page] for i in range(0,len(users_list),users_in_one_page)]
            try:
                option_users = list_lists[page_survey-1]  
            except IndexError:
                option_users = list_lists[0]   

            comment = [comment_list[i:i+users_in_one_page] for i in range(0,len(comment_list),users_in_one_page)]
            try:
                comment_list = comment[page_survey-1]  
            except IndexError:
                comment_list = comment[0]      

            star1 = []
            cursor.execute(f"SELECT id FROM survey WHERE grade = '1'")
            result = cursor.fetchall()
            for row in result:
                for x in row:    
                    star1.append(x)   
            star2 = []
            cursor.execute(f"SELECT id FROM survey WHERE grade = '2'")
            result = cursor.fetchall()
            for row in result:
                for x in row:    
                    star2.append(x)   
            star3 = []
            cursor.execute(f"SELECT id FROM survey WHERE grade = '3'")
            result = cursor.fetchall()
            for row in result:
                for x in row:    
                    star3.append(x)   

            star4 = []
            cursor.execute(f"SELECT id FROM survey WHERE grade = '4'")
            result = cursor.fetchall()
            for row in result:
                for x in row:    
                    star4.append(x)   

            star5 = []
            cursor.execute(f"SELECT id FROM survey WHERE grade = '5'")
            result = cursor.fetchall()
            for row in result:
                for x in row:    
                    star5.append(x)   

        
        try:
            page_survey = int(slug)  
        except:
            page_survey = 1 

        if len(users_list) == 0:
            pages = 1
            page_survey = 1
            option_users = [0]
            comment_list = [0]
            star1 = [0]
            star2 = [0]
            star3 = [0]
            star4 = [0]
            star5 = [0]
        return render_template('survey.html', option_users = option_users, pages = pages, page = page_survey, star1=star1, star2=star2, star3=star3, star4=star4, star5=star5, len = len(users_list), opt_len = len(option_users), comment = comment_list)
    else:
        return render_template('404.html')

if __name__ == "__main__":
    app.run(debug=True)