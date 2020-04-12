# -*- coding:utf-8 -*-
#import athus
import os
import threading
import time
from network import connect
from modules import module
import json
import requests

name = 'Athus'
icon = 'tanaka'
file_name = 'athus.cookie'
bot = connect.Connect(name=name, icon=icon)
enter_room = module.Commands()

if not os.path.isfile(file_name):
    bot.login()
    bot.save_cookie(file_name=file_name)

# rooms.load_cookie(file_name=file_name)
# rooms.search_room()
#url_input_room = input("Enter Room Id")
url_room = 'https://drrr.com/room/?id=koum79oolZ'  # .format(url_input_room)


# main
while 1:
    try:
        enter_room.load_cookie(file_name=file_name)
        e_room = enter_room.room_enter(url_room=url_room)
        is_leave = enter_room.room_update(room_text=e_room)
        if is_leave == True:
            break

    except Exception as e:
        print(e)
