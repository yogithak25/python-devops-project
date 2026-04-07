pipeline {
    agent any

    environment {
        IMAGE_NAME = "yogithak/python-devops-automation-project"
    }

    stages {

        stage('Setup Python Environment') {
            steps {
                sh '''
                docker run --rm \
                -v /var/jenkins_home/workspace/python-devops-pipeline:/app \
                -w /app \
                python:3.11-slim \
                sh -c "
                pip install --upgrade pip &&
                pip install -r requirements.txt
                "
                '''
            }
        }

        stage('Unit Tests') {
            steps {
                sh '''
                docker run --rm \
                -v /var/jenkins_home/workspace/python-devops-pipeline:/app \
                -w /app \
                python:3.11-slim \
                sh -c "
                pip install -r requirements.txt &&
                pytest --cov=. --cov-report=xml
                "
                '''
            }
        }

        stage('SonarQube Scan') {
            steps {
                script {
                    def scannerHome = tool 'sonar-scanner'
                    withSonarQubeEnv('sonarqube') {
                        sh """
                        . venv/bin/activate
                        ${scannerHome}/bin/sonar-scanner \
                        -Dsonar.projectKey=python-devops-project \
                        -Dsonar.sources=. \
                        -Dsonar.python.coverage.reportPaths=coverage.xml
                        """
                    }
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
                sh '''
                docker build -t ${IMAGE_NAME}:${BUILD_NUMBER} .
                '''
            }
        }

        stage('Trivy Scan') {
            steps {
                sh '''
                docker run --rm \
                -v /var/run/docker.sock:/var/run/docker.sock \
                aquasec/trivy:0.50.0 image \
                --scanners vuln \
                --severity HIGH,CRITICAL \
                --exit-code 1 \
                ${IMAGE_NAME}:${BUILD_NUMBER}
                '''
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
                    echo $PASS | docker login -u $USER --password-stdin
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
                    git commit -m "Update image version ${BUILD_NUMBER}" || echo "No changes"

                    git push
                    '''
                }
            }
        }
    }
}
