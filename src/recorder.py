#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import logging
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials
from tenacity import retry, stop_after_attempt, wait_exponential, before_log, after_log

logger = logging.getLogger(__name__)

class SheetRecorder:
    """Google Sheet记录器"""
    
    def __init__(self, config):
        self.credentials_file = config.get('google', 'credentials_file')
        self.spreadsheet_id = config.get('google', 'spreadsheet_id')
        self.worksheet_name = config.get('google', 'worksheet_name')
        
        logger.info(f"初始化Google Sheet记录器...")
        logger.info(f"使用凭证文件: {self.credentials_file}")
        logger.info(f"目标表格ID: {self.spreadsheet_id}")
        logger.info(f"工作表名称: {self.worksheet_name}")
        
        # 初始化Google Sheet客户端
        self.client = self._init_client()
        self.worksheet = self._get_worksheet()
        
    def _init_client(self):
        """初始化Google Sheet客户端"""
        try:
            logger.info("开始初始化Google Sheet客户端...")
            
            if not os.path.exists(self.credentials_file):
                raise FileNotFoundError(f"服务账号密钥文件不存在: {self.credentials_file}")
            
            scopes = [
                'https://www.googleapis.com/auth/spreadsheets',
                'https://www.googleapis.com/auth/drive'
            ]
            
            credentials = Credentials.from_service_account_file(
                self.credentials_file,
                scopes=scopes
            )
            
            client = gspread.authorize(credentials)
            logger.info("Google Sheet客户端初始化成功")
            return client
            
        except Exception as e:
            logger.error(f"初始化Google Sheet客户端失败: {str(e)}")
            raise
            
    def _get_worksheet(self):
        """获取或创建工作表"""
        try:
            logger.info(f"尝试打开电子表格: {self.spreadsheet_id}")
            # 打开电子表格
            spreadsheet = self.client.open_by_key(self.spreadsheet_id)
            logger.info("成功打开电子表格")
            
            # 尝试获取工作表
            try:
                logger.info(f"尝试获取工作表: {self.worksheet_name}")
                worksheet = spreadsheet.worksheet(self.worksheet_name)
                logger.info("成功获取工作表")
                
                # 检查并更新表头
                headers = worksheet.row_values(1)
                if '视频播放器' not in headers:
                    logger.info("添加视频播放器列")
                    worksheet.add_cols(1)  # 添加一列
                    headers.append('视频播放器')
                    worksheet.update('A1:F1', [headers])  # 更新表头
                
            except gspread.WorksheetNotFound:
                logger.info(f"工作表 {self.worksheet_name} 不存在，创建新工作表")
                # 如果工作表不存在，创建一个新的
                worksheet = spreadsheet.add_worksheet(
                    title=self.worksheet_name,
                    rows=1000,
                    cols=6  # 增加到6列
                )
                
                # 设置表头
                headers = ['时间', '文件名', '本地路径', '七牛云URL', '文件大小(MB)', '视频播放器']
                worksheet.append_row(headers)
                logger.info("成功创建新工作表并设置表头")
                
            return worksheet
            
        except Exception as e:
            logger.error(f"获取工作表失败: {str(e)}")
            raise

    def _generate_video_player_html(self, url):
        """生成视频播放器HTML代码
        
        Args:
            url: 视频URL
            
        Returns:
            str: 视频播放器HTML代码
        """
        return f'<video controls width="640" src="{url}"></video>'

    @retry(
        stop=stop_after_attempt(3),  # 最多重试3次
        wait=wait_exponential(multiplier=1, min=4, max=10),  # 指数退避重试
        before=before_log(logger, logging.INFO),  # 重试前记录日志
        after=after_log(logger, logging.INFO),    # 重试后记录日志
        reraise=True  # 重试失败后抛出原始异常
    )
    def _append_row(self, row_data):
        """添加一行数据到表格，支持重试
        
        Args:
            row_data: 要添加的数据行
        """
        return self.worksheet.append_row(row_data)
            
    def record(self, local_file, url):
        """记录文件信息到Google Sheet
        
        Args:
            local_file: 本地文件路径
            url: 七牛云文件URL
        """
        try:
            logger.info(f"开始记录文件信息: {local_file}")
            
            # 准备记录数据
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            file_name = os.path.basename(local_file)
            file_size = round(os.path.getsize(local_file) / (1024 * 1024), 2)  # 转换为MB
            video_player = self._generate_video_player_html(url)
            
            # 组装数据行
            row_data = [now, file_name, local_file, url, file_size, video_player]
            logger.info(f"准备写入数据: {row_data}")
            
            # 使用支持重试的方法追加数据到表格
            self._append_row(row_data)
            
            logger.info(f"成功记录文件信息: {file_name}")
            
        except Exception as e:
            logger.error(f"记录文件信息失败: {str(e)}")
            raise

    def view_records(self, limit=10):
        """查看最近的记录
        
        Args:
            limit: 显示最近的记录数量，默认10条
            
        Returns:
            list: 记录列表，每个记录是一个字典
        """
        try:
            # 获取所有记录
            records = self.worksheet.get_all_records()
            
            # 获取最近的记录
            recent_records = records[-limit:] if records else []
            
            # 打印记录
            logger.info(f"\n最近{len(recent_records)}条记录:")
            for record in recent_records:
                logger.info("-" * 80)
                logger.info(f"时间: {record['时间']}")
                logger.info(f"文件名: {record['文件名']}")
                logger.info(f"七牛云URL: {record['七牛云URL']}")
                logger.info(f"文件大小: {record['文件大小(MB)']}MB")
                logger.info(f"视频播放器: {record.get('视频播放器', '无')}")
            
            return recent_records
            
        except Exception as e:
            logger.error(f"获取记录失败: {str(e)}")
            raise 