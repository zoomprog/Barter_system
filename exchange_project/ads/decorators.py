from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from functools import wraps
from .models import Ad


def ad_author_required(view_func):
    """
    Декоратор для проверки, является ли пользователь автором объявления
    """

    @wraps(view_func)
    def wrapper(request, pk, *args, **kwargs):
        try:
            ad = Ad.objects.get(pk=pk)
        except Ad.DoesNotExist:
            messages.error(request, "Объявление не найдено.")
            return redirect('index')

        if ad.user != request.user:
            messages.error(request,
                           "У вас нет прав для редактирования этого объявления. Только автор может редактировать свои объявления.")
            return redirect('ad_detail', pk=pk)

        return view_func(request, pk, *args, **kwargs)

    return wrapper