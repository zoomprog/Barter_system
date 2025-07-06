"""
Корневой conftest.py для инициализации Django
"""

import os
import django
from django.conf import settings

# Настройка Django для тестов
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.test_settings')

# Инициализация Django
django.setup()

# Импорт фикстур из приложения
from ads.conftest import * 