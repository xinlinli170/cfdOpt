Ua = [3.0]
Omega = [0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0]

#Omega = [3.0]
import os

for j in Omega:
	for i in Ua:
		print "Ua = %f, Omega = %f" %(i,j)
		cmdstr = "python black_box.py %f 0 0 %f 0 0 0.1 0.1" %(j,i)
		os.system(cmdstr)
		#print "./BlackBox %f 0 0 %f 0 0 0.1 0.1" %(j,i)

