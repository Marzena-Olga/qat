import os
import QATlib

rp = (os.path.dirname(os.path.realpath(__file__)))
os.chdir(rp)

print('######################################### Update (start) ###################################################')
z = QATlib.get_vms()
ips = QATlib.ip_list(z)
QATlib.system_update(ips)

print('######################################### Update (end) ###################################################')
