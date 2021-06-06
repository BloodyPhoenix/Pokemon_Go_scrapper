import sqlite3
import os
from bs4 import BeautifulSoup
from bs4.element import NavigableString, Tag
from urllib.request import urlopen
import re

_TYPE_DICT = {"normal": "нормальный", "fighting": "боевой", "flying": "летающий", "poison": "ядовитый",
              "ground": "земляной", "rock": "каменный", "bug": "насекомый", "ghost": "призрачный", "steel": "стальной",
              "fire": "огненный", "water": "водный", "grass": "травяной", "electric": "электрический",
              "psychic": "психический", "ice": "ледяной", "dragon": "драконий", "dark": "тёмный", "fairy": "волшебный"}

html = urlopen("https://serebii.net/pokemongo/moves.shtml")
Soup = BeautifulSoup(html.read(), features="html.parser")
moves_table = Soup.find("li", {"title": "VCurrent"})
rows = moves_table.findAll("img", {"src": re.compile("(type)+")})
os.chdir("..")
for dir_path, *_ in os.walk(os.getcwd()):
    if "Databases" in str(dir_path):
        os.chdir(dir_path)
connection = sqlite3.Connection("GO_Moves.db")
with connection:
    cursor = connection.cursor()
    sql = "CREATE TABLE IF NOT EXISTS Fast_moves (name varchar(30), move_type varchar (15), " \
            "pve_damage int (2), pve_energy int (2), pve_time varchar (3), " \
            "pvp_damage int (2), pvp_energy int (2), pvp_time varchar (3))"
    cursor.execute(sql)
    sql = "CREATE TABLE IF NOT EXISTS Charge_moves (name varchar(30), move_type varchar (15), " \
            "time varchar (3), pve_damage int (2), pve_energy int (1), pvp_damage int (2), pvp_energy int(3))"
    cursor.execute(sql)


class GetMoveInfo:

    def __init__(self, row):
        self.row = row
        self.tags = []

    def save_fast_move(self):
        name = self.tags[0]
        move_type = self.tags[1]
        pve_damage = int(self.tags[3])
        pve_energy = int(self.tags[4])
        pve_time = self.tags[5][:-9]
        pvp_damage = int(self.tags[6])
        pvp_energy = int(self.tags[7])
        pvp_time = self.tags[8][:-9]
        sql = "SELECT name FROM Charge_moves"
        cursor.execute(sql)
        if name in cursor.fetchall():
            sql = f"UPDATE Fast_moves SET move_type = \"{move_type}\", pve_damage = {pve_damage}, " \
                  f"pve_time=\"{pve_time}\", pve_energy = {pve_energy}, pvp_damage = {pvp_damage}, " \
                  f"pvp_time = \"{pvp_time}, pvp_energy = {pvp_energy} WHERE name = \"{name}\""
        else:
            sql = f"INSERT INTO Fast_moves (name, move_type, pve_damage, pve_energy, pve_time, pvp_damage, pvp_energy," \
                  f"pvp_time) VALUES (\"{name}\", \"{move_type}\", {pve_damage}, {pve_energy}, \"{pve_time}\", " \
                  f"{pvp_damage}, {pvp_energy}, \"{pvp_time}\")"
        cursor.execute(sql)
        connection.commit()

    def save_charge_move(self):
        name = self.tags[0]
        move_type = self.tags[1]
        time = self.tags[4][:-8]
        pve_damage = int(self.tags[2])
        pve_energy = int(self.tags[5])
        pvp_damage = int(self.tags[6])
        pvp_energy = int(self.tags[7])
        sql = "SELECT name FROM Charge_moves"
        cursor.execute(sql)
        if name in cursor.fetchall():
            sql = f"UPDATE Charge_moves SET move_type = \"{move_type}\", pve_damage = {pve_damage}, " \
                  f"time=\"{time}\", pve_energy = {pve_energy}, pvp_damage = {pvp_damage}, pvp_energy = {pvp_energy} " \
                  f"WHERE name = \"{name}\""
        else:
            sql = f"INSERT INTO Charge_moves (name, move_type, time, pve_damage, pve_energy, pvp_damage, pvp_energy)" \
                  f"VALUES (\"{name}\", \"{move_type}\", \"{time}\", {pve_damage}, {pve_energy}, {pvp_damage}, " \
                  f"{pvp_energy})"
        cursor.execute(sql)
        connection.commit()

    def get_content(self):
        self.check_content(self.row)
        self.find_type()
        if "None" in self.tags:
            self.find_charges()
            if "Wrap" in self.tags[0] and len(self.tags[0]) > 5:
                return
            if len(self.tags) == 10:
                self.save_charge_move()
            else:
                print("Что-то пошло не так")
                print("Параметры движения:")
                for index, tag in enumerate(row_info.tags):
                    print(index, tag, end=" |")
                    print()
        else:
            if len(self.tags) == 9:
                self.save_fast_move()
            else:
                print("Что-то пошло не так")
                print("Параметры движения:")
                for index, tag in enumerate(row_info.tags):
                    print(index, tag, end=" |")
                    print()

    def find_type(self):
        type_img = str(self.row.find("img", {"src": re.compile("(type)+")}))
        for move_type in _TYPE_DICT:
            if move_type in type_img:
                move_type = _TYPE_DICT[move_type]
                self.tags.insert(1, move_type)
                break

    def find_charges(self):
        charges_img = self.row.find("img", {"src": re.compile("(energy)+")})
        try:
            charges = charges_img.get("alt")
            self.tags.insert(5, charges[0])
        except:
            self.tags.insert(5, 0)

    def check_content(self, obj):
        if isinstance(obj, NavigableString):
            line = str(obj).strip()
            self.check_value(line)
        elif isinstance(obj, Tag):
            children = obj.findChildren()
            if len(children) > 0:
                for child in children:
                    self.check_content(child)
            else:
                self.check_value(obj)

    def check_value(self, line):
        if isinstance(line, Tag):
            if line.has_attr("name"):
                line = line.parent.getText().strip()
            else:
                line = line.getText().strip()
        if len(line) > 0:
            self.tags.append(line)


for row in rows:
    full_row = row.parent.parent.parent
    row_info = GetMoveInfo(full_row)
    row_info.get_content()

sql = "SELECT * FROM Fast_moves"
cursor.execute(sql)
for move in cursor.fetchall():
    print(move)
sql = "SELECT * FROM Charge_moves"
cursor.execute(sql)
for move in cursor.fetchall():
    print(move)



