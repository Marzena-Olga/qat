REPO=qatlib
GITHUB_TARGET_BRANCH=main
GITHUB_SOURCE_BRANCH=main
SRC_REPO='https://github.com/intel/qatlib.git'
DEST_REPO='https://github.com/MarzenaOlga/libraries.qat.linux.qatlib.git'

echo "Start get repo"


if [ -d ${REPO} ]; then
  rm -rf ${REPO}
fi
echo "Cloning repo"
git clone ${SRC_REPO} ${REPO}
cd ${REPO}
git checkout ${GITHUB_SOURCE_BRANCH}

echo "Start push repo"

git remote rename origin upstream
git remote add origin ${DEST_REPO}
git push origin ${GITHUB_TARGET_BRANCH} --force