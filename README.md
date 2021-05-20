如果想要了解客户端的用法，可以用`run.py -h`来获得*命令帮助*，登录后可以在程序中输入`help`获得*查询帮助*.

# 输出信息解释

客户端的输出信息分为四种，错误级别从低到高分别为`Info`, `Warning`, `Error`, `Fatal`.

- `Info`指程序正常运行中产生的消息
- `Warning`指可能导致程序出错的警告消息
- `Error`指不影响程序整体运行的错误消息
- `Fatal`指严重出错导致程序无法进行的错误消息

|常见错误/警告信息|解释|建议|
|----------------|----|----|
|`Fatal: Empty password.`|密码未输入|依据提示输入密码|
|`Fatal: Invalid cookie input.`|cookie不合法|检查你的cookie|
|`Fatal: Login failed.`|登陆失败|检查你的登录凭证|
|`Fatal: No username or cookie specified.`|用户名未输入|按照正确格式输入用户名|
|`Warning: _login: invalid username or password.`|用户名不存在或密码错误|检查你的用户名和密码|
|`Warning: Connect timeout.`|网络连接超时|检查你的计算机网络连接，或稍后重试|
|`Warning: Connection error.`|网络连接错误|检查你的计算机网络连接|
|`Warning: Invalid request.`|非法请求|检查你的请求格式，可以在程序中输入`help`以获得帮助|
|`Warning: No pid specified.`|未指定题包编号|按照正确格式输入题包编号|
|`Warning: No eid specified.`|未指定题目编号|按照正确格式输入题目编号|

# 常用功能
## 登录
`run.py -u USERNAME --passwd PASSWORD` *(会在窗口中显示密码 )* 或 `run.py -u USERNAME`后依据提示输入密码. *(不会在窗口中显示密码，建议使用这种方式 )*  
以用户名 USERNAME 和 密码 PASSWORD 尝试登录; 若启用缓存, 首先尝试匹配已经保存的配置. 要获取配置文件相关的帮助, 可以查看[配置相关](#配置相关).  
如果网络畅通并且账号验证成功, 客户端会输出信息`Info: Login succeeded.(DisplayName)`, 其中 DisplayName 是你的昵称. 这表示你已经登录成功.

## 获取题包列表/信息
### 获取题包列表
`gp [N] [before PID]`.  
获取编号为 PID 的题包的前 N 个题包的信息; 若未指定 PID, 则获取最近 N 个题包的信息; N的默认值为8. 返回类型为*json*.  
在这里可以获取题包标题和编号等信息.  

### 获取题包信息（需先指定题包）
`showpack` 或 `sp`.  
获取题包信息. 返回类型为*json*.  
在这里可以获取题包的一些信息，包括题包起止时间、题包所包含题目的标题和编号等信息.

## 指定题包/题目

指定题包/题目需要通过其编号来指定. 下面用 pid 代表题包编号, eid 代表题目编号. *(注意这里的编号并不是通常意义上的编号，而是一个长字符串 )*

*Tips: 这个过程不需要联网，因为在这一步程序并不会检查 pid / eid 的合法性，而仅仅是为变量赋值。这意味着如果程序接收了错误的输入，在这一步不会输出错误信息。*

pid, eid 可以通过客户端查询, 也可以在网页端访问的链接中获得.  
网页链接中, `/pack/`后面的字符串为 pid, `/exercise/`后面的字符串为 eid. 如果没有`pack`字段, 则不需要指定 pid. *(若在之前的请求中指定了 pid, 需要清空 pid)*

例如，在`https://code.bdaa.pro/pack/cknyss3ge11084950tq960zopuwh/exercise/cknyjlcnf106869311nwaa5l3blo/coding`中, `cknyss3ge11084950tq960zopuwh` 为 pid, `cknyjlcnf106869311nwaa5l3blo` 为 eid.

### 指定题包

`pid PID` 或 `p PID`.  
指定编号为PID的题包.

### 取消指定题包

`pid` 或 `p`.  
取消指定题包.

### 指定题目

`eid EID` 或 `e EID`.  
指定编号为EID的题目.

## 查看题目内容

`getexercise` 或 `ge`.  
查看题目内容. 该函数可以指定返回类型, 直接调用默认为*dict*, 在查询时默认为*json*.

## 提交代码

`open PATH`.  
读取路径PATH上的文件内容并写入到变量`solutioncode`中.

`submit`.  
提交代码到服务器评测. 直接调用函数的返回类型为*requests.Response*, 查询时没有返回.  
根据 pid, eid 的值确定提交的题目，并以`solutioncode`的内容作为提交的代码.

*Tips: 提交之前请确保 `pid`, `eid`正确。可以获取题面以验证，方法参照：[查看题目内容](#查看题目内容)。另外建议提交之前检查一遍 `solutioncode`. 查询方法参照：[查看程序运行中的变量](#查看程序运行中的变量)。*

## 查询提交过的代码

`gc [K] [to [PATH]]`.  
获取倒数第 K 次提交的代码, K 默认为1; 若指定了 PATH, 会将获取到的代码输出到指定文件; 若输入了`to`但没有指定 PATH, 默认输出文件为运行目录下的*tmp.txt*. 返回类型为*str*.  

## 查询代码评判结果

`gr [K]`.  
获取倒数第 K 次提交的代码的评判结果, K 默认为1; 如果仍在评测中, 会返回空字典, 即`{}`. 返回类型为*json*.  

## 查看程序运行中的变量

`show [VAR]`.  
查看变量名为VAR的变量; 若没有指定变量名, 则返回所有变量 *(包括 `username`, `pid`, `eid`, `lang`, `solutioncode`)*. 返回类型为*json*.

# 辅助功能

## 配置相关

每次成功登录后默认会往配置文件 `./cache.passwd.conf` 中写入登录信息，包括: 
- 用户名 *(明文 )*
- 密码的哈希值 *(sha256)*
- cookie用AES加密的值 *(密钥为密码明文 )*

这种记录方法在绝大多数情况下保证无法从配置文件中获取密码的值，并且在密码不正确时不能获取对应的cookie.
在登录时会首先尝试匹配配置中的信息。成功匹配则直接使用配置中的cookie尝试登录，失败则会向服务器提交数据以获得新的cookie.  
若在启动程序时加上`--no-cache`的选项，则会禁用配置，即不会往配置文件中写入信息，也不会从配置文件中读取信息。**但已经写入的数据不会删除。**
