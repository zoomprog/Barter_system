import pytest
from django.urls import reverse
from ads.models import Ad, ExchangeProposal


@pytest.mark.django_db
@pytest.mark.models
class TestModelsWithFixtures:
    """Пример тестов моделей с использованием фикстур"""
    
    def test_ad_creation_with_fixture(self, user1, ad1):
        """Тест создания объявления с использованием фикстур"""
        assert ad1.user == user1
        assert ad1.title == 'Объявление 1'
        assert ad1.category == 'E'
        assert ad1.condition == 'N'
    
    def test_proposal_creation_with_fixtures(self, user1, ad1, ad2, proposal):
        """Тест создания предложения с использованием фикстур"""
        assert proposal.user == user1
        assert proposal.ad_sender == ad1
        assert proposal.ad_receiver == ad2
        assert proposal.status == 'P'
        assert proposal.comment == 'Тестовое предложение обмена'
    
    def test_multiple_ads_creation(self, multiple_ads):
        """Тест создания нескольких объявлений"""
        assert len(multiple_ads) == 10
        assert all(isinstance(ad, Ad) for ad in multiple_ads)
        
        # Проверяем, что все объявления имеют разные заголовки
        titles = [ad.title for ad in multiple_ads]
        assert len(set(titles)) == 10


@pytest.mark.django_db
@pytest.mark.views
class TestViewsWithFixtures:
    """Пример тестов представлений с использованием фикстур"""
    
    def test_index_view_authenticated(self, authenticated_client, ad1, ad2):
        """Тест главной страницы для авторизованного пользователя"""
        response = authenticated_client.get(reverse('index'))
        
        assert response.status_code == 200
        assert 'ads' in response.context
        assert len(response.context['ads']) == 2
        assert ad1 in response.context['ads']
        assert ad2 in response.context['ads']
    
    def test_index_view_unauthenticated(self, unauthenticated_client):
        """Тест главной страницы для неавторизованного пользователя"""
        response = unauthenticated_client.get(reverse('index'))
        
        assert response.status_code == 302
        assert response.url.startswith('/login/')
    
    def test_ad_detail_view(self, authenticated_client, ad1):
        """Тест страницы деталей объявления"""
        response = authenticated_client.get(reverse('ad_detail', kwargs={'pk': ad1.pk}))
        
        assert response.status_code == 200
        assert response.context['ad'] == ad1
        assert response.context['is_author'] is True
    
    def test_create_ad_view_valid_data(self, authenticated_client, valid_ad_data):
        """Тест создания объявления с валидными данными"""
        response = authenticated_client.post(reverse('create_ad'), valid_ad_data)
        
        assert response.status_code == 302
        assert response.url == reverse('index')
        
        # Проверяем, что объявление создано
        ad = Ad.objects.get(title=valid_ad_data['title'])
        assert ad.description == valid_ad_data['description']
        assert ad.category == valid_ad_data['category']
    
    def test_create_ad_view_invalid_data(self, authenticated_client, invalid_ad_data):
        """Тест создания объявления с невалидными данными"""
        response = authenticated_client.post(reverse('create_ad'), invalid_ad_data)
        
        assert response.status_code == 200
        assert not response.context['form'].is_valid()


@pytest.mark.django_db
@pytest.mark.forms
class TestFormsWithFixtures:
    """Пример тестов форм с использованием фикстур"""
    
    def test_ad_form_valid_data(self, valid_ad_data):
        """Тест формы объявления с валидными данными"""
        from ads.forms import AdForm
        form = AdForm(data=valid_ad_data)
        assert form.is_valid()
    
    def test_ad_form_invalid_data(self, invalid_ad_data):
        """Тест формы объявления с невалидными данными"""
        from ads.forms import AdForm
        form = AdForm(data=invalid_ad_data)
        assert not form.is_valid()
        assert 'title' in form.errors
        assert 'category' in form.errors
    
    def test_proposal_form_valid_data(self, valid_proposal_data):
        """Тест формы предложения с валидными данными"""
        from ads.forms import ProposalForm
        form = ProposalForm(data=valid_proposal_data)
        assert form.is_valid()
    
    def test_proposal_form_invalid_data(self, invalid_proposal_data):
        """Тест формы предложения с невалидными данными"""
        from ads.forms import ProposalForm
        form = ProposalForm(data=invalid_proposal_data)
        assert not form.is_valid()
        assert 'ad_sender' in form.errors


@pytest.mark.django_db
@pytest.mark.integration
class TestIntegrationWithFixtures:
    """Пример интеграционных тестов с использованием фикстур"""
    
    def test_full_workflow(self, authenticated_client, user2, ad1, ad2, valid_proposal_data):
        """Тест полного рабочего процесса"""
        # 1. Пользователь 1 отправляет предложение пользователю 2
        response = authenticated_client.post(
            reverse('ad_detail', kwargs={'pk': ad2.pk}), 
            valid_proposal_data
        )
        assert response.status_code == 302
        
        # Проверяем, что предложение создано
        proposal = ExchangeProposal.objects.get(
            user=ad1.user,
            ad_sender=ad1,
            ad_receiver=ad2
        )
        assert proposal.status == 'P'
        
        # 2. Пользователь 2 авторизуется и принимает предложение
        authenticated_client.login(username='user2', password='testpass123')
        response = authenticated_client.post(
            reverse('update_proposal_status', kwargs={'pk': proposal.pk}),
            {'status': 'A'}
        )
        assert response.status_code == 302
        
        # Проверяем, что статус обновлен
        proposal.refresh_from_db()
        assert proposal.status == 'A'
    
    def test_search_and_filter(self, authenticated_client, multiple_ads):
        """Тест поиска и фильтрации с множественными объявлениями"""
        # Тест поиска
        response = authenticated_client.get(reverse('index'), {'search': 'Объявление 0'})
        assert response.status_code == 200
        assert len(response.context['ads']) == 1
        
        # Тест фильтрации по категории
        response = authenticated_client.get(reverse('index'), {'category': 'E'})
        assert response.status_code == 200
        assert len(response.context['ads']) == 2  # Объявления 0 и 5
        
        # Тест фильтрации по состоянию
        response = authenticated_client.get(reverse('index'), {'condition': 'N'})
        assert response.status_code == 200
        assert len(response.context['ads']) == 5  # Объявления с четными индексами 