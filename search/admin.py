import json
import requests
import os, re

session = requests.session()


f = open('athus.cookie', 'r')
session.cookies.update(eval(f.read()))
f.close()

menssage = 'Londarks'
rooms = session.get("https://drrr.com/lounge?api=json")
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
# Adicionando parametros a salas
for j in range(len(salas)):
	print('Name|ID|Lang|')
	print("|{}|{}|{}|".format(salas[j]['name'],salas[j]['roomId'],salas[j]['language']))

# for loop in len(user):
#     print(user[loop]['name'])
#print("{}".format(user[0][2]))