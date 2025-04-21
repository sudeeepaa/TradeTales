pipeline {
    agent any

    stages {
        stage('Checkout Code') {
            steps {
                git branch: 'main', url: 'https://github.com/sudeeepaa/TradeTales.git'
            }
        }

        stage('Install Dependencies') {
            steps {
                sh 'pip install -r requirements.txt'
            }
        }

        stage('Run TradeTales App') {
            steps {
                sh 'nohup python main.py &'
            }
        }
    }
}
