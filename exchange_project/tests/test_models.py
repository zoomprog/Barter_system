import pytest
from django.contrib.auth.models import User
from django.test import TestCase
from ads.models import Ad, ExchangeProposal


class AdModelTest(TestCase):
    """Тесты для модели Ad"""
    
    def setUp(self):
        """Настройка тестовых данных"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.ad = Ad.objects.create(
            user=self.user,
            title='Тестовое объявление',
            description='Описание тестового объявления',
            category='E',
            condition='N',
            image_url='https://example.com/image.jpg'
        )
    
    def test_ad_creation(self):
        """Тест создания объявления"""
        self.assertEqual(self.ad.title, 'Тестовое объявление')
        self.assertEqual(self.ad.user, self.user)
        self.assertEqual(self.ad.category, 'E')
        self.assertEqual(self.ad.condition, 'N')
        self.assertEqual(str(self.ad), 'Тестовое объявление')
    
    def test_ad_categories(self):
        """Тест доступных категорий"""
        categories = dict(Ad.CATEGORIES)
        self.assertIn('E', categories)
        self.assertIn('C', categories)
        self.assertIn('F', categories)
        self.assertIn('B', categories)
        self.assertIn('O', categories)
    
    def test_ad_conditions(self):
        """Тест доступных состояний"""
        conditions = dict(Ad.CONDITIONS)
        self.assertIn('N', conditions)
        self.assertIn('U', conditions)


class ExchangeProposalModelTest(TestCase):
    """Тесты для модели ExchangeProposal"""
    
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
        
        self.proposal = ExchangeProposal.objects.create(
            user=self.user1,
            ad_sender=self.ad1,
            ad_receiver=self.ad2,
            comment='Предложение обмена',
            status='P'
        )
    
    def test_proposal_creation(self):
        """Тест создания предложения обмена"""
        self.assertEqual(self.proposal.user, self.user1)
        self.assertEqual(self.proposal.ad_sender, self.ad1)
        self.assertEqual(self.proposal.ad_receiver, self.ad2)
        self.assertEqual(self.proposal.status, 'P')
        self.assertEqual(self.proposal.comment, 'Предложение обмена')
    
    def test_proposal_str_representation(self):
        """Тест строкового представления предложения"""
        expected_str = f"Proposal from {self.ad1} to {self.ad2}"
        self.assertEqual(str(self.proposal), expected_str)
    
    def test_proposal_status_choices(self):
        """Тест доступных статусов предложений"""
        status_choices = dict(ExchangeProposal.STATUS_CHOICES)
        self.assertIn('P', status_choices)  # Pending
        self.assertIn('A', status_choices)  # Accepted
        self.assertIn('R', status_choices)  # Rejected
    
    def test_proposal_status_display_ru(self):
        """Тест русского отображения статусов"""
        self.assertEqual(self.proposal.get_status_display_ru(), 'Ожидает')
        
        # Тестируем другие статусы
        self.proposal.status = 'A'
        self.assertEqual(self.proposal.get_status_display_ru(), 'Принято')
        
        self.proposal.status = 'R'
        self.assertEqual(self.proposal.get_status_display_ru(), 'Отклонено')
    
    def test_proposal_ordering(self):
        """Тест сортировки предложений по дате создания"""
        # Проверяем, что предложения отсортированы по убыванию даты создания
        proposals = ExchangeProposal.objects.all()
        
        # Проверяем, что есть хотя бы одно предложение
        self.assertGreaterEqual(len(proposals), 1)
        
        # Проверяем, что предложения отсортированы правильно
        # (более новые первыми, согласно Meta.ordering = ['-created_at'])
        for i in range(len(proposals) - 1):
            self.assertGreaterEqual(proposals[i].created_at, proposals[i + 1].created_at) 