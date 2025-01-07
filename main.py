#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import logging
import configparser
from logging.handlers import RotatingFileHandler

from src.monitor import FileMonitor
from src.uploader import QiniuUploader
from src.recorder import SheetRecorder

def setup_logging(config):
    """设置日志配置"""
    log_level = getattr(logging, config.get('log', 'log_level', fallback='INFO'))
    log_file = config.get('log', 'log_file', fallback='logs/app.log')
    
    # 确保日志目录存在
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    # 配置日志
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            RotatingFileHandler(log_file, maxBytes=1024*1024, backupCount=5),
            logging.StreamHandler(sys.stdout)
        ]
    )

def load_config():
    """加载配置文件"""
    config = configparser.ConfigParser()
    config_path = 'config/config.ini'
    
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"配置文件不存在: {config_path}")
    
    config.read(config_path, encoding='utf-8')
    return config

def main():
    """主程序入口"""
    try:
        # 加载配置
        config = load_config()
        
        # 设置日志
        setup_logging(config)
        logger = logging.getLogger(__name__)
        
        logger.info("正在初始化服务...")
        
        # 初始化组件
        uploader = QiniuUploader(config)
        recorder = SheetRecorder(config)
        monitor = FileMonitor(config, uploader, recorder)
        
        logger.info("开始监控文件夹变化...")
        monitor.start()
        
    except Exception as e:
        logger.error(f"程序启动失败: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 