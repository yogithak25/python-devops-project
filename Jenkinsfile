pipeline {
    agent any
    environment {
        IMAGE_NAME = "yogithak/python-devops-app"
    }
    stages {
        stage('Install Dependencies') {
            steps {
                sh '''
                python3 -m venv venv
                . venv/bin/activate
                pip install --upgrade pip
                pip install -r requirements.txt
                '''
            }
        }
        stage('Unit Tests') {
            steps {
                sh '''
                . venv/bin/activate
                pytest --cov=. --cov-report=xml
                '''
            }
        }
        stage('SonarQube Scan') {
            environment {
                scannerHome = tool 'sonar-scanner'
            }
            steps {
                withSonarQubeEnv('sonarqube') {
                    sh '''
                    . venv/bin/activate
                    $scannerHome/bin/sonar-scanner
                    '''
                }
            }
        }
        stage('Quality Gate') {
            steps {
                timeout(time: 5, unit: 'MINUTES') {
                    waitForQualityGate abortPipeline: true
                }
            }
        }
        stage('Docker Build') {
            steps {
                sh "docker build -t ${IMAGE_NAME}:${BUILD_NUMBER} ."
            }
        }
        stage('Trivy Scan') {
            steps {
                 sh "trivy image ${IMAGE_NAME}:${BUILD_NUMBER}"
            }
        }
        stage('Docker Push') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'dockerhub-cred',
                    usernameVariable: 'USER',
                    passwordVariable: 'PASS'
                )]) {

                    sh '''
                    docker login -u $USER -p $PASS
                    docker push ${IMAGE_NAME}:${BUILD_NUMBER}
                    '''
                }
            }
        }
    }
}
