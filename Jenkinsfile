pipeline {
    agent none

    environment {
        // USE_MOCK_LLM = "true"
        // MODEL = "mock-model"
        // GROQ_API_KEY = "test-dummy-key"
    }

    stages {
        stage('Test') {
            agent {
                docker {
                    image 'prod-llm-python312:latest'
                    reuseNode true
                }
            }
            steps {
                sh '''                    
                    set -eu

                    ci_env="$(mktemp -d)"
                    trap 'rm -rf "$ci_env"' EXIT
                    
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