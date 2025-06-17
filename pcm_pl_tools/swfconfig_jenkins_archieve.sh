#!/bin/bash
#

#params
SWF_SRC='swf'
SWF_REPO='https://github.com/intel-innersource/drivers.qat.common.swfconfig.git'
SWF_BRANCH='main'
#SWF_TEMP_BRANCH='pr_qat_lin_dev_qate_93803'
#SWF_CONFIG='QAT20/LIN/QAT20_1.0.1'
#SWF_QAT_TICKET='QATE-93803'

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
echo "****************************************************************************"
git push origin -d ${SWF_TEMP_BRANCH}
git branch ${SWF_TEMP_BRANCH}
git checkout ${SWF_TEMP_BRANCH}
mkdir -p `dirname ./Archive/${SWF_CONFIG}`
mv ${SWF_CONFIG} ./Archive/${SWF_CONFIG}
git rm ${SWF_CONFIG}
git add ./Archive/${SWF_CONFIG}
git commit -m "${SWF_QAT_TICKET}: ${SWF_CONFIG} archieved" -m "Signed-off-by: ${EMAIL_MAINTAINER}>"
git push --set-upstream origin ${SWF_TEMP_BRANCH}
git checkout ${SWF_BRANCH}
git branch -d ${SWF_TEMP_BRANCH}
#git push origin -d ${SWF_TEMP_BRANCH}
