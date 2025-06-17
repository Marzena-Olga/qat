WORKSPACE=tp
REPO=cryptodev-2.6
GITHUB_PR_TARGET_BRANCH=master
GITHUB_PR_SOURCE_BRANCH=main
GITHUB_PR_NUMBER=0
JNAME=VERIFY_CRYPTODEV_UPSTREAM
config=foo



mkdir ${WORKSPACE}
cd ${WORKSPACE}

if [ ! -d ${REPO} ]; then
 echo "Repo does not exist - Cloning"
 git clone https://github.com/intel-innersource/drivers.qat.linux.qatkernel.git ${REPO}
 cd ${REPO}
 git checkout ${GITHUB_PR_SOURCE_BRANCH}
else
 echo "Pulling Updates!"
 cd ${REPO}
 git remote -v update --prune
 git fetch
 git checkout ${GITHUB_PR_SOURCE_BRANCH}
 git reset --hard origin/${GITHUB_PR_SOURCE_BRANCH}
fi

cd ${WORKSPACE}/${REPO}
ls -l 
gh pr list -L 1  
z=$(gh pr list -L 1)
echo $z
set -- $z
gh pr checkout $1
git status

#git log --pretty=format:"Commit: %H   Author: %an (Date: %aD)" -1 | tee git_commit_info 
gh pr view $1 --json commits


#### BUILD THE KERNEL ####
#cp -f ${WORKSPACE}/KERNEL_CONFIGS/cryptodev-2.6/SI.f26_64_UPSTREAM/.config ${WORKSPACE}/${REPO}/

echo "STEP_BUILD: KERNEL"
yes "" | make oldconfig > .makeoldconfig_output 2> /dev/null #redirect output so Kernel options with ERR and WARN in name are not caught by parser.
make -j modules_prepare
make -j 48
make M=drivers/crypto/qat clean


## Report version of sparse
#echo "sparse --version"
#sparse --version

## Build QAT driver with warnings enabled and Sparse
## Sparse temporarily disabled due to bug in version of Sparse used in build system
#make -j 48 M=drivers/crypto/qat W=1 #C=2
