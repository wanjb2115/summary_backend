# summary_backend

接口：
数据预处理：

GetFileNames为获取文件夹中的目录名
GetFileContent为获取指定路径文件的内容



-input

—获取events目录名：

http://59.110.152.105:5000/GetFileNames/data_process/input/events

—获取logcat目录名：

http://59.110.152.105:5000/GetFileNames/data_process/input/logcats

-output

—获取output目录名:

http://59.110.152.105:5000/GetFileNames/data_process/output
				
http://59.110.152.105:5000/GetFileNames/data_process/output/com.xdf.ucan

—获取某个文件内容：

http://59.110.152.105:5000/GetFileContent/data_process/output/com.xdf.ucan/1110_1/event.json

http://59.110.152.105:5000/GetFileContent/data_process/input/logcats/1000_1/com.example.myfristandroid.SplashActivity_1449718553852_1.txt
