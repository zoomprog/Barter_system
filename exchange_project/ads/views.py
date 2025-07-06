from django.shortcuts import render, get_object_or_404, redirect
from .models import Ad, ExchangeProposal
from .forms import AdForm, ProposalForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.views import generic
from django.urls import reverse_lazy
from django.http import Http404
from django.contrib import messages
from .decorators import ad_author_required
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

class SignUpView(generic.CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'ads/signup.html'

@login_required
def index(request):
    """
    Главная страница с поиском, фильтрацией и пагинацией объявлений
    """
    # Получаем параметры поиска и фильтрации из GET-запроса
    search_query = request.GET.get('search', '')
    category_filter = request.GET.get('category', '')
    condition_filter = request.GET.get('condition', '')
    
    # Начинаем с базового QuerySet
    ads = Ad.objects.all().order_by('-created_at')
    
    # Применяем поиск по ключевым словам
    if search_query:
        ads = ads.filter(
            Q(title__icontains=search_query) | 
            Q(description__icontains=search_query)
        )
    
    # Применяем фильтр по категории
    if category_filter:
        ads = ads.filter(category=category_filter)
    
    # Применяем фильтр по состоянию
    if condition_filter:
        ads = ads.filter(condition=condition_filter)
    
    # Пагинация
    paginator = Paginator(ads, 10)  # 10 объявлений на страницу
    page = request.GET.get('page')
    
    try:
        ads_page = paginator.page(page)
    except PageNotAnInteger:
        # Если страница не является числом, показываем первую страницу
        ads_page = paginator.page(1)
    except EmptyPage:
        # Если страница больше максимальной, показываем последнюю страницу
        ads_page = paginator.page(paginator.num_pages)
    
    # Подготавливаем контекст для фильтров
    context = {
        'ads': ads_page,
        'search_query': search_query,
        'category_filter': category_filter,
        'condition_filter': condition_filter,
        'categories': Ad.CATEGORIES,
        'conditions': Ad.CONDITIONS,
        'total_results': ads.count(),
        'has_filters': bool(search_query or category_filter or condition_filter)
    }
    
    return render(request, 'ads/index.html', context)


# В views.py - исправляем логику
@login_required
def ad_detail(request, pk):
    ad = get_object_or_404(Ad, pk=pk)
    is_author = ad.user == request.user

    if request.method == 'POST':
        if is_author:
            messages.error(request, "Вы не можете отправить предложение обмена самому себе.")
            return redirect('ad_detail', pk=pk)

        form = ProposalForm(request.POST)
        if form.is_valid():
            proposal = form.save(commit=False)
            proposal.ad_receiver = ad  # Объявление, на которое хотят обменять
            proposal.ad_sender = form.cleaned_data['ad_sender']  # Объявление пользователя
            proposal.user = request.user
            proposal.save()
            messages.success(request, "Предложение обмена отправлено!")
            return redirect('ad_detail', pk=pk)
    else:
        # Показываем только объявления текущего пользователя
        user_ads = Ad.objects.filter(user=request.user)
        form = ProposalForm()
        form.fields['ad_sender'].queryset = user_ads

    return render(request, 'ads/ad_detail.html', {
        'ad': ad,
        'form': form,
        'is_author': is_author
    })

@login_required
def create_ad(request):
    if request.method == 'POST':
        form = AdForm(request.POST)
        if form.is_valid():
            ad = form.save(commit=False)
            ad.user = request.user
            ad.save()
            return redirect('index')
    else:
        form = AdForm()
    return render(request, 'ads/create_ad.html', {'form': form})

@login_required
@ad_author_required
def edit_ad(request, pk):
    """
    Редактирование объявления с проверкой прав через декоратор
    """
    ad = Ad.objects.get(pk=pk)  # Уже проверено в декораторе
    if request.method == 'POST':
        form = AdForm(request.POST, instance=ad)
        if form.is_valid():
            form.save()
            messages.success(request, "Объявление успешно обновлено!")
            return redirect('ad_detail', pk=pk)
        else:
            messages.error(request, "Пожалуйста, исправьте ошибки в форме.")
    else:
        form = AdForm(instance=ad)

    return render(request, 'ads/edit_ad.html', {'form': form, 'ad': ad})

@login_required
@ad_author_required
def delete_ad(request, pk):
    """
    Удаление объявления с проверкой прав через декоратор
    """
    try:
        ad = Ad.objects.get(pk=pk)
        ad_title = ad.title  # Сохраняем название для сообщения
        
        if request.method == 'POST':
            # Подтверждение удаления
            # Удаляем связанные предложения обмена
            ExchangeProposal.objects.filter(ad_sender=ad).delete()
            ExchangeProposal.objects.filter(ad_receiver=ad).delete()
            
            # Удаляем само объявление
            ad.delete()
            messages.success(request, f"Объявление '{ad_title}' и все связанные предложения обмена успешно удалены!")
            return redirect('index')
        else:
            # Показываем страницу подтверждения
            # Подсчитываем количество связанных предложений
            sent_proposals_count = ExchangeProposal.objects.filter(ad_sender=ad).count()
            received_proposals_count = ExchangeProposal.objects.filter(ad_receiver=ad).count()
            total_proposals = sent_proposals_count + received_proposals_count
            
            return render(request, 'ads/delete_ad.html', {
                'ad': ad,
                'total_proposals': total_proposals,
                'sent_proposals_count': sent_proposals_count,
                'received_proposals_count': received_proposals_count
            })
            
    except Ad.DoesNotExist:
        messages.error(request, "Объявление не найдено.")
        return redirect('index')
    except Exception as e:
        messages.error(request, f"Произошла ошибка при удалении объявления: {str(e)}")
        return redirect('ad_detail', pk=pk)

@login_required
def my_proposals(request):
    """
    Просмотр предложений обмена пользователя
    """
    # Получаем параметры фильтрации
    status_filter = request.GET.get('status', '')
    proposal_type = request.GET.get('type', '')  # sent или received
    
    # Базовый QuerySet
    if proposal_type == 'sent':
        proposals = ExchangeProposal.objects.filter(user=request.user)
        title = "Мои отправленные предложения"
    elif proposal_type == 'received':
        proposals = ExchangeProposal.objects.filter(ad_receiver__user=request.user)
        title = "Полученные предложения"
    else:
        # Показываем все предложения пользователя
        proposals = ExchangeProposal.objects.filter(
            Q(user=request.user) | Q(ad_receiver__user=request.user)
        )
        title = "Все предложения обмена"
    
    # Фильтрация по статусу
    if status_filter:
        proposals = proposals.filter(status=status_filter)
    
    # Пагинация
    paginator = Paginator(proposals, 10)
    page = request.GET.get('page')
    
    try:
        proposals_page = paginator.page(page)
    except PageNotAnInteger:
        proposals_page = paginator.page(1)
    except EmptyPage:
        proposals_page = paginator.page(paginator.num_pages)
    
    context = {
        'proposals': proposals_page,
        'title': title,
        'status_filter': status_filter,
        'proposal_type': proposal_type,
        'status_choices': ExchangeProposal.STATUS_CHOICES,
        'total_proposals': proposals.count(),
    }
    
    return render(request, 'ads/my_proposals.html', context)

@login_required
def proposal_detail(request, pk):
    """
    Детальный просмотр предложения обмена
    """
    proposal = get_object_or_404(ExchangeProposal, pk=pk)
    
    # Проверяем права доступа
    if proposal.user != request.user and proposal.ad_receiver.user != request.user:
        messages.error(request, "У вас нет прав для просмотра этого предложения.")
        return redirect('my_proposals')
    
    context = {
        'proposal': proposal,
        'is_sender': proposal.user == request.user,
        'is_receiver': proposal.ad_receiver.user == request.user,
    }
    
    return render(request, 'ads/proposal_detail.html', context)

@login_required
def update_proposal_status(request, pk):
    """
    Обновление статуса предложения обмена
    """
    proposal = get_object_or_404(ExchangeProposal, pk=pk)
    
    # Проверяем права доступа (только получатель может изменять статус)
    if proposal.ad_receiver.user != request.user:
        messages.error(request, "У вас нет прав для изменения статуса этого предложения.")
        return redirect('proposal_detail', pk=pk)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in ['A', 'R']:  # Accepted или Rejected
            old_status = proposal.status
            proposal.status = new_status
            proposal.save()
            
            status_names = {
                'A': 'принято',
                'R': 'отклонено'
            }
            
            messages.success(request, f"Предложение обмена {status_names[new_status]}!")
            
            # Если предложение принято, можно автоматически обновить статусы других предложений
            if new_status == 'A':
                # Отклоняем все остальные предложения для этого объявления
                ExchangeProposal.objects.filter(
                    ad_receiver=proposal.ad_receiver,
                    status='P'
                ).exclude(pk=proposal.pk).update(status='R')
                
                messages.info(request, "Все остальные предложения для этого объявления автоматически отклонены.")
        
        return redirect('proposal_detail', pk=pk)
    
    return redirect('proposal_detail', pk=pk)

@login_required
def delete_proposal(request, pk):
    """
    Удаление предложения обмена
    """
    proposal = get_object_or_404(ExchangeProposal, pk=pk)
    
    # Проверяем права доступа (только отправитель может удалить)
    if proposal.user != request.user:
        messages.error(request, "У вас нет прав для удаления этого предложения.")
        return redirect('proposal_detail', pk=pk)
    
    if request.method == 'POST':
        proposal.delete()
        messages.success(request, "Предложение обмена удалено!")
        return redirect('my_proposals')
    
    return render(request, 'ads/delete_proposal.html', {'proposal': proposal})