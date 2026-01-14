#!/usr/bin/env python
"""
会议聊天室 - 主入口文件

运行方式：
    streamlit run meeting_app.py
"""

from src.ui.meeting_app import create_meeting_app

if __name__ == "__main__":
    create_meeting_app()
