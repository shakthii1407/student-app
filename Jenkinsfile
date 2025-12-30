pipeline {
    agent any

    environment {
        DOCKER_IMAGE = "shakthi14/student-backend"
    }

    stages {
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
    }
}

