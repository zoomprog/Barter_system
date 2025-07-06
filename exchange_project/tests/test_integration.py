import pytest
from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.messages import get_messages
from ads.models import Ad, ExchangeProposal


class IntegrationTest(TestCase):
    """Интеграционные тесты для проверки полного цикла работы приложения"""
    
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
    
    @pytest.mark.integration
    def test_full_ad_lifecycle(self):
        """Тест полного жизненного цикла объявления"""
        # 1. Авторизация пользователя
        self.client.login(username='user1', password='testpass123')
        
        # 2. Создание объявления
        ad_data = {
            'title': 'Тестовое объявление',
            'description': 'Описание объявления',
            'category': 'E',
            'condition': 'N',
            'image_url': 'https://example.com/image.jpg'
        }
        
        response = self.client.post(reverse('create_ad'), ad_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('index'))
        
        # Проверяем, что объявление создано
        ad = Ad.objects.get(title='Тестовое объявление')
        self.assertEqual(ad.user, self.user1)
        self.assertEqual(ad.category, 'E')
        
        # 3. Просмотр объявления
        response = self.client.get(reverse('ad_detail', kwargs={'pk': ad.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['ad'], ad)
        self.assertTrue(response.context['is_author'])
        
        # 4. Редактирование объявления
        edit_data = {
            'title': 'Обновленное объявление',
            'description': 'Обновленное описание',
            'category': 'C',
            'condition': 'U'
        }
        
        response = self.client.post(reverse('edit_ad', kwargs={'pk': ad.pk}), edit_data)
        self.assertEqual(response.status_code, 302)
        
        # Проверяем, что объявление обновлено
        ad.refresh_from_db()
        self.assertEqual(ad.title, 'Обновленное объявление')
        self.assertEqual(ad.category, 'C')
        
        # 5. Удаление объявления
        response = self.client.post(reverse('delete_ad', kwargs={'pk': ad.pk}))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('index'))
        
        # Проверяем, что объявление удалено
        self.assertFalse(Ad.objects.filter(pk=ad.pk).exists())
    
    @pytest.mark.integration
    def test_exchange_proposal_workflow(self):
        """Тест рабочего процесса предложения обмена"""
        # Создаем объявления для двух пользователей
        ad1 = Ad.objects.create(
            user=self.user1,
            title='Объявление пользователя 1',
            description='Описание 1',
            category='E',
            condition='N'
        )
        
        ad2 = Ad.objects.create(
            user=self.user2,
            title='Объявление пользователя 2',
            description='Описание 2',
            category='C',
            condition='U'
        )
        
        # 1. Пользователь 1 авторизуется и отправляет предложение
        self.client.login(username='user1', password='testpass123')
        
        proposal_data = {
            'ad_sender': ad1.id,
            'comment': 'Предложение обмена'
        }
        
        response = self.client.post(reverse('ad_detail', kwargs={'pk': ad2.pk}), proposal_data)
        self.assertEqual(response.status_code, 302)
        
        # Проверяем, что предложение создано
        proposal = ExchangeProposal.objects.get(
            user=self.user1,
            ad_sender=ad1,
            ad_receiver=ad2
        )
        self.assertEqual(proposal.status, 'P')
        self.assertEqual(proposal.comment, 'Предложение обмена')
        
        # 2. Пользователь 1 просматривает свои предложения
        response = self.client.get(reverse('my_proposals'))
        self.assertEqual(response.status_code, 200)
        self.assertIn(proposal, response.context['proposals'])
        
        # 3. Пользователь 2 авторизуется и просматривает полученные предложения
        self.client.login(username='user2', password='testpass123')
        
        response = self.client.get(reverse('my_proposals'))
        self.assertEqual(response.status_code, 200)
        self.assertIn(proposal, response.context['proposals'])
        
        # 4. Пользователь 2 принимает предложение
        response = self.client.post(reverse('update_proposal_status', kwargs={'pk': proposal.pk}), {
            'status': 'A'
        })
        self.assertEqual(response.status_code, 302)
        
        # Проверяем, что статус обновлен
        proposal.refresh_from_db()
        self.assertEqual(proposal.status, 'A')
    
    @pytest.mark.integration
    def test_search_and_filter_functionality(self):
        """Тест функциональности поиска и фильтрации"""
        # Создаем несколько объявлений
        ad1 = Ad.objects.create(
            user=self.user1,
            title='Электроника',
            description='Смартфон',
            category='E',
            condition='N'
        )
        
        ad2 = Ad.objects.create(
            user=self.user2,
            title='Одежда',
            description='Куртка',
            category='C',
            condition='U'
        )
        
        ad3 = Ad.objects.create(
            user=self.user1,
            title='Книга',
            description='Учебник',
            category='B',
            condition='N'
        )
        
        self.client.login(username='user1', password='testpass123')
        
        # 1. Тест поиска по ключевому слову
        response = self.client.get(reverse('index'), {'search': 'Электроника'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['ads']), 1)
        self.assertEqual(response.context['ads'][0], ad1)
        
        # 2. Тест фильтрации по категории
        response = self.client.get(reverse('index'), {'category': 'E'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['ads']), 1)
        self.assertEqual(response.context['ads'][0], ad1)
        
        # 3. Тест фильтрации по состоянию
        response = self.client.get(reverse('index'), {'condition': 'N'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['ads']), 2)  # ad1 и ad3
        
        # 4. Тест комбинированной фильтрации
        response = self.client.get(reverse('index'), {
            'search': 'Книга',
            'category': 'B',
            'condition': 'N'
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['ads']), 1)
        self.assertEqual(response.context['ads'][0], ad3)
    
    @pytest.mark.integration
    def test_unauthorized_access_restrictions(self):
        """Тест ограничений доступа для неавторизованных пользователей"""
        # Создаем объявление
        ad = Ad.objects.create(
            user=self.user1,
            title='Тестовое объявление',
            description='Описание',
            category='E',
            condition='N'
        )
        
        # 1. Попытка доступа к главной странице без авторизации
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/login/?next=/')
        
        # 2. Попытка создания объявления без авторизации
        response = self.client.get(reverse('create_ad'))
        self.assertEqual(response.status_code, 302)
        
        # 3. Попытка редактирования объявления без авторизации
        response = self.client.get(reverse('edit_ad', kwargs={'pk': ad.pk}))
        self.assertEqual(response.status_code, 302)
        
        # 4. Попытка удаления объявления без авторизации
        response = self.client.get(reverse('delete_ad', kwargs={'pk': ad.pk}))
        self.assertEqual(response.status_code, 302)
    
    @pytest.mark.integration
    def test_cross_user_access_restrictions(self):
        """Тест ограничений доступа между пользователями"""
        # Создаем объявление для пользователя 1
        ad = Ad.objects.create(
            user=self.user1,
            title='Объявление пользователя 1',
            description='Описание',
            category='E',
            condition='N'
        )
        
        # Пользователь 2 пытается редактировать объявление пользователя 1
        self.client.login(username='user2', password='testpass123')
        
        response = self.client.get(reverse('edit_ad', kwargs={'pk': ad.pk}))
        self.assertEqual(response.status_code, 302)
        
        # Проверяем сообщение об ошибке
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('нет прав' in str(message) for message in messages))
        
        # Пользователь 2 пытается удалить объявление пользователя 1
        response = self.client.get(reverse('delete_ad', kwargs={'pk': ad.pk}))
        self.assertEqual(response.status_code, 302)
        
        # Проверяем, что объявление не удалено
        self.assertTrue(Ad.objects.filter(pk=ad.pk).exists())
    
    @pytest.mark.integration
    def test_pagination_functionality(self):
        """Тест функциональности пагинации"""
        # Создаем много объявлений для тестирования пагинации
        for i in range(15):
            Ad.objects.create(
                user=self.user1,
                title=f'Объявление {i}',
                description=f'Описание {i}',
                category='E',
                condition='N'
            )
        
        self.client.login(username='user1', password='testpass123')
        
        # 1. Тест первой страницы
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['ads']), 10)  # 10 объявлений на страницу
        
        # 2. Тест второй страницы
        response = self.client.get(reverse('index'), {'page': 2})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['ads']), 5)  # Оставшиеся 5 объявлений
        
        # 3. Тест несуществующей страницы
        response = self.client.get(reverse('index'), {'page': 999})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['ads']), 5)  # Должна показаться последняя страница
        
        # 4. Тест некорректного номера страницы
        response = self.client.get(reverse('index'), {'page': 'abc'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['ads']), 10)  # Должна показаться первая страница 