#!/bin/bash

QAT_SRC="cryptodev-2.6"
FEDORA_KERNEL_SRC="kernel"
#QAT_REPO="git@github.com:intel-innersource/drivers.qat.linux.qatkernel.git"
QAT_REPO="https://github.com/intel-innersource/drivers.qat.linux.qatkernel.git"
FEDPKG_DEPS="fedpkg fedora-packager rpmdevtools ncurses-devel pesign grubby"
FEDORA_PATCHES_FILE="linux-kernel-test.patch"

QAT_PATCHES=(`echo $1 |tr ',' ' '`)
FEDORA_KERNEL_BRANCH=$2
WORKDIR=$3
QAT_BUILD_S_N=${4:-0000}
QAT_BUILD_STR=${5:-qat_custom}
QAT_BUILD_TAG=${QAT_BUILD_S_N}\\.${QAT_BUILD_STR}
QAT_BRANCH=${6:-master}

sudo dnf install -y ${FEDPKG_DEPS}
sudo grep `whoami` /etc/pesign/users || whoami | sudo tee -a /etc/pesign/users
sudo /usr/libexec/pesign/pesign-authorize

echo ${QAT_REPO}
echo ${QAT_REPO}
echo ${WORKDIR}
echo ${QAT_SRC} 
echo ${QAT_BRANCH}

git clone ${QAT_REPO} ${WORKDIR}/${QAT_SRC} -b ${QAT_BRANCH}
cd ${WORKDIR}/${QAT_SRC}

> ${WORKDIR}/${FEDORA_PATCHES_FILE}
for patch in "${QAT_PATCHES[@]}"
do
	patch_file=`git format-patch -1 $patch`
	cat $patch_file >> ${WORKDIR}/${FEDORA_PATCHES_FILE}
done

cd ${WORKDIR}
rm -rf ${WORKDIR}/${QAT_SRC}
fedpkg clone -a kernel
cd ${WORKDIR}/${FEDORA_KERNEL_SRC}
git checkout ${FEDORA_KERNEL_BRANCH}
sudo dnf -y builddep kernel.spec
sed -i "/define buildid/s/^# /%/g" kernel.spec
sed -i "/\.local/s/local/${QAT_BUILD_TAG}/g" kernel.spec
cp ${WORKDIR}/${FEDORA_PATCHES_FILE} ${FEDORA_PATCHES_FILE}
fedpkg local --define "_topdir $(pwd)/rpmroot"
#fedpkg local

WWWDIR=$(date +"%H.%M_%d_%m_%Y")
echo ${WWWDIR}
mkdir /var/www/html/${WWWDIR}
cp -r ${WORKDIR}/kernel/x86_64 /var/www/html/${WWWDIR}

# Upload to yum/dnf
