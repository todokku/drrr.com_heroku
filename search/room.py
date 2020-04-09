# -*- coding:utf-8 -*-
import json
import requests
import os, re


class Search(object):
    def __init__(self):
        self.session = requests.session()


    def load_cookie(self, file_name):
        f = open(file_name, 'r')
        self.session.cookies.update(eval(f.read()))
        f.close()

    def search_room(self):
    	rooms = self.session.get("https://drrr.com/lounge?api=json")
    	salas = []
    	host = [] 
    	room_name = []
    	room_host_name = []
    	room_id = []
    	room_lg = [] 
    	if rooms.status_code == 200:
    		rooms_data = json.loads(rooms.content)
    	for rooms in rooms_data['rooms']:
    		salas.append(rooms)
    	for rooms in salas:
    		room_name.append(rooms['name'])
    	for rooms in salas:
    		host.append(rooms['host'])
    	for player in host:
    		room_host_name.append(player['name'])
    	for id_room in salas:
    		room_id.append(id_room['roomId'])
    	for language_room in salas:
    		room_lg.append(language_room['language'])
    	print("|room name:{}||Host:{}||ID:{}||language:{}|".format(room_name[0],
        	                                                       room_host_name[0],
        	                                                       room_id[0],
        	                                                       room_lg[0]))
    	print("|room name:{}||Host:{}||ID:{}||language:{}|".format(room_name[1],
        	                                                       room_host_name[1],
        	                                                       room_id[1],
        	                                                       room_lg[1]))
    	print("|room name:{}||Host:{}||ID:{}||language:{}|".format(room_name[2],
        	                                                       room_host_name[2],
        	                                                       room_id[2],
        	                                                       room_lg[2]))
    	print("|room name:{}||Host:{}||ID:{}||language:{}|".format(room_name[3],
        	                                                       room_host_name[3],
        	                                                       room_id[3],
        	                                                       room_lg[3]))
    	print("|room name:{}||Host:{}||ID:{}||language:{}|".format(room_name[4],
        	                                                       room_host_name[4],
        	                                                       room_id[4],
        	                                                       room_lg[4]))
    	print("|room name:{}||Host:{}||ID:{}||language:{}|".format(room_name[5],
        	                                                       room_host_name[5],
        	                                                       room_id[5],
        	                                                       room_lg[5]))
    	print("|room name:{}||Host:{}||ID:{}||language:{}|".format(room_name[6],
        	                                                       room_host_name[6],
        	                                                       room_id[6],
        	                                                       room_lg[6]))
    	print("|room name:{}||Host:{}||ID:{}||language:{}|".format(room_name[7],
        	                                                       room_host_name[7],
        	                                                       room_id[7],
        	                                                       room_lg[7]))
    	print("|room name:{}||Host:{}||ID:{}||language:{}|".format(room_name[8],
        	                                                       room_host_name[8],
        	                                                       room_id[8],
        	                                                       room_lg[8]))
    	print("|room name:{}||Host:{}||ID:{}||language:{}|".format(room_name[9],
        	                                                       room_host_name[9],
        	                                                       room_id[9],
        	                                                       room_lg[9]))
    	print("|room name:{}||Host:{}||ID:{}||language:{}|".format(room_name[10],
        	                                                       room_host_name[10],
        	                                                       room_id[10],
        	                                                       room_lg[10]))
    	print("|room name:{}||Host:{}||ID:{}||language:{}|".format(room_name[11],
        	                                                       room_host_name[11],
        	                                                       room_id[11],
        	                                                       room_lg[11]))
    	print("|room name:{}||Host:{}||ID:{}||language:{}|".format(room_name[12],
        	                                                       room_host_name[12],
        	                                                       room_id[12],
        	                                                       room_lg[12]))
    	print("|room name:{}||Host:{}||ID:{}||language:{}|".format(room_name[13],
        	                                                       room_host_name[13],
        	                                                       room_id[13],
        	                                                       room_lg[13]))
    	print("|room name:{}||Host:{}||ID:{}||language:{}|".format(room_name[14],
        	                                                       room_host_name[14],
        	                                                       room_id[14],
        	                                                       room_lg[14]))
    	print("|room name:{}||Host:{}||ID:{}||language:{}|".format(room_name[15],
        	                                                       room_host_name[15],
        	                                                       room_id[15],
        	                                                       room_lg[15]))
    	print("|room name:{}||Host:{}||ID:{}||language:{}|".format(room_name[16],
        	                                                       room_host_name[16],
        	                                                       room_id[16],
        	                                                       room_lg[16]))
    	print("|room name:{}||Host:{}||ID:{}||language:{}|".format(room_name[17],
        	                                                       room_host_name[17],
        	                                                       room_id[17],
        	                                                       room_lg[17]))
    	print("|room name:{}||Host:{}||ID:{}||language:{}|".format(room_name[18],
        	                                                       room_host_name[18],
        	                                                       room_id[18],
        	                                                       room_lg[18]))
    	print("|room name:{}||Host:{}||ID:{}||language:{}|".format(room_name[19],
        	                                                       room_host_name[19],
        	                                                       room_id[19],
        	                                                       room_lg[19]))
    	print("|room name:{}||Host:{}||ID:{}||language:{}|".format(room_name[20],
        	                                                       room_host_name[20],
        	                                                       room_id[20],
        	                                                       room_lg[20]))