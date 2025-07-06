import pytest
from django.contrib.auth.models import User
from django.test import TestCase, Client, RequestFactory
from django.urls import reverse
from django.contrib.messages import get_messages
from django.contrib.messages.middleware import MessageMiddleware
from django.contrib.sessions.middleware import SessionMiddleware
from ads.models import Ad
from ads.decorators import ad_author_required


class DecoratorsTest(TestCase):
    """Тесты для декораторов"""
    
    def setUp(self):
        """Настройка тестовых данных"""
        self.client = Client()
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
    
    def test_ad_author_required_decorator_author(self):
        """Тест декоратора для автора объявления"""
        # Создаем простую view функцию для тестирования
        def test_view(request, pk):
            return {'status': 'success', 'pk': pk}
        
        # Применяем декоратор
        decorated_view = ad_author_required(test_view)
        
        # Создаем правильный request объект
        request = self._get_request_with_messages(self.user1)
        
        result = decorated_view(request, self.ad.pk)
        
        # Проверяем, что функция выполнилась успешно
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['pk'], self.ad.pk)
    
    def test_ad_author_required_decorator_not_author(self):
        """Тест декоратора для не автора объявления"""
        # Создаем простую view функцию для тестирования
        def test_view(request, pk):
            return {'status': 'success', 'pk': pk}
        
        # Применяем декоратор
        decorated_view = ad_author_required(test_view)
        
        # Создаем правильный request объект
        request = self._get_request_with_messages(self.user2)
        
        result = decorated_view(request, self.ad.pk)
        
        # Проверяем, что произошел редирект
        self.assertEqual(result.status_code, 302)
        self.assertEqual(result.url, reverse('ad_detail', kwargs={'pk': self.ad.pk}))
        
        # Проверяем сообщение об ошибке
        messages = list(get_messages(request))
        self.assertTrue(any('нет прав' in str(message) for message in messages))
    
    def test_ad_author_required_decorator_nonexistent_ad(self):
        """Тест декоратора для несуществующего объявления"""
        # Создаем простую view функцию для тестирования
        def test_view(request, pk):
            return {'status': 'success', 'pk': pk}
        
        # Применяем декоратор
        decorated_view = ad_author_required(test_view)
        
        # Создаем правильный request объект
        request = self._get_request_with_messages(self.user1)
        
        result = decorated_view(request, 99999)
        
        # Проверяем, что произошел редирект
        self.assertEqual(result.status_code, 302)
        self.assertEqual(result.url, reverse('index'))
        
        # Проверяем сообщение об ошибке
        messages = list(get_messages(request))
        self.assertTrue(any('не найдено' in str(message) for message in messages))
    
    def test_ad_author_required_decorator_unauthenticated(self):
        """Тест декоратора для неавторизованного пользователя"""
        # Создаем простую view функцию для тестирования
        def test_view(request, pk):
            return {'status': 'success', 'pk': pk}
        
        # Применяем декоратор
        decorated_view = ad_author_required(test_view)
        
        # Создаем правильный request объект
        request = self._get_request_with_messages(None)
        
        result = decorated_view(request, self.ad.pk)
        
        # Проверяем, что произошел редирект
        self.assertEqual(result.status_code, 302)
        self.assertEqual(result.url, reverse('ad_detail', kwargs={'pk': self.ad.pk}))
        
        # Проверяем сообщение об ошибке
        messages = list(get_messages(request))
        self.assertTrue(any('нет прав' in str(message) for message in messages))
    
    def test_decorator_preserves_function_metadata(self):
        """Тест сохранения метаданных функции декоратором"""
        def test_view(request, pk):
            """Тестовая функция с документацией"""
            return {'status': 'success'}
        
        # Применяем декоратор
        decorated_view = ad_author_required(test_view)
        
        # Проверяем, что имя и документация сохранены
        self.assertEqual(decorated_view.__name__, 'test_view')
        self.assertIsNotNone(decorated_view.__doc__)
    
    def test_decorator_with_additional_parameters(self):
        """Тест декоратора с дополнительными параметрами"""
        # Создаем view функцию с дополнительными параметрами
        def test_view(request, pk, extra_param=None):
            return {'status': 'success', 'pk': pk, 'extra': extra_param}
        
        # Применяем декоратор
        decorated_view = ad_author_required(test_view)
        
        # Создаем правильный request объект
        request = self._get_request_with_messages(self.user1)
        
        result = decorated_view(request, self.ad.pk, extra_param='test_value')
        
        # Проверяем, что функция выполнилась успешно
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['pk'], self.ad.pk)
        self.assertEqual(result['extra'], 'test_value') 