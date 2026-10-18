pipeline {
    agent any

    triggers {
        pollSCM('H/2 * * * *')
    }

    options {
        skipDefaultCheckout(true)
        disableConcurrentBuilds()
        timestamps()
        timeout(time: 15, unit: 'MINUTES')
    }

    environment {
        IMAGE_NAME = 'ghcr.io/code-x-abhijit/pulsedeploy'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Test') {
            steps {
                sh '''
                    set -eu
                    python3 -m venv .venv
                    .venv/bin/pip install -r requirements.txt pytest
                    .venv/bin/python -m pytest -q
                '''
            }
        }

        stage('Build Image') {
            steps {
                script {
                    env.IMAGE = "${env.IMAGE_NAME}:${sh(script: 'git rev-parse --short=12 HEAD', returnStdout: true).trim()}"
                }
                sh 'docker build --pull -t "$IMAGE" .'
            }
        }

        stage('Push Image') {
            steps {
                withCredentials([
                    usernamePassword(
                        credentialsId: 'ghcr-credentials',
                        usernameVariable: 'GHCR_USER',
                        passwordVariable: 'GHCR_TOKEN'
                    )
                ]) {
                    sh '''
                        set -eu
                        set +x
                        echo "$GHCR_TOKEN" |
                          docker login ghcr.io \
                            -u "$GHCR_USER" --password-stdin
                        docker push "$IMAGE"
                        docker logout ghcr.io
                    '''
                }
            }
        }

        stage('Deploy') {
            steps {
                withCredentials([
                    file(
                        credentialsId: 'kubeconfig-pulsedeploy-lab',
                        variable: 'KUBECONFIG_FILE'
                    )
                ]) {
                    sh '''
                        set -eu
                        export KUBECONFIG="$KUBECONFIG_FILE"

                        kubectl --context kind-pulsedeploy-lab \
                          apply -f k8s/namespace.yaml

                        kubectl --context kind-pulsedeploy-lab \
                          apply -f k8s/service.yaml

                        sed "s|IMAGE_PLACEHOLDER|$IMAGE|g" \
                          k8s/deployment.yaml |
                          kubectl --context kind-pulsedeploy-lab apply -f -

                        kubectl --context kind-pulsedeploy-lab \
                          rollout status deployment/pulsedeploy \
                          -n pulsedeploy --timeout=180s
                    '''
                }
            }
        }

        
        stage('Verify') {
            steps {
                withCredentials([
                    file(
                        credentialsId: 'kubeconfig-pulsedeploy-lab',
                        variable: 'KUBECONFIG_FILE'
                    )
                ]) {
                    sh '''
                        set -eu
                        export KUBECONFIG="$KUBECONFIG_FILE"

                        kubectl --context kind-pulsedeploy-lab \
                        get deployment,pods,service -n pulsedeploy

                        kubectl --context kind-pulsedeploy-lab \
                        rollout status deployment/pulsedeploy \
                        -n pulsedeploy --timeout=60s

                        echo "Checking PulseDeploy health on port 8081..."

                        curl --retry 10 \
                            --retry-delay 2 \
                            --retry-connrefused \
                            --fail \
                            http://127.0.0.1:8081/health

                        echo "PulseDeploy health check successful."
                    '''
                }
            }
        }
    }

    post {
        success {
            echo 'PulseDeploy deployment succeeded.'
        }
        failure {
            echo 'Pipeline failed. Check stage logs and Kubernetes rollout status.'
        }
    }
}
