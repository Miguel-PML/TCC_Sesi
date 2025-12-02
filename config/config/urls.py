"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from tcc import views 

urlpatterns = [
    # 1. Rota do Admin (Mantenha sempre esta)
    path('admin/', admin.site.urls),

    # 2. Área Pública
    path('consulta/', views.consulta_publica_os, name='consulta_publica'),

    # 3. Área Interna - Listagem e Detalhes
    path('', views.OSListView.as_view(), name='lista_os'),
    path('os/<int:pk>/', views.OSDetailView.as_view(), name='detalhe_os'),

    # 4. Área Interna - Cadastros (Recepcionista)
    path('cliente/novo/', views.ClienteCreateView.as_view(), name='novo_cliente'),
    path('equipamento/novo/', views.EquipamentoCreateView.as_view(), name='novo_equipamento'),
    path('os/nova/', views.OSCreateView.as_view(), name='nova_os'),

    # 5. Área Interna - Ação do Técnico
    path('os/<int:os_id>/atualizar/', views.AtualizacaoStatusCreateView.as_view(), name='atualizar_status'),
]