import requests
import time
import json
import re
import os
import random
from random import randint
import threading
import giphy_client
from giphy_client.rest import ApiException
from jikanpy import Jikan
import sqlite3
import youtube_dl
import sys
import mimetypes
from requests_toolbelt import MultipartEncoder, MultipartEncoderMonitor
import click

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
                'userhash': 'd4536907ecfa84d32cb37d993',
                'fileToUpload': (file.name, file)
            }
            response = self._multipart_post(data)
        finally:
            file.close()

        return response.text




# uploader_classes = {
#     "catbox": CatboxUploader,
#     "fileio": FileioUploader
# }




# def upload(host, name):
#     uploader_class = uploader_classes[host]
#     uploader_instance = uploader_class(name)
#     print(name)
#     result = uploader_instance.execute()
#     print("Your link : {}".format(result))
#     return result


class Commands(object):
    def __init__(self):
        self.session = requests.session()

        """
        Modulos de conexão com o servidor Drrr.com
        :load_cookie =  faz login no site utilizando o cookie salvo
        :leave_room = espesifica a função para o Bot sair da sala
        :kick_room = espesifica a função do Bot kikar alguém da sala
        :new_host = Essa função server para o Bot dar "Admin"/host para
        outra pessoa dentro da sala
        :post = função declada para poder mandar menssagem
        :share_music = função declada para poder mandar audio/musica
        """

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
        p = self.session.post(
            url='https://drrr.com/room/?ajax=1', data=post_body)
        p.close()

    def share_music(self, url, name=''):
        share_music_body = {
            'music': 'music',
            'name': name,
            'url': url
        }
        p = self.session.post(
            url='https://drrr.com/room/?ajax=1', data=share_music_body)
        p.close()

    def room_enter(self, url_room):
        re = self.session.get(url_room)
        re.close()
        room = self.session.get('https://drrr.com/json.php?fast=1')
        return room.text

    """
    room_update: Atualiza a Sala a cada 1 segundo  procurando novas menssagens
    e assim sabendo de algum usuario digitou alguém comando,
    alem de ser nessa mesma função onde o bot captura 
    info_sender = Informação do autor (tripcode, id e outras coisas)
    name_sender = Autor da menssagem
    message = Menssagem enviada
    """

    def room_update(self, room_text):
        update = re.search('"update":\d+.\d+', room_text).group(0)[9:]
        url_room_update = 'https://drrr.com/json.php?update=' + update
        while 1:
            time.sleep(1)
            ru = self.session.get(url_room_update)
            update = re.search('"update":\d+.\d+', ru.text).group(0)[9:]
            url_room_update = 'https://drrr.com/json.php?update=' + update
            """
            Quando alguem entra ou sai da sala ele solta uma preve frase
            "type":"join" referece a qunado alguem entra na sala o mesmo se aplica a
                                   "type":"leave" 
                todos esses dados são pegos na propria api do site
                        https://drrr.com/room/?ajax=1
            """
            if '"type":"join"' in ru.text:
                self.post('/me Bem-Vindo')
            ru.close()
            if '"type":"leave"' in ru.text:
                self.post('/me Vai tarde.!')
            ru.close()

            if 'talks' in ru.text:
                talks_update = re.findall(
                    '{"id".*?"message":".*?"}', re.search('"talks":.*', ru.text).group(0))
                # talk in "talks" block
                for tu in talks_update:
                    info_sender = re.findall('"from":{.*?}', tu)
                    info_sender = info_sender[0]
                    # tripcode = re.findall(
                    #     '"tripcode":".*?"', info_sender)[0][12:-1]
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
                            # tripcode = re.findall(
                            #     '"tripcode":".*?"', info_sender)[0][12:-1]
                            # condição para o bot nao ficar auto se respondendo suas requisições
                            if name_sender == 'Athus':
                                continue
                            id_sender = re.findall(
                                '"id":".*?"', info_sender)[0][6:-1]
                            # pesquisa "to" no bloco html
                            info_receiver = re.findall('"to":{.*?}', tu)
                            # condição no main para verificar se o bot esta fora da sala/banido de alguma sala
                            if info_receiver:
                                is_leave = self.handle_private_message(message=message, id_sender=id_sender,
                                                                       name_sender=name_sender)
                                if is_leave:
                                    return True
                            else:
                                self.handle_message(message=message, name_sender=name_sender,
                                                    id_sender=id_sender)
            ru.close()

# comandos do bot

    def help(self, message, name_sender):
        self.post(
            message="|/help|\n |/gif <name_gif>|\n |/m <Id_music_yt>|\n |/post_music|\n |/dado|")

    def music(self, message, name_sender, to=''):
        uploader_classes = {
        "catbox": CatboxUploader,
        "fileio": FileioUploader}

        def upload(self, host, name):
            uploader_class = uploader_classes[host]
            uploader_instance = uploader_class(name)
            print(name)
            result = uploader_instance.execute()
            print("Your link : {}".format(result))
            self.share_music(url=result,name='Song')
            os.remove("./cache/music_1.mp3")

        def sand_music(self, message):
            if re.findall('/m', message):
                message = message[4:]
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
                self.post(message="Carregando...")
                with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                    link = "https://www.youtube.com/watch?v={}".format(message)
                    filenames = ([link])
                    ydl.download(filenames)
                prefixo ='.mp3'
                upload(self,host = 'catbox', name = '{}{}'.format(title, prefixo))
        sand_music(self,message=message)
            
            #self.post(message="link:{}".format(upload(result)))

            #upload(host = 'catbox', name = '{}{}'.format(filenames, prefixo))
            #self.post(message="link:{}".format(result))

    # def music(self, message, name_sender, to=''):
    #     try:
    #         if re.findall('/m', message):
    #             message = message[4:]
    #             # print(message)
    #             link = "https://www.youtube.com/watch?v={}".format(message)
    #             url = "http://michaelbelgium.me/ytconverter/convert.php?youtubelink={}".format(
    #                 link)
    #             open_bbc_page = requests.get(url).json()
    #             # print(url)
    #             # time.sleep(1)
    #             # % (open_bbc_page['file'],open_bbc_page['title']))
    #             self.share_music(
    #                 url=open_bbc_page['file'], name=open_bbc_page['title'])
    #     except KeyError:
    #         self.post(message="Servidor Offline")

    def top_animes(self, message, name_sender):
        jikan = Jikan()
        anime_name = []
        top_anime = jikan.top(type='anime')
        for episode in top_anime['top']:
            anime_name.append([episode['title']])
        self.post(message="Top_5 animes \n 1°{}\n2°{}\n3°{}\n4°{}\n5°{}.".format(
            anime_name[0], anime_name[1], anime_name[2], anime_name[3], anime_name[4]))

    def ghipy(self, message, name_sender, to=''):
        if re.findall('/gif .*', message):
            message = message[5:]
            api_instance = giphy_client.DefaultApi()
            # str | Giphy API Key.
            api_key = 'oe533d6kfwvoxrJgC6fDSi6WcSnqyEPb'
            tag = message  # str | Filters results by specified tag. (optional)
            # str | Filters results by specified rating. (optional)
            rating = 'g'
            # str | Used to indicate the expected response format. Default is Json. (optional) (default to json)
            fmt = 'json'

            api_response = api_instance.gifs_random_get(
                api_key, tag=tag, rating=rating, fmt=fmt)
            self.post(message='{}-@{}'.format(message, name_sender),
                      url='%s' % (api_response.data.image_url))

    def music_help(self, message, name_sender):
        ajuda_musica = "https://i.imgur.com/qDe9YpO.png"
        self.post(message="Como usar musica.", url='{}'.format
                  (ajuda_musica))  # deixa a sala

    """

    Sistema arcaico de RPG

    """

    def dado(self, message, name_sender, to=''):
        list_dados = ['1', '2', '3', '4', '5', '6', ]
        list_dados2 = ['1', '2', '3', '4', '5', '6', ]
        list_dados3 = ['1', '2', '3', '4', '5', '6', ]
        list_dados4 = ['1', '2', '3', '4', '5', '6', ]
        list_dados = random.choice(list_dados)
        list_dados2 = random.choice(list_dados2)
        list_dados3 = random.choice(list_dados3)
        list_dados4 = random.choice(list_dados4)
        time.sleep(2)
        self.post(message='Irei girar o dado @{}, se sair com um trio de: {} você ganha. Caiu em: {}-{}-{}'.format
                  (name_sender, list_dados, list_dados2, list_dados3, list_dados4))

        # if list_dados2 == list_dados3 and list_dados4:
        #     conn = sqlite3.connect('RPG/Rank.db')
        #     cursor = conn.cursor()
        #     user_name = "{}".format(name_sender)
        #     id_user = "{}".format(tripcode)
        #     sequencia = "{},{},{}".format(
        #         list_dados2, list_dados3, list_dados4)
        #     conn.close()

    def register(self, message, name_sender, id_sender):
        usr_ATK = 5
        usr_DEF = 8
        usr_LIFE = 100
        conn = sqlite3.connect('RPG/rpg.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO players (name,id_chat,ATK,DEF,LIFE) VALUES (?,?,?,?,?)", (name_sender,id_sender,usr_ATK,usr_DEF,usr_LIFE))
        conn.commit()
        conn.close()
        self.post(message='Registrador')

    def info(self, message, name_sender, id_sender):
        conn = sqlite3.connect('RPG/rpg.db')
        cursor = conn.cursor()
        login = cursor.execute('SELECT name,ATK,DEF,LIFE From players WHERE id_chat="%s"' % (id_sender))
        conn.commit()
        conn.close()
        self.post(message='seu id:{}'.format(id_sender))


    def login_messagem(self, to=''):
        self.post(message='fala meu bacano',to=to)
    
    # def rank(self, message, name_sender):
    #     conn = sqlite3.connect('RPG/Rank.db')
    #     cursor = conn.cursor()
    #     consulta = cursor.execute('SELECT name,tipcode,sequencia From rank')
    #     db_consulta = []
    #     rows = cursor.fetchone()
    #     for row in rows:
    #         db_consulta.append(row)
    #     self.post(message='Rank:\n|1º{} -- {}|\n|2º -- |\n|3º -- |\n|4º -- |\n|5º -- |'.format(
    #         db_consulta[0], db_consulta[2]))



    def mensagemprivate(self, message, name_sender, to=''):
        if re.findall('/sms .*', message):
           message = message[5:] #conta 5 carateres e depois imprime aquilo escrito
           self.post(message='%s' % (message)) #imprime a menssagem dita

    def qresp(self, frase_secreta,message=''):
        digitadas = []
        acertos = []
        erros = 0
        while True:
            senha = ""
            for letra in frase_secreta:
                senha += letra if letra in acertos else "."
            print(senha)
            if senha == frase_secreta:
               self.post(message='Você acertou!')
                #print("Você acertou!")
               break
            tentativa=message
            #tentativa = input("\nDigite uma letra:").lower().strip()
            if tentativa in digitadas:
               self.post(message="Você já tentou esta letra!")
               continue
            else:
               digitadas += tentativa
               if tentativa in frase_secreta:
                     acertos += tentativa
               else:
                     erros += 1
                     self.post(message='Você errou!')
            if erros == 2:
                self.post(message='Você errou!')
            elif erros == 3:
                self.post(message='Você errou!')
            elif erros >= 4:
               self.post(message='Você errou!')
            if erros == 5:
                self.post(message='Você errou!')
            elif erros >= 6:
                self.post(message='Você errou!')
            if erros == 6:
                self.post(message="Enforcado!")
                break

    def forca(self, message, name_sender):
        game = open('games_lista.json', 'r')
        start = json.load(game)
        frase_index = randint(1,5)
        game_frase = 'game_'+ (str)(frase_index)
        frase_secreta = start['games_list'][game_frase]['nome'].lower().strip()
        dica_secreta = start['games_list'][game_frase]['dica_1'].lower().strip()#dica_1
        self.post(message='Dica: '+ dica_secreta)
        print("A frase secreta é: " + frase_secreta)
        self.qresp(frase_secreta=frase_secreta)





    """
    ===============================
    Comandos Para administradores
    /kick == kika o usuario
    /ban == bane o usaurio
    /unban == desbane o usuario
    ===============================
    """

    # def admin_host(self, message, name_sender, tripcode, id_sender):
    #     # print(tripcode)
    #     # print(id_sender)
    #     # print(message)
    #     if tripcode == "Bb8\/DUMRJU":
    #         new_host_body = {'new_host': id_sender}
    #         nh = self.session.post(
    #             'https://drrr.com/room/?ajax=1', new_host_body)
    #         nh.close()
    #         return True
    #     elif tripcode != "Bb8\/DUMRJU":
    #         self.post(message='Você Não tem permissão! @{}'.format(name_sender))
    #     elif tripcode == None:
    #         self.post(message='Você Não tem permissão! @{}'.format(name_sender))

    # def admin_kick(self, message, name_sender, tripcode, id_sender):
    #     if tripcode == "Bb8\/DUMRJU":
    #         if re.findall('/kick', message):
    #             message = message[8:]

    #             rooms = self.session.get("https://drrr.com/json.php?update=")
    #             user = []
    #             id_user = []

    #             if rooms.status_code == 200:
    #                 rooms_data = json.loads(rooms.content)
    #             for rooms in rooms_data['users']:
    #                 user.append(rooms)
    #             # print('lendo')
    #             # print(f'messagem:{message}')
    #             # print(f'messagem:{user}')
    #             for j in range(len(user)):
    #                 # print(user[j]['name'])
    #                 if user[j]['name'] == message:
    #                     # print(user[j]['id'])
    #                     # print(message)
    #                     kick_body = {'kick': user[j]['id']}
    #                     kc = self.session.post(
    #                         'https://drrr.com/room/?ajax=1', kick_body)
    #                     kc.close()
    #                     break
    #     else:
    #         self.post(message='Você Não tem permissão! @{}'.format(name_sender))


    # def admin_ban(self, message, name_sender, tripcode, id_sender):
    #     if tripcode == "Bb8\/DUMRJU":
    #         if re.findall('/ban', message):
    #             message = message[7:]
    #             rooms = self.session.get("https://drrr.com/json.php?update=")
    #             user = []
    #             id_user = []

    #             if rooms.status_code == 200:
    #                 rooms_data = json.loads(rooms.content)
    #             for rooms in rooms_data['users']:
    #                 user.append(rooms)
    #             # print('lendo')
    #             # print(f'messagem:{message}')
    #             # print(f'messagem:{user}')
    #             for j in range(len(user)):
    #                 # print(user[j]['name'])
    #                 if user[j]['name'] == message:
    #                     # print(user[j]['id'])
    #                     # print(message)
    #                     ban_body = {'ban': user[j]['id']}
    #                     kc = self.session.post(
    #                         'https://drrr.com/room/?ajax=1', ban_body)
    #                     kc.close()
    #                     break
    #     else:
    #         self.post(message='Você Não tem permissão! @{}'.format(name_sender))

    # def admin_unban(self, message, name_sender, tripcode, id_sender):
    #     if tripcode == "Bb8\/DUMRJU":
    #         if re.findall('/unban', message):
    #             message = message[8:]
    #             rooms = self.session.get("https://drrr.com/json.php?update=")
    #             user = []
    #             id_user = []

    #             if rooms.status_code == 200:
    #                 rooms_data = json.loads(rooms.content)
    #             for rooms in rooms_data['users']:
    #                 user.append(rooms)
    #             # print('lendo')
    #             # print(f'messagem:{message}')
    #             # print(f'messagem:{user}')
    #             for j in range(len(user)):
    #                 # print(user[j]['name'])
    #                 if user[j]['name'] == message:
    #                     # print(user[j]['id'])
    #                     # print(message)
    #                     unban_body = {'unban': user[j]['id']}
    #                     kc = self.session.post(
    #                         'https://drrr.com/room/?ajax=1', unban_body)
    #                     kc.close()
    #                     break 
    #     else:
    #         self.post(message='Você Não tem permissão! @{}'.format(name_sender))


# checa o comando e execulta


    def handle_message(self, message, name_sender, id_sender):
        if '/help' in message:
            t_help = threading.Thread(
                target=self.help, args=(message, name_sender))
            t_help.start()
        elif '/gif' in message:
            t_ghipy = threading.Thread(
                target=self.ghipy, args=(message, name_sender))
            t_ghipy.start()
        elif '/m' in message:
            t_music = threading.Thread(
                target=self.music, args=(message, name_sender))
            t_music.start()
        elif '/top_animes' in message:
            t_top_animes = threading.Thread(
                target=self.top_animes, args=(message, name_sender))
            t_top_animes.start()
        elif '/post_music' in message:
            t_music_help = threading.Thread(
                target=self.music_help, args=(message, name_sender))
            t_music_help.start()
        elif '/forca' in message:
            t_forca = threading.Thread(
                target=self.forca, args=(message, name_sender))
            t_forca.start()
        elif '/qr' in message:
            t_qresp = threading.Thread(
                target=self.qresp, args=(message, name_sender))
            t_qresp.start()
        # elif '/admin' in message:
        #     t_host = threading.Thread(target=self.admin_host, args=(
        #         message, name_sender, tripcode, id_sender))
        #     t_host.start()
        # elif '/kick' in message:
        #     t_kick = threading.Thread(target=self.admin_kick, args=(
        #         message, name_sender, tripcode, id_sender))
        #     t_kick.start()
        # elif '/ban' in message:
        #     t_ban = threading.Thread(target=self.admin_ban, args=(
        #         message, name_sender, tripcode, id_sender))
        #     t_ban.start()
        # elif '/unban' in message:
        #     t_unban = threading.Thread(target=self.admin_unban, args=(
        #         message, name_sender, tripcode, id_sender))
        #     t_unban.start()
        elif '/dado' in message:
            t_dado = threading.Thread(
                target=self.dado, args=(message, name_sender))
            t_dado.start()
        elif '/register' in message:
            t_rank = threading.Thread(
                target=self.register, args=(message, name_sender, id_sender))
            t_rank.start()
        elif '/info' in message:
            t_info = threading.Thread(
                target=self.info, args=(message, name_sender, id_sender))
            t_info.start()




    def handle_private_message(self, message, id_sender, name_sender):
        if '/koi' in message:
            self.leave_room() # deixa a sala
            return True
        elif '/sms' in message:
            t_mensagemprivate = threading.Thread(target=self.mensagemprivate, args=(message, name_sender, id_sender))
            t_mensagemprivate.start()
        elif '/login' in message:
            t_login_messagem = threading.Thread(target=self.login_messagem, args=(id_sender,))
            t_login_messagem.start()
        return False