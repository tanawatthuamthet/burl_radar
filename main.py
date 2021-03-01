from cefpython3 import cefpython as cef
import codecs
import numpy
import matplotlib.pyplot as plt
import pandas as pd
import time
import math
import os
import sys
import tkinter as tk
import threading

data_set = []
state = 0

with codecs.open("index.html","r",encoding="utf-8") as file:
	global html_code
	html_code = file.read()

class LoadHandler(object):
	def OnLoadingStateChange(self,browser,is_loading,**_):
		browser.WasResized()

def twocompre(bit):
	n=0
	if(bit[:1]=='1'):
		txt=''
		for i in bit:
			u='1'
			if(i=='1'):
				u='0'
			txt+=u
			n+=1
		bit=bin(int(txt,2)+1)[2:].zfill(16)
		bit="-"+str(int(bit,2))
		return int(bit)
	bit=int(bit,2)
	return bit

def load_csv():
	global data
	data=pd.read_csv("data uart1_1.csv")
	data_temp=[]
	i=-1
	while i < len(data["1:UART: RX/TX"])-1:
		i+=1
		if(data["1:UART: RX/TX"][i]!="Start bit" and data["1:UART: RX/TX"][i]!="Stop bit"):
			#print(i,data["1:UART: RX/TX"][i],data["1:UART: RX/TX"][i],data["Time[s]"][i],len(data["1:UART: RX/TX"]))
			if(data["1:UART: RX/TX"][i]=="02" and data["1:UART: RX/TX"][i+3]=="02"):
				#print("===========================")
				if i+3 < len(data["1:UART: RX/TX"]):
					i+=3
				if(len(data_temp)>0):
					data_set.append(data_temp)
					data_temp=[]
			else:
				data_temp.append([data["1:UART: RX/TX"][i],data["Time[s]"][i]])

def process_position():
	pass

def convert_nm(number):
	x_=bin(int(data_set[number][4][0],16))[2:].zfill(8)+bin(int(data_set[number][5][0],16))[2:].zfill(8)
	y_=bin(int(data_set[number][6][0],16))[2:].zfill(8)+bin(int(data_set[number][7][0],16))[2:].zfill(8)
	x_=twocompre(x_)
	y_=twocompre(y_)
	x_nm=(x_/8)
	y_nm=(y_/8)
	x_km=x_nm * 1.852
	y_km=y_nm * 1.852
	rm=math.sqrt((x_nm*x_nm)+(y_nm*y_nm))
	rk=math.sqrt((x_km*x_km)+(y_km*y_km))
	theta_rag=math.atan2(y_nm,x_nm)
	theta_deg=numpy.rad2deg(theta_rag)
	return [
		(float("{:.2f}".format(rm))),
		(float("{:.2f}".format(rk)))
		],[
		(float("{:.2f}".format(theta_rag))),
		(float("{:.2f}".format(theta_deg)))
		]

def plot_graph(action,callback):
	print("response javascript")
	global state
	if action == 1 and state < len(data_set)-1:
		state+= 1
	elif action == -1 and state > 0:
		state-= 1
	try:
		callback.Call([convert_nm(state),state])
	except:
		print("error")

def setBindings(browser):
	print("add bindings")
	bindings = cef.JavascriptBindings()
	bindings.SetFunction("change_status",plot_graph)
	browser.SetJavascriptBindings(bindings)

def main_cef(frame):
	print("main")
	print(len(data_set)-1)
	global w, h
	sys.excepthook = cef.ExceptHook
	window_info = cef.WindowInfo(frame.winfo_id())
	window_info.SetAsChild(frame.winfo_id(),[0,0,w,h])
	cef.Initialize()
	browser = cef.CreateBrowserSync(
		window_info,
		url=cef.GetDataUrl(html_code))
	browser.SetClientHandler(LoadHandler())
	setBindings(browser)
	cef.MessageLoop()
	print("end thread")

def closing():
	print("end")
	root.destroy()
	cef.Shutdown()

if __name__ == "__main__":
	load_csv()
	root = tk.Tk()
	root.state("zoomed")
	global w, h
	w, h = root.winfo_screenwidth(), root.winfo_screenheight()
	root.geometry('%dx%d+0+0' % (w, h))
	root.protocol('WM_DELETE_WINDOW',closing)
	frame = tk.Frame(root, height=h)
	frame.pack(side='top', fill='x')
	thread = threading.Thread(target=main_cef, args=(frame,))
	thread.start()
	root.mainloop()