"""
Простой тест для проверки работоспособности pytest с Django
"""

import pytest
from django.test import TestCase
from django.contrib.auth.models import User
from ads.models import Ad


class SimpleTest(TestCase):
    """Простой тест для проверки базовой функциональности"""
    
    def test_django_works(self):
        """Тест что Django работает"""
        self.assertTrue(True)
    
    def test_can_create_user(self):
        """Тест создания пользователя"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@example.com')
    
    def test_can_create_ad(self):
        """Тест создания объявления"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        ad = Ad.objects.create(
            user=user,
            title='Тестовое объявление',
            description='Описание',
            category='E',
            condition='N'
        )
        
        self.assertEqual(ad.title, 'Тестовое объявление')
        self.assertEqual(ad.user, user)
        self.assertEqual(ad.category, 'E')


@pytest.mark.django_db
def test_pytest_with_django():
    """Тест pytest с Django"""
    user = User.objects.create_user(
        username='pytestuser',
        email='pytest@example.com',
        password='testpass123'
    )
    
    ad = Ad.objects.create(
        user=user,
        title='Pytest объявление',
        description='Описание',
        category='C',
        condition='U'
    )
    
    assert ad.title == 'Pytest объявление'
    assert ad.user == user
    assert ad.category == 'C' 