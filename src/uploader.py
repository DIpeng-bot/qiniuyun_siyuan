#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import logging
from qiniu import Auth, put_file, BucketManager

logger = logging.getLogger(__name__)

class QiniuUploader:
    """七牛云上传器"""
    
    def __init__(self, config):
        self.access_key = config.get('qiniu', 'access_key')
        self.secret_key = config.get('qiniu', 'secret_key')
        self.bucket = config.get('qiniu', 'bucket')
        self.domain = config.get('qiniu', 'domain')
        
        # 初始化认证
        self.auth = Auth(self.access_key, self.secret_key)
        self.bucket_manager = BucketManager(self.auth)
        
    def get_upload_token(self, key):
        """获取上传凭证"""
        return self.auth.upload_token(self.bucket, key)
        
    def get_file_url(self, key):
        """获取文件的访问URL"""
        return f"http://{self.domain}/{key}"
        
    def upload(self, local_file, relative_path=None, retry_times=3):
        """上传文件到七牛云
        
        Args:
            local_file: 本地文件路径
            relative_path: 相对路径，用于在七牛云中保持文件夹结构
            retry_times: 重试次数
            
        Returns:
            str: 文件的访问URL，上传失败返回None
        """
        if not os.path.exists(local_file):
            logger.error(f"文件不存在: {local_file}")
            return None
            
        # 生成文件key，保持文件夹结构
        file_name = os.path.basename(local_file)
        if relative_path and relative_path != '.':
            # 使用正斜杠(/)作为路径分隔符，确保URL正确
            key = f"{relative_path.replace(os.sep, '/')}/{file_name}"
        else:
            key = file_name
            
        logger.info(f"上传文件: {local_file} -> {key}")
        
        # 获取上传凭证
        token = self.get_upload_token(key)
        
        # 尝试上传，最多重试指定次数
        for i in range(retry_times):
            try:
                ret, info = put_file(token, key, local_file)
                
                if info.status_code == 200:
                    logger.info(f"文件上传成功: {local_file}")
                    return self.get_file_url(key)
                else:
                    logger.warning(f"第{i+1}次上传失败: {info.error}")
                    
            except Exception as e:
                logger.error(f"上传出错: {str(e)}")
                if i == retry_times - 1:  # 最后一次重试
                    return None
                
        return None 