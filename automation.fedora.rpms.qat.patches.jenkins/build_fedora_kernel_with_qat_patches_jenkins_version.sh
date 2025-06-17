#!/bin/bash
start=$(date +%s)

QAT_SRC="cryptodev-2.6"
FEDORA_KERNEL_SRC="kernel"
#QAT_REPO="git@github.com:intel-innersource/drivers.qat.linux.qatkernel.git"
QAT_REPO="https://github.com/intel-innersource/drivers.qat.linux.qatkernel.git"
FEDPKG_DEPS="fedpkg fedora-packager rpmdevtools ncurses-devel pesign grubby"
FEDORA_PATCHES_FILE="linux-kernel-test.patch"
FEDORA_REPO="https://src.fedoraproject.org/rpms/kernel.git"

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
echo ${WORKDIR}
echo ${QAT_SRC} 
echo ${QAT_BRANCH}


if [ ! -d ${WORKDIR} ]; then
  mkdir ${WORKDIR}
fi
cd ${WORKDIR}

if [ ! -d ${QAT_SRC} ]; then
  echo "Repo does not exist - Cloning CryptoDev repo"
  git clone ${QAT_REPO} ${QAT_SRC} -b ${QAT_BRANCH}
  cd ${QAT_SRC}
  git checkout ${QAT_BRANCH}
else
  echo "Pulling Updates CryptoDev repo!"
  cd ${QAT_SRC}
  git remote -v update --prune
  git fetch
  git checkout ${QAT_BRANCH}
  git reset --hard origin/${QAT_BRANCH}
fi
git status
if [ $? -ne 0 ]; then
    echo "Problem with CryptoDev repo"
    exit -1
fi
echo "*************************************************************************************************"

echo 'Create empty linux-kernel-test.patch file'
cd ..
> ${FEDORA_PATCHES_FILE}
cat ${FEDORA_PATCHES_FILE}
echo "*************************************************************************************************"

echo 'Add patches to linux-kernel-test.patch file'
cd ${QAT_SRC}
 
for patch in "${QAT_PATCHES[@]}"
do
	patch_file=`git format-patch -1 $patch`
  if [ $? -ne 0]; then
    echo "Problem with patch"
    exit -1
  fi
	cat $patch_file >> ../${FEDORA_PATCHES_FILE}
done

cd ..
cat ${FEDORA_PATCHES_FILE}
echo "*************************************************************************************************"

git config --global core.compression 0

if [ ! -d ${FEDORA_KERNEL_SRC} ]; then
  echo "Repo does not exist - Cloning Fedora repo"
  git clone ${FEDORA_REPO} ${FEDORA_KERNEL_SRC} -b ${FEDORA_KERNEL_BRANCH}
  #git clone https://src.fedoraproject.org/rpms/kernel.git kernel -b main
  cd ${FEDORA_KERNEL_SRC}
  git checkout ${FEDORA_KERNEL_BRANCH}
 else
  echo "Pulling Updates Fedora repo!"
  cd ${FEDORA_KERNEL_SRC}
  git remote -v update --prune
  git fetch
  git checkout ${FEDORA_KERNEL_BRANCH}
  git reset --hard origin/${FEDORA_KERNEL_BRANCH}
fi
git status
if [ $? -ne 0 ]; then
    echo "Problem with Fedora repo"
    exit -1
fi
echo "*************************************************************************************************"
for entry in "."/kernel*.config
do
  echo "$entry"
  str='CONFIG_CRYPTO_DEV_QAT_420XX=m'
  grep -r $str $entry
  ret=$?
  if [ $ret -ne 0 ]; then
    sed -i '/CONFIG_CRYPTO_DEV_QAT_4XXX=m/a CONFIG_CRYPTO_DEV_QAT_420XX=m' $entry
    echo "Added" $str	
  fi
	
  str='CONFIG_CRYPTO_DEV_QAT_ERROR_INJECTION=y'
  grep -r $str $entry
  ret=$?
  if [ $ret -ne 0 ]; then
    sed -i '/CONFIG_CRYPTO_DEV_QAT_420XX=m/a CONFIG_CRYPTO_DEV_QAT_ERROR_INJECTION=y' $entry
    echo "Added" $str	
  fi
done
echo "*************************************************************************************************"
sudo dnf -y builddep kernel.spec
sed -i "/define buildid/s/^# /%/g" kernel.spec
sed -i "/\.local/s/local/${QAT_BUILD_TAG}/g" kernel.spec
cp ../${FEDORA_PATCHES_FILE} ${FEDORA_PATCHES_FILE}
echo "*************************************************************************************************"
rm -rf ./x86_64/*
fedpkg local --define "_topdir $(pwd)/rpmroot"
ret=$?
if [ $ret -ne 0 ]; then
  exit 1	
fi
#fedpkg local


WWWDIR=$(date +"%H_%M_%d_%m_%Y")
echo ${WWWDIR}
mkdir ./x86_64/${WWWDIR}
cp ./x86_64/*.rpm ./x86_64/${WWWDIR}/
scp -r ./x86_64/${WWWDIR} root@10.102.16.187:/var/www/html/
echo http://10.102.16.187/${WWWDIR}
echo "*************************************************************************************************"
end=$(date +%s)
echo "Elapsed Time: $(($end-$start)) seconds"
secs=$(($end-$start))
printf '%dh:%dm:%ds\n' $((secs/3600)) $((secs%3600/60)) $((secs%60))
