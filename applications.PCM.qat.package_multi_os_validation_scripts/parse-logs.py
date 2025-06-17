
import os
import QATlib


rp = (os.path.dirname(os.path.realpath(__file__)))
os.chdir(rp)


print('######################################### Parse logs (start) ###################################################')    
tb_list = QATlib.parse_logs()
tb = QATlib.set_table(tb_list)
raw_html = QATlib.set_html(tb, QATlib.get_file())
QATlib.save_html(raw_html)
print('######################################### Parse logs (stop) ####################################################') 