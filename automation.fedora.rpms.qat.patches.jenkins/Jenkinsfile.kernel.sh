HTTPS_PROXY="http://proxy-dmz.intel.com:912/"
HTTP_PROXY="http://proxy-dmz.intel.com:912/"
NO_PROXY="localhost,intel.com,192.168.0.0/16,172.16.0.0/12,127.0.0.0/8,10.0.0.0/8,163.33.0.0/16,137.46.0.0/16,137.102.0.0/16"

pipeline {
    
    agent {
        //label('fedora36rpm')
        label params.OS == "any" ? "" : params.OS
    }


    parameters {
        string name: 'QAT_PATCHES', defaultValue: '5ee52118ac14,92bf269fbfe9,16c1ed95d1c4,d4cfb144f605', description: 'List QAT patches', trim: false
        //string name: 'FEDORA_KERNEL_BRANCH', defaultValue: 'f36', description: 'Branch on fedora repository', trim: false
        //string name: 'BUILD_DIRECTORY', defaultValue: 'fed_rpms_4_dev_conf', description: 'Build directory', trim: false
        string name: 'BUILD_SN', defaultValue: '0000', description: 'Build sn', trim: false
        string name: 'BUILD_STRING', defaultValue: 'qat_custom', description: 'Build string', trim: false
        //string name: 'BRANCH', defaultValue: 'master', description: 'Kernel branch', trim: false
        string name: 'EMAIL_MAINTAINER', defaultValue: 'marzena.kupniewska@intel.com', description: 'Main person to send mail to. Only this person gets mail when pipe crashes.',  trim: false
        string name: 'EMAIL_RECEIPENTS', defaultValue: 'marzena.kupniewska@intel.com', description: 'List of coma separated email receipents to CC mail.',  trim: false
        choice(name: "OS", choices: ["fedora36dell", "fedora36rpm", "fedora37rpm", "fedora38rpm", "fedora39rpm"])
    }
    
    environment {
        // GIT_TRACE_PACKET = 1
        // GIT_TRACE = 1
        // GIT_CURL_VERBOSE = 1
        BUILD_DIRECTORY = 'fed_rpms_4_dev_conf'
        BRANCH = 'master'
        CREDS = credentials('MarzenaOlga_AD')
    }
    
       
        
    stages {

        stage('prereq'){
            steps{
                echo "STEP 5 - Set fedora repo branch based on choosen OS"
                script{
                    switch(params.OS) {
                        case "fedora36rpm":
                          env.FEDORA_KERNEL_BRANCH = "f36";
                          break
                        case "fedora36dell":
                          env.FEDORA_KERNEL_BRANCH = "f36";
                          break
                        case "fedora36dell":
                          env.FEDORA_KERNEL_BRANCH = "f36";
                          break                        
                        case "fedora37rpm":
                          env.FEDORA_KERNEL_BRANCH = "f37";
                          break
                        case "fedora38rpm":
                          env.FEDORA_KERNEL_BRANCH = "f38";
                          break
                        case "fedora38rpm":
                          env.FEDORA_KERNEL_BRANCH = "f38";
                          break
                        case "fedora39rpm":
                          env.FEDORA_KERNEL_BRANCH = "f39";
                          break  
                        default:
                          env.FEDORA_KERNEL_BRANCH = "main";
                          break
                    }
                    echo "${env.FEDORA_KERNEL_BRANCH}"
                }
            }
        }

        stage('run'){
            steps {
                git branch: 'main',
                url: 'https://github.com/intel-sandbox/automation.fedora.rpms.qat.patches.jenkins.git'
                script {
                    sh('echo ${WORKSPACE}')
                    sh 'chmod +x ./build_fedora_kernel_with_qat_patches_jenkins_version.sh'
                    sh './build_fedora_kernel_with_qat_patches_jenkins_version.sh ${QAT_PATCHES} ${FEDORA_KERNEL_BRANCH} ${BUILD_DIRECTORY} ${BUILD_SN} ${BUILD_STRING} ${BRANCH}'
                    // ./build_fedora_kernel_with_qat_patches.sh 196e6cc2214be8d1011e81c31f4e5e22060d75db,ca097feb0584bf63ad9144959734ffda75e2697a f36 fed_rpms_4_dev_conf 0001 cfg qat_nex
                }
            }
        }

        // stage('JFrog - upload rpms'){
        //     steps {
        //         script {
        //             env.RPMsEXISTANCE = sh(script: "ls ./${BUILD_DIRECTORY}/kernel/x86_64/*.rpm", returnStdout: true).trim()
        //             if ("${env.RPMsEXISTANCE}" != "") {
        //                 rtServer(
        //                     id: 'AF_creds',
        //                     url: 'https://af01p-ir.devtools.intel.com/artifactory',
        //                     credentialsId: "${env.artifactoryCreds}",
        //                     bypassProxy: true,
        //                     timeout: 300
        //                 )
        //                 rtUpload(
        //                     serverId: 'AF_creds',
        //                     spec: """{
        //                         "files":[{
        //                             "pattern": "./${BUILD_DIRECTORY}/kernel/x86_64/*.rpm",
        //                             "target": "scb-local/QAT_packages/QAT_UPSTREAM_LIN/FEDORA36_kernel_packages/${BUILD_NUMBER}/",
        //                             "props": "retention.days=730;build.number=${BUILD_NUMBER}"
        //                         }]
        //                     }""",
        //                 )
        //             } else {
        //                 error("Something wrong with RPMs - most probably they don't exists!")
        //             }
        //         }
        //     }
        // }

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
