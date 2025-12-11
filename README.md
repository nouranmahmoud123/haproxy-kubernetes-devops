# Kubernetes HAProxy DevOps Project

## نظرة عامة
مشروع Kubernetes متكامل يتضمن:
- HAProxy/Nginx Ingress Controller
- Multiple Deployments (Backend, Nginx, API Viewer)
- RBAC Configuration
- Kubernetes API Viewer Dashboard

## المتطلبات
- Minikube
- Docker
- kubectl
- Python 3.11+ (للـ development)

## البدء السريع

### 1. تشغيل Minikube
```bash
minikube start --driver=docker --cpus=2 --memory=2048
```

### 2. تفعيل Ingress Addon
```bash
minikube addons enable ingress
```

### 3. تطبيق Kubernetes Manifests
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

### 6. الدخول على التطبيق
```bash
MINIKUBE_IP=$(minikube ip)
echo "API Viewer: http://$MINIKUBE_IP:32456/"
echo "Nginx App: http://$MINIKUBE_IP/"
```

## الـ Architecture
