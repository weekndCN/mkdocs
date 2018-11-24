# Installing k8s HA

#### 1. 开启IPVS（开机需要再次加载）
```bash tab="Bash"
modprobe ip_vs
modprobe ip_vs
modprobe ip_vs_rr
modprobe ip_vs_wrr
modprobe ip_vs_sh
modprobe nf_conntrack_ipv4
```

#### 2. 安装etables和keepalived
```bash tab="Bash"
yum install -y ebtables keepalived
```

#### 3. 修改/etc/hosts
```bash tab="Bash"
cat >>/etc/hosts<<EOF
172.16.5.70 master01
172.16.5.71 master02
172.16.5.72 master03
172.16.5.90 vip-k8s
EOF
```

#### 4. 修改主机名

```bash tab="Master01"
hostnamectl set-hostname master01
```

```bash tab="Master02"
hostnamectl set-hostname master03
```

```bash tab="Master03"
hostnamectl set-hostname master03
```

#### 5. 关闭selinux
```bash tab="Bash"
setenforce 0

sed -i "s/^SELINUX=enforcing/SELINUX=disabled/g" /etc/sysconfig/selinux 

sed -i "s/^SELINUX=enforcing/SELINUX=disabled/g" /etc/selinux/config 

sed -i "s/^SELINUX=permissive/SELINUX=disabled/g" /etc/sysconfig/selinux 

sed -i "s/^SELINUX=permissive/SELINUX=disabled/g" /etc/selinux/config
```

#### 6. 关闭swap
```bash tab="Bash"
swapoff -a

vi /etc/fstab
#/dev/vdb                                swap                    swap    defaults        0 0
```

!!! Warning ""
    `swapoff -a`    :为 **临时** 关闭 swap  
    `vi /etc/fstab` :注释掉 swap 启动挂载项为 **永久** 关闭
    
#### 7. 修改iptables

!!! Tip ""
    Docker从1.13版本开始调整了默认的防火墙规则，禁用了iptables filter表中FOWARD链，这样会引起Kubernetes集群中跨Node的Pod无法通信。
    
```bash tab="Bash"
iptables -P FORWARD ACCEPT
```

#### 8. 关闭firewalld
```bash tab="Bash"
systemctl stop firewalld

systemctl disable firewalld
```

#### 9. 配置转发
```bash tab="Bash"
cat <<EOF >  /etc/sysctl.d/k8s.conf
net.bridge.bridge-nf-call-ip6tables = 1
net.bridge.bridge-nf-call-iptables = 1
vm.swappiness=0
EOF
```

#### 10. 配置互信

##### 10.1 生成key

!!! Note ""
    在所有的master上执行，一路回车即可！
```bash tab="Bash"
ssh-keygen -t rsa
```

##### 10.2 添加公钥

!!! Abstract ""
    在所有的master上执行！
    
```bash tab="Bash"
ssh-copy-id -i  .ssh/id_rsa.pub root@master01

ssh-copy-id -i  .ssh/id_rsa.pub root@master02

ssh-copy-id -i  .ssh/id_rsa.pub root@master03
```

#### 11. 安装Docker

##### 11.1 卸载已存在的docker
```bash tab="Bash"
yum remove docker docker-common docker-selinux docker-engine
```

##### 11.2 安装docker-ce-selinux
```bash tab="Bash"
yum install https://mirrors.aliyun.com/docker-ce/linux/centos/7/x86_64/stable/Packages/docker-ce-selinux-17.03.2.ce-1.el7.centos.noarch.rpm  -y
```

##### 11.3 安装docker-ce
```bash tab="Bash"
yum install https://mirrors.aliyun.com/docker-ce/linux/centos/7/x86_64/stable/Packages/docker-ce-17.03.2.ce-1.el7.centos.x86_64.rpm  -y
```

#### 12. 配置&启动docker

##### 12.1 修改启动参数
```bash tab="Bash"
vi /usr/lib/systemd/system/docker.service

ExecStart=/usr/bin/dockerd  -H tcp://0.0.0.0:2375 -H unix:///var/run/docker.sock  --registry-mirror=https://ms3cfraz.mirror.aliyuncs.com
```
##### 12.2 启动docker
```bash tab="Bash"
systemctl enable docker && systemctl restart docker
```

!!! Failure "docker启动失败"
    **错误信息** ：9月 30 17:40:29 cicd dockerd[22642]: Error starting daemon: error initializing graphdriver: driver not supported  
    **解决方法** ：修改daemon.json
    
    ```bash tab="/etc/docker/daemon.json"
    { 
        "storage-driver": "overlay2", 
        "storage-opts": [ 
        "overlay2.override_kernel_check=true" 
    ] }
    ```
#### 13 安装kubernetes
##### 13.1 配置kubernete Yum源
```bash tab="Bash"
cat <<EOF > /etc/yum.repos.d/kubernetes.repo
[kubernetes]
name=Kubernetes
baseurl=https://mirrors.aliyun.com/kubernetes/yum/repos/kubernetes-el7-x86_64
enabled=1
gpgcheck=1
repo_gpgcheck=1
gpgkey=https://mirrors.aliyun.com/kubernetes/yum/doc/yum-key.gpg https://mirrors.aliyun.com/kubernetes/yum/doc/rpm-package-key.gpg
EOF
```
##### 13.2 安装k8s
```bash tab="Bash"
yum install -y kubelet kubeadm kubectl ipvsadm
```

##### 13.2 设置kubelet开机启动
```bash tab="Bash"
systemctl enable kubelet.service
```

##### 13.3 获取需要的镜像版本
```bash tab="Bash"
kubeadm config images list

k8s.gcr.io/kube-apiserver:v1.12.2
k8s.gcr.io/kube-controller-manager:v1.12.2
k8s.gcr.io/kube-scheduler:v1.12.2
k8s.gcr.io/kube-proxy:v1.12.2
k8s.gcr.io/pause:3.1
k8s.gcr.io/etcd:3.2.24
k8s.gcr.io/coredns:1.2.2
```

##### 13.4 从harbor拉取镜像
```bash tab="image.sh"
#!/bin/bash
images=(kube-apiserver:v1.12.2 kkube-controller-manager:v1.12.2 kube-scheduler:v1.12.2 kube-proxy:v1.12.2 pause:3.1 etcd:3.2.24 coredns:1.2.2)
for imageName in ${images[@]} ; do
  docker pull reg.xxxx.xxx/k8s.gcr.io/$imageName
  docker tag reg.xxxx.xxx/k8s.gcr.io/$imageName k8s.gcr.io/$imageName
  docker rmi reg.xxxx.xxx/k8s.gcr.io/$imageName
done
```

##### 13.5 拉取镜像
```bash tab="Bash"
sh image.sh
```

#### 14 编写集群信息
```bash tab="CLUSTER_INFO"
# MASTER01 IP
CP0_IP=172.16.5.70
# MASTER01 NAME
CP0_HOSTNAME=master01
# MASTER02 IP
CP1_IP=172.16.5.71
# MASTER02 IP
CP1_HOSTNAME=master02
# MASTER03 IP
CP2_IP=172.16.5.72
# MASTER03 IP
CP2_HOSTNAME=master03
# VIP(KEEPALIVED)
VIP=172.16.5.90
# 获取NIC（走流量的网卡名）
NET_IF=eth0
# POD IP
CIDR=172.20.0.0/16
# SERVICE IP
SVCRANGE=172.30.0.0/16
```

!!! Tip ""
    这里编写了一个批量获取NIC和IP的命令，可根据实际情况做修改   
    ```
    export NODES="master01 master02 master03"          
    # 获取走流量网卡ip  
    ip route get 172.16.5.0 | awk '{print $NF; exit}'    
    # 获取所有master节点的ip  
    ssh ${NODE} "ip route get 172.16.5.0" | awk '{print $NF; exit}' 
    # 获取NIC（走流量的网卡名）  
    ssh ${NODE} "ip route get 172.16.5.0" | awk '{print $4; exit}'  
    ```

#### 15 配置集群并启动
##### 15.1 编写Calico Yaml
```bash tab="calico.yaml"
# Calico Version v3.2.4
# https://docs.projectcalico.org/v3.2/releases#v3.2.4
# This manifest includes the following component versions:
#   calico/node:v3.2.4
#   calico/cni:v3.2.4

# This ConfigMap is used to configure a self-hosted Calico installation.
kind: ConfigMap
apiVersion: v1
metadata:
  name: calico-config
  namespace: kube-system
data:
  # To enable Typha, set this to "calico-typha" *and* set a non-zero value for Typha replicas
  # below.  We recommend using Typha if you have more than 50 nodes. Above 100 nodes it is
  # essential.
  typha_service_name: "none"
  # Configure the Calico backend to use.
  calico_backend: "bird"

  # Configure the MTU to use
  veth_mtu: "1440"

  # The CNI network configuration to install on each node.  The special
  # values in this config will be automatically populated.
  cni_network_config: |-
    {
      "name": "k8s-pod-network",
      "cniVersion": "0.3.0",
      "plugins": [
        {
          "type": "calico",
          "log_level": "info",
          "datastore_type": "kubernetes",
          "nodename": "__KUBERNETES_NODE_NAME__",
          "mtu": __CNI_MTU__,
          "ipam": {
            "type": "host-local",
            "subnet": "usePodCidr"
          },
          "policy": {
              "type": "k8s"
          },
          "kubernetes": {
              "kubeconfig": "__KUBECONFIG_FILEPATH__"
          }
        },
        {
          "type": "portmap",
          "snat": true,
          "capabilities": {"portMappings": true}
        }
      ]
    }

---


# This manifest creates a Service, which will be backed by Calico's Typha daemon.
# Typha sits in between Felix and the API server, reducing Calico's load on the API server.

apiVersion: v1
kind: Service
metadata:
  name: calico-typha
  namespace: kube-system
  labels:
    k8s-app: calico-typha
spec:
  ports:
    - port: 5473
      protocol: TCP
      targetPort: calico-typha
      name: calico-typha
  selector:
    k8s-app: calico-typha

---

# This manifest creates a Deployment of Typha to back the above service.

apiVersion: apps/v1beta1
kind: Deployment
metadata:
  name: calico-typha
  namespace: kube-system
  labels:
    k8s-app: calico-typha
spec:
  # Number of Typha replicas.  To enable Typha, set this to a non-zero value *and* set the
  # typha_service_name variable in the calico-config ConfigMap above.
  #
  # We recommend using Typha if you have more than 50 nodes.  Above 100 nodes it is essential
  # (when using the Kubernetes datastore).  Use one replica for every 100-200 nodes.  In
  # production, we recommend running at least 3 replicas to reduce the impact of rolling upgrade.
  replicas: 0
  revisionHistoryLimit: 2
  template:
    metadata:
      labels:
        k8s-app: calico-typha
      annotations:
        # This, along with the CriticalAddonsOnly toleration below, marks the pod as a critical
        # add-on, ensuring it gets priority scheduling and that its resources are reserved
        # if it ever gets evicted.
        scheduler.alpha.kubernetes.io/critical-pod: ''
    spec:
      nodeSelector:
        beta.kubernetes.io/os: linux
      hostNetwork: true
      tolerations:
        # Mark the pod as a critical add-on for rescheduling.
        - key: CriticalAddonsOnly
          operator: Exists
      # Since Calico can't network a pod until Typha is up, we need to run Typha itself
      # as a host-networked pod.
      serviceAccountName: calico-node
      containers:
      - image: quay.io/calico/typha:v3.2.4
        name: calico-typha
        ports:
        - containerPort: 5473
          name: calico-typha
          protocol: TCP
        env:
          # Enable "info" logging by default.  Can be set to "debug" to increase verbosity.
          - name: TYPHA_LOGSEVERITYSCREEN
            value: "info"
          # Disable logging to file and syslog since those don't make sense in Kubernetes.
          - name: TYPHA_LOGFILEPATH
            value: "none"
          - name: TYPHA_LOGSEVERITYSYS
            value: "none"
          # Monitor the Kubernetes API to find the number of running instances and rebalance
          # connections.
          - name: TYPHA_CONNECTIONREBALANCINGMODE
            value: "kubernetes"
          - name: TYPHA_DATASTORETYPE
            value: "kubernetes"
          - name: TYPHA_HEALTHENABLED
            value: "true"
          # Uncomment these lines to enable prometheus metrics.  Since Typha is host-networked,
          # this opens a port on the host, which may need to be secured.
          #- name: TYPHA_PROMETHEUSMETRICSENABLED
          #  value: "true"
          #- name: TYPHA_PROMETHEUSMETRICSPORT
          #  value: "9093"
        livenessProbe:
          exec:
            command:
            - calico-typha
            - check
            - liveness
          periodSeconds: 30
          initialDelaySeconds: 30
        readinessProbe:
          exec:
            command:
            - calico-typha
            - check
            - readiness
          periodSeconds: 10

---

# This manifest installs the calico/node container, as well
# as the Calico CNI plugins and network config on
# each master and worker node in a Kubernetes cluster.
kind: DaemonSet
apiVersion: extensions/v1beta1
metadata:
  name: calico-node
  namespace: kube-system
  labels:
    k8s-app: calico-node
spec:
  selector:
    matchLabels:
      k8s-app: calico-node
  updateStrategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 1
  template:
    metadata:
      labels:
        k8s-app: calico-node
      annotations:
        # This, along with the CriticalAddonsOnly toleration below,
        # marks the pod as a critical add-on, ensuring it gets
        # priority scheduling and that its resources are reserved
        # if it ever gets evicted.
        scheduler.alpha.kubernetes.io/critical-pod: ''
    spec:
      nodeSelector:
        beta.kubernetes.io/os: linux
      hostNetwork: true
      tolerations:
        # Make sure calico-node gets scheduled on all nodes.
        - effect: NoSchedule
          operator: Exists
        # Mark the pod as a critical add-on for rescheduling.
        - key: CriticalAddonsOnly
          operator: Exists
        - effect: NoExecute
          operator: Exists
      serviceAccountName: calico-node
      # Minimize downtime during a rolling upgrade or deletion; tell Kubernetes to do a "force
      # deletion": https://kubernetes.io/docs/concepts/workloads/pods/pod/#termination-of-pods.
      terminationGracePeriodSeconds: 0
      containers:
        # Runs calico/node container on each Kubernetes node.  This
        # container programs network policy and routes on each
        # host.
        - name: calico-node
          image: quay.io/calico/node:v3.2.4
          env:
            # Use Kubernetes API as the backing datastore.
            - name: DATASTORE_TYPE
              value: "kubernetes"
            # Typha support: controlled by the ConfigMap.
            - name: FELIX_TYPHAK8SSERVICENAME
              valueFrom:
                configMapKeyRef:
                  name: calico-config
                  key: typha_service_name
            # Wait for the datastore.
            - name: WAIT_FOR_DATASTORE
              value: "true"
            # Set based on the k8s node name.
            - name: NODENAME
              valueFrom:
                fieldRef:
                  fieldPath: spec.nodeName
            # Choose the backend to use.
            - name: CALICO_NETWORKING_BACKEND
              valueFrom:
                configMapKeyRef:
                  name: calico-config
                  key: calico_backend
            # Cluster type to identify the deployment type
            - name: CLUSTER_TYPE
              value: "k8s,bgp"
            # Auto-detect the BGP IP address.
            - name: IP
              value: "autodetect"
            # Enable IPIP
            - name: CALICO_IPV4POOL_IPIP
              value: "Always"
            # Enable IP-in-IP within Felix.
            - name: FELIX_IPINIPENABLED
              value: "true"
            # Set MTU for tunnel device used if ipip is enabled
            - name: FELIX_IPINIPMTU
              valueFrom:
                configMapKeyRef:
                  name: calico-config
                  key: veth_mtu
            # The default IPv4 pool to create on startup if none exists. Pod IPs will be
            # chosen from this range. Changing this value after installation will have
            # no effect. This should fall within `--cluster-cidr`.
            - name: CALICO_IPV4POOL_CIDR
              value: "172.20.0.0/16"
            # Disable file logging so `kubectl logs` works.
            - name: CALICO_DISABLE_FILE_LOGGING
              value: "true"
            # Set Felix endpoint to host default action to ACCEPT.
            - name: FELIX_DEFAULTENDPOINTTOHOSTACTION
              value: "ACCEPT"
            # Disable IPv6 on Kubernetes.
            - name: FELIX_IPV6SUPPORT
              value: "false"
            # Set Felix logging to "info"
            - name: FELIX_LOGSEVERITYSCREEN
              value: "info"
            - name: FELIX_HEALTHENABLED
              value: "true"
          securityContext:
            privileged: true
          resources:
            requests:
              cpu: 250m
          livenessProbe:
            httpGet:
              path: /liveness
              port: 9099
              host: localhost
            periodSeconds: 10
            initialDelaySeconds: 10
            failureThreshold: 6
          readinessProbe:
            exec:
              command:
              - /bin/calico-node
              - -bird-ready
              - -felix-ready
            periodSeconds: 10
          volumeMounts:
            - mountPath: /lib/modules
              name: lib-modules
              readOnly: true
            - mountPath: /var/run/calico
              name: var-run-calico
              readOnly: false
            - mountPath: /var/lib/calico
              name: var-lib-calico
              readOnly: false
        # This container installs the Calico CNI binaries
        # and CNI network config file on each node.
        - name: install-cni
          image: quay.io/calico/cni:v3.2.4
          command: ["/install-cni.sh"]
          env:
            # Name of the CNI config file to create.
            - name: CNI_CONF_NAME
              value: "10-calico.conflist"
            # Set the hostname based on the k8s node name.
            - name: KUBERNETES_NODE_NAME
              valueFrom:
                fieldRef:
                  fieldPath: spec.nodeName
            # The CNI network config to install on each node.
            - name: CNI_NETWORK_CONFIG
              valueFrom:
                configMapKeyRef:
                  name: calico-config
                  key: cni_network_config
            # CNI MTU Config variable
            - name: CNI_MTU
              valueFrom:
                configMapKeyRef:
                  name: calico-config
                  key: veth_mtu
          volumeMounts:
            - mountPath: /host/opt/cni/bin
              name: cni-bin-dir
            - mountPath: /host/etc/cni/net.d
              name: cni-net-dir
      volumes:
        # Used by calico/node.
        - name: lib-modules
          hostPath:
            path: /lib/modules
        - name: var-run-calico
          hostPath:
            path: /var/run/calico
        - name: var-lib-calico
          hostPath:
            path: /var/lib/calico
        # Used to install CNI.
        - name: cni-bin-dir
          hostPath:
            path: /opt/cni/bin
        - name: cni-net-dir
          hostPath:
            path: /etc/cni/net.d
---

apiVersion: v1
kind: ServiceAccount
metadata:
  name: calico-node
  namespace: kube-system

---

# Create all the CustomResourceDefinitions needed for
# Calico policy and networking mode.

apiVersion: apiextensions.k8s.io/v1beta1
kind: CustomResourceDefinition
metadata:
   name: felixconfigurations.crd.projectcalico.org
spec:
  scope: Cluster
  group: crd.projectcalico.org
  version: v1
  names:
    kind: FelixConfiguration
    plural: felixconfigurations
    singular: felixconfiguration
---

apiVersion: apiextensions.k8s.io/v1beta1
kind: CustomResourceDefinition
metadata:
  name: bgppeers.crd.projectcalico.org
spec:
  scope: Cluster
  group: crd.projectcalico.org
  version: v1
  names:
    kind: BGPPeer
    plural: bgppeers
    singular: bgppeer

---

apiVersion: apiextensions.k8s.io/v1beta1
kind: CustomResourceDefinition
metadata:
  name: bgpconfigurations.crd.projectcalico.org
spec:
  scope: Cluster
  group: crd.projectcalico.org
  version: v1
  names:
    kind: BGPConfiguration
    plural: bgpconfigurations
    singular: bgpconfiguration

---

apiVersion: apiextensions.k8s.io/v1beta1
kind: CustomResourceDefinition
metadata:
  name: ippools.crd.projectcalico.org
spec:
  scope: Cluster
  group: crd.projectcalico.org
  version: v1
  names:
    kind: IPPool
    plural: ippools
    singular: ippool

---

apiVersion: apiextensions.k8s.io/v1beta1
kind: CustomResourceDefinition
metadata:
  name: hostendpoints.crd.projectcalico.org
spec:
  scope: Cluster
  group: crd.projectcalico.org
  version: v1
  names:
    kind: HostEndpoint
    plural: hostendpoints
    singular: hostendpoint

---

apiVersion: apiextensions.k8s.io/v1beta1
kind: CustomResourceDefinition
metadata:
  name: clusterinformations.crd.projectcalico.org
spec:
  scope: Cluster
  group: crd.projectcalico.org
  version: v1
  names:
    kind: ClusterInformation
    plural: clusterinformations
    singular: clusterinformation

---

apiVersion: apiextensions.k8s.io/v1beta1
kind: CustomResourceDefinition
metadata:
  name: globalnetworkpolicies.crd.projectcalico.org
spec:
  scope: Cluster
  group: crd.projectcalico.org
  version: v1
  names:
    kind: GlobalNetworkPolicy
    plural: globalnetworkpolicies
    singular: globalnetworkpolicy

---

apiVersion: apiextensions.k8s.io/v1beta1
kind: CustomResourceDefinition
metadata:
  name: globalnetworksets.crd.projectcalico.org
spec:
  scope: Cluster
  group: crd.projectcalico.org
  version: v1
  names:
    kind: GlobalNetworkSet
    plural: globalnetworksets
    singular: globalnetworkset

---

apiVersion: apiextensions.k8s.io/v1beta1
kind: CustomResourceDefinition
metadata:
  name: networkpolicies.crd.projectcalico.org
spec:
  scope: Namespaced
  group: crd.projectcalico.org
  version: v1
  names:
    kind: NetworkPolicy
    plural: networkpolicies
    singular: networkpolicy


```

```bash tab="rbac.yaml"
# Calico Version v3.2.4
# https://docs.projectcalico.org/v3.2/releases#v3.2.4
kind: ClusterRole
apiVersion: rbac.authorization.k8s.io/v1beta1
metadata:
  name: calico-node
rules:
  - apiGroups: [""]
    resources:
      - namespaces
      - serviceaccounts
    verbs:
      - get
      - list
      - watch
  - apiGroups: [""]
    resources:
      - pods/status
    verbs:
      - update
  - apiGroups: [""]
    resources:
      - pods
    verbs:
      - get
      - list
      - watch
      - patch
  - apiGroups: [""]
    resources:
      - services
    verbs:
      - get
  - apiGroups: [""]
    resources:
      - endpoints
    verbs:
      - get
  - apiGroups: [""]
    resources:
      - nodes
    verbs:
      - get
      - list
      - update
      - watch
  - apiGroups: ["extensions"]
    resources:
      - networkpolicies
    verbs:
      - get
      - list
      - watch
  - apiGroups: ["networking.k8s.io"]
    resources:
      - networkpolicies
    verbs:
      - watch
      - list
  - apiGroups: ["crd.projectcalico.org"]
    resources:
      - globalfelixconfigs
      - felixconfigurations
      - bgppeers
      - globalbgpconfigs
      - bgpconfigurations
      - ippools
      - globalnetworkpolicies
      - globalnetworksets
      - networkpolicies
      - clusterinformations
      - hostendpoints
    verbs:
      - create
      - get
      - list
      - update
      - watch

---

apiVersion: rbac.authorization.k8s.io/v1beta1
kind: ClusterRoleBinding
metadata:
  name: calico-node
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: calico-node
subjects:
- kind: ServiceAccount
  name: calico-node
  namespace: kube-system

```

##### 15.2 编写自动配置脚本

!!! Warning ""
    自动配置脚本要,集群配置文件,Calico放在同级目录

```bash tab="setup.sh"
#/bin/bash

function check_parm()
{
  if [ "${2}" == "" ]; then
    echo -n "${1}"
    return 1
  else
    return 0
  fi
}

if [ -f ./master-info ]; then
	source ./CLUSTER_INFO 
fi

check_parm "Enter the IP address of master-01: " ${CP0_IP} 
if [ $? -eq 1 ]; then
	read CP0_IP
fi
check_parm "Enter the Hostname of master-01: " ${CP0_HOSTNAME}
if [ $? -eq 1 ]; then
	read CP0_HOSTNAME
fi
check_parm "Enter the IP address of master-02: " ${CP1_IP}
if [ $? -eq 1 ]; then
	read CP1_IP
fi
check_parm "Enter the Hostname of master-02: " ${CP1_HOSTNAME}
if [ $? -eq 1 ]; then
	read CP1_HOSTNAME
fi
check_parm "Enter the IP address of master-03: " ${CP2_IP}
if [ $? -eq 1 ]; then
	read CP2_IP
fi
check_parm "Enter the Hostname of master-03: " ${CP2_HOSTNAME}
if [ $? -eq 1 ]; then
	read CP2_HOSTNAME
fi
check_parm "Enter the VIP: " ${VIP}
if [ $? -eq 1 ]; then
	read VIP
fi
check_parm "Enter the Net Interface: " ${NET_IF}
if [ $? -eq 1 ]; then
	read NET_IF
fi
check_parm "Enter the cluster CIDR: " ${CIDR}
if [ $? -eq 1 ]; then
	read CIDR
fi

echo """
cluster-info:
  master-01:        ${CP0_IP}
                    ${CP0_HOSTNAME}
  master-02:        ${CP1_IP}
                    ${CP1_HOSTNAME}
  master-03:        ${CP2_IP}
                    ${CP2_HOSTNAME}
  VIP:              ${VIP}
  Net Interface:    ${NET_IF}
  CIDR:             ${CIDR}
"""
echo -n 'Please print "yes" to continue or "no" to cancle: '
read AGREE
while [ "${AGREE}" != "yes" ]; do
	if [ "${AGREE}" == "no" ]; then
		exit 0;
	else
		echo -n 'Please print "yes" to continue or "no" to cancle: '
		read AGREE
	fi
done

mkdir -p ~/ikube/tls

HOSTS=(${CP0_HOSTNAME} ${CP1_HOSTNAME} ${CP2_HOSTNAME})
IPS=(${CP0_IP} ${CP1_IP} ${CP2_IP})

PRIORITY=(100 50 30)
STATE=("MASTER" "BACKUP" "BACKUP")
HEALTH_CHECK=""
for index in 0 1 2; do
  HEALTH_CHECK=${HEALTH_CHECK}"""
    real_server ${IPS[$index]} 6443 {
        weight 1
        SSL_GET {
            url {
              path /healthz
              status_code 200
            }
            connect_timeout 3
            nb_get_retry 3
            delay_before_retry 3
        }
    }
"""
done

for index in 0 1 2; do
  host=${HOSTS[${index}]}
  ip=${IPS[${index}]}
  echo """
global_defs {
   router_id LVS_DEVEL
}

vrrp_instance VI_1 {
    state ${STATE[${index}]}
    interface ${NET_IF}
    virtual_router_id 80
    priority ${PRIORITY[${index}]}
    advert_int 1
    authentication {
        auth_type PASS
        auth_pass just0kk
    }
    virtual_ipaddress {
        ${VIP}
    }
}

virtual_server ${VIP} 6443 {
    delay_loop 6
    lb_algo rr
    lb_kind NAT
    persistence_timeout 50
    protocol TCP

${HEALTH_CHECK}
}
""" > ~/ikube/keepalived-${index}.conf
  scp ~/ikube/keepalived-${index}.conf ${host}:/etc/keepalived/keepalived.conf

  ssh ${host} "
    systemctl restart keepalived
    kubeadm reset -f
    rm -rf /etc/kubernetes/pki/"

  if [ ${index} -ne 0 ]; then
    ETCD_MEMBER="${ETCD_MEMBER},"
    ETCD_STATUS="existing"
  else
    ETCD_MEMBER=""
    ETCD_STATUS="new"
  fi
  ETCD_MEMBER="${ETCD_MEMBER}${host}=https://${ip}:2380"

  echo """
apiVersion: kubeadm.k8s.io/v1alpha2
kind: MasterConfiguration
kubernetesVersion: v1.12.2
apiServerCertSANs:
- ${CP0_IP}
- ${CP1_IP}
- ${CP2_IP}
- ${CP0_HOSTNAME}
- ${CP1_HOSTNAME}
- ${CP2_HOSTNAME}
- ${VIP}
kubeProxy:
  config:
    mode: ipvs
etcd:
  local:
    extraArgs:
      listen-client-urls: https://127.0.0.1:2379,https://${ip}:2379
      advertise-client-urls: https://${ip}:2379
      listen-peer-urls: https://${ip}:2380
      initial-advertise-peer-urls: https://${ip}:2380
      initial-cluster: ${ETCD_MEMBER}
      initial-cluster-state: ${ETCD_STATUS}
    serverCertSANs:
      - ${host}
      - ${ip}
    peerCertSANs:
      - ${host}
      - ${ip}
networking:
  # This CIDR is a Calico default. Substitute or remove for your CNI provider.
  podSubnet: ${CIDR}
  serviceSubnet: ${SVCRANGE}
""" > ~/ikube/kubeadm-config-m${index}.yaml

  scp ~/ikube/kubeadm-config-m${index}.yaml ${host}:/etc/kubernetes/kubeadm-config.yaml
done

kubeadm init --config /etc/kubernetes/kubeadm-config.yaml
mkdir -p $HOME/.kube
cp -f /etc/kubernetes/admin.conf ${HOME}/.kube/config

ETCD=`kubectl get pods -n kube-system 2>&1|grep etcd|awk '{print $3}'`
echo "Waiting for etcd bootup..."
while [ "${ETCD}" != "Running" ]; do
  sleep 1
  ETCD=`kubectl get pods -n kube-system 2>&1|grep etcd|awk '{print $3}'`
done

for index in 1 2; do
  host=${HOSTS[${index}]}
  ip=${IPS[${index}]}
  ssh $host "mkdir -p /etc/kubernetes/pki/etcd"
  ssh $host "mkdir -p $HOME/.kube"
  scp /etc/kubernetes/pki/ca.crt $host:/etc/kubernetes/pki/ca.crt
  scp /etc/kubernetes/pki/ca.key $host:/etc/kubernetes/pki/ca.key
  scp /etc/kubernetes/pki/sa.key $host:/etc/kubernetes/pki/sa.key
  scp /etc/kubernetes/pki/sa.pub $host:/etc/kubernetes/pki/sa.pub
  scp /etc/kubernetes/pki/front-proxy-ca.crt $host:/etc/kubernetes/pki/front-proxy-ca.crt
  scp /etc/kubernetes/pki/front-proxy-ca.key $host:/etc/kubernetes/pki/front-proxy-ca.key
  scp /etc/kubernetes/pki/etcd/ca.crt $host:/etc/kubernetes/pki/etcd/ca.crt
  scp /etc/kubernetes/pki/etcd/ca.key $host:/etc/kubernetes/pki/etcd/ca.key
  scp /etc/kubernetes/admin.conf $host:/etc/kubernetes/admin.conf
  scp /etc/kubernetes/admin.conf $host:~/.kube/config

  kubectl exec \
    -n kube-system etcd-${CP0_HOSTNAME} -- etcdctl \
    --ca-file /etc/kubernetes/pki/etcd/ca.crt \
    --cert-file /etc/kubernetes/pki/etcd/peer.crt \
    --key-file /etc/kubernetes/pki/etcd/peer.key \
    --endpoints=https://${CP0_IP}:2379 \
    member add ${host} https://${ip}:2380

  ssh ${host} "
    kubeadm alpha phase certs all --config /etc/kubernetes/kubeadm-config.yaml
    kubeadm alpha phase kubeconfig controller-manager --config /etc/kubernetes/kubeadm-config.yaml
    kubeadm alpha phase kubeconfig scheduler --config /etc/kubernetes/kubeadm-config.yaml
    kubeadm alpha phase kubelet config write-to-disk --config /etc/kubernetes/kubeadm-config.yaml
    kubeadm alpha phase kubelet write-env-file --config /etc/kubernetes/kubeadm-config.yaml
    kubeadm alpha phase kubeconfig kubelet --config /etc/kubernetes/kubeadm-config.yaml
    systemctl restart kubelet
    kubeadm alpha phase etcd local --config /etc/kubernetes/kubeadm-config.yaml
    kubeadm alpha phase kubeconfig all --config /etc/kubernetes/kubeadm-config.yaml
    kubeadm alpha phase controlplane all --config /etc/kubernetes/kubeadm-config.yaml
    kubeadm alpha phase mark-master --config /etc/kubernetes/kubeadm-config.yaml"
done

kubectl apply -f rbac.yaml
kubectl apply -f calico.yaml

echo "Cluster create finished."

echo """
[req] 
distinguished_name = req_distinguished_name
prompt = yes

[ req_distinguished_name ]
countryName                     = Country Name (2 letter code)
countryName_value               = CN

stateOrProvinceName             = State or Province Name (full name)
stateOrProvinceName_value       = Shanghai

localityName                    = Locality Name (eg, city)
localityName_value              = Shanghai

organizationName                = Organization Name (eg, company)
organizationName_value          = Weeknd

organizationalUnitName          = Organizational Unit Name (eg, section)
organizationalUnitName_value    = R & D Department

commonName                      = Common Name (eg, your name or your server\'s hostname)
commonName_value                = *.multi.io


emailAddress                    = Email Address
emailAddress_value              = weeknd.su@hotmail.com
""" > ~/ikube/tls/openssl.cnf
openssl req -newkey rsa:4096 -nodes -config ~/ikube/tls/openssl.cnf -days 3650 -x509 -out ~/ikube/tls/tls.crt -keyout ~/ikube/tls/tls.key
kubectl create -n kube-system secret tls ssl --cert ~/ikube/tls/tls.crt --key ~/ikube/tls/tls.key

for index in 0 1 2; do
  host=${HOSTS[${index}]}
  ssh ${host} "sed -i 's/etcd-servers=https:\/\/127.0.0.1:2379/etcd-servers=https:\/\/${CP0_IP}:2379,https:\/\/${CP1_IP}:2379,https:\/\/${CP2_IP}:2379/g' /etc/kubernetes/manifests/kube-apiserver.yaml"
  ssh ${host} "sed -i 's/${CP0_IP}/${VIP}/g' ~/.kube/config"
done

echo "Plugin install finished."
echo "Waiting for all pods into 'Running' statu. You can press 'Ctrl + c' to terminate this waiting any time you like."
POD_UNREADY=`kubectl get pods -n kube-system 2>&1|awk '{print $3}'|grep -vE 'Running|STATUS'`
NODE_UNREADY=`kubectl get nodes 2>&1|awk '{print $2}'|grep 'NotReady'`
while [ "${POD_UNREADY}" != "" -o "${NODE_UNREADY}" != "" ]; do
  sleep 1
  POD_UNREADY=`kubectl get pods -n kube-system 2>&1|awk '{print $3}'|grep -vE 'Running|STATUS'`
  NODE_UNREADY=`kubectl get nodes 2>&1|awk '{print $2}'|grep 'NotReady'`
done
```

##### 15.3 运行脚本
```bash tab="Bash"
sh setup.sh
```

#### 配置结束
    
