# 七牛云视频下载上传与归档工具

这是一个用于自动下载视频并上传到七牛云存储,同时记录视频URL到Google Sheet的工具。

## 主要功能

- 从指定的URL列表下载视频文件到本地文件夹
- 将本地视频文件上传到七牛云存储空间  
- 将视频的本地路径和七牛云URL记录到Google Sheet表格中
- 支持定时执行和文件夹监控触发两种运行模式

## 运行环境

- Python 3.6+
- 操作系统: Windows、Linux或macOS

## 安装依赖

1. 安装Python 3.6或更高版本
2. 克隆此仓库到本地 
3. 进入项目目录,执行以下命令安装所需库:

```bash
pip install -r requirements.txt
```

## 配置说明

在运行程序前,你需要进行以下配置:

1. 在项目根目录创建一个`config.ini`文件,内容参考`config.example.ini`
2. 在`[qiniu]`部分填写你的七牛云账号的`access_key`和`secret_key`,以及要上传的`bucket`名称
3. 在`[google]`部分填写你的Google服务账号的JSON密钥文件路径以及要写入的Google Sheet的ID
4. 在`[local]`部分填写本地视频文件夹路径和下载视频的URL列表文件路径

## 使用方法

### 命令行参数

```
python main.py [-h] [--mode MODE] [--interval INTERVAL]

optional arguments:
  -h, --help           show this help message and exit
  --mode MODE          运行模式: 'schedule' 或 'monitor' (默认为'schedule')
  --interval INTERVAL  在'schedule'模式下,任务执行的时间间隔,单位秒 (默认为3600)
```

### 定时模式

在该模式下,程序会每隔指定的时间间隔执行一次下载上传任务。适合视频更新频率比较固定的场景。

运行示例: 
```bash
python main.py --mode schedule --interval 1800  
```

### 监控模式

在该模式下,程序会持续监控指定的本地文件夹,当有新的视频文件出现时就会触发上传任务。适合视频更新没有固定频率的场景。

运行示例:

```bash
python main.py --mode monitor
```

## 项目结构

```
|- main.py          // 主程序入口  
|- downloader.py    // 视频下载模块
|- uploader.py      // 七牛云上传模块
|- recorder.py      // Google Sheet写入模块  
|- requirements.txt // 依赖库列表
|- config.example.ini // 配置文件模板
|- README.md        // 项目说明文档
```

## 常见问题  

1. 运行程序时提示`No module named 'xxx'`: 
  - 检查是否已安装所有requirements.txt中列出的依赖库
  - 尝试重新执行`pip install -r requirements.txt`

2. 上传到七牛云失败:
  - 检查`config.ini`中填写的七牛云密钥是否正确
  - 确保本地网络可以连接到七牛云服务器
   
3. 写入Google Sheet失败:  
  - 检查`config.ini`中填写的Google服务账号密钥文件路径是否正确
  - 确保该服务账号拥有对目标Google Sheet的写权限

## 贡献指南

如果你希望为这个项目做贡献,欢迎提交Issue和Pull Request。在提交Pull Request之前,请先阅读[贡献指南](./CONTRIBUTING.md)。

## 许可证

该项目基于MIT许可证开源 - 详见[LICENSE](./LICENSE)文件。
