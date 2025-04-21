pipeline {
    agent any

    environment {
        APP_DIR = 'RestApi'
    }

    stages {
        stage('Checkout Code') {
            steps {
                git branch: 'main', url: 'https://github.com/sudeeepaa/TradeTales.git'
            }
        }

        stage('Install Dependencies') {
            steps {
                dir("${env.APP_DIR}") {
                    sh 'pip install -r requirements.txt'
                }
            }
        }

        stage('Run TradeTales Flask App') {
            steps {
                dir("${env.APP_DIR}") {
                    sh 'nohup python main.py &'
                }
            }
        }
    }
}
