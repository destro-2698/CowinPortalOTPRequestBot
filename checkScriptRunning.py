import subprocess


pytonProcess = subprocess.check_output("ps -ef | grep botStart.py",shell=True).decode()
pytonProcess = pytonProcess.split('\n')

for process in pytonProcess:
	print(process)
