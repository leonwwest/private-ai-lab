#!/usr/bin/env bash
set -euo pipefail

if ! command -v k3d >/dev/null 2>&1; then
  echo "k3d is required. Install it first: https://k3d.io/"
  exit 1
fi

if ! command -v kubectl >/dev/null 2>&1; then
  echo "kubectl is required."
  exit 1
fi

if k3d cluster list private-ai-lab >/dev/null 2>&1; then
  echo "k3d cluster private-ai-lab already exists"
else
  k3d cluster create private-ai-lab \
    --servers 1 \
    --agents 1 \
    --port "8080:80@loadbalancer"
fi

kubectl config use-context k3d-private-ai-lab
