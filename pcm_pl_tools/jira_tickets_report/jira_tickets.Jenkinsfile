HTTPS_PROXY="http://proxy-dmz.intel.com:912/"
HTTP_PROXY="http://proxy-dmz.intel.com:912/"
NO_PROXY="localhost,intel.com,192.168.0.0/16,172.16.0.0/12,127.0.0.0/8,10.0.0.0/8,163.33.0.0/16,137.46.0.0/16,137.102.0.0/16"

 

// Several plugins like WithPyenv is not working perfectly accross platform when using Virtual Env.
// Put this method outside pipeline
def Python(String command) {
    if (env.ISUNIX == "TRUE") {
        sh script:"source pyenv/bin/activate && python ${command}", label: "python ${command}"
    }
    else {
        powershell script:"pyenv\\Scripts\\Activate.ps1 ; python ${command}", label: "python ${command}"
    }
}

pipeline {
    
     agent {
        label('gklab-16-205')
    }
    
    
    parameters {
        //string name: 'PACKAGE_LINK', defaultValue: '', description: 'Link to package (https://af01p-ir.devtools.intel.com/artifactory/scb-local/QAT_packages/QAT20/QAT20_1.1.21/QAT20.L.1.1.21-00030/QAT20.L.1.1.21-00030.tar.gz)', trim: false
        //string name: 'JIRA_TICKETS', defaultValue: '', description: 'List of Jira tickets with Protex and Klocwork reports (QPJN-57, QPJN-58)', trim: false
        string name: 'PROJECT_KEY', defaultValue: 'LSG', description: 'Name of project', trim: false
        //string name: 'EMAIL_MAINTAINER', defaultValue: 'nex.sw.pid.sve.qat@intel.com, marzena.kupniewska@intel.com', description: 'Main person to send mail to. Only this person gets mail when pipe crashes.',  trim: false
        string name: 'EMAIL_MAINTAINER', defaultValue: 'marzena.kupniewska@intel.com', description: 'Main person to send mail to. Only this person gets mail when pipe crashes.',  trim: false
        string name: 'EMAIL_RECEIPENTS', defaultValue: 'nex.sw.pid.sve.qat@intel.com, marzena.kupniewska@intel.com', description: 'List of coma separated email receipents to CC mail.',  trim: false
		//nex.sw.pid.sve.qat@intel.com
    }
    
    environment {
        CREDS = credentials('MarzenaOlga_AD')
    }

    
        
    stages {
        
        stage('Prepare venv') {
            steps {
                script {
                    if (isUnix()) {
                        sh "echo LINUX"
                        env.ISUNIX = "TRUE" // cache isUnix() function to prevent blueocean show too many duplicate step (Checks if running on a Unix-like node) in python function below
                        sh 'python3 -m venv pyenv'
                        PYTHON_PATH =  sh(script: 'echo ${WORKSPACE}/pyenv/bin/', returnStdout: true).trim()                        
                    }
                    else {
                        env.ISUNIX = "FALSE"
                        powershell(script:"py -3 -m venv pyenv") // windows not allow call python3.exe with venv. https://github.com/msys2/MINGW-packages/issues/5001
                        PYTHON_PATH =  sh(script: 'echo ${WORKSPACE}/pyenv/Scripts/', returnStdout: true).trim()
                    }

                    try  {
                        // Sometime agent with older pip version can cause error due to non compatible plugin.
                        Python("-m pip install --upgrade pip --proxy=http://proxy-dmz.intel.com:912")
                    } 
                    catch (ignore) { } // update pip always return false when already lastest version
                    // After this you can call Python() anywhere from pipeline
                    //pip freeze > requirements.txt
                    //Python("-m pip install -r requirements.txt --proxy=http://proxy-chain.intel.com:911")
                    Python("-m pip install requests --proxy=http://proxy-dmz.intel.com:912")
                    echo ""
                }                
            }
        }
        
        stage('run'){
            steps {
                git branch: 'main',
                url: 'https://github.com/intel-sandbox/pcm_pl_tools.git'
                Python ('./jira_tickets_report/jira_tickets_report.py')
            }
        }

    }
    
    
    
    
    post{
        success{
            emailext body: 'Check console output at  ${BUILD_URL}.\n ${FILE,path="tickets_table.html"} ', attachmentsPattern: '*.log' , attachLog: true, mimeType: 'text/html', subject: '[Ticket list][QAT] ${JOB_NAME} - (${BUILD_NUMBER}) Finished Successfuly!', to: '$EMAIL_RECEIPENTS'
            //cleanWs()
            echo "Success"
        }
        unsuccessful{
            emailext body: 'Check console output at  ${BUILD_URL}.\n ${FILE,path="tickets_table.html"}  ', attachmentsPattern: '*.log' , attachLog: true, mimeType: 'text/html', subject: '[IA] ${JOB_NAME} - (${BUILD_NUMBER}) Failed!', to: '$EMAIL_MAINTAINER'
            //cleanWs()
            echo "Fail"
        }
    }
}
