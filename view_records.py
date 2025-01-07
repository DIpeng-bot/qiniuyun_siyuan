#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import configparser
from src.recorder import SheetRecorder

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'  # 简化日志格式，只显示消息
)

def main():
    # 加载配置
    config = configparser.ConfigParser()
    config.read('config/config.ini', encoding='utf-8')
    
    # 初始化记录器
    recorder = SheetRecorder(config)
    
    # 查看最近10条记录
    recorder.view_records(limit=10)

if __name__ == "__main__":
    main() 