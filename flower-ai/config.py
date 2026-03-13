"""
Flower AI Configuration
"""

import os

# API Configuration
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "your-api-key-here")
MODEL = "gpt-4o-mini"

# Application Configuration
APP_NAME = "Flower AI v8"
APP_VERSION = "8.0.0"

# Logging
LOG_DIR = os.path.join(os.path.dirname(__file__), "logs")
LOG_FILE = os.path.join(LOG_DIR, "flower.log")

# Memory and Learning
MEMORY_MAX_SIZE = 1000
EMOTION_UPDATE_INTERVAL = 3000  # ms

# System Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BRAIN_PATH = os.path.join(BASE_DIR, "brain")
MEMORY_PATH = os.path.join(BASE_DIR, "memory")