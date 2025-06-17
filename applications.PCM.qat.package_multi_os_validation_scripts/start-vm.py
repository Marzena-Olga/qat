import os
import time
import QATlib


rp = (os.path.dirname(os.path.realpath(__file__)))
os.chdir(rp)


print('######################################### Start VM-s (start) ###################################################')
z = QATlib.get_vms()
#QATlib.run_vm(QATlib.host_list(z))
QATlib.run_vm_esxi(QATlib.host_list(z))
time.sleep(60)
print('######################################### Start VM-s (end) #####################################################')