# /usr/bash
rm -rf *.tar.gz
wget --user=${CREDS_USR} --password=${CREDS_PSW}  ${PACKAGE_URL}
#wget https://af01p-ir.devtools.intel.com/artifactory/scb-local/QAT_packages/QAT_U/QAT_UPSTREAM_00000.0.3/QAT_UPSTREAM_00000.0.3.L.0.0.0-00007/QAT_UPSTREAM_00000.0.3.L.0.0.0-00007.tar.gz
rm -rf ./QAT
mkdir ./QAT
tar -zxf *.tar.gz -C ./QAT
if [ $? -ne 0 ];then
exit -1
fi
cd ./QAT
mkdir m4
./autogen.sh
./configure
  make
  export ICP_ROOT=$(pwd)
  ../check_api.sh
  echo $?