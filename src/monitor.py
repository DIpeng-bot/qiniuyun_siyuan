#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import time
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

logger = logging.getLogger(__name__)

class VideoFileHandler(FileSystemEventHandler):
    """视频文件处理器"""
    
    # 支持的视频文件扩展名
    VIDEO_EXTENSIONS = {'.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv'}
    
    def __init__(self, uploader, recorder):
        self.uploader = uploader
        self.recorder = recorder
        
    def is_video_file(self, file_path):
        """检查是否为视频文件"""
        return os.path.splitext(file_path)[1].lower() in self.VIDEO_EXTENSIONS
        
    def process_video_file(self, file_path, relative_path=None):
        """处理单个视频文件
        
        Args:
            file_path: 视频文件的完整路径
            relative_path: 相对于监控文件夹的路径，用于保持文件夹结构
        """
        try:
            # 等待文件写入完成
            time.sleep(1)  # 简单等待，实际应该检查文件是否完全写入
            
            # 上传文件到七牛云，保持文件夹结构
            url = self.uploader.upload(file_path, relative_path)
            if url:
                # 记录到Google Sheet
                self.recorder.record(file_path, url)
                logger.info(f"文件处理完成: {file_path}")
            else:
                logger.error(f"文件上传失败: {file_path}")
                
        except Exception as e:
            logger.error(f"处理文件时出错 {file_path}: {str(e)}")
            
    def process_directory(self, directory):
        """处理整个目录
        
        Args:
            directory: 要处理的目录路径
        """
        base_path = os.path.dirname(directory)  # 获取父目录
        for root, _, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                if self.is_video_file(file_path):
                    # 计算相对路径，用于在七牛云中保持文件夹结构
                    relative_path = os.path.relpath(root, base_path)
                    logger.info(f"处理文件: {file_path}")
                    self.process_video_file(file_path, relative_path)
    
    def on_created(self, event):
        """处理新创建的文件或目录"""
        if event.is_directory:
            logger.info(f"检测到新文件夹: {event.src_path}")
            # 等待文件夹及其内容完全写入
            time.sleep(2)
            self.process_directory(event.src_path)
            return
            
        file_path = event.src_path
        if not self.is_video_file(file_path):
            return
            
        logger.info(f"检测到新视频文件: {file_path}")
        self.process_video_file(file_path)

class FileMonitor:
    """文件监控器"""
    
    def __init__(self, config, uploader, recorder):
        self.config = config
        self.watch_folder = config.get('local', 'watch_folder')
        self.event_handler = VideoFileHandler(uploader, recorder)
        self.observer = Observer()
        
    def start(self):
        """启动监控"""
        if not os.path.exists(self.watch_folder):
            os.makedirs(self.watch_folder)
            
        # 处理已存在的文件和文件夹
        self.process_existing_files()
            
        self.observer.schedule(self.event_handler, self.watch_folder, recursive=True)
        self.observer.start()
        
        logger.info(f"开始监控文件夹: {self.watch_folder}")
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop()
            
    def process_existing_files(self):
        """处理监控文件夹中已存在的文件和文件夹"""
        logger.info("检查已存在的文件...")
        for root, dirs, files in os.walk(self.watch_folder):
            for file in files:
                file_path = os.path.join(root, file)
                if self.event_handler.is_video_file(file_path):
                    relative_path = os.path.relpath(root, os.path.dirname(self.watch_folder))
                    logger.info(f"处理已存在的文件: {file_path}")
                    self.event_handler.process_video_file(file_path, relative_path)
            
    def stop(self):
        """停止监控"""
        self.observer.stop()
        self.observer.join()
        logger.info("停止监控") 