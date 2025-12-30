pipeline {
    agent any

    environment {
        DOCKER_IMAGE = "shakthi14/student-backend"
    }

    stages {

        stage('Clean Workspace') {
            steps {
                cleanWs()
            }
        }

        stage('Git Pull') {
            steps {
                git branch: 'main',
                    credentialsId: 'github-creds',
                    url: 'https://github.com/shakthii1407/student-app.git'
            }
        }

        stage('Docker Build') {
            steps {
                sh 'docker build -t $DOCKER_IMAGE:latest backend'
            }
        }

        stage('Docker Push') {
            steps {
                withDockerRegistry([credentialsId: 'dockerhub-creds', url: '']) {
                    sh 'docker push $DOCKER_IMAGE:latest'
                }
            }
        }

        stage('Deploy Backend') {
            steps {
                withCredentials([string(credentialsId: 'backend-secret-key', variable: 'SECRET_KEY')]) {
                    sh '''
                      docker rm -f student-backend || true
                      docker run -d \
                        -p 8000:8000 \
                        --restart unless-stopped \
                        --name student-backend \
                        -e SECRET_KEY=$SECRET_KEY \
                        shakthi14/student-backend:latest
                    '''
                }
            }
        }
    }
}
