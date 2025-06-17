
import os
import sys
import QATlib

rp = (os.path.dirname(os.path.realpath(__file__)))
os.chdir(rp)




def main():
    try:
        url_path = os.environ['ARTI_PATH']
    except:
        print ("No Jenkins environment")    
        url_path = ("https://af01p-ir.devtools.intel.com/artifactory/scb-local/QAT_packages/QAT17/QAT17_MAIN/")
        #url_path = ("https://af01p-ir.devtools.intel.com/artifactory/scb-local/QAT_packages/QAT18/QAT18_MAIN/")
        #url_path = ("https://af01p-ir.devtools.intel.com/artifactory/scb-local/QAT_packages/QAT18/QAT18_1.3.0/")
    print(url_path)
    #QATlib.set_html_cred(QATlib.get_cred(),url_path)
    #url_file = (QATlib.get_html_packages(url_path))
    #r = QATlib.select_html_package(url_file)
    r = QATlib.get_package(url_path)
    print(r)
    QATlib.download_package(r)

print('######################################### Get package (start) ###################################################') 
main()
print('######################################### Get package (stop) ####################################################') 