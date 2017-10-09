import subprocess

def dailyBAT():

    with open('C:\\Users\\Alan\\Documents\\GitHub\\clustering-pipelines\\dailyBAT.bat','w+') as f:
        f.write('title daily auto clustering \n')
        f.write('cd C:\\Users\\Alan\\Documents\\GitHub\\clustering-pipelines\n')
        f.write('call python writeAutoLog.py\n')
        f.write('call python autoClusterForMountainsort.py\n')
        #f.write('pause\n') ## for troubleshooting
        f.write('exit\n')

    p = subprocess.Popen('C:\\users\\Alan\\Documents\\Github\\clustering-pipelines\\dailyBAT.bat',shell=True) #run the dailyBAT file.
    stdout, stderr = p.communicate()


def main():
    dailyBAT()

if __name__ == '__main__':
    main()