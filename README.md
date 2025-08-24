kubectl apply -f mysql-secret.yaml
kubectl create configmap mysql-initdb-script --from-file=../src/init.sql
kubectl apply -f mysql-service-headless.yaml
kubectl apply -f mysql-service-clusterip.yaml
kubectl apply -f mysql-statefulset.yaml
kubectl wait --for=condition=ready pod/mysql-0 --timeout=600s

kubectl apply -f workprofile-configmap.yaml
kubectl apply -f workprofile-deployment-temp.yaml
kubectl apply -f workprofile-service.yaml
kubectl wait --for=condition=available deployment/workprofile --timeout=600s

NODE_PORT=$(kubectl get service workprofile-service -o jsonpath='{.spec.ports[0].nodePort}')
echo "WorkProfile NodePort: $NODE_PORT"

NODE_IP=$(kubectl get nodes -o jsonpath='{.items[0].status.addresses[?(@.type=="InternalIP")].address}')
echo "Node IP: $NODE_IP"

curl -f http://$NODE_IP:$NODE_PORT/ && echo "✓ Kubernetes app works"
curl -f http://$NODE_IP:$NODE_PORT/health && echo "✓ Kubernetes health works"
curl -s http://$NODE_IP:$NODE_PORT/health | grep "Application: Healthy" && echo "✓ Kubernetes database works (via app health)"


kubectl port-forward --address 0.0.0.0 deployment/workprofile 5000:5000 &
FORWARD_PID=$!
sleep 5

kubectl delete -f mysql-secret.yaml || true
kubectl delete -f mysql-service-headless.yaml || true
kubectl delete -f mysql-service-clusterip.yaml || true
kubectl delete -f mysql-statefulset.yaml || true
kubectl delete -f workprofile-configmap.yaml || true
kubectl delete -f workprofile-service.yaml || true
kubectl delete -f workprofile-deployment-temp.yaml || true
kubectl delete pvc mysql-persistent-storage-mysql-0 || true
kubectl delete configmap mysql-initdb-script || true
rm workprofile-deployment-temp.yaml || true



https://github.com/Esti-Atias/WorkProfile.git