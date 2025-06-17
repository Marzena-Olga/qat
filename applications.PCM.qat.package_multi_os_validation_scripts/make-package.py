
import os
import QATlib

rp = (os.path.dirname(os.path.realpath(__file__)))
os.chdir(rp)


print('######################################### Make Package (start) ###################################################')
QATlib.build_package(QATlib.get_vms())
print('######################################### Make Package (end) #####################################################')