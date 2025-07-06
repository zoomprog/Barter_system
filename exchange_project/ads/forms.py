from django import forms
from .models import Ad, ExchangeProposal

class AdForm(forms.ModelForm):
    class Meta:
        model = Ad
        fields = ['title', 'description', 'image_url', 'category', 'condition']

class ProposalForm(forms.ModelForm):
    class Meta:
        model = ExchangeProposal
        fields = ['ad_sender', 'comment']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            # Показываем только объявления пользователя
            self.fields['ad_sender'].queryset = Ad.objects.filter(user=user)
            self.fields['ad_sender'].label = "Мое объявление для обмена"
            self.fields['ad_sender'].help_text = "Выберите ваше объявление, которое вы хотите обменять"