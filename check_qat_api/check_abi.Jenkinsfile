HTTPS_PROXY="http://proxy-dmz.intel.com:912/"
HTTP_PROXY="http://proxy-dmz.intel.com:912/"
NO_PROXY="localhost,intel.com,192.168.0.0/16,172.16.0.0/12,127.0.0.0/8,10.0.0.0/8,163.33.0.0/16,137.46.0.0/16,137.102.0.0/16"

pipeline {
    
    agent {
        label('fedora38dell')
        //label params.OS == "any" ? "" : params.OS
    }


    parameters {
        string name: 'PACKAGE_URL_0', defaultValue: 'https://af01p-ir.devtools.intel.com/artifactory/scb-local/QAT_packages/QAT_U/QAT_UPSTREAM_22.07.2/QAT_UPSTREAM_22.07.2.L.0.0.0-00003/QAT_UPSTREAM_22.07.2.L.0.0.0-00003.tar.gz', description: 'First package', trim: false
        string name: 'PACKAGE_URL_1', defaultValue: 'https://af01p-ir.devtools.intel.com/artifactory/scb-local/QAT_packages/QAT_U/QAT_UPSTREAM_23.02.0/QAT_UPSTREAM_23.02.0.L.0.0.0-00010/QAT_UPSTREAM_23.02.0.L.0.0.0-00010.tar.gz', description: 'Package to check',  trim: false
        string name: 'EMAIL_MAINTAINER', defaultValue: 'marzena.kupniewska@intel.com', description: 'Main person to send mail to. Only this person gets mail when pipe crashes.',  trim: false
        string name: 'EMAIL_RECEIPENTS', defaultValue: 'marzena.kupniewska@intel.com', description: 'List of coma separated email receipents to CC mail.',  trim: false
        // choice(name: "OS", choices: ["Fedora36dell", "fedora36rpm", "fedora37rpm", "Fedora38rpm"])
    }
    
    environment {
        //CREDS = credentials('MarzenaOlga_AD')
        //artifactoryCreds = 'artifactory-username-and-password'
        mo_creds = 'MarzenaOlga_AD'

    }


        
    stages {

        stage('run'){
            steps {
		withCredentials([usernamePassword(credentialsId: "${env.mo_creds}", passwordVariable: 'CREDS_PSW', usernameVariable: 'CREDS_USR')]){
                    sh '''
                        echo ${WORKSPACE}
                    	chmod +x ./check_abi.sh
                        ./check_abi.sh             
                    '''
                }
            }
        }        
        
        // stage('run'){
        //     steps {
        //         git branch: 'main',
        //         url: 'https://github.com/intel-sandbox/check_qat_api.git'
        //         script {
        //             sh('echo ${WORKSPACE}')
        //             sh 'chmod +x ./code_spell.sh'
        //             sh './code_spell.sh ${REPO} ${SRC} ${BRANCH}'  
        //         }
        //     }
        // }

    }
    
    
    
    
    post{
        success{
            //emailext body: 'Check console output at  ${BUILD_URL}.\n ', attachmentsPattern: '*.log' , attachLog: true, mimeType: 'text/html', subject: '[RPM generation][QAT] ${JOB_NAME} - (${BUILD_NUMBER}) Finished Successfuly!', to: '$EMAIL_MAINTAINER'
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
