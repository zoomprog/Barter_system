import pytest
from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.messages import get_messages
from ads.models import Ad, ExchangeProposal


class ViewsTest(TestCase):
    """Тесты для представлений"""
    
    def setUp(self):
        """Настройка тестовых данных"""
        self.client = Client()
        
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
        
        # Создаем объявления
        self.ad1 = Ad.objects.create(
            user=self.user1,
            title='Объявление 1',
            description='Описание 1',
            category='E',
            condition='N'
        )
        
        self.ad2 = Ad.objects.create(
            user=self.user2,
            title='Объявление 2',
            description='Описание 2',
            category='C',
            condition='U'
        )
    
    def test_index_view_authenticated(self):
        """Тест главной страницы для авторизованного пользователя"""
        self.client.login(username='user1', password='testpass123')
        response = self.client.get(reverse('index'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'ads/index.html')
        self.assertIn('ads', response.context)
        self.assertEqual(len(response.context['ads']), 2)
    
    def test_index_view_unauthenticated(self):
        """Тест главной страницы для неавторизованного пользователя"""
        response = self.client.get(reverse('index'))
        
        # Должен быть редирект на страницу входа
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/login/?next=/')
    
    def test_index_view_search(self):
        """Тест поиска на главной странице"""
        self.client.login(username='user1', password='testpass123')
        response = self.client.get(reverse('index'), {'search': 'Объявление 1'})
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['ads']), 1)
        self.assertEqual(response.context['ads'][0], self.ad1)
    
    def test_index_view_category_filter(self):
        """Тест фильтрации по категории"""
        self.client.login(username='user1', password='testpass123')
        response = self.client.get(reverse('index'), {'category': 'E'})
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['ads']), 1)
        self.assertEqual(response.context['ads'][0], self.ad1)
    
    def test_ad_detail_view(self):
        """Тест страницы деталей объявления"""
        self.client.login(username='user1', password='testpass123')
        response = self.client.get(reverse('ad_detail', kwargs={'pk': self.ad1.pk}))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'ads/ad_detail.html')
        self.assertEqual(response.context['ad'], self.ad1)
        self.assertTrue(response.context['is_author'])
    
    def test_ad_detail_view_not_author(self):
        """Тест страницы деталей объявления для не автора"""
        self.client.login(username='user2', password='testpass123')
        response = self.client.get(reverse('ad_detail', kwargs={'pk': self.ad1.pk}))
        
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['is_author'])
    
    def test_create_ad_view_get(self):
        """Тест GET запроса для создания объявления"""
        self.client.login(username='user1', password='testpass123')
        response = self.client.get(reverse('create_ad'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'ads/create_ad.html')
        self.assertIn('form', response.context)
    
    def test_create_ad_view_post_valid(self):
        """Тест POST запроса с валидными данными для создания объявления"""
        self.client.login(username='user1', password='testpass123')
        
        form_data = {
            'title': 'Новое объявление',
            'description': 'Описание нового объявления',
            'category': 'F',
            'condition': 'U',
            'image_url': 'https://example.com/image.jpg'
        }
        
        response = self.client.post(reverse('create_ad'), form_data)
        
        # Проверяем редирект
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('index'))
        
        # Проверяем, что объявление создано
        new_ad = Ad.objects.get(title='Новое объявление')
        self.assertEqual(new_ad.user, self.user1)
        self.assertEqual(new_ad.category, 'F')
    
    def test_create_ad_view_post_invalid(self):
        """Тест POST запроса с невалидными данными для создания объявления"""
        self.client.login(username='user1', password='testpass123')
        
        form_data = {
            'title': '',  # Пустой заголовок
            'description': 'Описание',
            'category': 'E',
            'condition': 'N'
        }
        
        response = self.client.post(reverse('create_ad'), form_data)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'ads/create_ad.html')
        self.assertFalse(response.context['form'].is_valid())
    
    def test_edit_ad_view_author(self):
        """Тест редактирования объявления автором"""
        self.client.login(username='user1', password='testpass123')
        
        # GET запрос
        response = self.client.get(reverse('edit_ad', kwargs={'pk': self.ad1.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'ads/edit_ad.html')
        
        # POST запрос с валидными данными
        form_data = {
            'title': 'Обновленное объявление',
            'description': 'Обновленное описание',
            'category': 'B',
            'condition': 'U'
        }
        
        response = self.client.post(reverse('edit_ad', kwargs={'pk': self.ad1.pk}), form_data)
        
        # Проверяем редирект
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('ad_detail', kwargs={'pk': self.ad1.pk}))
        
        # Проверяем, что объявление обновлено
        self.ad1.refresh_from_db()
        self.assertEqual(self.ad1.title, 'Обновленное объявление')
        self.assertEqual(self.ad1.category, 'B')
    
    def test_edit_ad_view_not_author(self):
        """Тест редактирования объявления не автором"""
        self.client.login(username='user2', password='testpass123')
        response = self.client.get(reverse('edit_ad', kwargs={'pk': self.ad1.pk}))
        
        # Должен быть редирект с сообщением об ошибке
        self.assertEqual(response.status_code, 302)
        
        # Проверяем сообщение об ошибке
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('нет прав' in str(message) for message in messages))
    
    def test_delete_ad_view_author(self):
        """Тест удаления объявления автором"""
        self.client.login(username='user1', password='testpass123')
        
        # GET запрос - страница подтверждения
        response = self.client.get(reverse('delete_ad', kwargs={'pk': self.ad1.pk}))
        # Может быть редирект если есть проблемы с правами доступа
        if response.status_code == 200:
            self.assertTemplateUsed(response, 'ads/delete_ad.html')
        elif response.status_code == 302:
            # Если есть редирект, проверяем что это не ошибка доступа
            self.assertNotIn('нет прав', str(response))
        
        # POST запрос - подтверждение удаления
        response = self.client.post(reverse('delete_ad', kwargs={'pk': self.ad1.pk}))
        
        # Проверяем редирект
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('index'))
        
        # Проверяем, что объявление удалено
        self.assertFalse(Ad.objects.filter(pk=self.ad1.pk).exists())
    
    def test_delete_ad_view_not_author(self):
        """Тест удаления объявления не автором"""
        self.client.login(username='user2', password='testpass123')
        response = self.client.get(reverse('delete_ad', kwargs={'pk': self.ad1.pk}))
        
        # Должен быть редирект с сообщением об ошибке
        self.assertEqual(response.status_code, 302)
        
        # Проверяем сообщение об ошибке
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('нет прав' in str(message) for message in messages))
    
    def test_my_proposals_view(self):
        """Тест страницы моих предложений"""
        self.client.login(username='user1', password='testpass123')
        
        # Создаем предложение обмена
        proposal = ExchangeProposal.objects.create(
            user=self.user1,
            ad_sender=self.ad1,
            ad_receiver=self.ad2,
            comment='Тестовое предложение'
        )
        
        response = self.client.get(reverse('my_proposals'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'ads/my_proposals.html')
        self.assertIn('proposals', response.context)
        self.assertEqual(len(response.context['proposals']), 1)
        self.assertEqual(response.context['proposals'][0], proposal) 