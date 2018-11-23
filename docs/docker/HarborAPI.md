# 1. 项目管理

#### 1.1     查看仓库中项目详细信息

```bash tab="Bash"
curl -u "admin:Harbor12345" -X GET -H "Content-Type: application/json" "https://192.168.56.106/api/projects?project_name=guest"
```

#### 1.2     搜索镜像

```bash tab="Bash"
curl  -u "admin:Harbor12345"  -X GET -H "Content-Type: application/json" "https://192.168.56.106/api/search?q=nginx"
```

#### 1.3     删除项目

```bash tab="Bash"
curl  -u "admin:Harbor12345"  -X DELETE  -H "Content-Type: application/json" "https://192.168.56.106/api/projects/{project_id}"
```

#### 1.4     创建项目

```bash tab="Bash"
curl -u "admin:Harbor12345" -X POST -H "Content-Type: application/json" "https://192.168.56.106/api/projects" -d @createproject.json
```

!!! Tip "createproject.json"
        {
                "project_name": "testrpo",
                "public": 0
        }


#### 1.5     查看项目日志

```bash tab="Bash"
curl -u "admin:Harbor12345" -X POST -H "Content-Type: application/json" "https://192.168.56.106/api/projects/{project_id}/logs/filter" -d @log.json
```

!!! Note "log.json"
    {
      "username": "admin"
    }


#### 1.6     创建账号

```bash tab="Bash"
curl -u "admin:Harbor12345" -X POST -H "Content-Type: application/json" "https://192.168.56.106/api/users" -d @user.json
```

!!! Info "user.json"
    {
      "user_id": 5,
      "username": "xinju",
      "email": "xinju@gmail.com",
      "password": "Xinju12345",
      "realname": "xinju",
      "role_id": 2
    }


#### 1.7     获取用户信息

```bash tab="Bash"
curl -u "admin:Harbor12345" -X GET -H "Content-Type: application/json" "https://192.168.56.106/api/users"
```

#### 1.8     获取当前用户信息

```bash tab="Bash"
curl -u "admin:Harbor12345" -X GET -H "Content-Type: application/json" "https://192.168.56.106/api/users/current"
```

#### 1.9     删除用户

```bash tab="Bash"
curl -u "admin:Harbor12345" -X DELETE  -H "Content-Type: application/json" "https://192.168.56.106/api/users/{user_id}"
```

#### 2.0     修改用户密码

```bash tab="Bash"
curl -u "admin:Harbor12345" -X PUT -H "Content-Type: application/json" "https://192.168.56.106/api/users/{user_id}/password" -d @uppwd.json
```


!!! Abstract "uppwd.json"
    {
      "old_password": "Harbor123456",
      "new_password": "Harbor12345"
    }

#### 2.1     查看项目相关角色

```bash tab="Bash"
curl -u "admin:Harbor12345" -X GET -H "Content-Type: application/json" "https://192.168.56.106/api/projects/{project_id}/members/"
```

#### 2.2     项目添加角色

```bash tab="Bash"
curl -u "jaymarco:Harbor123456" -X POST  -H "Content-Type: application/json" "https://192.168.56.106/api/projects/{project_id}/members/" -d @role.json
```


!!! Tip "role.json"
    {
      "roles": [3],
      "username": "guest"
    }


#### 2.3 用weeknd用户创建一个dcos项目，并对dcos加一个权限

```bash tab="Bash"
curl -u "weeknd:Harbor123456" -X POST -H "Content-Type: application/json" "https://192.168.56.106/api/projects" -d @createproject.json
```

#### 2.4     删除项目中用户权限

```bash tab="Bash"
curl -u "admin:Harbor12345" -X DELETE -H "Content-Type: application/json" "https://192.168.56.106/api/projects/{project_id}/members/{user_id}"
```



#### 2.5     获取与用户相关的项目编号和存储库编号

```bash tab="Bash"
curl -u "admin:Harbor12345" -X GET -H "Content-Type: application/json" "https://192.168.56.106/api/statistics"

```
```



#### 2.6    修改当前用户角色
!!! Warning ""
    has_admin_role ：0  普通用户
    has_admin_role ：1  管理员

```bash tab="Bash"
curl -u "admin:Harbor12345" -X PUT -H "Content-Type: application/json" "https://192.168.56.106/api/users/{user_id}/sysadmin " -d @chgrole.json
```

!!! Info "chgrole.json"
    {
      "has_admin_role": 1
    }

#### 2.7     查询镜像

```bash tab="Bash"
curl -u "admin:Harbor12345" -X GET -H "Content-Type: application/json" "https://192.168.56.106/api/repositories?project_id={project_id}&q=dcos%2Fcentos"
```



#### 2.8    删除镜像

```bash tab="Bash"
curl -u "admin:Harbor12345" -X DELETE -H "Content-Type: application/json" "https://192.168.56.106/api/repositories?repo_name=dcos%2Fetcd "
```

#### 2.9    获取镜像标签

```bash tab="Bash"
curl -u "admin:Harbor12345" -X GET -H "Content-Type: application/json" "https://192.168.56.106/api/repositories/tags?repo_name=dcos%2Fcentos"
```

[@joeydeMacBook-Pro:docker]$
[@joeydeMacBook-Pro:docker]$
[@joeydeMacBook-Pro:docker]$
[@joeydeMacBook-Pro:docker]$
[@joeydeMacBook-Pro:docker]$ cat /dev/null > HarborAPI.md
[@joeydeMacBook-Pro:docker]$ vi HarborAPI.md
[@joeydeMacBook-Pro:docker]$ vi HarborAPI.md
[@joeydeMacBook-Pro:docker]$ more HarborAPI.md
# 1. 项目管理

#### 1.1     查看仓库中项目详细信息

```bash tab="Bash"
curl -u "admin:Harbor12345" -X GET -H "Content-Type: application/json" "https://192.168.1.100/api/projects?project_name=guest"
```

#### 1.2     搜索镜像

```bash tab="Bash"
curl  -u "admin:Harbor12345"  -X GET -H "Content-Type: application/json" "https://192.168.1.100/api/search?q=nginx"
```

#### 1.3     删除项目

```bash tab="Bash"
curl  -u "admin:Harbor12345"  -X DELETE  -H "Content-Type: application/json" "https://192.168.1.100/api/projects/{project_id}"
```

#### 1.4     创建项目

```bash tab="Bash"
curl -u "admin:Harbor12345" -X POST -H "Content-Type: application/json" "https://192.168.1.100/api/projects" -d @createproject.json
```

!!! Tip "createproject.json"
        {
                "project_name": "testrpo",
                "public": 0
        }


#### 1.5     查看项目日志

```bash tab="Bash"
curl -u "admin:Harbor12345" -X POST -H "Content-Type: application/json" "https://192.168.1.100/api/projects/{project_id}/logs/filter" -d @log.json
```

!!! Note "log.json"
    {
      "username": "admin"
    }


#### 1.6     创建账号

```bash tab="Bash"
curl -u "admin:Harbor12345" -X POST -H "Content-Type: application/json" "https://192.168.1.100/api/users" -d @user.json
```

!!! Info "user.json"
    {
      "user_id": 5,
      "username": "weeknd",
      "email": "weeknd.su@hotmail.com",
      "password": "12345",
      "realname": "weeknd",
      "role_id": 2
    }


#### 1.7     获取用户信息

```bash tab="Bash"
curl -u "admin:Harbor12345" -X GET -H "Content-Type: application/json" "https://192.168.1.100/api/users"
```

#### 1.8     获取当前用户信息

```bash tab="Bash"
curl -u "admin:Harbor12345" -X GET -H "Content-Type: application/json" "https://192.168.1.100/api/users/current"
```

#### 1.9     删除用户

```bash tab="Bash"
curl -u "admin:Harbor12345" -X DELETE  -H "Content-Type: application/json" "https://192.168.1.100/api/users/{user_id}"
```

#### 2.0     修改用户密码

```bash tab="Bash"
curl -u "admin:Harbor12345" -X PUT -H "Content-Type: application/json" "https://192.168.1.100/api/users/{user_id}/password" -d @uppwd.json
```


!!! Abstract "uppwd.json"
    {
      "old_password": "Harbor123456",
      "new_password": "Harbor12345"
    }

#### 2.1     查看项目相关角色

```bash tab="Bash"
curl -u "admin:Harbor12345" -X GET -H "Content-Type: application/json" "https://192.168.1.100/api/projects/{project_id}/members/"
```

#### 2.2     项目添加角色

```bash tab="Bash"
curl -u "jaymarco:Harbor123456" -X POST  -H "Content-Type: application/json" "https://192.168.1.100/api/projects/{project_id}/members/" -d @role.json
```


!!! Tip "role.json"
    {
      "roles": [3],
      "username": "guest"
    }


#### 2.3 用weeknd用户创建一个dcos项目，并对dcos加一个权限

```bash tab="Bash"
curl -u "weeknd:Harbor123456" -X POST -H "Content-Type: application/json" "https://192.168.1.100/api/projects" -d @createproject.json
```

#### 2.4     删除项目中用户权限

```bash tab="Bash"
curl -u "admin:Harbor12345" -X DELETE -H "Content-Type: application/json" "https://192.168.1.100/api/projects/{project_id}/members/{user_id}"
```



#### 2.5     获取与用户相关的项目编号和存储库编号

```bash tab="Bash"
curl -u "admin:Harbor12345" -X GET -H "Content-Type: application/json" "https://192.168.1.100/api/statistics"
```



#### 2.6    修改当前用户角色
!!! Warning ""
    `has_admin_role ：0`  **普通用户**
    `has_admin_role ：1`  **管理员**

```bash tab="Bash"
curl -u "admin:Harbor12345" -X PUT -H "Content-Type: application/json" "https://192.168.1.100/api/users/{user_id}/sysadmin " -d @chgrole.json
```

!!! Info "chgrole.json"
    {
      "has_admin_role": 1
    }

#### 2.7     查询镜像

```bash tab="Bash"
curl -u "admin:Harbor12345" -X GET -H "Content-Type: application/json" "https://192.168.1.100/api/repositories?project_id={project_id}&q=dcos%2Fcentos"
```



#### 2.8    删除镜像

```bash tab="Bash"
curl -u "admin:Harbor12345" -X DELETE -H "Content-Type: application/json" "https://192.168.1.100/api/repositories?repo_name=dcos%2Fetcd "
```

#### 2.9    获取镜像标签

```bash tab="Bash"
curl -u "admin:Harbor12345" -X GET -H "Content-Type: application/json" "https://192.168.1.100/api/repositories/tags?repo_name=dcos%2Fcentos"
```
