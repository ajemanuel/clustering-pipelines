import os
import datetime

def writeAutoLog():
	d = datetime.datetime.now()
	with open('C:\\Data\\autoClusterLogs\\log'+d.strftime('%Y%m%d')+'.txt','a+') as f:
	# x gives date in local format and X gives time in local format
		f.write('Ran Autocluster today, '+d.strftime('%x')+' at '+d.strftime('%X')+'.\n')
	
def main():
	writeAutoLog()

if __name__ == '__main__':
	main()