# Kubernetes HAProxy DevOps Project
**PROJECT:**
- HAProxy/Nginx Ingress Controller
- Multiple Deployments (Backend, Nginx, API Viewer)
- RBAC Configuration
- Kubernetes API Viewer Dashboard

##Prerequisite 
- Minikube
- Docker
- kubectl
- Python 3.11+ (للـ development)


### 1. Minikube
```bash
minikube start --driver=docker --cpus=2 --memory=2048
```

### 2.  Ingress Addon
```bash
minikube addons enable ingress
```

### 3.  Kubernetes Manifests
```bash
kubectl apply -f kubernetes-manifests/
```

### 4. Build الـ Docker Image
```bash
eval $(minikube docker-env)
docker build -t k8s-api-viewer:latest -f docker/Dockerfile app/
```

### 5. Deploy الـ API Viewer
```bash
kubectl apply -f kubernetes-manifests/09-api-viewer.yaml
```

### 6.app
```bash
MINIKUBE_IP=$(minikube ip)
echo "API Viewer: http://$MINIKUBE_IP:32456/"
echo "Nginx App: http://$MINIKUBE_IP/"
```

## Architecture
