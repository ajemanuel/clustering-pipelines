import subprocess

def dailyBAT():

	with open('C:\\Users\\Alan\\Documents\\GitHub\\kwik-tools\\dailyBAT.bat','w+') as f:
		f.write('title daily auto clustering \n')
		f.write('cd C:\\Users\\Alan\\Documents\\GitHub\\kwik-tools\n')
		f.write('call python writeAutoLog.py\n')
		f.write('call python autoExtract.py\n')
		f.write('call python autoCluster.py\n')

	p = subprocess.Popen('C:\\users\\Alan\\Documents\\Github\\kwik-tools\\dailyBAT.bat',shell=True) #run the dailyBAT file.
	stdout, stderr = p.communicate()
		
		
def main():
	dailyBAT()

if __name__ == '__main__':
	main()	