import pytest
from django.contrib.auth.models import User
from django.test import Client
from .models import Ad, ExchangeProposal


@pytest.fixture
def user1():
    """Фикстура для создания первого пользователя"""
    return User.objects.create_user(
        username='user1',
        email='user1@example.com',
        password='testpass123'
    )


@pytest.fixture
def user2():
    """Фикстура для создания второго пользователя"""
    return User.objects.create_user(
        username='user2',
        email='user2@example.com',
        password='testpass123'
    )


@pytest.fixture
def ad1(user1):
    """Фикстура для создания первого объявления"""
    return Ad.objects.create(
        user=user1,
        title='Объявление 1',
        description='Описание объявления 1',
        category='E',
        condition='N',
        image_url='https://example.com/image1.jpg'
    )


@pytest.fixture
def ad2(user2):
    """Фикстура для создания второго объявления"""
    return Ad.objects.create(
        user=user2,
        title='Объявление 2',
        description='Описание объявления 2',
        category='C',
        condition='U',
        image_url='https://example.com/image2.jpg'
    )


@pytest.fixture
def proposal(user1, ad1, ad2):
    """Фикстура для создания предложения обмена"""
    return ExchangeProposal.objects.create(
        user=user1,
        ad_sender=ad1,
        ad_receiver=ad2,
        comment='Тестовое предложение обмена',
        status='P'
    )


@pytest.fixture
def multiple_ads(user1):
    """Фикстура для создания нескольких объявлений"""
    ads = []
    categories = ['E', 'C', 'F', 'B', 'O']
    conditions = ['N', 'U']
    
    for i in range(10):
        ad = Ad.objects.create(
            user=user1,
            title=f'Объявление {i}',
            description=f'Описание объявления {i}',
            category=categories[i % len(categories)],
            condition=conditions[i % len(conditions)],
            image_url=f'https://example.com/image{i}.jpg'
        )
        ads.append(ad)
    
    return ads


@pytest.fixture
def valid_ad_data():
    """Фикстура с валидными данными для создания объявления"""
    return {
        'title': 'Тестовое объявление',
        'description': 'Описание тестового объявления',
        'category': 'E',
        'condition': 'N',
        'image_url': 'https://example.com/image.jpg'
    }


@pytest.fixture
def invalid_ad_data():
    """Фикстура с невалидными данными для создания объявления"""
    return {
        'title': '',  # Пустой заголовок
        'description': 'Описание',
        'category': 'X',  # Несуществующая категория
        'condition': 'N'
    }


@pytest.fixture
def valid_proposal_data(ad1):
    """Фикстура с валидными данными для создания предложения"""
    return {
        'ad_sender': ad1.id,
        'comment': 'Тестовое предложение обмена'
    }


@pytest.fixture
def invalid_proposal_data():
    """Фикстура с невалидными данными для создания предложения"""
    return {
        'ad_sender': '',  # Пустое поле
        'comment': 'Комментарий'
    }


@pytest.fixture
def authenticated_client(client, user1):
    """Фикстура для авторизованного клиента"""
    client.login(username='user1', password='testpass123')
    return client


@pytest.fixture
def unauthenticated_client(client):
    """Фикстура для неавторизованного клиента"""
    return client 