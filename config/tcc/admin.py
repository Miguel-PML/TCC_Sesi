from django.contrib import admin
from .models import Cliente, Equipamento, OrdemDeServico, AtualizacaoStatus

# Register your models here.

admin.site.register(Cliente),
admin.site.register(Equipamento),
admin.site.register(OrdemDeServico),
admin.site.register(AtualizacaoStatus)