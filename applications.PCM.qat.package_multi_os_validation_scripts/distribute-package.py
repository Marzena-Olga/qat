
import os
import QATlib

rp = (os.path.dirname(os.path.realpath(__file__)))
os.chdir(rp)




print('######################################### Copy Package (start) ###################################################')
z = QATlib.get_vms()
ip_host_list = QATlib.ip_list(z)
lt_file = QATlib.get_file()
QATlib.send_package(lt_file, ip_host_list)
print('######################################### Copy Package (end) #####################################################')