# nfs-provisioner

### Before you start

当你的**NFS服务存储**只配置了**一个exported path**，而又想基于在这个exported path划分**不同**的**child directory**给K8S使用时。则可以用使用此**nfs-client**。**nfs-client** 是一个基于已经配置好的NFS服务端，支持通过K8S的**PVC**动态分配**PV**的的automatic provisioner。

### Deploy nfs-client on k8s

#### STEP 1:创建一个namespaces

```shell
kubectl create namespace misc
```

#### STEP 2:创建RBAC

- 创建rbac.yaml

```yaml
kind: ClusterRole
apiVersion: rbac.authorization.k8s.io/v1
metadata:
  name: nfs-client-provisioner-runner
  namespace: misc
rules:
  - apiGroups: [""]
    resources: ["persistentvolumes"]
    verbs: ["get", "list", "watch", "create", "delete"]
  - apiGroups: [""]
    resources: ["persistentvolumeclaims"]
    verbs: ["get", "list", "watch", "update"]
  - apiGroups: ["storage.k8s.io"]
    resources: ["storageclasses"]
    verbs: ["get", "list", "watch"]
  - apiGroups: [""]
    resources: ["events"]
    verbs: ["create", "update", "patch"]
---
kind: ClusterRoleBinding
apiVersion: rbac.authorization.k8s.io/v1
metadata:
  name: run-nfs-client-provisioner
  namespace: misc
subjects:
  - kind: ServiceAccount
    name: nfs-client-provisioner
    namespace: misc
roleRef:
  kind: ClusterRole
  name: nfs-client-provisioner-runner
  apiGroup: rbac.authorization.k8s.io
---
kind: Role
apiVersion: rbac.authorization.k8s.io/v1
metadata:
  name: leader-locking-nfs-client-provisioner
  namespace: misc
rules:
  - apiGroups: [""]
    resources: ["endpoints"]
    verbs: ["get", "list", "watch", "create", "update", "patch"]
---
kind: RoleBinding
apiVersion: rbac.authorization.k8s.io/v1
metadata:
  name: leader-locking-nfs-client-provisioner
  namespace: misc
subjects:
  - kind: ServiceAccount
    name: nfs-client-provisioner
    # replace with namespace where provisioner is deployed
    namespace: misc
roleRef:
  kind: Role
  name: leader-locking-nfs-client-provisioner
 apiGroup: rbac.authorization.k8s.io
```

- 应用RBAC

```shell
kubectl create -f rbac.yaml
```

#### STEP 3:创建nfs-client-provisioner

- 编写nfs-client-provisioner的deployment.yaml

```
apiVersion: v1
kind: ServiceAccount
metadata:
  name: nfs-client-provisioner
  namespace: misc
---
kind: Deployment
apiVersion: extensions/v1beta1
metadata:
  name: nfs-client-provisioner
  namespace: misc
spec:
  replicas: 1
  strategy:
    type: Recreate
  template:
    metadata:
      labels:
        app: nfs-client-provisioner
    spec:
      serviceAccountName: nfs-client-provisioner
      containers:
        - name: nfs-client-provisioner
          image: quay.io/external_storage/nfs-client-provisioner:latest
          volumeMounts:
            - name: nfs-client-root
              mountPath: /persistentvolumes
          env:
            - name: PROVISIONER_NAME
              value: <PROVISIONER_NAME>
            - name: NFS_SERVER
              value: <NFS-SERVICE-IP>
            - name: NFS_PATH
              value: <EXPORT-PATH>
      volumes:
        - name: nfs-client-root
          nfs:
            server: <NFS-SERVER-IP>
            path: <EXPORT-PATH>
```

- 创建deployment

```shell
kubectl create -f deployment.yaml
```

#### STEP 4:创建一个storageClass

- 编写storageclass.yaml(provisioner需要和deployment的<PROVISIONER_NAME>填写的值一致)

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: managed-nfs-storage
  namespace: misc
provisioner: <PROVISIONER_NAME>
parameters:
  archiveOnDelete: "false"
```

- 创建storageClass

```shell
kubectl create -f storageclass.yaml
```

#### STEP 5:创建一个PVC

- 编写test-claim.yaml

```yaml
kind: PersistentVolumeClaim
apiVersion: v1
metadata:
  name: test-claim
  namespace: misc
  annotations:
    volume.beta.kubernetes.io/storage-class: "managed-nfs-storage"
spec:
  accessModes:
    - ReadWriteMany
  resources:
    requests:
      storage: 1Mi
```

- 创建PVC

```yaml
kind: PersistentVolumeClaim
apiVersion: v1
metadata:
  name: test-claim
  namespace: misc
  annotations:
    volume.beta.kubernetes.io/storage-class: "managed-nfs-storage"
spec:
  accessModes:
    - ReadWriteMany
  resources:
    requests:
      storage: 1Mi
```

- 检查PVC

```shell
[root@m01 nfs]# kubectl get pvc -n misc

NAME         STATUS   VOLUME                                     CAPACITY   ACCESS MODES   STORAGECLASS          AGE
test-claim   Bound    pvc-bcaa05f3-fad2-11e8-8e48-52540016b134   1Mi        RWX            managed-nfs-storage   158m
```

#### STEP 6:测试PV

- 编写test-pod.yaml

```yaml
kind: Pod
apiVersion: v1
metadata:
  name: test-pod
  namespace: misc
spec:
  containers:
  - name: test-pod
    image: busybox:1.24
    command:
      - "/bin/sh"
    args:
      - "-c"
      - "touch /mnt/SUCCESS && exit 0 || exit 1"
    volumeMounts:
      - name: nfs-pvc
        mountPath: "/mnt"
  restartPolicy: "Never"
  volumes:
    - name: nfs-pvc
      persistentVolumeClaim:
        claimName: test-claim
```

- 创建pod

```shell
kubectl create -f deployment.yaml
```

- 检查生成的文件

```shell
# 检查目录
pwd
/nfs/misc-test-claim-pvc-bcaa05f3-fad2-11e8-8e48-52540016b134
# 检查文件
ls
SUCCESS
```

#### STEP 7:删除测试

- 删除pod和pvc（注意顺序）

```shell
kubectl delete -f test-pod.yaml -f test-claim.yaml
```

- 检查文件和目录

```shell
cd /nfs/misc-test-claim-pvc-bcaa05f3-fad2-11e8-8e48-52540016b134
-bash: cd: /nfs/misc-test-claim-pvc-bcaa05f3-fad2-11e8-8e48-52540016b134: No such file or directory
```

- 已删除文件和目录
