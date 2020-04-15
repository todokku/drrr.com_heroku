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
    def uploadGofile(filename):
        try:
            #sistema de upload "multipart/form-data" que envia o arquivo para o  servidor 
            mp_encoder = MultipartEncoder(
                fields={
                    'filesUploaded': ('./cache/{}'.format(filename), open('./cache/{}'.format(filename), 'rb')),
                    'email':'athushollow@gmail.com'
                }
            )
            r = requests.post(
                'https://srv-file9.gofile.io/upload',
                data=mp_encoder, 
                headers={'Content-Type': mp_encoder.content_type}
            )
            #pegando a resposta do json
            scrap =  r.json()
            #retornando o "token do arquivo"
            result = scrap['data']['code']
            return result,filename
        except Exception as e:
            print(e)

    def validator(result,filename):
        try:
            session = requests.Session()
            #valida o Arquivo na api
            validLink = 'https://apiv2.gofile.io/getServer?c={}'.format(result)
            #coloca ele disponivel para download
            uploadLink = 'https://srv-file9.gofile.io/getUpload?c={}'.format(result)
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36 OPR/67.0.3575.137'}
            time.sleep(3)
            session.get(validLink, headers=headers)
            session.get(uploadLink, headers=headers)
            r = 'https://srv-file9.gofile.io/download/{}/{}'.format(result, filename)
            return r
        except Exception as e:
            print(e)


class Commands(object):
    def __init__(self):
        self.session = requests.session()
        self.start_time = ''
        self.start_time = datetime.datetime.utcnow()
        self.spam = {"next":False,"skip":False,"pause":False,"admin_list":False,"admin":False,"gif":False,"help":False,"music":False,"post_music":False}
        self.admin_list = ['Pa7gprEIMI','TqOzGmy5V.','YJMpA.Wge2','NICKx2f4bE','vaW3kagV3.']
        self.music_info = ''
        self.host = 'https://drrr.com/room/?ajax=1'
        self.paylist_cont = 0
        self.paylist_duration = []
        self.paylist = []
        self.paylist_title = []
        self.pause = True
        self.nextCont = 0
        self.playStatus = False
        self.name='music_1.mp3'
    
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

    def ban_room(self,id_sender):
        ban_body = {
            'ban': id_sender
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
            self.post(message="|==Comandos==|\n |/help|\n |/gif naruto|\n |/add music(ID)|\n|/play|\n|/skip|\n|/pause|\n|/queue|\n|/post_music|")
            self.spam[commandName] = True
            self.avoid_spam(commandName)

    def admin(self, message, name_sender):
        commandName = 'admin'
        if self.spam[commandName] == False:
            self.post(message="|==ADMIN==|\n |/adm_list| \n |/kick name|\n |/ban name|\n |/room_name Name_room|\n |/room_info Description|")
            self.spam[commandName] = True
            self.avoid_spam(commandName)

    def listAdmin(self, message, name_sender):
        commandName = 'admin_list'
        if self.spam[commandName] == False:
            self.post(message="|==ADMIN's==| \n |@londarks|\n |@alim|\n |@NICK!|\n |@jenni|\n |@NEKO|")
            self.spam[commandName] = True
            self.avoid_spam(commandName)

    def play(self):
        if self.playStatus == False:
            self.playStatus = True
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
                    self.post(message="/me Playlist Vazia")
                    self.playStatus = False
                    return
        else:
            self.post(message="/me:Musica em andamento")

    def pause_playlist(self):
        commandName = 'pause'
        if self.spam[commandName] == False:
            self.spam[commandName] = True
            self.pause = True
            self.playStatus = False
            self.post(message="/me Playlist Pausada")
            time.sleep(10)
            self.avoid_spam(commandName)

    def skip_playlist(self):
        commandName = 'skip'
        if self.spam[commandName] == False:
            self.spam[commandName] = True
            self.pause = True
            self.playStatus = False
            self.post(message="/me Musica Pulada")
            time.sleep(2)
            t_skip = threading.Thread(target=self.play())
            t_skip.start()
            time.sleep(20)
            self.avoid_spam(commandName)

    def next(self):
        commandName = 'next'
        if self.spam[commandName] == False:
            self.spam[commandName] = True
            self.playStatus = False
            try:
                self.post(message="/me Proxima Musica: {} ".format(self.paylist_title[self.paylist_cont]))
            except Exception:
                self.post(message="/me Playlist Vazia")
            time.sleep(10)
            self.avoid_spam(commandName)

    def rebotPlaylist(self):
        self.post(message="/me Restart Playlist Total de Musicas: {}".format(len(self.paylist)))
        self.paylist_cont = 0
        self.pause = True
        self.playStatus = False
        time.sleep(1)
        t_skip = threading.Thread(target=self.play())
        t_skip.start()



    def playlist(self, message, name_sender, id_sender):
        commandName = 'music'
        if self.spam[commandName] == False:

            def upload(self,filename):
                #novo hospedagem de dados
                uploader_class = Uploader.uploadGofile(filename=filename)
                result = Uploader.validator(result=uploader_class[0],filename=uploader_class[1])
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
                        link = "https://www.youtube.com/watch?v={}".format(message)
                        ydl_consult = {
                        'quiet': True,
                        'skip_download': True,
                        }
                        with youtube_dl.YoutubeDL(ydl_consult) as ydl:
                            info = ydl.extract_info(link)
                            if info['duration'] > 600 :
                                self.post(message="/me Musica cancelada devido a sua duração.!")
                                self.avoid_spam(commandName)
                                return
                    except Exception:
                        self.post(message="/me Erro Link Invalido")
                        self.avoid_spam(commandName)
                        return
                    try:
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
                        self.post(message="/me ▷Carregando musica▷")
                        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                            #link = "https://www.youtube.com/watch?v={}".format(message)
                            filenames = ([link])
                            ydl.download(filenames)
                            self.music_info = info
                        upload(self,filename=self.name)
                        self.avoid_spam(commandName)
                        self.post(message="/me @{}▷Musica Colocada na Playlist...▷".format(name_sender))
                    except Exception as e:
                        self.post(message="/me Erro Link Invalido")
                        self.avoid_spam(commandName)
            self.spam[commandName] = True
            sand_music(self,message=message)


    def playlist_anonimo(self, message, name_sender, id_sender):
        commandName = 'music'
        if self.spam[commandName] == False:

            def upload(self,filename):
                #novo hospedagem de dados
                uploader_class = Uploader.uploadGofile(filename=filename)
                result = Uploader.validator(result=uploader_class[0],filename=uploader_class[1])
                print("Your link : {}".format(result))
                #self.share_music(url=result,name=self.music_info['title'])
                self.paylist.append(result)
                self.paylist_duration.append(self.music_info['duration'])
                self.paylist_title.append("NONE")
                os.remove("./cache/music_1.mp3")

            def sand_music(self, message):
                if re.findall('/add', message):
                    try:
                        message = message[6:]
                        link = "https://www.youtube.com/watch?v={}".format(message)
                        ydl_consult = {
                        'quiet': True,
                        'skip_download': True,
                        }
                        with youtube_dl.YoutubeDL(ydl_consult) as ydl:
                            info = ydl.extract_info(link)
                            if info['duration'] > 600 :
                                self.post(message="/me Musica cancelada devido a sua duração.!")
                                self.avoid_spam(commandName)
                                return
                    except Exception:
                        self.post(message="/me Erro Link Invalido")
                        self.avoid_spam(commandName)
                        return
                    try:
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
                        self.post(message="/me ▷Carregando musica▷")
                        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                            #link = "https://www.youtube.com/watch?v={}".format(message)
                            filenames = ([link])
                            ydl.download(filenames)
                            self.music_info = info
                        upload(self,filename=self.name)
                        self.avoid_spam(commandName)
                        self.post(message="/me @{}▷Musica Colocada na Playlist...▷".format(name_sender))
                    except Exception as e:
                        self.post(message="/me Erro Link Invalido")
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
            ajuda_musica = "https://i.imgur.com/hmmERQi.png"
            self.post(message="Como usar musica.", url='{}'.format(ajuda_musica))  # deixa a sala
            self.spam[commandName] = True
            time.sleep(30)
            self.avoid_spam(commandName)

    def mensagemprivate(self, message, name_sender, to=''):
        if re.findall('/say .*', message):
           message = message[5:] #conta 5 carateres e depois imprime aquilo escrito
           self.post(message='%s' % (message)) #imprime a menssagem dita
    
    def validador(self):
        validLink = 'https://apiv2.gofile.io/getServer?c=zyPIxB'
        uploadLink = 'https://srv-file9.gofile.io/getUpload?c=zyPIxB'
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36 OPR/67.0.3575.137'}
        self.session.get(validLink, headers=headers)
        self.session.get(uploadLink, headers=headers)

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

    
    def ship(self):
        ...




    def groom(self,new_host_id):
        new_host_body = {
            'new_host': new_host_id
        }
        nh = self.session.post(self.host, new_host_body)
        nh.close()
        return True

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
        elif '/skip' in message:
            t_skip = threading.Thread(
                target=self.skip_playlist)
            t_skip.start()
        elif '/queue' in message:
            t_next = threading.Thread(
                target=self.next)
            t_next.start()
#===================fim=======================#
        elif '/post_music' in message:
            t_music_help = threading.Thread(
                target=self.music_help, args=(message, name_sender))
            t_music_help.start()

        elif '/validador' in message:
            validador = threading.Thread(
                target=self.validador)
            validador.start()

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
        elif'/rebot_p' in message:
            t_rebotPlaylist = threading.Thread(target=self.rebotPlaylist)
            t_rebotPlaylist.start()
        return False