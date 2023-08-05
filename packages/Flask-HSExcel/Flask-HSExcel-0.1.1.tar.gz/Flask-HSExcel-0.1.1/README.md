# 环思excel插件 

### 插件功能
1. 提供excel维护功能,包括上传,获得上传记录列表,批量删除,下载上传的文件,下载带错误的excel
2. 提供灵活可配置的错误校验机制,实现对不同业务系统不同excel格式的配置
3. 将excel内容解析成json字符串存入数据库中
4. 使用celery进行异步任务,后台进行错误校验,错误添加

### 安装与配置



1. 上传excel,给出excel列表的维护接口
2. 在后台celery自动调用异步任务，然后完成excel的校验，带错误excel的生成
3. excel的内容加上错误存成一个大的json字符串
4. 提供下载excel的接口，具体的预览接口以及查看错误接口单独实现

### excel格式要求

1.　excel第一行必须为英文，第二行为对应英文的汉语解释，严格要求格式
2. 读取excel的时候只会取读取第一个sheet页的内容


### docker 里面要安装

nohup celery worker -A celery_worker.celery -l INFO > celery.log 2>&1 &
