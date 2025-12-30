pipeline {
    agent any

    environment {
        BACKEND_IMAGE  = "shakthi14/student-backend"
        FRONTEND_IMAGE = "shakthi14/student-frontend"
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


        stage('Build Backend Image') {
            steps {
                sh 'docker build -t $BACKEND_IMAGE:latest backend'
            }
        }

        stage('Push Backend Image') {
            steps {
                withDockerRegistry([credentialsId: 'dockerhub-creds', url: '']) {
                    sh 'docker push $BACKEND_IMAGE:latest'
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


        stage('Build Frontend Image') {
            steps {
                sh 'docker build -t $FRONTEND_IMAGE:latest frontend'
            }
        }

        stage('Push Frontend Image') {
            steps {
                withDockerRegistry([credentialsId: 'dockerhub-creds', url: '']) {
                    sh 'docker push $FRONTEND_IMAGE:latest'
                }
            }
        }

        stage('Deploy Frontend') {
            steps {
                sh '''
                  docker rm -f student-frontend || true
                  docker run -d \
                    -p 3000:80 \
                    --restart unless-stopped \
                    --name student-frontend \
                    shakthi14/student-frontend:latest
                '''
            }
        }
    }
}
