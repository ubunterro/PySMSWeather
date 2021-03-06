#!/usr/bin/env python
# coding: utf-8

from urllib import urlretrieve
from urllib2 import urlopen
import time
import xml.etree.ElementTree as ET

# Списки температур и погодных явлений
temp = {}
prec = {}

def decPrec(prec): #Преобразуем код погодного явления в транслитированую сокращенную версию
	if prec == "overcast":
		prec = "oblachno"
	elif prec == "cloudy":
		prec = "obl.%20s%20proy."
	elif prec == "mostly-clear":
		prec = "maloobl."
	elif prec == "clear":
		prec = "Yasno"
	elif prec == "overcast-and-light-snow":
		prec = "obl,%20neb.%20sneg"
	elif prec == "cloudy-and-light-snow":
		prec = "per.%20obl;neb.%20sneg"
	return prec
	
def GetTomorrow(): #Получаем завтрашнюю дату в формате дд.мм
	strn = time.localtime(time.time() + 24*3600)
	strn = str(strn[2])+"."+str(strn[1])	
	return strn

def Repl20(text):#Заменяет все %20 на " " обратно
	space = "%20"
	for word in space:
		text = text.replace(space, ' ')
	return text

config = ET.parse('config.xml')
confroot = config.getroot()

api_id = confroot[0].text # Индивидувльный идентификатор доступа к шлюзу sms.ru
sity = confroot[1].text #  Код города, выбран Курск, другие коды могут быть найдены на http://weather.yandex.ru/static/cities.xml (id)
tel = confroot[2].text # Номер телефона, на который будет посылаться СМС

#Скачиваем XML с прогнозом погоды
xml_addr = "http://export.yandex.ru/weather-ng/forecasts/"+sity+".xml"
urlretrieve(xml_addr,"db.xml") #										<====== Загрузчик

#Парсим его
tree = ET.parse('db.xml')
root = tree.getroot()

temp[0] = root[4][6][0].text
temp[1] = root[4][6][1].text

temp[2] = root[4][7][0].text
temp[3] = root[4][7][1].text

temp[4] = root[4][8][0].text
temp[5] = root[4][8][1].text

temp[6] = root[4][9][0].text
temp[7] = root[4][9][1].text

prec[0] =root[4][6][3].attrib["code"]
prec[1] =root[4][7][3].attrib["code"]
prec[2] =root[4][8][3].attrib["code"]
prec[3] =root[4][9][3].attrib["code"]

'''Составляем строку, которую будем посылать.
1) Пробелы заменены на "%20"- ограничение GET запроса.
2) Используется транслит - позволяет вдвое увеличить размер посылаемой СМС (с 70 до 140 символов латиницей)
'''
sms = "Prognoz%20na%20"+GetTomorrow()+\
":%20utro:%20"+ temp[0]+".."+temp[1]+",%20"+decPrec(prec[0])+\
"%20den\':%20"+ temp[2]+".."+temp[3]+",%20"+decPrec(prec[1])+\
"%20vecher:%20"+ temp[4]+".."+temp[5]+",%20"+decPrec(prec[2])+\
"%20noch\':%20"+ temp[6]+".."+temp[7]+",%20"+decPrec(prec[3])

#print sms #Для отладки
geturl = "http://sms.ru/sms/send?api_id="+api_id+"&to="+tel+"&text="+sms #GET запрос
#print geturl #Для отладки
#Посылаем GET запрос на сервер sms.ru с api_id, номером телефона, и текстом сообщения.
urlopen(geturl) #												<====== Отправитель

print "Готово! Отправлено сообщение:"
print Repl20(sms)






