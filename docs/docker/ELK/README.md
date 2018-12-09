# ELK for Docker

### Before you start

**ELK** 是一套日志解决方案，通过开源的**elasticsearch**，**logstash**，**kibana** 组合而成的日志**采集**，**分析**，**可视化**的集成套件。这是通过**docker-compose**简单一套**ELK**，这里的参数只适用于**test**，如果生产，请了解各个组件。并修改符合生产环境的参数，再启用。

### Deploy ELK on Docker

#### STEP 1: Requirements

- docker 1.17  or above
- docker-compose 1.8 or above

#### STEP 2:Install docker

- on Centos

```shell
yum install docker
```

- on Ubuntu

```shell
apt install docker
```

- Windows(不做解释)

#### STEP 3:Install docker-compose

- Centos

```shel l
curl -L https://github.com/docker/compose/releases/download/1.14.0/docker-compose-`uname -s`-`uname -m` > /usr/local/bin/docker-compose

sudo chmod +x /usr/local/bin/docker-compose
```

- Ubuntu(同Centos)

```shell
curl -L https://github.com/docker/compose/releases/download/1.14.0/docker-compose-`uname -s`-`uname -m` > /usr/local/bin/docker-compose

sudo chmod +x /usr/local/bin/docker-compose
```

- Windows(不做解释)

#### STEP 4:List all files

```shell
├── README.md
├── docker-compose.yml 
├── elasticsearch
│   ├── Dockerfile 
│   └── config
│       └── elasticsearch.yml
├── kibana
│   ├── Dockerfile
│   └── config
│       └── kibana.yml
└── logstash
    ├── Dockerfile
    ├── config
    │   └── logstash.yml
    └── pipeline
        └── logstash.conf
```

#### STEP 5:Get Files

- [Click Me](https://github.com/weekndchina/mkdocs/tree/master/docs/docker/ELK)

#### STEP 6: Build ELK

```shell
docker-compose build
```

#### STEP 7: ELK UP

```shell
docker-compose up
```
