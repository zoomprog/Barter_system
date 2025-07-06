from django.shortcuts import render, get_object_or_404, redirect
from .models import Ad, ExchangeProposal
from .forms import AdForm, ProposalForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.views import generic
from django.urls import reverse_lazy
from django.http import Http404
from django.contrib import messages
# Create your views here.

class SignUpView(generic.CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'ads/signup.html'


@login_required
def index(request):
    ads = Ad.objects.all()
    return render(request, 'ads/index.html', {'ads': ads})

@login_required
def ad_detail(request, pk):
    ad = get_object_or_404(Ad, pk=pk)
    if request.method == 'POST':
        form = ProposalForm(request.POST)
        if form.is_valid():
            proposal = form.save(commit=False)
            proposal.ad_sender = ad
            proposal.user = request.user
            proposal.save()
            return redirect('ad_detail', pk=pk)
    else:
        form = ProposalForm()
    return render(request, 'ads/ad_detail.html', {'ad': ad, 'form': form})

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
def edit_ad(request, pk):
    ad = get_object_or_404(Ad, pk=pk)
    # Проверяем пользователь автор объявления
    if ad.user != request.user:
        messages.error(request, 'Вы можете редактировать только свои собственные объявления.')
        return redirect('ad_detail', pk=pk)
    if request.method == 'POST':
        form = AdForm(request.POST, instance=ad)
        if form.is_valid():
            form.save()
            messages.success(request, 'Ad updated successfully!')
            return redirect('ad_detail', pk=pk)
    else:
        form = AdForm(instance=ad)
    return render(request, 'ads/edit_ad.html', {'form': form, 'ad': ad},)