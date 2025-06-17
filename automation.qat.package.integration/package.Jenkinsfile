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
        string name: 'RELEASE_PACKAGE', defaultValue: 'https://af01p-ir.devtools.intel.com/artifactory/scb-local/QAT_packages/QAT_U/QAT_UPSTREAM_23.08.0/QAT_UPSTREAM_23.08.0.L.0.0.0-00017/QAT_UPSTREAM_23.08.0.L.0.0.0-00017.tar.gz', description: 'Release package, eq: QAT_UPSTREAM_23.08.0.L.0.0.0-00017.tar.gz', trim: false
        string name: 'GITHUB_TARGET_BRANCH', defaultValue: 'staging_branch_for_23.08', description: '',  trim: false
        //string name: 'EMAIL_MAINTAINER', defaultValue: 'marzena.kupniewska@intel.com', description: 'Main person to send mail to. Only this person gets mail when pipe crashes.',  trim: false
        //string name: 'EMAIL_RECEIPENTS', defaultValue: 'marzena.kupniewska@intel.com', description: 'List of coma separated email receipents to CC mail.',  trim: false
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
        REPO_URL = 'https://github.com/intel-sandbox/automation.qat.package.integration.git'
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
                    #cd Upstream
                    #python3 -m venv pkg
                    #. pkg/bin/activate
                    #python3 -m pip install --upgrade pip
                    #python3 -m pip install requests
                    #deactivate
                    pwd
                '''
            }
        }
        stage('get_pkg'){
            steps {
                withCredentials([usernamePassword(credentialsId: "${env.artifactoryCreds}", passwordVariable: 'CREDS_PSW', usernameVariable: 'CREDS_USR')]){
                    sh '''
                        #cd Upstream
                        #. pkg/bin/activate
                        #python3 detect_package.py -u
                        #deactivate
                        chmod +x ./integration.sh
                        ./integration.sh
                        echo ${RELEASE_PACKAGE}
                    '''
            
                }
            }
        }        
        }
    
    post {
        success{
            //emailext body: 'Check console output at  ${BUILD_URL}.\n ${FILE,path="abidiff.html"} ${FILE,path="usdm.html"}  ${FILE,path="qat.html"} ', attachmentsPattern: '*.log' , attachLog: true, mimeType: 'text/html', subject: '[QAT IA AUTOMATION][QAT] ${JOB_NAME} - (${BUILD_NUMBER}) Finished Successfuly!', to: '$EMAIL_MAINTAINER, cc: $EMAIL_RECEIPENTS'
            //cleanWs()
            echo "Success"
        }
        unsuccessful{
            //emailext body: 'Check console output at  ${BUILD_URL}.\n ', attachmentsPattern: '*.log' , attachLog: true, mimeType: 'text/html', subject: '[IA] ${JOB_NAME} - (${BUILD_NUMBER}) Failed!', to: '$EMAIL_MAINTAINER'
            //cleanWs()
            echo "Fail"
        }
    }
}
