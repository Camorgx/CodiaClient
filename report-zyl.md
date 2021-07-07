# 程序设计II大作业实验报告

姓名：郑以勒

学号：PB20000082

## 实验题目与要求

本次实验主要内容是实现一个简单的CODIA客户端。项目位于USTC gitlab，地址为https://git.ustc.edu.cn/zzyyyl/codiaclient. dev分支为命令行部分最新进展，gui-master分支为gui部分最新进展。一些实现功能如下。

### 基本功能部分

#### 登录

`run.py -u USERNAME [--passwd PASSWORD]`.  
以用户名 USERNAME 和 密码 PASSWORD 尝试登录; 若没有指定PASSWORD, 程序会在启动时提示输入密码（此处会隐藏键盘输入，以回车结束）; 若启用缓存, 首先尝试匹配已经保存的配置.  
如果网络畅通并且账号验证成功, 客户端会输出信息`Info: Login succeeded.(DisplayName)`, 其中 `DisplayName` 是你的昵称（没有设置会显示 `UNDEFINED` ）. 这表示你已经登录成功.

<img src=".\img\login.png" style="zoom:60%;" />

#### 找回密码

`run.py -u USERNAME`后使密码留空，以`y`确定更改密码并依据提示根据邮箱或手机号找回密码，若成功修改则会以修改后的密码尝试自动登录。

<img src=".\img\password_change.png" style="zoom:60%;" />

#### 注册

`run.py --register -u USERNAME [--passwd PASSWORD]`.  
以用户名 USERNAME 和 密码 PASSWORD 尝试注册; 若没有指定PASSWORD, 程序会在启动时提示输入密码（此处会隐藏键盘输入，以回车结束）; 需要依据提示输入邮箱和验证码。  
注册成功后会直接登录；若用户名存在并且密码正确也会直接登录。  

<img src=".\img\register.png" style="zoom:60%;" />

#### 指定题包/题目

指定题包/题目需要通过其编号来指定. 下面用 pid 代表题包编号, eid 代表题目编号. 

这个过程不需要联网，因为在这一步程序并不会检查 pid / eid 的合法性，而仅仅是为变量赋值。这意味着如果程序接收了错误的输入，在这一步不会输出错误信息。

pid, eid 可以通过客户端查询, 也可以在网页端访问的链接中获得.  
如果没有`pack`字段, 则不需要指定 pid. *(若在之前的请求中指定了 pid, 需要清空 pid)*

例如，在`https://code.bdaa.pro/pack/cknyss3ge11084950tq960zopuwh/exercise/cknyjlcnf106869311nwaa5l3blo/coding`中, `cknyss3ge11084950tq960zopuwh` 为 pid, `cknyjlcnf106869311nwaa5l3blo` 为 eid.

- 指定题包  
`pid PID` 或 `p PID`.  
指定编号为PID的题包.

- 取消指定题包  
`del pid` .  
取消指定题包.

- 指定题目  
`eid EID` 或 `e EID`.  
指定编号为EID的题目.

以上实际为对程序内变量的赋值操作，在后文[修改变量](#修改变量)中有详细说明。

#### 获取题包列表

`getpack [N] [before|after PID]`.  
获取编号为 PID 的题包的前（后） N 个题包的信息; 若未指定 PID, 则获取最近 N 个题包的信息; N的默认值为8.  
在这里可以获取题包标题和编号等信息.  

#### 获取题包信息

`showpack` 或 `sp`.  
获取题包信息.   
在这里可以获取题包的一些信息，包括题包起止时间、题包所包含题目的标题和编号等信息.  

<img src=".\img\pack.png" style="zoom:60%;" />

#### 查看题目内容

`getexercise` 或 `ge`.  
查看题目内容.  
在这里可以获取题目的一些信息，包括题目标题、内容和样例，题目所给定的缺省代码，提交统计等信息。  

<img src=".\img\exer.png" style="zoom:60%;" />

#### 开始题包

`startpack`.  
开始一个题包的答题.  

#### 提交代码

`open PATH`.  
读取路径PATH上的文件内容并写入到变量`solutioncode`中.  

`submit`.  
提交代码到服务器评测.  
根据 pid, eid 的值确定提交的题目，并以`solutioncode`的内容作为提交的代码.  
如果在提交题包中的题目的代码前没有开始过这个题包，可能会无法记录提交结果。  

#### 查询变量
`show [VAR]`.  
查询变量（别）名VAR的变量; 若没有指定变量名, 则返回`requests_var`中的所有变量.  

#### 修改变量
`VAR VAL`.  
将变量（别）名为VAR的变量的值修改为VAL, VAL不允许为空。  

#### 重置变量
`del [VAR]`或`reset [VAR]`.  
将变量（别）名为VAR的变量的值修改为*None*; 若没有指定变量名，则重置所有变量。  

<img src=".\img\var.png" style="zoom:60%;" />


### 扩展部分

#### 查询提交过的代码

`gc [K] [to [PATH]]`.  
获取倒数第 K 次提交的代码, K 默认为1; 若指定了 PATH, 会将获取到的代码输出到指定文件; 若输入了`to`但没有指定 PATH, 默认输出文件为运行目录下的*tmp.txt*.

#### 查询代码评判结果

`gr [K]`.  
获取倒数第 K 次提交的代码的评判结果, K 默认为1; 如果仍在评测中, 会返回空字典, 即`{}`.

<img src=".\img\code.png" style="zoom:60%;" />

#### 接口相关
若非直接命令行运行, 启动时加上`--origin`选项可以获取未解码的数据, 数据以 Unicode 编码, *python* 可以直接以`str.encode('utf-8').decode('unicode-escape')`的形式解码, 可以参考`./run.py`.

#### 配置相关
每次成功登录后默认会往配置文件 `./codiaclient.cache` 中写入登录信息，包括: 
- 用户名 *(明文 )*
- 用户邮箱 *(明文 )*
- 密码的 *sha256* 哈希值 *(在记住密码时储存明文 )*
- cookie用 *AES* 加密的值 *(密钥为密码明文 )*

这种记录方法在绝大多数情况下保证无法从配置文件中获取密码的值，并且在密码不正确时不能获取对应的cookie.  
在登录时会首先尝试匹配配置中的信息。成功匹配则直接使用配置中的cookie尝试登录，失败则会向服务器提交数据以获得新的cookie.  
若在启动程序时加上`--no-cache`的选项，则会禁用配置，即不会往配置文件中写入信息，也不会从配置文件中读取信息。**已经写入的数据不会删除。**

#### 按钮设计
对于图形化的 CODIA 客户端，按钮在 Windows 下的样式由默认改为圆角按钮，动画形式也略有更改，尽量保证了视觉上的舒适性。

#### 进度条设计
对于图形化的 CODIA 客户端，在调节进度条的值时有默认1.5秒的动态效果，由 QEasingCurve.OutQuart 函数实现了缓动。

## 具体设计

下面对我们的项目进行一些简单的介绍。

### 文件结构

```bash
run.py
codiaclient/__init__.py
codiaclient/argparse.py
codiaclient/cachectrl.py
codiaclient/network.py
codiaclient/requests.py
codiaclient/report.py
codiaclient/utils.py
```

### 主要函数与类

#### 网络相关

#####  client_login
`client_login(args=None, username=None, password=None, cookie=None)`  
主登录函数。传入的参数为命令行启动时输入的参数。  
没有给定密码则在函数内隐蔽的输入密码（采用了`getpass.getpass()`函数）。  
若在这一步输入的密码为空，则可以选择进入找回密码的程序，确认执行则转到`change_password()`函数，等待执行完后继续尝试下面的登录操作。  
若命令行参数指定注册，这个函数会把获得的用户名和密码传递给`register()`函数，等待执行完注册程序后尝试下面的登录操作。  
在启用缓存时，这个函数会先检测用户名和密码，并试图从缓存中读取cookie。  
没有启用缓存，或读取不到缓存中对应的cookie，则会使用输入的用户名和密码执行`login()`函数。  
在登录后，以函数`logined()`验证是否登录。  
登录成功后会直接修改`headers['cookie']`, 登录失败则会`raise`一个错误（`codiaclient.report.Error`）.  

##### logined
`logined(reportUnverified: bool = True)`  
检查登录状态的函数。  
向服务器发送`me`请求。  
未登录或检查失败返回`("FAILED", None)`;  
登录成功但与缓存状态不符需重写缓存时返回`("UNMATCHED", displayName)`, 其中displayName是用户昵称,下同;  
登录成功且一切正常返回`("SUCCESS", displayName)`.  

##### login
`login(username, passwd)`  
登录函数。  
向服务器发送`login`请求，登录失败返回`False`并有`"Login Failed."`错误;  
登录成功返回`True`并有`"Login succeeded.(displayName)"`提示。  

##### register
`register(username, passwd, email=None)`  
注册函数。  
在没有给定email时在函数内由`input()`接收注册所用的邮箱账号。  
向服务器发送`signup`请求，注册失败返回`False`;  
注册成功返回字典`{id, login, displayName, defaultEmail, avatarUrl, verified}`，代表所注册的用户信息.  

##### change_password
`change_password(identifier=None, vercode=None, passwd=None, passwordconfirm=None)`  
通过函数`_acquire_verification()`向服务器申请验证码；并根据输入的验证码向服务器发送`verify`和`passwordChange`请求。  
失败返回`False`，成功返回修改后的密码。  

##### submit
`submit(eid, pid, lang, solutioncode)`  
提交solutioncode内的代码到题包编号为pid，题目编号为eid的题目上。  

##### get_data
`get_data(eid, pid, before=None, after=None, cnt=None)`  
获取题包编号为pid，题目编号为eid的题目的做题信息。  

##### get_exercise
`get_exercise(eid, pid, lang, feedback='dict')`  
获取题包编号为pid，题目编号为eid的题目的题目信息。  

##### get_pack
`get_pack(before=None, after=None, cnt=None)`  
获取题包缩略信息。  

##### show_pack
`show_pack(pid)`  
获取题包编号为pid的题包信息。  

##### start_pack
`start_pack(pid)`  
开始编号为pid的题包的答题。  

#### 缓存相关

##### cache_for_login
`cache_for_login(userdic, passwd, cookie=None, passwd_store_on=0)`  
缓存密码等登录用信息。  
事实上，这个函数并不会缓存密码明文，**除非**指定了记住密码模式为2（默认值为1）.  
默认情况下，函数将缓存用户名、默认邮箱、以密码明文作为密钥的AES加密后的cookie、哈希后的密码（仅作登录校验，但在记住密码模式为2是密码明文）。  
Windows下缓存路径为`"%AppData%/codiaclient/.cache"`, mac下为`"~/Library/codiaclient/.cache"`, 其他为`"./codiaclient/.cache"`.

#### 错误处理相关

##### *class* Error
`class Error(Exception)`  
类下有成员deg和text，deg储存错误程度（`["Info", "Warning", "Error", "Fatal"]`），text储存错误信息。  

##### report
`report(text, deg=0, filestream=stderr, end='\n')`  
向filestream中输出错误程度为deg的程序信息text。并将deg在允许范围外的错误raise.  

##### error_translate
`error_translate(e: Error)`  
将错误信息翻译为中文。  
无法翻译的返回False，成功翻译的返回中文的字符串.  

#### 杂项

##### *class* AliasesDict
`class AliasesDict(dict)`  
别名字典。  
类下成员aliaseslist为别名表，将别名映射为原名。  
查询时可以直接以原名/别名作为[]的参数。  

##### passwd_hash
`passwd_hash(passwd)`  
返回将password以sha256哈希后的字符串。  

##### cookie_encrypt
`cookie_encrypt(cookie, passwd)`  
返回将cookie以password作为密钥的AES加密后的字符串。  

##### cookie_encrypt
`cookie_encrypt(_cookie, passwd)`  
返回将\_cookie以password作为密钥的AES解密后的字符串。  

## 实验过程

### 常见错误信息与警告信息

我们为客户端做了简单的错误处理。  
客户端的输出信息分为四种，错误级别从低到高分别为`Info`, `Warning`, `Error`, `Fatal`.

- `Info`指程序正常运行中产生的消息
- `Warning`指可能导致程序出错的警告消息
- `Error`指不影响程序整体运行的错误消息
- `Fatal`指严重出错导致程序无法进行的错误消息

|信息内容|解释|建议|
|----------------|----|----|
|`Error: _login: invalid username or password.`|用户名不存在或密码错误|检查你的用户名和密码|
|`Fatal: change_password: Acquiring status error.`|修改密码时获取凭证状态错误|检查你的网络连接和输入的凭证|
|`Fatal: Empty password.`|密码未输入|依据提示输入密码|
|`Fatal: Identifier error.`|凭证错误|检查你输入的凭证|
|`Fatal: Invalid cookie input.`|输入的cookie不合法|检查你的cookie|
|`Fatal: Login failed.`|登陆失败|检查你的登录凭证|
|`Fatal: No username or cookie specified.`|用户名未输入|按照正确格式输入用户名|
|`Fatal: Unknown error.`|未知错误|检查你之前的操作|
|`Fatal: Verification acquiring error.`|认证凭证获取失败|检查你的网络并稍后重试|
|`Warning: Cache loading failed.`|缓存失败|删除缓存文件|
|`Warning: Connect timeout.`|网络连接超时|检查你的计算机网络连接，或稍后重试|
|`Warning: Connection error.`|网络连接错误|检查你的计算机网络连接|
|``Warning: FUN: Variable `VAR` type error.``|变量类型错误|检查你调用函数名为`FUN`的函数时参数名为`VAR`的参数类型|
|`Warning: Invalid cached cookie.`|缓存的cookie不合法|等待程序登录|
|`Warning: Invalid cookie input.`|输入的cookie不合法|检查你的cookie或等待程序登录|
|`Warning: Invalid request.`|非法请求|检查你的请求格式，可以在程序中输入`help`以获得帮助|
|`Warning: Unknown login error.`|未知登录错误|检查你的登录凭证并稍后再次尝试|
|`Warning: No pid specified.`|未指定题包编号|按照正确格式输入题包编号|
|`Warning: No eid specified.`|未指定题目编号|按照正确格式输入题目编号|
|`Warning: This pack is already ongoing.`|题包已经正在进行|不需要开始题包，可以直接答题|
|`Warning: The user has not verified.`|用户未认证|通过网页认证所使用的登录账号|

### 合作相关

我的搭档为我的程序提供了许多修改意见，包括了函数的返回值类型、错误翻译以及代码结构等。  
我也为我的搭档提供了许多帮助。在图形化上，我为Windows下按钮以及其他小部分UI做了美化设计；在网络处理上，我提供了多线程的实现代码。

## 实验总结

通过这次的大作业，我在写命令行界面的代码时了解了python中requests库的一些简单网络处理、graphql的简单应用与简单的错误处理，并熟练了以多个文件来编写程序的方法。在帮助搭档处理图形化时，我熟悉了PyQt与Qt Designer的应用，熟悉了多线程的写法并了解了其在处理网络通信时的重要性。
