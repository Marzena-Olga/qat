#Install-Module posh-git -Scope CurrentUser -Force
#Install-Module PowerShellGet -Force -SkipPublisherCheck

Import-Module posh-git
Add-PoshGitToProfile -AllHosts

$swfconfig = 'QAT_UPSTREAM_24.02.0'
$reg_str = '((qat)(_upstream|_[0-9]\.[0-9](\.[0-9])?))?(_(lin|win|vmw|bsd|xse|all)_)?(main|master|next|rel_[0-9]+\.[0-9]+\.[0-9]*)'
$QatTicket = 'QATE-93803'
$EmailMaintener = 'marzena.kupniewska@intel.com'

#param($swfconfig, $QatTicket, $EmailMaintener)

#Variables

$swfconfig = 'QAT_UPSTREAM_24.02.0'               #swfconfig name 
$QatTicket = 'QATE-93803'                         #Jira ticket for commit and PR
$EmailMaintener = 'marzena.kupniewska@intel.com'  #sign-off email for commit and PR

$reg_str = '((qat)(_upstream|_[0-9]\.[0-9](\.[0-9])?))?(_(lin|win|vmw|bsd|xse|all)_)?(main|master|next|rel_[0-9]+\.[0-9]+\.[0-9]*)'   # regular for check  name of branch

$repo_list = @{                            #list repos in swfconfig
  Sal = 'https://github.com/intel-sandbox/applications.devops.software-core-tools.staging.qat.common.sal'
  Osal = 'https://github.com/intel-sandbox/applications.devops.software-core-tools.staging.qat.common.osal'
  Inline = 'https://github.com/intel-restricted/drivers.qat.inline.inline'
  Adf = 'https://github.com/intel-sandbox/applications.devops.software-core-tools.staging.qat.common.adf'
  Adf_ctl = 'https://github.com/intel-sandbox/applications.devops.software-core-tools.staging.qat.common.adf-ctl'
  Sample_code = 'https://github.com/intel-sandbox/applications.devops.software-core-tools.staging.qat.common.sample-code'
  Release_files = 'https://github.com/intel-innersource/drivers.qat.common.release-files'
  Build_system = 'https://github.com/intel-innersource/drivers.qat.common.build-system'
  Api = 'https://github.com/intel-innersource/drivers.qat.api.api'
  Usdm = 'https://github.com/intel-innersource/drivers.qat.common.usdm'
  Cryptodev = 'https://git.kernel.org//pub/scm/linux/kernel/git/herbertcryptodev-2.6'
  System_test = 'https://github.com/intel-innersource/drivers.qat.validation.system-test'
}

$branch_list = @{}  #empty branches list

if (!(Test-Path -Path 'set_branches')){New-Item -Name 'set_branches' -ItemType directory}          #check, prepare and cjange work directory
Set-Location -Path .\set_branches  

$command = 'git clone https://github.com/intel-innersource/drivers.qat.common.swfconfig.git swf'    #clone swfconfog repo
cmd.exe /c $command
Set-Location -Path .\swf
dir
$swf = Get-Childitem –Path . -Include $swfconfig -Recurse -ErrorAction SilentlyContinue             #search swfconfog file location
write-host $swf
$swf_content = get-content $swf                                                                     #get swfconfig file content
cd ..                                                                                               #back to work directory

foreach ($i in $swf_content){
  write-host $i
  $branch = $i.Split('=')                                                                             #assign branches to repo ID 

  if ($branch[0] -eq 'OSAL_USER_BranchorTag')     { $branch_list['Osal']          += $branch[1]} #1
  if ($branch[0] -eq 'SAL_BranchorTag')           { $branch_list['Sal']           += $branch[1]} #2
  if ($branch[0] -eq 'INLINE_BranchorTag')        { $branch_list['Inline']        += $branch[1]} #3
  if ($branch[0] -eq 'ADF_UPSTREAM_BranchorTag')  { $branch_list['Adf']           += $branch[1]} #4
  if ($branch[0] -eq 'ADF_CTL_BranchorTag')       { $branch_list['Adf_ctl']       += $branch[1]} #5
  if ($branch[0] -eq 'SYSTEM_TEST_BranchorTag')   { $branch_list['System_test']   += $branch[1]} #6
  if ($branch[0] -eq 'SAMPLE_USER_BranchorTag')   { $branch_list['Sample_code']   += $branch[1]} #7
  if ($branch[0] -eq 'RELEASE_FILES_BranchorTag') { $branch_list['Release_files'] += $branch[1]} #8
  if ($branch[0] -eq 'BS_BranchorTag')            { $branch_list['Build_system']  += $branch[1]} #9
  if ($branch[0] -eq 'API_BranchorTag')           { $branch_list['Api']           += $branch[1]} #10
  if ($branch[0] -eq 'CMD_USER_BranchorTag')      { $branch_list['Usdm']          += $branch[1]} #11
  if ($branch[0] -eq 'CRYPTODEV_BranchorTag')     { $branch_list['Cryptodev']     += $branch[1]} #12
}

foreach ($key in $branch_list.GetEnumerator()) {                                           
    #"$($key.Name): $($key.Value)"
    $test_result = $key.Value | Select-String -Pattern $reg_str                                     #check if branch is commit tag or not
    if ($test_result -ne $null) {
        #$test_result.Matches[0].Value
        write-host $key.Name,`t, $key.Value,`t, $repo_list[$key.Name]                                  
        #New-Branch -RepoId $key.Name -Branch $key.Value -RepoURL $repo_list[$key.Name]             #if branch is in regular expression run New-Branch function 
        }
    }


Function New-Branch{
param ($RepoId, $RepoURL, $Branch )
if (!(Test-Path -Path $RepoId)) {              #clone repo
    git clone $RepoURL $RepoId
    cd $RepoId
    git checkout main
    }
else {
   cd $RepoId                                 #refresh repo
   git remote -v update --prune
   git fetch
   git checkout main
   git reset --hard origin/main
   }
$check_branch = git ls-remote --heads origin refs/heads/$Branch         #check if remote branch exist
write-host $check_branch 

if ($check_branch.Length -eq 0){                                        #if not create new branch
    write-host "No branch"
    #git push origin -d $Branch
    git branch $Branch
    git checkout $Branch
    $command = ('git commit -m "{0}: created branch {1}" -m "Signed-off-by: <{2}>"' -f $QatTicket, $Branch, $EmailMaintener)
    cmd.exe /c $command
    git push --set-upstream origin $Branch
    }
cd ..
}

#Set-Location ..\..\
#Remove-Item -Path 'set_branches' -Force -Recurse
