from flask import Flask, render_template_string
from kubernetes import client, config
from datetime import datetime
import socket
import os

app = Flask(__name__)

# Load Kubernetes config from inside Pod
try:
    config.load_incluster_config()
except:
    config.load_kube_config()

v1 = client.CoreV1Api()
apps_v1 = client.AppsV1Api()
networking_v1 = client.NetworkingV1Api()

NAMESPACE = os.getenv('NAMESPACE', 'haproxy-controller-devops')

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Kubernetes Resources Viewer</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        .header h1 { font-size: 2.5em; margin-bottom: 10px; }
        .info-box {
            background: rgba(255,255,255,0.2);
            border-radius: 8px;
            padding: 15px;
            margin-top: 15px;
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
        }
        .info-item {
            background: rgba(255,255,255,0.1);
            padding: 10px;
            border-radius: 5px;
            border-left: 3px solid white;
        }
        .info-item strong { display: block; font-size: 0.9em; opacity: 0.9; }
        .info-item span { display: block; font-size: 1.1em; margin-top: 5px; }
        .content {
            padding: 30px;
        }
        .section {
            margin-bottom: 40px;
        }
        .section-title {
            font-size: 1.8em;
            color: #333;
            border-bottom: 3px solid #667eea;
            padding-bottom: 10px;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            background: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        th {
            background: #667eea;
            color: white;
            padding: 15px;
            text-align: left;
            font-weight: 600;
        }
        td {
            padding: 15px;
            border-bottom: 1px solid #eee;
        }
        tr:hover {
            background: #f8f9ff;
        }
        tr:last-child td {
            border-bottom: none;
        }
        .status-Running { color: #27ae60; font-weight: bold; }
        .status-Pending { color: #f39c12; font-weight: bold; }
        .status-Failed { color: #e74c3c; font-weight: bold; }
        .status-Succeeded { color: #27ae60; font-weight: bold; }
        .status-Unknown { color: #95a5a6; font-weight: bold; }
        .empty-state {
            text-align: center;
            padding: 40px;
            color: #7f8c8d;
            font-size: 1.1em;
        }
        .emoji { font-size: 1.3em; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Kubernetes Resources Viewer</h1>
            <div class="info-box">
                <div class="info-item">
                    <strong>Namespace</strong>
                    <span>{{ namespace }}</span>
                </div>
                <div class="info-item">
                    <strong>Pod Name</strong>
                    <span>{{ pod_name }}</span>
                </div>
                <div class="info-item">
                    <strong>Last Updated</strong>
                    <span>{{ timestamp }}</span>
                </div>
            </div>
        </div>

        <div class="content">
            <!-- Pods Section -->
            <div class="section">
                <div class="section-title">
                    <span class="emoji">🐳</span>
                    <span>Pods ({{ pods|length }})</span>
                </div>
                {% if pods %}
                <table>
                    <thead>
                        <tr>
                            <th>Pod Name</th>
                            <th>Status</th>
                            <th>Ready</th>
                            <th>Restarts</th>
                            <th>Age</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for pod in pods %}
                        <tr>
                            <td><strong>{{ pod['name'] }}</strong></td>
                            <td><span class="status-{{ pod['status'] }}">{{ pod['status'] }}</span></td>
                            <td>{{ pod['ready'] }}</td>
                            <td>{{ pod['restarts'] }}</td>
                            <td>{{ pod['age'] }}</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
                {% else %}
                <div class="empty-state">No Pods found</div>
                {% endif %}
            </div>

            <!-- Services Section -->
            <div class="section">
                <div class="section-title">
                    <span class="emoji">🔌</span>
                    <span>Services ({{ services|length }})</span>
                </div>
                {% if services %}
                <table>
                    <thead>
                        <tr>
                            <th>Service Name</th>
                            <th>Type</th>
                            <th>Cluster IP</th>
                            <th>Port</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for svc in services %}
                        <tr>
                            <td><strong>{{ svc['name'] }}</strong></td>
                            <td>{{ svc['type'] }}</td>
                            <td><code>{{ svc['cluster_ip'] }}</code></td>
                            <td>{{ svc['port'] }}</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
                {% else %}
                <div class="empty-state">No Services found</div>
                {% endif %}
            </div>

            <!-- Deployments Section -->
            <div class="section">
                <div class="section-title">
                    <span class="emoji">📦</span>
                    <span>Deployments ({{ deployments|length }})</span>
                </div>
                {% if deployments %}
                <table>
                    <thead>
                        <tr>
                            <th>Deployment Name</th>
                            <th>Ready</th>
                            <th>Up-to-date</th>
                            <th>Available</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for dep in deployments %}
                        <tr>
                            <td><strong>{{ dep['name'] }}</strong></td>
                            <td>{{ dep['ready'] }}</td>
                            <td>{{ dep['updated'] }}</td>
                            <td>{{ dep['available'] }}</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
                {% else %}
                <div class="empty-state">No Deployments found</div>
                {% endif %}
            </div>

            <!-- Ingresses Section -->
            <div class="section">
                <div class="section-title">
                    <span class="emoji">🌐</span>
                    <span>Ingresses ({{ ingresses|length }})</span>
                </div>
                {% if ingresses %}
                <table>
                    <thead>
                        <tr>
                            <th>Ingress Name</th>
                            <th>Host</th>
                            <th>Service</th>
                            <th>Port</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for ing in ingresses %}
                        <tr>
                            <td><strong>{{ ing['name'] }}</strong></td>
                            <td>{{ ing['host'] }}</td>
                            <td>{{ ing['service'] }}</td>
                            <td>{{ ing['port'] }}</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
                {% else %}
                <div class="empty-state">No Ingresses found</div>
                {% endif %}
            </div>

            <!-- ConfigMaps Section -->
            <div class="section">
                <div class="section-title">
                    <span class="emoji">⚙️</span>
                    <span>ConfigMaps ({{ configmaps|length }})</span>
                </div>
                {% if configmaps %}
                <table>
                    <thead>
                        <tr>
                            <th>ConfigMap Name</th>
                            <th>Keys Count</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for cm in configmaps %}
                        <tr>
                            <td><strong>{{ cm['name'] }}</strong></td>
                            <td>{{ cm['keys'] }}</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
                {% else %}
                <div class="empty-state">No ConfigMaps found</div>
                {% endif %}
            </div>

            <!-- Secrets Section -->
            <div class="section">
                <div class="section-title">
                    <span class="emoji">🔐</span>
                    <span>Secrets ({{ secrets|length }})</span>
                </div>
                {% if secrets %}
                <table>
                    <thead>
                        <tr>
                            <th>Secret Name</th>
                            <th>Type</th>
                            <th>Keys Count</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for secret in secrets %}
                        <tr>
                            <td><strong>{{ secret['name'] }}</strong></td>
                            <td>{{ secret['type'] }}</td>
                            <td>{{ secret['keys'] }}</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
                {% else %}
                <div class="empty-state">No Secrets found</div>
                {% endif %}
            </div>
        </div>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    try:
        # Get Pods
        pods_list = v1.list_namespaced_pod(NAMESPACE)
        pods = []
        for pod in pods_list.items:
            status = pod.status.phase
            ready = sum(1 for c in (pod.status.container_statuses or []) if c.ready)
            restarts = sum(c.restart_count for c in (pod.status.container_statuses or []))
            age_seconds = (datetime.now(pod.metadata.creation_timestamp.tzinfo) - pod.metadata.creation_timestamp).total_seconds()
            if age_seconds < 60:
                age = f"{int(age_seconds)}s"
            elif age_seconds < 3600:
                age = f"{int(age_seconds/60)}m"
            else:
                age = f"{int(age_seconds/3600)}h"
            
            pods.append({
                'name': pod.metadata.name,
                'status': status,
                'ready': f"{ready}/{len(pod.spec.containers)}",
                'restarts': restarts,
                'age': age
            })

        # Get Services
        services_list = v1.list_namespaced_service(NAMESPACE)
        services = []
        for svc in services_list.items:
            port = svc.spec.ports[0].port if svc.spec.ports else 'N/A'
            services.append({
                'name': svc.metadata.name,
                'type': svc.spec.type,
                'cluster_ip': svc.spec.cluster_ip,
                'port': port
            })

        # Get Deployments
        deployments_list = apps_v1.list_namespaced_deployment(NAMESPACE)
        deployments = []
        for dep in deployments_list.items:
            deployments.append({
                'name': dep.metadata.name,
                'ready': f"{dep.status.ready_replicas or 0}/{dep.spec.replicas}",
                'updated': dep.status.updated_replicas or 0,
                'available': dep.status.available_replicas or 0
            })

        # Get Ingresses
        ingresses_list = networking_v1.list_namespaced_ingress(NAMESPACE)
        ingresses = []
        for ing in ingresses_list.items:
            if ing.spec.rules:
                host = ing.spec.rules[0].host
                service = 'N/A'
                port = 'N/A'
                if ing.spec.rules[0].http and ing.spec.rules[0].http.paths:
                    service = ing.spec.rules[0].http.paths[0].backend.service.name
                    if ing.spec.rules[0].http.paths[0].backend.service.port:
                        port = ing.spec.rules[0].http.paths[0].backend.service.port.number
                ingresses.append({
                    'name': ing.metadata.name,
                    'host': host,
                    'service': service,
                    'port': port
                })

        # Get ConfigMaps
        configmaps_list = v1.list_namespaced_config_map(NAMESPACE)
        configmaps = []
        for cm in configmaps_list.items:
            configmaps.append({
                'name': cm.metadata.name,
                'keys': len(cm.data or {})
            })

        # Get Secrets
        secrets_list = v1.list_namespaced_secret(NAMESPACE)
        secrets = []
        for secret in secrets_list.items:
            secrets.append({
                'name': secret.metadata.name,
                'type': secret.type,
                'keys': len(secret.data or {})
            })

        pod_name = socket.gethostname()
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        return render_template_string(
            HTML_TEMPLATE,
            namespace=NAMESPACE,
            pod_name=pod_name,
            timestamp=timestamp,
            pods=pods,
            services=services,
            deployments=deployments,
            ingresses=ingresses,
            configmaps=configmaps,
            secrets=secrets
        )
    except Exception as e:
        return f"<h1>❌ Error</h1><p><strong>{type(e).__name__}:</strong> {str(e)}</p>", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=False)
