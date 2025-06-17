#!/bin/bash
#
#params

SAl_REPO='https://github.com/intel-sandbox/applications.devops.software-core-tools.staging.qat.common.sal'
OSAL_REPO='https://github.com/intel-sandbox/applications.devops.software-core-tools.staging.qat.common.osal'
INLINE_REPO='https://github.com/intel-restricted/drivers.qat.inline.inline'
ADF_REPO='https://github.com/intel-sandbox/applications.devops.software-core-tools.staging.qat.common.adf'
ADF_CTL_REPO='https://github.com/intel-sandbox/applications.devops.software-core-tools.staging.qat.common.adf-ctl'
SAMPLE_CODE_REPO='https://github.com/intel-sandbox/applications.devops.software-core-tools.staging.qat.common.sample-code'
RELEASE_FILES_REPO='https://github.com/intel-innersource/drivers.qat.common.release-files'
BUILD_SYSTEM_REPO='https://github.com/intel-innersource/drivers.qat.common.build-system'
API_REPO='https://github.com/intel-innersource/drivers.qat.api.api'
USDM_REPO='https://github.com/intel-innersource/drivers.qat.common.usdm'
CRYPTODEV_REPO='https://git.kernel.org//pub/scm/linux/kernel/git/herbertcryptodev-2.6'
SYSTEM_TEST_REPO='https://github.com/intel-innersource/drivers.qat.validation.system-test'

#TEST_REGEX="((qat)(_upstream|_[0-9]\.[0-9](\.[0-9])?))?(_(lin|win|vmw|bsd|xse|all)_)?(main|master|next|rel_[0-9]+\.[0-9]+\.[0-9]+[a-zA-z0-9\_]{0,30}|(protected_)?dev_[a-zA-z0-9\_]{1,30}|mirror_[0-9]+\.[0-9]+\.[0-9]+[a-zA-z0-9\_]*)"
#TEST_REGEX="((qat)(_upstream|_[0-9].[0-9](\.[0-9])?))?(_(lin|win|vmw|bsd|xse|all)_)?(main|master|next|rel_[0-9]+\.[0-9]+\.[0-9]+[a-zA-z0-9\_]{0,30}|(protected_)?dev_[a-zA-z0-9\_]{1,30}|mirror_[0-9]+\.[0-9]+\.[0-9]+[a-zA-z0-9\_]*)*"
#TEST_REGEX="qat*"

SWF_SRC='swf'
SWF_REPO='https://github.com/intel-innersource/drivers.qat.common.swfconfig.git'
SWF_BRANCH='main'
BRANCH_ARRAY=($OSAL $SAL $ADF $ADF_CTL $API $INLINE $USDM $CRYPTODEV $SYSTEM_TEST $SAMPLE_CODE $RELESE_FILES $BUILS_SYSTEM)
declare -A BRANCH_TABLE=( [$OSAL_REPO]=$OSAL [$SAL_REPO]=$SAL )

echo "****************************************************************************"
if [ ! -d ${SWF_SRC} ]; then
  echo "Repo does not exist - Cloning SWFConfig repo"
  git clone ${SWF_REPO} ${SWF_SRC} -b ${SWF_BRANCH}
  cd ${SWF_SRC}
  git checkout ${SWF_BRANCH}
else
  echo "Pulling Updates SWFConfig repo!"
  cd ${SWF_SRC}
  git remote -v update --prune
  git fetch
  git checkout ${SWF_BRANCH}
  git reset --hard origin/${SWF_BRANCH}
fi
cd ..


echo "Regex test"
for  i in ${BRANCH_ARRAY[@]}; do
  echo $i
  if [[ $i == "qat_"* ]]; then
    python3 check_reg.py $i
    if [[ $? -ne 0 ]]; then
      exit 1
    fi
  fi
done

for i in "${!BRANCH_TABLE[@]}"
do
echo "${i}=${BRANCH_TABLE[$i]}"
done




#echo $TEST_REGEX

#echo "Regex test"
#[[ $OSAL =~  $TEST_REGEX ]] && echo "yes"
#python3 check_reg.py $OSAL
#echo "Regex test"
