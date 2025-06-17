HTTPS_PROXY="http://proxy-dmz.intel.com:912/"
HTTP_PROXY="http://proxy-dmz.intel.com:912/"
NO_PROXY="localhost,intel.com,192.168.0.0/16,172.16.0.0/12,127.0.0.0/8,10.0.0.0/8,163.33.0.0/16,137.46.0.0/16,137.102.0.0/16"

pipeline {
    
    agent {
        label('fedora36rpm')
        //label params.OS == "any" ? "" : params.OS
    }


    parameters {
        string name: 'REPO', defaultValue: 'https://github.com/intel-innersource/drivers.qat.common.sal.git', description: 'Repo to check', trim: false
        // string name: 'SRC', defaultValue: 'sal', description: 'Local folder',  trim: false
        string name: 'BRANCH', defaultValue: '92d9c444f1bb65f33fa935893f06d7416a45057c', description: 'Branch to check',  trim: false
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
                    	chmod +x ./code_spell.sh
                        ./code_spell.sh  ${REPO} ${BRANCH}              
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
