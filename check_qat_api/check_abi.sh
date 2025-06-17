#!/bin/bash


./abi-compliance-checker/abi-compliance-checker.pl --help >> /dev/null
if [ $? -ne 0 ]; then
    git clone https://github.com/lvc/abi-compliance-checker.git
    cd abi-compliance-checker/
    sudo make install prefix=/usr
    cd ..
fi
./abi-dumper/abi-dumper.pl --help >> /dev/null
if [ $? -ne 0 ]; then
    git clone https://github.com/lvc/abi-dumper.git
    cd abi-dumper/
    sudo make install prefix=/usr
    cd ..
fi
sudo yum install libabigail -y

#PACKAGE_URL_0=$(cat package_0.txt)
echo $1
echo $2
PACKAGE_URL_0=${RELEASE_PACKAGE}
PACKAGE_URL_1=${CHECK_PACKAGE}
echo '****************'
echo ${ABI_REPORTS}
echo '****************'
#PACKAGE_URL_1=$2
#PACKAGE_URL_0=$1
#PACKAGE_URL_0='https://af01p-ir.devtools.intel.com/artifactory/scb-local/QAT_packages/QAT_U/QAT_UPSTREAM_22.07.2/QAT_UPSTREAM_22.07.2.L.0.0.0-00003/QAT_UPSTREAM_22.07.2.L.0.0.0-00003.tar.gz'
#PACKAGE_URL_1='https://af01p-ir.devtools.intel.com/artifactory/scb-local/QAT_packages/QAT_U/QAT_UPSTREAM_23.02.0/QAT_UPSTREAM_23.02.0.L.0.0.0-00010/QAT_UPSTREAM_23.02.0.L.0.0.0-00010.tar.gz'
PACKAGE_NAME_0="${PACKAGE_URL_0##*/}"
PACKAGE_NAME_1="${PACKAGE_URL_1##*/}"
PACKAGE_FOLDER_0=${PACKAGE_NAME_0%.*.*}
PACKAGE_FOLDER_1=${PACKAGE_NAME_1%.*.*}

echo "Params:"
echo ${PACKAGE_URL_0}
echo ${PACKAGE_URL_1}
echo ${PACKAGE_NAME_0} ${PACKAGE_NAME_1} ${PACKAGE_FOLDER_0} ${PACKAGE_FOLDER_1}

if [ -z ${PACKAGE_URL_0} ];then
    echo "No first package URL"
    exit -1
fi
if [ -z ${PACKAGE_URL_1} ];then
    echo "No second package URL"
    exit -1
fi


rm -rf *.tar.gz ${PACKAGE_FOLDER_0} ${PACKAGE_FOLDER_1} QAT_UPSTREAM*
wget --user=${CREDS_USR} --password=${CREDS_PSW} ${PACKAGE_URL_0}
if [ $? -ne 0 ];then
    echo "First package download error"
    exit -1
fi
wget --user=${CREDS_USR} --password=${CREDS_PSW} ${PACKAGE_URL_1}
if [ $? -ne 0 ];then
    echo "Second package download error"
    exit -1
fi
mkdir ${PACKAGE_FOLDER_0} ${PACKAGE_FOLDER_1}
tar -zxf ${PACKAGE_NAME_0} -C ${PACKAGE_FOLDER_0}
tar -zxf ${PACKAGE_NAME_1} -C ${PACKAGE_FOLDER_1}

#package 0
cd ${PACKAGE_FOLDER_0}
mkdir m4
./autogen.sh
CFLAGS="-g -Og" ./configure --enable-service
make -j
cd ..

#package 1
cd ${PACKAGE_FOLDER_1}
mkdir m4
./autogen.sh
CFLAGS="-g -Og" ./configure --enable-service
make -j
cd ..

#abidiff
rm -rf abidiff.log
echo "### AbiDiff Log ###" 2>&1 | tee -a abidiff.log
echo "Packages:"  2>&1 | tee -a abidiff.log
echo ${PACKAGE_NAME_0} 2>&1 | tee -a abidiff.log
echo "" 2>&1 | tee -a abidiff.log
echo ${PACKAGE_NAME_1} 2>&1 | tee -a abidiff.log
echo "####################################################################################################################################" 2>&1 | tee -a abidiff.log
echo '' 2>&1 | tee -a abidiff.log
echo "abidiff symlinks&variables:" 
echo "Abidiff usdm:" 2>&1 | tee -a abidiff.log
USDM_LIB_0=$(readlink ./${PACKAGE_FOLDER_0}/.libs/libusdm.so)
USDM_LIB_1=$(readlink ./${PACKAGE_FOLDER_1}/.libs/libusdm.so)
echo "Libraries:" ${USDM_LIB_0} ${USDM_LIB_1} 2>&1 | tee -a abidiff.log
echo '' 2>&1 | tee -a abidiff.log
echo 'abidiff' ${PACKAGE_FOLDER_0}'/.libs/'${USDM_LIB_0} ${PACKAGE_FOLDER_1}'/.libs/'${USDM_LIB_1} 2>&1 | tee -a abidiff.log
echo '' 2>&1 | tee -a abidiff.log
abidiff ${PACKAGE_FOLDER_0}/.libs/${USDM_LIB_0} ${PACKAGE_FOLDER_1}/.libs/${USDM_LIB_1} 2>&1 | tee -a abidiff.log
echo "####################################################################################################################################" 2>&1 | tee -a abidiff.log
echo '' 2>&1 | tee -a abidiff.log
echo "Abidiff qat:" 2>&1 | tee -a abidiff.log
QAT_LIB_0=$(readlink ./${PACKAGE_FOLDER_0}/.libs/libqat.so)
QAT_LIB_1=$(readlink ./${PACKAGE_FOLDER_1}/.libs/libqat.so)
echo "Libraries:" ${QAT_LIB_0} ${QAT_LIB_1} 2>&1 | tee -a abidiff.log
echo '' 2>&1 | tee -a abidiff.log
echo 'abidiff' ${PACKAGE_FOLDER_0}'/.libs/'${QAT_LIB_0} ${PACKAGE_FOLDER_1}'/.libs/'${QAT_LIB_1} 2>&1 | tee -a abidiff.log
echo '' 2>&1 | tee -a abidiff.log
abidiff ${PACKAGE_FOLDER_0}/.libs/${QAT_LIB_0} ${PACKAGE_FOLDER_1}/.libs/${QAT_LIB_1} 2>&1 | tee -a abidiff.log
echo "####################################################################################################################################" 2>&1 | tee -a abidiff.log

#convert log to html
txt2html --infile abidiff.log --title "AbiDiff Report" --outfile abidiff.html


#abidump
abi-dumper ${PACKAGE_FOLDER_0}/.libs/${USDM_LIB_0} -o ABI-0.dump -lver 0
abi-dumper ${PACKAGE_FOLDER_1}/.libs/${USDM_LIB_1} -o ABI-1.dump -lver 1
abi-compliance-checker -l NAME -old ABI-0.dump -new ABI-1.dump
cp compat_reports/NAME/0_to_1/compat_report.html ./usdm.html

abi-dumper ${PACKAGE_FOLDER_0}/.libs/${QAT_LIB_0} -o ABI-0.dump -lver 0
abi-dumper ${PACKAGE_FOLDER_1}/.libs/${QAT_LIB_1} -o ABI-1.dump -lver 1
abi-compliance-checker -l NAME -old ABI-0.dump -new ABI-1.dump
cp compat_reports/NAME/0_to_1/compat_report.html ./qat.html

