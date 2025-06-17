REPO=qatlib
#GITHUB_TARGET_BRANCH=main
GITHUB_SOURCE_BRANCH=main
#SRC_REPO='https://github.com/intel/qatlib.git'
SRC_REPO='https://github.com/intel-sandbox/qatlib.mirror.repo.git'
WDIR=qat


rm -rf ${REPO}

if [ ! -d ${REPO} ]; then
  echo "Repo does not exist - Cloning"
  git clone ${SRC_REPO} ${REPO}
  cd ${REPO}
  git checkout ${GITHUB_SOURCE_BRANCH}
else
  echo "Pulling Updates!"
  cd ${REPO}
  git remote -v update --prune
  git fetch
  git checkout ${GITHUB_SOURCE_BRANCH}
  git reset --hard origin/${GITHUB_SOURCE_BRANCH}
fi

git push origin --delete ${GITHUB_TARGET_BRANCH}
git branch ${GITHUB_TARGET_BRANCH}
git checkout ${GITHUB_TARGET_BRANCH}
echo ${GITHUB_TARGET_BRANCH}
cd ..

echo ${RELEASE_PACKAGE}
wget --user=${CREDS_USR}  --password=${CREDS_PSW}  --no-proxy ${RELEASE_PACKAGE}
rm -rf ./${WDIR}
mkdir ./${WDIR}
PACKAGE_NAME="${RELEASE_PACKAGE##*/}"
tar -zxf ${PACKAGE_NAME} -C ./${WDIR}
rm -rf ${PACKAGE_NAME}

COMM=$(python3 commit_extractor.py ./${WDIR}/README.md)
echo ${COMM}

cd ${REPO}
rm -rf *
echo "#### status #######################################################################################"
git status
cp  -r ../${WDIR}/* .

echo "#### status #######################################################################################"
git status
echo "##### add ######################################################################################"
git add *
echo "### commit ########################################################################################"
git commit -m "${COMM}"
echo "####### status ####################################################################################"
git status
echo "###########################################################################################"
git push -f --set-upstream origin ${GITHUB_TARGET_BRANCH}