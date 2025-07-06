from django.db import models
from django.contrib.auth.models import User


class Ad(models.Model):
    CATEGORIES = (
        ('E','Electronic'),
        ('C', 'Clothing'),
        ('F', 'Furniture'),
        ('B', 'Books'),
        ('O', 'Other'),
    )
    CONDITIONS = (
        ('N', 'New'),
        ('U', 'Used'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    image_url = models.URLField(blank=True, null=True)
    category = models.CharField(max_length=1, choices=CATEGORIES)
    condition = models.CharField(max_length=1, choices=CONDITIONS)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class ExchangeProposal(models.Model):
    STATUS_CHOICES = (
        ('P', 'Pending'),
        ('A', 'Accepted'),
        ('R', 'Rejected'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='exchange_proposals', null=True, blank=True)
    ad_sender = models.ForeignKey(Ad, related_name='sent_proposals', on_delete=models.CASCADE)
    ad_receiver = models.ForeignKey(Ad, related_name='received_proposals', on_delete=models.CASCADE)
    comment = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='P')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Proposal from {self.ad_sender} to {self.ad_receiver}"

    def get_status_display_ru(self):
        """Возвращает русское название статуса"""
        status_dict = {
            'P': 'Ожидает',
            'A': 'Принято',
            'R': 'Отклонено'
        }
        return status_dict.get(str(self.status), str(self.status))