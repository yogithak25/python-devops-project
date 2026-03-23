pipeline {
    agent any
    environment {
        IMAGE_NAME = "yogithak/python-devops-automation-app"
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
        stage('Update Kubernetes Manifest Repo') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'github-cred',
                    usernameVariable: 'GIT_USER',
                    passwordVariable: 'GIT_PASS'
                )]) {
                    sh '''
                    rm -rf python-devops-k8s-manifests
                    git clone https://$GIT_USER:$GIT_PASS@github.com/yogithak25/python-devops-k8s-manifests.git
                    cd python-devops-k8s-manifests
                    sed -i "s|image:.*|image: ${IMAGE_NAME}:${BUILD_NUMBER}|g" python-deployment.yaml

                    git config user.email "yogithak25@gmail.com"
                    git config user.name "yogithak25"

                    git add python-deployment.yaml
                    git commit -m "Update image version ${BUILD_NUMBER}"

                    git push
                    '''
                }

            }
        }
    }
}
