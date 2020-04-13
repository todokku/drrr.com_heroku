import requests
import time
import json
import re
import os
from random import randint 
import threading
import giphy_client
from giphy_client.rest import ApiException
import sqlite3
import youtube_dl
import sys
import mimetypes
from requests_toolbelt import MultipartEncoder, MultipartEncoderMonitor
import click
import datetime

global ts_last_greeting
ts_last_greeting = 0


class Uploader:
    def __init(self, filename, file_host_url):
        self.filename = filename
        self.file_host_url = file_host_url

    def _multipart_post(self, data):
        encoder = MultipartEncoder(fields=data)
        monitor = MultipartEncoderMonitor(encoder)
        r = requests.post(self.file_host_url,
                          data=monitor,
                          headers={'Content-Type': monitor.content_type})
        return r

class FileioUploader(Uploader):
    def __init__(self, filename):
        self.filename = filename
        self.file_host_url = "https://file.io"

    def execute(self):
        file = open('./cache/{}'.format(self.filename), 'rb')
        try:
            data = {'file': (file.name, file, self._mimetype())}
            response = self._multipart_post(data)
        finally:
            file.close()

        return response.json()['link']


class CatboxUploader(Uploader):
    def __init__(self, filename):
        self.filename = filename
        self.file_host_url = "https://catbox.moe/user/api.php"

    def execute(self):
        file = open('./cache/{}'.format(self.filename), 'rb')
        try:
            data = {
                'reqtype': 'fileupload',
                'userhash': 'f30cb59306e2d72a0e958cbec',
                'fileToUpload': (file.name, file)
            }
            response = self._multipart_post(data)
        finally:
            file.close()

        return response.text


class Commands(object):
    def __init__(self):
        self.session = requests.session()
        self.start_time = ''
        self.start_time = datetime.datetime.utcnow()
        self.spam = {"pause":False,"admin_list":False,"admin":False,"gif":False,"help":False,"music":False,"post_music":False}
        self.admin_list = ['Pa7gprEIMI','TqOzGmy5V.','YJMpA.Wge2','NICKx2f4bE','vaW3kagV3.']
        self.music_info = ''
        self.host = 'https://drrr.com/room/?ajax=1'
        self.paylist_cont = 0
        self.paylist_duration = []
        self.paylist = []
        self.paylist_title = []
        self.pause = True
    
    def avoid_spam(self,com):
        time.sleep(5)
        self.spam[com] = False

    def load_cookie(self, file_name):
        f = open(file_name, 'r')
        self.session.cookies.update(eval(f.read()))
        f.close()

    def setRomm_Description(self,message,tripcode):
        for i in range(len(self.admin_list)):
            if tripcode == self.admin_list[i]:
                message = message[11:]
                room_description_body = {
                    'room_description': 'night {}'.format(message)
                }
                rd = self.session.post(self.host, room_description_body)
                rd.close()

    def setRomm_name(self,message,tripcode):
        for i in range(len(self.admin_list)):
            if tripcode == self.admin_list[i]:
                message = message[11:]
                room_name_body = {
                    'room_name': message
                }
                rn = self.session.post(self.host, room_name_body)
                rn.close()

    def leave_room(self):
        leave_body = {
            'leave': 'leave'
        }
        lr = self.session.post(self.host, leave_body)
        lr.close()

    def kick_room(self):
        kick_body = {
            'kick': 'kick'
        }
        kc = self.session.post(self.host, kick_body)
        kc.close()

    def new_host(self, new_host_id):
        new_host_body = {
            'new_host': new_host_id
        }
        nh = self.session.post(self.host, new_host_body)
        nh.close()

    def post(self, message, url='', to=''):
        post_body = {
            'message': message,
            'url': url,
            'to': to
        }
        p = self.session.post(
            url=self.host, data=post_body)
        p.close()

    def share_music(self, url, name=''):
        share_music_body = {
            'music': 'music',
            'name': name,
            'url': url
        }
        p = self.session.post(
            url=self.host, data=share_music_body)
        p.close()

    def room_enter(self, url_room):
        re = self.session.get(url_room)
        re.close()
        room = self.session.get('https://drrr.com/json.php?fast=1')
        return room.text

    def room_update(self, room_text):
        update = re.search('"update":\d+.\d+', room_text).group(0)[9:]
        url_room_update = 'https://drrr.com/json.php?update=' + update
        while 1:
            time.sleep(1)
            ru = self.session.get(url_room_update)
            update = re.search('"update":\d+.\d+', ru.text).group(0)[9:]
            url_room_update = 'https://drrr.com/json.php?update=' + update

            if 'talks' in ru.text:
                talks_update = re.findall(
                    '{"id".*?"message":".*?"}', re.search('"talks":.*', ru.text).group(0))
                # talk in "talks" block
                for tu in talks_update:
                    info_sender = re.findall('"from":{.*?}', tu)
                    info_sender = info_sender[0]
                    try:
                        tripcode = re.findall(
                            '"tripcode":".*?"', info_sender)[0][12:-1]
                    except Exception:
                        tripcode = None
                    name_sender = re.findall(
                        '"name":".*?"', info_sender)[0][8:-1]
                    message = re.search('"message":".*?"', tu).group(0)[11:-1].encode(encoding='utf-8').decode(
                        encoding='unicode-escape')
                    # log mostrado no shell quando se execulta o bot
                    #print('@%s: %s' % (name_sender,message))
                    if '/' in message or '@Athus' in message:
                        info_sender = re.findall('"from":{.*?}', tu)
                        if info_sender:
                            info_sender = info_sender[0]
                            name_sender = re.findall(
                                '"name":".*?"', info_sender)[0][8:-1]
                            try:
                                tripcode = re.findall('"tripcode":".*?"', info_sender)[0][12:-1]
                            except Exception:
                                tripcode = None
                            # condição para o bot nao ficar auto se respondendo suas requisições
                            if name_sender == u'Athus':
                                continue
                            id_sender = re.findall(
                                '"id":".*?"', info_sender)[0][6:-1]
                            # pesquisa "to" no bloco html
                            info_receiver = re.findall('"to":{.*?}', tu)
                            # condição no main para verificar se o bot esta fora da sala/banido de alguma sala
                            if info_receiver:
                                is_leave = self.handle_private_message(message=message, id_sender=id_sender,
                                                                       name_sender=name_sender,tripcode=tripcode)
                                if is_leave:
                                    return True
                            else:
                                self.handle_message(message=message, name_sender=name_sender,
                                                    id_sender=id_sender)
            ru.close()

# comandos do bot

    def merchan(self):
        mercham = "https://github.com/londarks"
        self.post(message="Olá Meu nome e Athus e eu fui Criado por Londarks\n Caso queira saber como fui feito segue o link abaixo", url='{}'.format
                  (mercham))  # de

    def help(self, message, name_sender):
        commandName = 'help'
        if self.spam[commandName] == False:
            self.post(message="|==Comandos==|\n |/help|\n |/gif naruto|\n |/add music(ID)|\n |/play|\n|/pause|\n |/post_music|\n |/admin|\n |/adm_list|")
            self.spam[commandName] = True
            self.avoid_spam(commandName)

    def admin(self, message, name_sender):
        commandName = 'admin'
        if self.spam[commandName] == False:
            self.post(message="|==ADMIN==| \n |/kick name|\n |/ban name|\n |/room_name Name_room|\n |/room_info Description|")
            self.spam[commandName] = True
            self.avoid_spam(commandName)

    def listAdmin(self, message, name_sender):
        commandName = 'admin_list'
        if self.spam[commandName] == False:
            self.post(message="|==ADMIN's==| \n |@londarks|\n |@alim|\n |@NICK!|\n |@jenni|\n |@NEKO|")
            self.spam[commandName] = True
            self.avoid_spam(commandName)

    def play(self):
        self.pause = False
        while True:
            try:
                if self.pause == False:
                    self.share_music(url=self.paylist[self.paylist_cont],name=self.paylist_title[self.paylist_cont])
                    self.paylist_cont += 1
                    loop = self.paylist_cont - 1
                    for i in range(0,self.paylist_duration[loop]):
                        if self.pause == True:
                            return
                        time.sleep(1)
                else:
                    return
            except Exception as e:
                self.post(message="Playlist Vazia")
                return

    def pause_playlist(self):
        commandName = 'pause'
        self.spam[commandName] = True
        self.pause = True
        self.post(message="Playlist Pausada")
        time.sleep(10)
        self.avoid_spam(commandName)


    def playlist(self, message, name_sender, id_sender):
        commandName = 'music'
        if self.spam[commandName] == False:
            uploader_classes = {
            "catbox": CatboxUploader,
            "fileio": FileioUploader}

            def upload(self, host, name):
                uploader_class = uploader_classes[host]
                uploader_instance = uploader_class(name)
                print(name)
                result = uploader_instance.execute()
                print("Your link : {}".format(result))
                #self.share_music(url=result,name=self.music_info['title'])
                self.paylist.append(result)
                self.paylist_duration.append(self.music_info['duration'])
                self.paylist_title.append(self.music_info['title'])
                os.remove("./cache/music_1.mp3")

            def sand_music(self, message):
                if re.findall('/add', message):
                    try:
                        message = message[6:]
                        print(message)
                        title = 'music_1'
                        extp = '.webm'
                        ydl_opts = {
                                   'format': 'bestaudio/best',
                                   'outtmpl': './cache/{}{}'.format(title,extp),
                                   'postprocessors': [{
                                       'key': 'FFmpegExtractAudio',
                                       'preferredcodec': 'mp3',
                                       'preferredquality': '192',
                          }],
                        }
                        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                            link = "https://www.youtube.com/watch?v={}".format(message)
                            filenames = ([link])
                            ydl.download(filenames)
                            info = ydl.extract_info(link)
                            self.music_info = info
                        prefixo ='.mp3'
                        upload(self,host = 'catbox', name = '{}{}'.format(title, prefixo))
                        self.avoid_spam(commandName)
                        self.post(message="@{}▷Colocando na Playlist...▷".format(name_sender))
                    except Exception:
                        self.post(message="Erro Link Invalido")
                        self.avoid_spam(commandName)
            self.spam[commandName] = True
            sand_music(self,message=message)



    def playlist_anonimo(self, message, name_sender, id_sender):
        commandName = 'music'
        if self.spam[commandName] == False:
            uploader_classes = {
            "catbox": CatboxUploader,
            "fileio": FileioUploader}

            def upload(self, host, name):
                uploader_class = uploader_classes[host]
                uploader_instance = uploader_class(name)
                print(name)
                result = uploader_instance.execute()
                print("Your link : {}".format(result))
                #self.share_music(url=result,name=self.music_info['title'])
                self.paylist.append(result)
                self.paylist_duration.append(self.music_info['duration'])
                self.paylist_title.append(self.music_info['title'])
                os.remove("./cache/music_1.mp3")

            def sand_music(self, message):
                if re.findall('/add', message):
                    try:
                        message = message[6:]
                        print(message)
                        title = 'music_1'
                        extp = '.webm'
                        ydl_opts = {
                                   'format': 'bestaudio/best',
                                   'outtmpl': './cache/{}{}'.format(title,extp),
                                   'postprocessors': [{
                                       'key': 'FFmpegExtractAudio',
                                       'preferredcodec': 'mp3',
                                       'preferredquality': '192',
                          }],
                        }
                        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                            link = "https://www.youtube.com/watch?v={}".format(message)
                            filenames = ([link])
                            ydl.download(filenames)
                            info = ydl.extract_info(link)
                            self.music_info = info
                        prefixo ='.mp3'
                        upload(self,host = 'catbox', name = '{}{}'.format(title, prefixo))
                        self.avoid_spam(commandName)
                        self.post(message="@Anonymo ▷Colocando na Playlist...▷")
                    except Exception:
                        self.post(message="Erro Link Invalido")
                        self.avoid_spam(commandName)
            self.spam[commandName] = True
            sand_music(self,message=message)


    def ghipy(self, message, name_sender, id_sender):
        commandName = 'gif'
        if self.spam[commandName] == False:
            message = message[5:]

            apikey = "LIVDSRZULELA"  # test value
            lmt = 8
            list_gif = []
            # our test search
            search_term = message

            r = requests.get(
                "https://api.tenor.com/v1/search?q=%s&key=%s&limit=%s" % (search_term, apikey, lmt))
            if r.status_code == 200:
                top_8gifs = json.loads(r.content)
                maximo = len(top_8gifs['results']) -1
                x = randint(0,maximo)
                list_gif.append(top_8gifs['results'][x])
                url = list_gif[0]['media'][0]['mediumgif']['url']
            self.post(message='{}-@{}'.format(message, name_sender),
                         url='%s' % (url))
            self.spam[commandName] = True
            self.avoid_spam(commandName)

    def music_help(self, message, name_sender):
        commandName = 'post_music'
        if self.spam[commandName] == False:
            ajuda_musica = "https://i.imgur.com/qDe9YpO.png"
            self.post(message="Como usar musica.", url='{}'.format(ajuda_musica))  # deixa a sala
            self.spam[commandName] = True
            time.sleep(120)
            self.avoid_spam(commandName)

    def mensagemprivate(self, message, name_sender, to=''):
        if re.findall('/say .*', message):
           message = message[5:] #conta 5 carateres e depois imprime aquilo escrito
           self.post(message='%s' % (message)) #imprime a menssagem dita



    def groom(self,new_host_id):
        new_host_body = {
            'new_host': new_host_id
        }
        nh = self.session.post(self.host, new_host_body)
        nh.close()
        return True

    def loop_msg(self):
        while 1:
            time.sleep(600)
            print("loop pegando")
            now = datetime.datetime.utcnow() # Timestamp of when uptime function is run
            delta = now - self.start_time
            hours, remainder = divmod(int(delta.total_seconds()), 3600)
            minutes, seconds = divmod(remainder, 60)
            days, hours = divmod(hours, 24)
            if days:
                time_format = "{d}days,{h}hours,{m}minutes,{s}seconds."
            else:
                time_format = "{d}days,{h}hours,{m}minutes,{s}seconds."
            uptime_stamp = time_format.format(d=days, h=hours, m=minutes, s=seconds)
            self.post(message='/me Time Online:{}'.format(uptime_stamp))

    def Online(self):
        now = datetime.datetime.utcnow() # Timestamp of when uptime function is run
        delta = now - self.start_time
        hours, remainder = divmod(int(delta.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        days, hours = divmod(hours, 24)
        if days:
            time_format = "{d}days,{h}hours,{m}minutes,{s}seconds."
        else:
            time_format = "{d}days,{h}hours,{m}minutes,{s}seconds."
        uptime_stamp = time_format.format(d=days, h=hours, m=minutes, s=seconds)
        self.post(message='/me Online:{}'.format(uptime_stamp))


    def admin_kick(self, message, name_sender, tripcode, id_sender):
        for i in range(len(self.admin_list)):
            if tripcode == self.admin_list[i]:
                if re.findall('/kick', message):
                    message = message[7:]

                    rooms = self.session.get("https://drrr.com/json.php?update=")
                    user = []
                    id_user = []

                    if rooms.status_code == 200:
                        rooms_data = json.loads(rooms.content)
                    for rooms in rooms_data['users']:
                        user.append(rooms)
                    for j in range(len(user)):
                        if user[j]['name'] == message:
                            kick_body = {'kick': user[j]['id']}
                            kc = self.session.post(
                                self.host, kick_body)
                            kc.close()
                            break


    def admin_ban(self, message, name_sender, tripcode, id_sender):
        for i in range(len(self.admin_list)):
            if tripcode == self.admin_list[i]:
                if re.findall('/ban', message):
                    message = message[6:]
                    rooms = self.session.get("https://drrr.com/json.php?update=")
                    user = []
                    id_user = []

                    if rooms.status_code == 200:
                        rooms_data = json.loads(rooms.content)
                    for rooms in rooms_data['users']:
                        user.append(rooms)
                    for j in range(len(user)):
                        if user[j]['name'] == message:
                            ban_body = {'ban': user[j]['id']}
                            kc = self.session.post(
                                self.host, ban_body)
                            kc.close()
                            break


    def handle_message(self, message, name_sender, id_sender):
        if '/help' in message:
            t_help = threading.Thread(
                target=self.help, args=(message, name_sender))
            t_help.start()
        elif '/admin' in message:
            t_admin = threading.Thread(
                target=self.admin, args=(message, name_sender))
            t_admin.start()
        elif '/adm_list' in message:
            t_listAdmin = threading.Thread(
                target=self.listAdmin, args=(message, name_sender))
            t_listAdmin.start()
        elif '/gif' in message:
            t_ghipy = threading.Thread(
                target=self.ghipy, args=(message, name_sender, id_sender))
            t_ghipy.start()
#===================comandos de musica=======================#
        elif '/add' in message:
            t_music = threading.Thread(
                target=self.playlist, args=(message, name_sender,id_sender))
            t_music.start()
        elif '/play' in message:
            t_play = threading.Thread(
                target=self.play)
            t_play.start()
        elif '/pause' in message:
            t_pause = threading.Thread(
                target=self.pause_playlist)
            t_pause.start()
#===================fim=======================#
        elif '/post_music' in message:
            t_music_help = threading.Thread(
                target=self.music_help, args=(message, name_sender))
            t_music_help.start()


    def handle_private_message(self, message, id_sender, name_sender, tripcode):
        if '/koi' in message:
            self.leave_room() # deixa a sala
            return True
        elif '/say' in message:
            t_mensagemprivate = threading.Thread(target=self.mensagemprivate, args=(message, name_sender, id_sender))
            t_mensagemprivate.start()
        elif '/add' in message:
            t_music = threading.Thread(
                target=self.playlist_anonimo, args=(message, name_sender,id_sender))
            t_music.start()
        elif '/groom' in message:
            self.groom(new_host_id=id_sender)
        elif '/time_up' in message:
            self.Online()
        elif '/kloop' in message:
            t_loop = threading.Thread(target=self.loop_msg)
            t_loop.start()
        elif '/kick' in message:
            t_adm_k = threading.Thread(target=self.admin_kick, args=(message, name_sender, tripcode, id_sender))
            t_adm_k.start()
        elif '/ban' in message:
            t_adm_ban = threading.Thread(target=self.admin_ban, args=(message, name_sender, tripcode, id_sender))
            t_adm_ban.start()
        elif'/github' in message:
            self.merchan()
        elif'/room_name' in message:
            t_adm_name = threading.Thread(target=self.setRomm_name, args=(message, tripcode))
            t_adm_name.start()
        elif'/room_info' in message:
            t_adm_description = threading.Thread(target=self.setRomm_Description, args=(message, tripcode))
            t_adm_description.start()
        return False