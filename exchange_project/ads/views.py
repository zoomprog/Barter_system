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

class SignUpView(generic.CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'ads/signup.html'

@login_required
def index(request):
    ads = Ad.objects.all()
    return render(request, 'ads/index.html', {'ads': ads})


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