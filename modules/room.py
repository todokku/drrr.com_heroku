import requests
import time
import json
import os , re
import threading
import giphy_client
from giphy_client.rest import ApiException
from jikanpy import Jikan

global ts_last_greeting
ts_last_greeting = 0

class Commands(object):
    def __init__(self):
        self.session = requests.session()


    def load_cookie(self, file_name):
        f = open(file_name, 'r')
        self.session.cookies.update(eval(f.read()))
        f.close()
    def leave_room(self):
        leave_body = {
            'leave': 'leave'
        }
        lr = self.session.post('https://drrr.com/room/?ajax=1', leave_body)
        lr.close()

    def kick_room(self):
        kick_body = {
            'kick': 'kick'
        }
        kc = self.session.post('https://drrr.com/room/?ajax=1', kick_body)
        kc.close()

    def new_host(self, new_host_id):
        new_host_body = {
            'new_host': new_host_id
        }
        nh = self.session.post('https://drrr.com/room/?ajax=1', new_host_body)
        nh.close()

    def post(self, message, url='', to=''):
        post_body = {
            'message': message,
            'url': url,
            'to': to
        }
        p = self.session.post(url='https://drrr.com/room/?ajax=1', data=post_body)
        p.close()

    def share_music(self, url, name=''):
        share_music_body = {
            'music': 'music',
            'name': name,
            'url': url
        }
        p = self.session.post(url='https://drrr.com/room/?ajax=1', data=share_music_body)
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
            time.sleep(0.5)
            ru = self.session.get(url_room_update)
            update = re.search('"update":\d+.\d+', ru.text).group(0)[9:]
            url_room_update = 'https://drrr.com/json.php?update=' + update
           # search "talks" block in room update response
            if '"type":"join"' in ru.text:
                self.post('/me Bem-Vindo')
            ru.close()
            if '"type":"leave"' in ru.text:
                self.post('/me Vai tarde.!')
            ru.close()
            if 'talks' in ru.text:
                talks_update = re.findall('{"id".*?"message":".*?"}', re.search('"talks":.*', ru.text).group(0))
                # talk in "talks" block
                for tu in talks_update:
                    info_sender = re.findall('"from":{.*?}', tu)
                    info_sender = info_sender[0]
                    name_sender = re.findall('"name":".*?"', info_sender)[0][8:-1]
                    message = re.search('"message":".*?"', tu).group(0)[11:-1].encode(encoding='utf-8').decode(
                        encoding='unicode-escape')
                    print('@%s: %s' % (name_sender,message))
                    if '!' in message or '@Athus' in message:
                        # search "from" blockw
                        info_sender = re.findall('"from":{.*?}', tu)
                        if info_sender:
                            info_sender = info_sender[0]
                            name_sender = re.findall('"name":".*?"', info_sender)[0][8:-1]
                            if name_sender == u'Athus':
                                continue
                            id_sender = re.findall('"id":".*?"', info_sender)[0][6:-1]
                            # search "to" block in html
                            info_receiver = re.findall('"to":{.*?}', tu)
                            if info_receiver:
                                # info_receiver = info_receiver[0].decode('unicode_escape').encode('utf-8')
                                is_leave = self.handle_private_message(message=message, id_sender=id_sender,
                                                                       name_sender=name_sender)
                                if is_leave:
                                    return True
                            else:
                                self.handle_message(message=message, name_sender=name_sender)
            ru.close()

#comandos do bot 

    def help(self,message,name_sender):
        self.post(message="|!help|\n |!gif <name_gif>|\n |!m <Id_music_yt>|\n |!post_music|\n |!dado|") 



    def music(self, message, name_sender, to=''):
        message = message[4:]
        r_link = message
        print(message)
        link = "https://www.youtube.com/watch?v=%s" % (r_link)
        url="http://michaelbelgium.me/ytconverter/convert.php?youtubelink=%s " % (link)
        open_bbc_page = requests.get(url).json() 
        print(open_bbc_page)
        #time.sleep(1)
        self.share_music(url=open_bbc_page['file'],name=open_bbc_page['title'] )#% (open_bbc_page['file'],open_bbc_page['title']))

        #else:
        #    self.post(message='/me Algo deu errado...Bip...Bop...!!!')

    def top_animes(self,message,name_sender):
        jikan = Jikan()
        anime_name = []
        top_anime = jikan.top(type='anime')
        for episode in top_anime['top']:
          anime_name.append([episode['title']])
        self.post(message="Top_5 animes \n 1°%s\n2°%s\n3°%s\n4°%s\n5°%s." % (anime_name[0],anime_name[1],anime_name[2],anime_name[3],anime_name[4]))
    
    def ghipy(self, message, name_sender, to=''):
        if re.findall('/gif .*', message):
           message = message[5:]
           api_instance = giphy_client.DefaultApi()
           api_key = 'oe533d6kfwvoxrJgC6fDSi6WcSnqyEPb' # str | Giphy API Key.
           tag = message # str | Filters results by specified tag. (optional)
           rating = 'g' # str | Filters results by specified rating. (optional)
           fmt = 'json' # str | Used to indicate the expected response format. Default is Json. (optional) (default to json)
        try:
    # Random Endpoint
           api_response = api_instance.gifs_random_get(api_key, tag=tag, rating=rating, fmt=fmt)
           self.post(message='Gif %s-@%s' % (message, name_sender), url='%s' % (api_response.data.image_url))
        except ApiException as e:
             self.post(message='sem Resultados %s' %e)

    def music_help(self,message,name_sender):
        ajuda_musica = "https://i.imgur.com/qDe9YpO.png"
        self.post(message="Como usar musica.",url='%s' % (ajuda_musica)) # deixa a sala


#checa o comando e execulta
    def handle_message(self, message, name_sender):
        if '!help' in message:
            t_help = threading.Thread(target=self.help, args=(message, name_sender))
            t_help.start()
        elif '!gif' in message:
            t_ghipy = threading.Thread(target=self.ghipy, args=(message, name_sender))
            t_ghipy.start()
        elif '!m' in message:
            t_music = threading.Thread(target=self.music, args=(message, name_sender))
            t_music.start()
        elif '!top_animes' in message:
            t_top_animes = threading.Thread(target=self.top_animes, args=(message, name_sender))
            t_top_animes.start()
        elif '!post_music' == message:
            t_music_help = threading.Thread(target=self.music_help, args=(message, name_sender))
            t_music_help.start()