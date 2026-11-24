pipeline {
    agent any

    stages {
        stage('Test') {
            steps {
                
                sh '''#!/usr/bin/env bash
                    set -euo pipefail

                    git ls-files --error-unmatch requirements.txt requirements-dev.txt
                    git archive --format=tar HEAD | docker run --rm -i \
                        -w /workspace prod-llm-python312:latest sh -ec '
                            tar -xf -
                            python3.12 --version
                            python3.12 -m venv /tmp/ci-venv
                            /tmp/ci-venv/bin/python -m pip install -r requirements-dev.txt
                            /tmp/ci-venv/bin/python -m pytest -q
                        '
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