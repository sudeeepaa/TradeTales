pipeline {
    agent any

    stages {
        stage('Checkout Code') {
            steps {
                git branch: 'main', url: 'https://github.com/sudeeepaa/TradeTales.git'
            }
        }

        stage('Build Docker Image') {
            steps {
                sh 'sh 'docker build -t tradetales-app -f RestApi/Dockerfile RestApi'
            }
        }

        stage('Run TradeTales Container') {
            steps {
                sh 'docker run -d --name tradetales-container tradetales-app'
            }
        }
    }
}
