HTTPS_PROXY="http://proxy-dmz.intel.com:912/"
HTTP_PROXY="http://proxy-dmz.intel.com:912/"
NO_PROXY="localhost,intel.com,192.168.0.0/16,172.16.0.0/12,127.0.0.0/8,10.0.0.0/8,163.33.0.0/16,137.46.0.0/16,137.102.0.0/16"

pipeline {
    
    agent {
        label('fedora38dell')
        //label params.OS == "any" ? "" : params.OS
    }


    parameters {
        string name: 'SWF_CONFIG', defaultValue: 'QAT20/LIN/QAT20_1.0.1', description: 'pathes to swfconfig file', trim: false
        string name: 'SWF_QAT_TICKET', defaultValue: 'QATE-93803', description: 'Jira ticket', trim: false
        string name: 'SWF_TEMP_BRANCH', defaultValue: 'pr_qat_lin_dev_qate_93803', description: 'Temporary branch', trim: false
        string name: 'EMAIL_MAINTAINER', defaultValue: 'marzena.kupniewska@intel.com', description: 'Main person to send mail to. Only this person gets mail when pipe crashes.',  trim: false
        string name: 'EMAIL_RECEIPENTS', defaultValue: 'qat.sw.pcm.pl@intel.com', description: 'List of coma separated email receipents to CC mail.',  trim: false
        //choice(name: "OS", choices: ["Fedora36dell", "fedora36rpm", "fedora37rpm", "Fedora38rpm"])
    }
    
    environment {
        CREDS = credentials('MarzenaOlga_AD')
    }
        
    stages {
        
        stage('run'){
            steps {
                git branch: 'main',
                url: 'https://github.com/intel-sandbox/pcm_pl_tools.git'
                script {
                    sh('echo ${WORKSPACE}')
                    sh 'chmod +x ./swfconfig_jenkins_archieve.sh'
                    sh './swfconfig_jenkins_archieve.sh'
                }
            }
        }

    }
    
    
    
    
    post{
        success{
            emailext body: 'Check console output at  ${BUILD_URL}.\n ', attachmentsPattern: '*.log' , attachLog: true, mimeType: 'text/html', subject: '[RPM generation][QAT] ${JOB_NAME} - (${BUILD_NUMBER}) Finished Successfuly!', to: '$EMAIL_MAINTAINER'
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
