# jingyun

# 0.2.9
jy-supervisord jy-supervisorctl 执行前，先进行source .bash_profile

# 0.2.8
jy-oss-download 添加参数 -f --force 无论要下载的文件是否已存在，都进行下载

# 0.2.7
jy-oss-download 添加参数 -n --name  下载后保存的文件名，仅在下载文件只有一个时有效，超过一个下载文件将忽略该参数

# 0.2.6
jy-oss-download下载时如果文件存在将不进行下载

# 0.2.5
jy-supervisord
jy-supervisorctl

# 0.2.2
add jy-jingd-usermod
udpate jy-conf-read 添加参数 -i --ignore

# 0.2.1
add jy-conf-read

## 0.1.10
add jy-ssh-nonkey

## 0.1.9
jy-conf-format 支持遍历和筛选整个目录下的文件

## 0.1.8
jy-conf-format add mode params

## 0.1.7
add jy-conf-format

## 0.1.6
jy-key add --only-value 只打印密钥要打印的密钥中的属性值，不打印属性

## 0.1.5
fix not include jingyun_cli/key

## 0.1.4
key cli 上线 jy-key

## 0.1.3
oss cli 上线 jy-oss-download

## 0.1
json cli 上线 json-merge