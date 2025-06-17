def ABI_REPORTS = ""
pipeline {
    options {
        disableConcurrentBuilds()
        timeout(time: 3, unit: 'HOURS')
        //ansiColor('xterm')
        //timestamps()
        buildDiscarder(
            logRotator(
                daysToKeepStr: '730', 
                numToKeepStr: '100'
            )
        )      
    }
    
    agent {
        label("fedora38dell")
    }
    
    parameters {
        string name: 'RELEASE_PACKAGE', defaultValue: '', description: 'Release package (if field is empty script will choice last package marked "Released_External"), eq: QAT_UPSTREAM_23.08.0.L.0.0.0-00017.tar.gz', trim: false
        string name: 'PACKAGE_TO_CHECK', defaultValue: '', description: 'Package to check (if field is empty script will choice last created package) eq: QAT_UPSTREAM_23.02.0.L.0.0.0-00010.tar.gz',  trim: false
        string name: 'EMAIL_MAINTAINER', defaultValue: 'marzena.kupniewska@intel.com', description: 'Main person to send mail to. Only this person gets mail when pipe crashes.',  trim: false
        string name: 'EMAIL_RECEIPENTS', defaultValue: 'marzena.kupniewska@intel.com', description: 'List of coma separated email receipents to CC mail.',  trim: false
    }
    
    environment {
        //proxy related
        http_proxy="http://proxy-dmz.intel.com:912/"
        https_proxy="http://proxy-dmz.intel.com:912/"
        no_proxy=".intel.com"
        //ABI_REPORTS=""
        //GIT related
        GIT_TRACE_PACKET = 1
        GIT_TRACE = 1
        //GIT_CURL_VERBOSE = 1
        REPO_URL = 'https://github.com/intel-sandbox/check_qat_api.git'
        REPO_NAME = 'Jenkins Pipelines for QAT'
        BRANCH_NAME = 'main'
        
        //credentials related
        gitHubCredsId = 'MarzenaOlga_AD'
        // artifactoryCreds = 'artifactory-username-and-password-4-qat'
         artifactoryCreds = 'MarzenaOlga_AD'
    }
    
    stages {
        stage('prereq'){
            steps{
                checkout([
                    $class: 'GitSCM', 
                    branches: [[name: "${env.BRANCH_NAME}"]], 
                    doGenerateSubmoduleConfigurations: false, 
                    //extensions: [[
                    //    $class: 'RelativeTargetDirectory', 
                    //    relativeTargetDir: "${env.REPO_NAME}"]], 
                    gitTool: 'Default', 
                    submoduleCfg: [], 
                    userRemoteConfigs: [[
                        credentialsId: "${env.gitHubCredsId}",
                        url: "${env.REPO_URL}"]]
                ])
                sh '''
                    #!/usr/bin/env bash
                    #sudo dnf install -y python3-virtualenv-api nasm dh-autoreconf.noarch fedora-packager rpmdevtools gcc
                    #cd Upstream
                    python3 -m venv checkabi
                    . checkabi/bin/activate
                    python3 -m pip install --upgrade pip
                    python3 -m pip install requests
                    deactivate
                '''
            }
        }
        stage('check abi'){
            steps {
                withCredentials([usernamePassword(credentialsId: "${env.artifactoryCreds}", passwordVariable: 'CREDS_PSW', usernameVariable: 'CREDS_USR')]){
                    sh '''
                        #cd Upstream
                        . checkabi/bin/activate
                        python3 detect_package.py -u
                        cat path.txt
                        deactivate
                        export ABI_REPORTS=$(cat path.txt)
                        #env|sort
                    '''
                script {

                    ABI_REPORTS = sh(script: 'cat path.txt', returnStdout: true).trim().readLines()
                    sh(script: 'env|sort', returnStdout: true).trim().readLines()
                    //rtServer(
                    //    id: 'AF_creds',
                    //    url: 'https://af01p-ir.devtools.intel.com/artifactory',
                    //    credentialsId: artifactoryCreds,
                    //    bypassProxy: true,
                    //    timeout: 300
                    //)
                    //rtUpload(
                    //    serverId: 'AF_creds',
                    //    spec: """{
                    //        "files":[{
                    //            "pattern": "${WORKSPACE}/Upstream/*.html",
                    //            "target": "${ABI_REPORTS}/abi_check/${BUILD_NUMBER}/",
                    //            "props": "retention.days=365;build.number=${BUILD_NUMBER}"
                    //        }]
                    //    }""",
                    //)
                } //end of script
                }
            }
        }        
        }
    
    post {
        success{
            emailext body: 'Check console output at  ${BUILD_URL}.\n ${FILE,path="abidiff.html"} ${FILE,path="usdm.html"}  ${FILE,path="qat.html"} ', attachmentsPattern: '*.log' , attachLog: true, mimeType: 'text/html', subject: '[QAT IA AUTOMATION][QAT] ${JOB_NAME} - (${BUILD_NUMBER}) Finished Successfuly!', to: '$EMAIL_MAINTAINER, cc: $EMAIL_RECEIPENTS'
            //cleanWs()
            echo "Success"
        }
        unsuccessful{
            emailext body: 'Check console output at  ${BUILD_URL}.\n ', attachmentsPattern: '*.log' , attachLog: true, mimeType: 'text/html', subject: '[IA] ${JOB_NAME} - (${BUILD_NUMBER}) Failed!', to: '$EMAIL_MAINTAINER'
            //cleanWs()
            echo "Fail"
        }
    }
}
