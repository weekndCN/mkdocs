# Install k8s HA

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

