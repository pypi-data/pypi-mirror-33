import sys
import os
import time

is_RPI = False
program_directory=sys.path[0]

if sys.version_info[0] < 3:
	'''
	try:
		import Tkinter as tk 
		import ttk
	except:
		print("python2: \"Tkinter\" sang suulgana uu: \nsudo apt-get install python-tk")
		quit()


	try:
		import cayenne.client
	except:
		print("python2: \"cayenne\" sang suulgana uu: \nsudo pip install cayenne-mqtt")
		quit()
	'''
	print("python3 -g ashiglana uu:")
	quit()


elif sys.version_info[0] == 3:
	try:
		import tkinter as tk
		from tkinter import ttk
	except:
		print("Дараах сан суугдаагүй байна\t\"tkinter\"\nсуулгах:\tsudo apt-get install python3-tk")
		quit()

	try:
		import cayenne.client
	except:
		print("Дараах сан суугдаагүй байна\t\"cayenne-mqtt\"\nсуулгах:\tsudo python3 -m pip install cayenne-mqtt")
		quit()

	try:
		import RPi.GPIO as GPIO 
		is_RPI = True
	except:
		print("Энэ нь Комьютер нь RPi биш байна.")
		for i in range(10):
			#print('.', end = '')
			time.sleep(.1)
	"""
	try:
		import matplotlib.pyplot as plt

	except:
		print("Дараах сан суугдаагүй байна\t\"matplotlib\"\nсуулгах:\tsudo python3 -m pip install matplotlib")
		quit()
	"""
	try:
		from PIL import Image, ImageTk
	except:
		print("Дараах сан суугдаагүй байна\t\"PIL\"\nсуулгах:\tsudo python3 -m pip install pil")



MQTT_USERNAME  = "703efb90-2a56-11e8-b949-51e66782563e"
MQTT_PASSWORD  = "ebfe2bc570ce3e98d3f15168daac36bcbe5e907e"
MQTT_CLIENT_ID = "51aadea0-58ce-11e8-b666-5747f1aa7b74"


################################# code #########################################################################


client = cayenne.client.CayenneMQTTClient()
app = tk.Tk()

All = []
all_scroll = []

def print_asdfasdfasdf(_event=None):
	print("you presseed")

class Nud():
	def __init__(self, a, virtualC,  name, file_on = "/usr/local/lib/python3.5/dist-packages/nomunkhet_rpi/lamp.png", file_off = "/usr/local/lib/python3.5/dist-packages/nomunkhet_rpi/lamp (1).png", r = 0, c = 0, port = 0, keyboard_short = None):
		global All, app
		All.append(self)
		self.virtualChannel = virtualC
		self.port = port
		print("hello:", name)
		self.name = name
		self.photo1  = tk.PhotoImage(file=file_on)
		self.photo0  = tk.PhotoImage(file=file_off)
		#self.photo0.zoom(.5)
		self.digital = 0
		self.root = a
		self.button = tk.Button(a, image=self.photo0, text=name,
			command = lambda: self.change_value_to(True, -1),
			height=80, width=70, compound=tk.TOP)
		self.button.grid(row=r, column=c)
		self.change_port_value()

		if keyboard_short != None:
			print("binded: key: ", keyboard_short)
			app.bind(keyboard_short, self.change_value_to)

	def change_value_to(self, isSendToCayenne = True, changeValueto=-1, _event=None):
		if(isSendToCayenne):
			if(self.digital == 1):
				self.digital = 0
			else:
				print("iishee orohgui bnu uu")
				self.digital = 1
			print("asdf", self.digital)
			client.virtualWrite(self.virtualChannel, self.digital)
		else:
			self.digital = changeValueto
			print(":p", self.digital, type(self.digital))
			#self.digital = value
			#if(self.digital == 0):
				#self.digtial = 1
				#End port asaana
			#else:
				#self.digtial = 0
		self.change_port_value()
			#print(self.name, self.digtial)

	def change_port_value(self):
		if(self.digital == 1):
			print("port", self.port, ":\ton")
			self.button.configure(image = self.photo1)
		else:
			print("port", self.port, ":\toff")
			self.button.configure(image = self.photo0)

class shirdeg():
	def __init__(self, a, virtualC, name, r = 0, c = 0, port = 0, keyboard_short = None, max=100, min=0):
		global all_scroll
		all_scroll.append(self)
		self.root = a
		self.virtualChannel = virtualC
		self.name = name
		self.value = 0
		self.isValueChanged = True
		self.scale = tk.Scale(self.root, from_=min, to=max, orient=tk.HORIZONTAL, command=self.getValue)
		self.scale.grid(row=r, column=c)
		#self.scale.pack()

	def getValue(self, event):
		self.value = self.scale.get()
		self.isValueChanged = True
		#print("scale:", self.value)
		#client.virtualWrite(self.virtualChannel, self.value)
		#time.sleep(100)


	def setValue(self, value):
		self.value = value
		self.scale.set(self.value)


print("Сайн байна уу")

app.title("Электроникийн сургалт")
app.iconphoto(True, tk.PhotoImage(file=os.path.join(program_directory, "/usr/local/lib/python3.5/dist-packages/nomunkhet_rpi/eslogo.txt"))) #end uurchlult hiih
app.geometry("500x600")

#list = [first0,first1,first2,first3]
'''
def on_message(message):
	global list
	print("Recieved: "+ str(message))
	splittedMsg = str(message).split(',') #end daraa n harah
	valueStr    = splittedMsg[0]
	channelStr  = splittedMsg[3]
	print(valueStr)
	print(channelStr)
	channel = int(channelStr.split(' ')[-1])
	value   = int(valueStr.split('\'')[-2])
	print(value)

	for each_Nud in list:
		if each_Nud.virtualChannel == channel:
			print(each_Nud.name, value)'''
""" {'channel': 1, 'value': '0', 'client_id': '51aadea0-58ce-11e8-b666-5747f1aa7b74', 'topic': 'cmd', 'msg_id': 'qFsJGM0zuvuJFLy'} """
'''def on_message1(message):
	print("ive got:\t",message)
	print("\tend of")
	msg = str(message)
	splited = msg.split(',')
	income_channel = -1
	income_value   = -1
	for each_data in splited:
		if each_data.find('channel')>=0:
			income_value = int(each_data.split('\'')[-2])
		if each_data.find('value')>=0:
			income_channel = int(each_data.split('\'')[-2])
	print("processed", income_channel, income_value)'''
def on_message2(message):
	global All
	print("start:\t", message, "\tend\n")
	print("topic: %s \nvalue:%s\nchannel:%s\n" % (message.topic, message.value, message.channel))
	print(type(message.topic), type(message.value), type(message.channel))

	for each_Nud in All:
		if 	each_Nud.virtualChannel == message.channel:
			each_Nud.change_value_to(False, changeValueto = int(message.value))


client.on_message = on_message2




def do_it():
	client.loop()
	for each_scroll in all_scroll:
		if each_scroll.isValueChanged == True:
			client.virtualWrite(each_scroll.virtualChannel, each_scroll.value)
			each_scroll.isValueChanged = False
			print(each_scroll.name, each_scroll.value)
	app.after(1000, do_it)
app.after(1000,  do_it)