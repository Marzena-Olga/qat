REPO=qatlib
GITHUB_TARGET_BRANCH=main
GITHUB_SOURCE_BRANCH=main
SRC_REPO='https://github.com/intel/qatlib.git'
DEST_REPO='https://github.com/MarzenaOlga/libraries.qat.linux.qatlib.git'

echo "Start get repo"


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

echo "Start push repo"

git remote rename origin upstream
git remote add origin ${DEST_REPO}
git push origin ${GITHUB_TARGET_BRANCH} --force
