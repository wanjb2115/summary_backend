# summary_backend

接口：

1. 数据预处理：

—获取input目录名：
http://59.110.152.105:5000/GetFileNames/input/events
http://59.110.152.105:5000/GetFileNames/input/logcats

-output
—获取output目录名:
http://59.110.152.105:5000/GetFileNames/output
http://59.110.152.105:5000/GetFileNames/output/com.xdf.ucan

—获取某个文件内容：
http://59.110.152.105:5000/GetFileContent/output/com.xdf.ucan/1110_1/event.json
http://59.110.152.105:5000/GetFileContent/input/logcats/1000_1/com.example.myfristandroid.SplashActivity_1449718553852_1.txt

2. 数据切分
http://59.110.152.105:5000/SliceEvent/com.example.myfristandroid/695_1

3. 翻译总结
http://59.110.152.105:5000/Translate/com.example.myfristandroid/1001_1
