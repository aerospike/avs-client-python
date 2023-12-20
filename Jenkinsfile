pipeline {
    agent any

    options {
        disableConcurrentBuilds()
        buildDiscarder(logRotator(numToKeepStr: '5', artifactNumToKeepStr: '5'))
    }

    stages {
        stage("Pipeline") {
            stages {
                stage("Checkout") {
                    steps {
                        checkout([
                                $class           : 'GitSCM',
                                branches         : scm.branches,
                                extensions       : scm.extensions + [[$class: 'CleanBeforeCheckout']],
                                userRemoteConfigs: scm.userRemoteConfigs
                        ])
                    }
                }

                stage("Build") {
                    steps {
                        echo "Building.."
                        sh "python3 -m venv .venv"
                        sh '''#!/bin/bash
                                source .venv/bin/activate
                        '''
                        sh "./proto/codegen.sh"
                        sh "python3 -m pip install build"
                        sh "python3 -m build"
                    }
                }

                stage("Upload") {
                    steps {
                        echo "Uploading archives.."
                        sh "python3 -m pip install twine"
                        sh "python3 -m twine upload --repository ecosystem-python-dev-local dist/*"
                    }
                }
            }
        }
    }

    post {
        cleanup {
            cleanWs()
        }
    }
}
