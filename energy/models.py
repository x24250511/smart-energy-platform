from django.db import models
from accounts.models import EnergyUser

class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('buyback', 'Buyback'),
        ('loan', 'Loan'),
        ('donation', 'Donation'),
    ]
    
    from_user = models.ForeignKey(EnergyUser, on_delete=models.CASCADE, related_name='transactions_sent')
    to_user = models.ForeignKey(EnergyUser, on_delete=models.CASCADE, null=True, blank=True, related_name='transactions_received')
    amount = models.FloatField()
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.transaction_type} - {self.amount} kWh"
    
    class Meta:
        ordering = ['-timestamp']
