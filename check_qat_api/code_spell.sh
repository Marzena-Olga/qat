# /usr/bash

pip install codespell --proxy http://proxy-chain.intel.com:911
git config --global advice.detachedHead false

#SRC='sal'
#REPO='https://github.com/intel-innersource/drivers.qat.common.sal.git'
#BRANCH='92d9c444f1bb65f33fa935893f06d7416a45057c'

REPO=$1
BRANCH=$2

SRC=$(grep -Po '\w\K/\w+[^?]+' <<<$(grep -Po '\w\K/\w+[^?]+' <<<$REPO))
SRC=${SRC#'/'}
SRC=${SRC%'.git'}
echo $SRC


if [ ! -d ${SRC} ]; then
  echo "Repo does not exist - Cloning repo"
  git clone ${REPO} ${SRC}
  # -b ${QAT_BRANCH}
  cd ${SRC}
  git checkout ${BRANCH}
else
  echo "Pulling Updates repo!"
  cd ${SRC}
  git remote -v update --prune
  git fetch
  git checkout ${BRANCH}
  git reset --hard origin/${BRANCH}
fi
git status
if [ $? -ne 0 ]; then
    cd ..
    rm -rf ${SRC}
    echo "Problem with repo - try again"
    git clone ${REPO} ${SRC}
    cd ${SRC}
    git checkout ${BRANCH}
    #exit -1
fi

#dict with excluded words"
dict_words='plack,wth,sie,afile,edn,caf,ore,hda,thn,clen,coo,gost,fpr,pres,te,ccompiler,modee,fo,shs,thrid,nd,ond,ody,ure,ot,cle,bu,end,ue,woh,caf.ore,ded,ofo,wel,lik,sav,ptd,vas,ans,3nd,whn,iif,caf.ore,wil,suh,fof,2rd,vie,daa,wew,nce,suh,fro,ket,slq,hda,thn'


#dict with excluded files"
dict_files='*.pdf,calgary,canterbury,calgary32'

pwd
echo "***************************** CodeSpell *****************************************"
codespell -S ${dict_files} -L ${dict_words}
echo "Exit CodeSpell:" $?
