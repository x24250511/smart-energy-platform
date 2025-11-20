from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from smart_energy_lib import EnergyAccount

class EnergyUserManager(BaseUserManager):
    def create_user(self, energy_number, name, password=None):
        if not energy_number:
            raise ValueError('Energy number required')
        user = self.model(energy_number=energy_number, name=name)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, energy_number, name, password):
        user = self.create_user(energy_number, name, password)
        user.is_admin = True
        user.save(using=self._db)
        return user

class EnergyUser(AbstractBaseUser):
    energy_number = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    generated = models.FloatField(default=0)
    consumed = models.FloatField(default=0)
    credits = models.FloatField(default=0)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    objects = EnergyUserManager()
    
    USERNAME_FIELD = 'energy_number'
    REQUIRED_FIELDS = ['name']
    
    def __str__(self):
        return f"{self.energy_number} - {self.name}"
    
    def calculate_surplus(self):
        account = EnergyAccount(self.energy_number, self.name, self.generated, self.consumed)
        return account.calculate_surplus()
    
    def calculate_deficit(self):
        account = EnergyAccount(self.energy_number, self.name, self.generated, self.consumed)
        return account.calculate_deficit()
    
    def has_perm(self, perm, obj=None):
        return True
    
    def has_module_perms(self, app_label):
        return True
    
    @property
    def is_staff(self):
        return self.is_admin
