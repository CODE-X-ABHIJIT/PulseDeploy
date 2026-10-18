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
                    .venv/bin/pytest -q
                '''
            }
        }

        stage('Build Image') {
            steps {
                script {
                    env.IMAGE = "${env.IMAGE_NAME}:${env.GIT_COMMIT.take(12)}"
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

                        kubectl --context kind-pulsedeploy-lab \
                          port-forward -n pulsedeploy \
                          service/pulsedeploy 18080:80 \
                          >/tmp/pulsedeploy-pf.log 2>&1 &
                        PF_PID=$!
                        trap 'kill "$PF_PID" 2>/dev/null || true' EXIT

                        for i in $(seq 1 20); do
                            if curl -fsS http://127.0.0.1:18080/health; then
                                exit 0
                            fi
                            sleep 2
                        done

                        echo "Health check failed"
                        exit 1
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
