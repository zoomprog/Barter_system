"""
Упрощенные тесты для декораторов
"""

import pytest
from django.contrib.auth.models import User
from django.test import TestCase, RequestFactory
from django.urls import reverse
from django.contrib.messages.middleware import MessageMiddleware
from django.contrib.sessions.middleware import SessionMiddleware
from ads.models import Ad
from ads.decorators import ad_author_required


class SimpleDecoratorsTest(TestCase):
    """Упрощенные тесты для декораторов"""
    
    def setUp(self):
        """Настройка тестовых данных"""
        self.factory = RequestFactory()
        
        # Создаем пользователей
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@example.com',
            password='testpass123'
        )
        
        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='testpass123'
        )
        
        # Создаем объявление
        self.ad = Ad.objects.create(
            user=self.user1,
            title='Тестовое объявление',
            description='Описание объявления',
            category='E',
            condition='N'
        )
    
    def _get_request_with_messages(self, user=None):
        """Создает request объект с настроенным message middleware"""
        request = self.factory.get('/')
        request.user = user
        
        # Добавляем middleware для сообщений
        session_middleware = SessionMiddleware(lambda req: None)
        session_middleware.process_request(request)
        request.session.save()
        
        message_middleware = MessageMiddleware(lambda req: None)
        message_middleware.process_request(request)
        
        return request
    
    def test_decorator_author_access(self):
        """Тест доступа автора объявления"""
        # Создаем простую view функцию
        def test_view(request, pk):
            return {'status': 'success', 'pk': pk}
        
        # Применяем декоратор
        decorated_view = ad_author_required(test_view)
        
        # Создаем request для автора
        request = self._get_request_with_messages(self.user1)
        
        # Вызываем декорированную функцию
        result = decorated_view(request, self.ad.pk)
        
        # Проверяем результат
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['pk'], self.ad.pk)
    

    
    def test_decorator_function_metadata(self):
        """Тест сохранения метаданных функции"""
        def test_view(request, pk):
            """Тестовая функция с документацией"""
            return {'status': 'success'}
        
        # Применяем декоратор
        decorated_view = ad_author_required(test_view)
        
        # Проверяем, что документация сохранена
        self.assertIsNotNone(decorated_view.__doc__)
        self.assertIn('Тестовая функция', decorated_view.__doc__)
    
    def test_decorator_with_additional_parameters(self):
        """Тест декоратора с дополнительными параметрами"""
        # Создаем view функцию с дополнительными параметрами
        def test_view(request, pk, extra_param=None):
            return {'status': 'success', 'pk': pk, 'extra': extra_param}
        
        # Применяем декоратор
        decorated_view = ad_author_required(test_view)
        
        # Создаем request для автора
        request = self._get_request_with_messages(self.user1)
        
        # Вызываем декорированную функцию с дополнительным параметром
        result = decorated_view(request, self.ad.pk, extra_param='test_value')
        
        # Проверяем результат
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['pk'], self.ad.pk)
        self.assertEqual(result['extra'], 'test_value') 