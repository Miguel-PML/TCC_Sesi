from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, DetailView, UpdateView
from django.contrib import messages
from django.db.models import Q

# Importa os modelos definidos no seu arquivo
from .models import Cliente, Equipamento, OrdemDeServico, AtualizacaoStatus

# AREA DO CLIENTE
def consulta_publica_os(request):
    """
    View baseada em função para o Cliente consultar o status pelo código.
    Não exige login.
    """
    ordem = None
    erro = None

    if 'codigo' in request.GET:
        codigo = request.GET.get('codigo').strip().upper()
        try:
            # Tenta buscar a OS pelo código único de 8 dígitos
            ordem = OrdemDeServico.objects.get(codigo_consulta=codigo)
        except OrdemDeServico.DoesNotExist:
            erro = "Ordem de Serviço não encontrada. Verifique o código digitado."

    return render(request, 'os/consulta_publica.html', {
        'ordem': ordem,
        'erro': erro
    })


# AREA INTERNA

class ClienteCreateView(CreateView):
    """ Cadastra um novo Cliente """
    model = Cliente
    fields = ['nome', 'telefone', 'email']
    template_name = 'os/cliente_form.html'
    success_url = reverse_lazy('lista_os') # Redireciona para lista após criar

    def form_valid(self, form):
        messages.success(self.request, "Cliente cadastrado com sucesso!")
        return super().form_valid(form)


class EquipamentoCreateView(CreateView):
    """ Cadastra um novo Equipamento """
    model = Equipamento
    fields = ['tipo', 'marca', 'modelo', 'numero_serie']
    template_name = 'os/equipamento_form.html'
    success_url = reverse_lazy('lista_os')


class OSCreateView(CreateView):
    """ 
    Abertura de nova Ordem de Serviço.
    A Recepcionista seleciona o Cliente e o Equipamento já cadastrados.
    """
    model = OrdemDeServico
    fields = ['cliente', 'equipamento', 'defeito_relatado']
    template_name = 'os/os_form.html'
    success_url = reverse_lazy('lista_os')

    def form_valid(self, form):
        response = super().form_valid(form)
        # Cria o primeiro registro no histórico automaticamente
        AtualizacaoStatus.objects.create(
            os=self.object,
            novo_status='aberto',
            observacoes=f"OS Aberta. Defeito: {self.object.defeito_relatado}"
        )
        messages.success(self.request, f"OS {self.object.codigo_consulta} aberta com sucesso!")
        return response

# AREA DO TÉCNICO

class OSListView(ListView):
    """ Lista todas as OS para a equipe interna ver o painel geral """
    model = OrdemDeServico
    template_name = 'os/os_list.html'
    context_object_name = 'ordens'
    paginate_by = 10

    def get_queryset(self):
        # Permite filtrar por status se passado na URL (ex: ?status=em_analise)
        status_filter = self.request.GET.get('status')
        if status_filter:
            return OrdemDeServico.objects.filter(status_atual=status_filter)
        return OrdemDeServico.objects.all()


class OSDetailView(DetailView):
    """ 
    Detalhes completos da OS, incluindo o histórico de atualizações.
    """
    model = OrdemDeServico
    template_name = 'os/os_detail.html'
    context_object_name = 'os'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Adiciona o histórico de atualizações ao contexto
        context['historico'] = self.object.atualizacaostatus_set.all().order_by('-data_atualizacao')
        return context


class AtualizacaoStatusCreateView(CreateView):
    """
    View crítica: Onde o técnico atualiza o andamento.
    Ao salvar a atualização, ela ATUALIZA AUTOMATICAMENTE o status da OS pai.
    """
    model = AtualizacaoStatus
    fields = ['novo_status', 'observacoes']
    template_name = 'os/atualizacao_form.html'

    def dispatch(self, request, *args, **kwargs):
        # Pega a OS da URL para vincular à atualização
        self.os_obj = get_object_or_404(OrdemDeServico, pk=self.kwargs['os_id'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.os = self.os_obj # Vincula a OS
        response = super().form_valid(form)
        
        # --- Lógica de Negócio ---
        # Atualiza o status atual na tabela OrdemDeServico
        self.os_obj.status_atual = form.instance.novo_status
        self.os_obj.save()
        
        messages.success(self.request, "Status atualizado com sucesso!")
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['os'] = self.os_obj
        return context

    def get_success_url(self):
        return reverse_lazy('detalhe_os', kwargs={'pk': self.os_obj.pk})