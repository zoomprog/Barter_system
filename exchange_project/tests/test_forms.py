import pytest
from django.contrib.auth.models import User
from django.test import TestCase
from ads.forms import AdForm, ProposalForm
from ads.models import Ad, ExchangeProposal


class AdFormTest(TestCase):
    """Тесты для формы AdForm"""
    
    def setUp(self):
        """Настройка тестовых данных"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_ad_form_valid_data(self):
        """Тест валидных данных формы объявления"""
        form_data = {
            'title': 'Тестовое объявление',
            'description': 'Описание тестового объявления',
            'category': 'E',
            'condition': 'N',
            'image_url': 'https://example.com/image.jpg'
        }
        form = AdForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_ad_form_invalid_data(self):
        """Тест невалидных данных формы объявления"""
        # Пустой заголовок
        form_data = {
            'title': '',
            'description': 'Описание',
            'category': 'E',
            'condition': 'N'
        }
        form = AdForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)
        
        # Неверная категория
        form_data = {
            'title': 'Заголовок',
            'description': 'Описание',
            'category': 'X',  # Несуществующая категория
            'condition': 'N'
        }
        form = AdForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('category', form.errors)
    
    def test_ad_form_fields(self):
        """Тест полей формы объявления"""
        form = AdForm()
        expected_fields = ['title', 'description', 'image_url', 'category', 'condition']
        self.assertEqual(list(form.fields.keys()), expected_fields)
    
    def test_ad_form_widgets(self):
        """Тест виджетов формы объявления"""
        form = AdForm()
        
        # Проверяем CSS классы виджетов
        self.assertIn('form-control', str(form.fields['title'].widget.attrs.get('class', '')))
        self.assertIn('form-control', str(form.fields['description'].widget.attrs.get('class', '')))
        self.assertIn('form-control', str(form.fields['image_url'].widget.attrs.get('class', '')))
        self.assertIn('form-select', str(form.fields['category'].widget.attrs.get('class', '')))
        self.assertIn('form-select', str(form.fields['condition'].widget.attrs.get('class', '')))


class ProposalFormTest(TestCase):
    """Тесты для формы ProposalForm"""
    
    def setUp(self):
        """Настройка тестовых данных"""
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
    
    def test_proposal_form_valid_data(self):
        """Тест валидных данных формы предложения"""
        form_data = {
            'ad_sender': self.ad1.id,
            'comment': 'Предложение обмена'
        }
        form = ProposalForm(data=form_data, user=self.user1)
        self.assertTrue(form.is_valid())
    
    def test_proposal_form_invalid_data(self):
        """Тест невалидных данных формы предложения"""
        # Пустое поле ad_sender
        form_data = {
            'ad_sender': '',
            'comment': 'Комментарий'
        }
        form = ProposalForm(data=form_data, user=self.user1)
        self.assertFalse(form.is_valid())
        self.assertIn('ad_sender', form.errors)
    
    def test_proposal_form_fields(self):
        """Тест полей формы предложения"""
        form = ProposalForm(user=self.user1)
        expected_fields = ['ad_sender', 'comment']
        self.assertEqual(list(form.fields.keys()), expected_fields)
    
    def test_proposal_form_user_filtering(self):
        """Тест фильтрации объявлений по пользователю"""
        form = ProposalForm(user=self.user1)
        
        # Проверяем, что в queryset только объявления пользователя
        queryset = form.fields['ad_sender'].queryset
        self.assertEqual(queryset.count(), 1)
        self.assertEqual(queryset.first(), self.ad1)
        
        # Проверяем, что объявления другого пользователя не включены
        self.assertNotIn(self.ad2, queryset)
    
    def test_proposal_form_labels_and_help_text(self):
        """Тест меток и подсказок формы"""
        form = ProposalForm(user=self.user1)
        
        # Проверяем метку поля
        self.assertEqual(form.fields['ad_sender'].label, "Мое объявление для обмена")
        
        # Проверяем подсказку
        self.assertIn("Выберите ваше объявление", form.fields['ad_sender'].help_text)
    
    def test_proposal_form_widgets(self):
        """Тест виджетов формы предложения"""
        form = ProposalForm(user=self.user1)
        
        # Проверяем CSS классы виджетов
        self.assertIn('form-select', str(form.fields['ad_sender'].widget.attrs.get('class', '')))
        self.assertIn('form-control', str(form.fields['comment'].widget.attrs.get('class', '')))
        
        # Проверяем rows для textarea
        self.assertEqual(form.fields['comment'].widget.attrs.get('rows'), 3) 