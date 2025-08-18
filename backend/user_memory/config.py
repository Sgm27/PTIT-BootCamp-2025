#!/usr/bin/env python3
"""
Configuration for User Memory System
"""
import os

# Base directory for user memory
USER_MEMORY_DIR = os.path.join(os.path.dirname(__file__))

# Memory file path
USER_MEMORY_FILE = os.path.join(USER_MEMORY_DIR, 'user_memory.txt')

# Backup directory
BACKUP_DIR = os.path.join(USER_MEMORY_DIR, 'backups')

# Maximum file size (in bytes) before warning
MAX_FILE_SIZE = 1024 * 1024  # 1MB

# Maximum number of entries before cleanup
MAX_ENTRIES = 1000

# Backup frequency (in days)
BACKUP_FREQUENCY_DAYS = 7

# Memory categories for better organization
MEMORY_CATEGORIES = {
    'health': 'Thông tin sức khỏe',
    'medication': 'Thuốc men',
    'preferences': 'Sở thích và thói quen',
    'family': 'Thông tin gia đình',
    'medical_history': 'Lịch sử bệnh',
    'lifestyle': 'Lối sống',
    'other': 'Thông tin khác'
}

# File encoding
FILE_ENCODING = 'utf-8'

# Timestamp format
TIMESTAMP_FORMAT = '%Y-%m-%d %H:%M:%S'

# Logging configuration
LOG_LEVEL = 'INFO'
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s' 