from django.db import models
from django.contrib.auth.models import User
from django.forms import ValidationError
from uteis import validacpf
import re


# Create your models here.

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='Usuário')
    age = models.PositiveIntegerField()
    birth_date = models.DateField()
    cpf = models.CharField(max_length=11)
    address = models.CharField(max_length=50)
    number = models.CharField(max_length=30)
    complement = models.CharField(max_length=30)
    neighborhood = models.CharField(max_length=30)
    cep = models.CharField(max_length=8)
    city = models.CharField(max_length=30)
    state = models.CharField(
        max_length=2,
        default='SP',
        choices=(
            ('AC', 'Acre'),
            ('AL', 'Alagoas'),
            ('AP', 'Amapá'),
            ('AM', 'Amazonas'),
            ('BA', 'Bahia'),
            ('CE', 'Ceará'),
            ('DF', 'Distrito Federal'),
            ('ES', 'Espírito Santo'),
            ('GO', 'Goiás'),
            ('MA', 'Maranhão'),
            ('MT', 'Mato Grosso'),
            ('MS', 'Mato Grosso do Sul'),
            ('MG', 'Minas Gerais'),
            ('PA', 'Pará'),
            ('PB', 'Paraíba'),
            ('PR', 'Paraná'),
            ('PE', 'Pernambuco'),
            ('PI', 'Piauí'),
            ('RJ', 'Rio de Janeiro'),
            ('RN', 'Rio Grande do Norte'),
            ('RS', 'Rio Grande do Sul'),
            ('RO', 'Rondônia'),
            ('RR', 'Roraima'),
            ('SC', 'Santa Catarina'),
            ('SP', 'São Paulo'),
            ('SE', 'Sergipe'),
            ('TO', 'Tocantins'),
        )
    )
    
    def __str__(self):
        if self.user.first_name:
            return f'{self.user.first_name} {self.user.last_name}'
        return f'{self.user}'
    
    def clean(self):
        error_messages = {}

        cpf_sended = self.cpf or None
        cpf_saved = None
        profile = Profile.objects.filter(cpf=cpf_sended).first()

        if profile:
            cpf_saved = profile.cpf
        
            if cpf_saved is not None and self.pk != profile.pk:
                error_messages['cpf'] = 'CPF already exists'

        if not validacpf.valida_cpf(self.cpf):
            error_messages['cpf'] = 'Type a valid CPF'

        if re.search(r'[^0-9]', self.cep):
            error_messages['cep'] = 'Type a valid CEP'

        if error_messages:
            raise ValidationError(error_messages)

    class Meta:
        verbose_name = 'Profile'
        verbose_name_plural = 'Profiles'