 #criando tabalas e data base dos monstros


import sqlite3

# conectando...
conn = sqlite3.connect('users.db')
# definindo um cursor
cursor = conn.cursor()

# criando a tabela (schema)
cursor.execute("""
CREATE TABLE mobs (
        id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        SPAWN INTEGER NOT NULL,
        ATK INTEGER NOT NULL,
        DEF INTEGER NOT NULL,
        CRIT INTEGER NOT NULL,
        LIFE INTEGER NOT NULL,
        XP INTEGER NOT NULL,
        url TEXT NOT NULL


);
""")
cursor.execute("""
CREATE TABLE users (
        id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        id_chat INTEGER NOT NULL,
        ATK INTEGER NOT NULL,
        DEF INTEGER NOT NULL,
        CRIT INTEGER NOT NULL,
        CASH INTEGER NOT NULL,
        LIFE INTEGER NOT NULL,
        XP INTEGER NOT NULL,
        LVL INTEGER NOT NULL,
        WEPON INTEGER NOT NULL

);
""")

cursor.execute("""
CREATE TABLE Itens (
        id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
        Name TEXT NOT NULL,
        Damange INTEGER NOT NULL,
        Description TEXT NOT NULL,
        Price INTEGER NOT NULL,
        Weight INTEGER NOT NULL,
        url TEXT NOT NULL



);
""")
cursor.execute("""
CREATE TABLE experiencia (
        id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
        name INTEGER NOT NULL,
        experiencia INTEGER NOT NULL

);
""")


print('Tabela criada com sucesso.')
# desconectando...
conn.close()