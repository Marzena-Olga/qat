
start=$(date +%s)
REPO=cryptodev-2.6
GITHUB_PR_TARGET_BRANCH=master
GITHUB_PR_SOURCE_BRANCH=master
#GITHUB_PR_NUMBER=0
JNAME=VERIFY_CRYPTODEV_UPSTREAM
config=foo

echo "Start check commits in PR"
SRC_REPO='https://github.com/intel-innersource/drivers.qat.linux.qatkernel.git'  

#PULL_REQUEST=${GITHUB_PR_NUMBER}
#pull_request_branch = ${GITHUB_PR_SOURCE_BRANCH}
JOB=${JOB_BASE_NAME}

function make_check {
#cp -f ${WORKSPACE}/KERNEL_CONFIGS/cryptodev-2.6/SI.f26_64_UPSTREAM/.config ${WORKSPACE}/${REPO}/
echo "STEP_BUILD: KERNEL"
echo 'yes "" | make oldconfig > .makeoldconfig_output 2>&1 /dev/null'
yes "" | make oldconfig > .makeoldconfig_output 2>&1 /dev/null #redirect output so Kernel options with ERR and WARN in name are not caught by parser.
echo 'make -j modules_prepare 2>&1 > /dev/null'
make -j modules_prepare 2>&1 > /dev/null
echo 'make -j 48 2>&1 > /dev/null'
make -j 48 2>&1 > /dev/null
echo 'make M=drivers/crypto/intel/qat clean 2>&1 > /dev/null'
make M=drivers/crypto/intel/qat clean 2>&1 > /dev/null
# Report version of sparse
#echo "sparse --version"
#sparse --version
# Build QAT driver with warnings enabled and Sparse
# Sparse temporarily disabled due to bug in version of Sparse used in build system
echo 'make -j 48 M=drivers/crypto/intel/qat W=1 2>&1 > /dev/null'
make -j 48 M=drivers/crypto/intel/qat W=1 2>&1 > /dev/null #C=2 
output=$?
echo "Output:" $output
#echo $output
return $output
}

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
echo "*************************************************************************************************"

cd ${WORKSPACE}/${REPO} 

if [ -z "$GITHUB_PR_NUMBER" ]
then 
  GITHUB_PR_NUMBER=$(gh pr list -L 1)  
  echo "Get last PR"
fi
echo "PR:" ${GITHUB_PR_NUMBER}
git config --global advice.detachedHead false
set -- ${GITHUB_PR_NUMBER}
gh pr checkout $1
git pull
echo "*************************************************************************************************"
git status
JSON=$(gh pr view $1 --json commits)
echo "*************************************************************************************************"
echo "Commits:"
#echo "*************************************************************************************************"
echo $JSON | jq '.commits[] | {oid, messageHeadline, committedDate} | join(" ")'
echo "*************************************************************************************************"
MESSAGE=$( echo $JSON | jq '.commits[] | {oid, messageHeadline, committedDate} | join(" ")')
echo "Oids:"
#echo "*************************************************************************************************"
echo $JSON | jq '.commits[] | {oid} | join(" ")'
OUT=$( echo $JSON | jq '.commits[] | {oid} | join(" ")')
#echo "*************************************************************************************************"
RES2=0
for i in ${OUT}
do
  echo "*************************************************************************************************"
  #i=${echo "$i" | sed `s/"$//`} 
  temp=`echo $i | sed 's/.\(.*\)/\1/' | sed 's/\(.*\)./\1/'`
  echo "OID:" $temp
  git checkout $temp
  make_check
  RES=$?
  if [ ${RES} -ne 0 ]; then
    RES2=${RES}
  fi
done
echo "*************************************************************************************************"
end=$(date +%s)
echo "Elapsed Time: $(($end-$start)) seconds"
echo "*************************************************************************************************"
if [ ${RES2} -ne 0 ]; then
    echo "Error in commit:" $temp
    exit -1
fi