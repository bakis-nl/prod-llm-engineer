pipeline {
    agent { 
        label 'python312' 
    }
    stages {
        stage('Test') {
            steps {
                sh '''
                    set -eu

                    ci_env="$(mktemp -d)"
                    trap 'rm -rf "$ci_env"' EXIT
                    command -v python3.12 || true
                    python3.12 --version || true
                    command -v python3.12 || true
                    python3.12 -m venv "$ci_env"
                    "$ci_env/bin/python" -m pip install -r requirements-dev.txt
                    "$ci_env/bin/python" -m pytest -q
                '''
            }
        }
    }
    post {
        always {
            cleanWs()
        }
    }
}