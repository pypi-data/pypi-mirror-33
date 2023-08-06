# 环思excel插件 

**该插件会在c_api里面有完整成熟的应用,请参考c_api的代码组织方式,应用方式**

### 插件功能
1. 提供excel维护功能,包括上传,获得上传记录列表,批量删除,下载上传的文件,下载带错误的excel,详情可看flask_hsexcel.view里面代码
2. 提供灵活可配置的错误校验机制,实现对不同业务系统不同excel格式的配置
3. 将excel内容解析成json字符串存入数据库中hs_excel.content字段中,解析成功之后,查询excel列表的status会为1
4. 使用celery进行异步任务,后台进行错误校验,根据自定义的错误校验类,自动进行错误校验,content中dict的key为error自动添加.成功完成错误校验之后status会变成2

### 安装与配置
1. 安装
    ```shell
    pip install flask_hsexcel
    ```
    **注意**  
    - 国内源安装不上的话,请使用pipy源安装
    ```shell
    pip install flask_hsexcel -i https://pypi.org/simple/
    ```
2. 配置,请参考c_api仓库里面的配置方式
    1. 创建error_checker.py 文件,该文件为创建错误校验类,集中配置的地方,
        - 定义错误配置类,继承ErrorChecker,配置config,tuple里面的第一个参数为excel列名,第二个参数为调用的校验类型,第三个参数为,校验为通过时候提示的字符串.
        - 关于错误校验方法,提供了基础类型校验 check_str ==> 校验非空,check_int ==> 校验整数
        check_float ==> 校验浮点数  check_date ==> 校验日期类型 check_datetime ==> 校验时间类型
        - 配置checker,格式为字典,需要在初始化hs_excel中初始化
        ```python
        from flask_hsexcel.checker import ErrorChecker


        class HelloCheck(ErrorChecker):
            config = [
                ('str', 'check_str', '不是字符'),
                ('int', 'check_int', '不是整数'),
                ('float', 'check_float', '不是浮点数'),
                ('date', 'check_date', '不是日期型'),
                ('datetime', 'check_datetime', '不是时间型')
            ]

        checker = {
            'hello': HelloCheck
        }

        ```
    2. 初始化hs_excel,一般在create_app方法里面
        ```python
        from flask_sqlalchemy import SQLAlchemy
        from flask_hsexcel import HsExcel
        from error_checker import checker
        db = SQLAlchemy()
        hsexcel = HsExcel()
        db.init_app(app=app)
        hsexcel.init_app(app=app, checker=checker)
        ```
    3. 给flask配置参数,这是为postgresql配置的,关于CELERY_BROKER_URL配置请参考celery文档
        ``` python
        SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://chao:123456@localhost:3333/postgres'
        SQLALCHEMY_TRACK_MODIFICATIONS = False
        EXCEL_PATH = os.path.join(basedir, 'excel')
        CELERY_BROKER_URL = 'sqla+postgresql://chao:123456@localhost:3333/postgres'
        ```

    4. 配置celery的工作进程,创建celery_worker.py
        ``` python
        # 在当前环境运行的flask实例app 以及在初始化flask实例的时候注册的hsexcel
        from manage import hsexcel,app
        from flask_hsexcel.task import check_error
        celery = hsexcel.make_celery()
        app.app_context().push()
        ```

        运行如下命令启动celery
        ``` shell
         nohup celery worker -A celery_worker.celery -l INFO
        ```

        以守护进程的模式来运行,celery的运行日志就会追加到 celery.log中
        ``` bash
         nohup celery worker -A celery_worker.celery -l INFO > celery.log 2>&1 &
        ```

### 提供接口,详情参考flask_hsexcel.view里面代码

    1. excel上传,列表,删除多条的接口. /hs_excel/import/ 需要传excel_type,系统会根据excel_type去checker里面寻找,该上传的excel对应的错误类.
    2. excel单个excel下载接口 /hs_excel/one/excel/
    3. excel单个带错误excel下载接口 /error/export/

### excel格式要求

    1.　excel第一行必须为英文,允许有空格，第二行为对应英文的汉语解释，严格要求格式,解析excel是会跳过第一二行.
    2. 读取excel的时候只会取读取第一个sheet页的内容,请把业务数据放在第一个sheet页中


### docker 里面要安装,要在docker_entry里面启动celery

nohup celery worker -A celery_worker.celery -l INFO > celery.log 2>&1 &
