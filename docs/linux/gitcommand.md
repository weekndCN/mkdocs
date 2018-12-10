# Git 常用指令

### 操作文件

- 显示command的help

```shell
git help <command> 
```

- 显示某次提交的内容

```shell
git show $id
```

- 抛弃工作区修改

```shell
git co -- <file>
```

- 抛弃工作区修改

```shell
git co .
```

- 将工作文件修改提交到本地暂存区

```shell
git add <file>
```

- 将所有修改过的工作文件提交暂存区

```shell
git add .
```

- 从版本库中删除文件

```shell
git rm <file>
```

- 从版本库中删除文件，但不删除文件

```shell
git rm <file> --cached
```

- 从暂存区恢复到工作文件

```shell
git reset <file>
```

- 从暂存区恢复到工作文件

```shell
git reset -- .
```

- 恢复最近一次提交过的状态，即放弃上次提交后的所有本次修改

```shell
git reset --hardgit ci --amend
```

- 将git add, git rm和git ci等操作都合并在一起做　　　　　　　　　　　　　　　　

```shell
git ci <file> git ci . git ci -a 
```

- 改最后一git diff <branch1>..<branch2> # 在两个分支之间比较

```shell
git ci --amend
```

- 比较暂存区和版本库差异

```shell
git diff --staged
```

- 比较暂存区和版本库差异

```shell
git diff --cached
```

- 仅仅比较统计信息

```shell
git diff --stat
```

### 次提交记录

- 恢复某次提交的状态，恢复动作本身也创建次提交对象

```shell
git revert <$id>
```

- 恢复最后一次提交的状态

```shell
git revert HEAD
```

### 查看文件diff

- 比较当前文件和暂存区文件差异

```shell
git diff <file>
```

- 比较当前文件和暂存区文件差异

```shell
git diff <id1><id2>
```

### 查看提交记录

- 查看该文件每次提交记录

```shell
git log git log <file> 
```

- 查看每次详细修改内容的diff

```shell
git log -p <file> 
```

- 查看每次详细修改内容的diff

```shell
git log -p -2
```

- 查看提交统计信息

```shell
git log --stat
```



!!! Warning ""
​    **Mac** 上可以使用 **tig** 代替 **diff** 和 **log**
​    ```
​	brew install tig
​    ```


### Git 本地分支管理

#### 查看、切换、创建和删除分支

- 查看远程分支

```shell
git br -r
```

- 创建新的分支

```shell
git br <new_branch>
```

- 查看各个分支最后提交信息

```shell
git br -v
```

- 查看已经被合并到当前分支的分支

```shell
git br --merged
```

- 查看尚未被合并到当前分支的分支

```shell
git br --no-merged
```

- 切换到某个分支

```shell
git co <branch> 
```

- 创建新的分支，并且切换过去

```shell
git co -b <new_branch> 
```

- 基于branch创建新的new_branch

```shell
git co -b <new_branch> <branch>
```

- 把某次历史提交记录checkout出来，但无分支信息，切换到其他分支会自动删除

```shell
git co $id
```

- 把某次历史提交记录checkout出来，创建成一个分支

```shell
git co $id
```

- 删除某个分支

```shell
git br -d <branch> 
```

- 强制删除某个分支 (未被合并的分支被删除的时候需要强制)

```shell
git br -D <branch> 
```

#### 分支合并和rebase

- 将branch分支合并到当前分支

```shell
git merge <branch> 
```

- 不要Fast-Foward合并，这样可以生成merge提交

```shell
git merge origin/master --no-ff 
```

- 将master rebase到branch

```shell
git rebase master <branch>
```



!!! Info "等价于"
​    git co <branch> && git rebase master && git co master && git merge <branch>



### Git补丁管理

- 生成补丁

```shell
git diff > ../sync.patch
```

- 打补丁

```shell
git apply ../sync.patch
```

- 测试补丁能否成功

```shell
git apply --check ../sync.patch
```

### Git暂存管理

- 暂存

```shell
git stash
```

- 列所有stash

```shell
git stash list
```

- 恢复暂存的内容

```shell
git stash apply
```

- 删除暂存区

```shell
git stash drop
```

### Git远程分支管理

- 抓取远程仓库所有分支更新并合并到本地

```shell
git pull
```

- 抓取远程仓库所有分支更新并合并到本地，不要快进合并

```shell
git pull --no-ff
```

- 抓取远程仓库更新

```shell
git fetch origin
```

- 将远程主分支合并到本地当前分支

```shell
git merge origin/master
```

- 跟踪某个远程分支创建相应的本地分支

```shell
git co --track origin/branch
```

- 基于远程分支创建本地分支，功能同上

```shell
git co -b <local_branch> origin/<remote_branch>
```

- push所有分支

```shell
git push
```

- 将本地主分支推到远程主分支

```shell
git push origin master
```

- 将本地主分支推到远程(如无远程主分支则创建，用于初始化远程仓库)

```shell
git push -u origin master
```

- 创建远程分支， origin是远程仓库名

```shell
git push origin <local_branch>
```

- 创建远程分支

```shell
git push origin <local_branch>:<remote_branch>
```

- 先删除本地分支(git br -d <branch>)，然后再push删除远程分支

```shell
git push origin :<remote_branch>
```

### Git远程仓库管理

#### GitHub

- 查看远程服务器地址和仓库名称

```shell
git remote -v
```

- 查看远程服务器仓库状态

```shell
git remote show origin
```

- 添加远程仓库地址

```shell
git remote add origin git@ github:robbin/robbin_site.git
```

- 设置远程仓库地址(用于修改远程仓库地址) 

```shell
git remote set-url origin git@ github.com:robbin/robbin_site.git
```

- 删除远程仓库

```shell
git remote rm <repository>
```

#### 创建远程仓库

- 用带版本的项目创建纯版本仓库

```shell
git clone --bare test test.git
```

- 在服务器创建纯仓库

```shell
mkdir test.git && cd test.git && git --bare init
```

- 在服务器创建纯仓库

```shell
git remote add origin https://github.com/<USERNAME>/test.git
```

- 客户端首次提交

```shell
git push -u origin master
```
