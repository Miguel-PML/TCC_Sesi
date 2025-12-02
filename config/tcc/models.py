from django.db import models

import uuid # Usaremos para gerar um código único para o Cliente consultar

# --- 1. Modelo Cliente ---
class Cliente(models.Model):
    nome = models.CharField(max_length=100)
    telefone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    
    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"

    def __str__(self):
        return self.nome

# --- 2. Modelo Equipamento ---
class Equipamento(models.Model):
    tipo = models.CharField(max_length=50, help_text="Ex: Computador, Telemóvel, TV")
    marca = models.CharField(max_length=50)
    modelo = models.CharField(max_length=50)
    numero_serie = models.CharField(max_length=100, unique=True, blank=True, null=True)
    
    class Meta:
        verbose_name = "Equipamento"
        verbose_name_plural = "Equipamentos"

    def __str__(self):
        return f"{self.marca} {self.modelo} ({self.tipo})"

# --- 3. Modelo OrdemDeServico (OS) ---
class OrdemDeServico(models.Model):
    # Status possíveis
    STATUS_CHOICES = [
        ('aberto', 'Aberta'),
        ('em_analise', 'Em Análise'),
        ('aguardando_peca', 'Aguardando Peça'),
        ('em_reparo', 'Em Reparo'),
        ('concluido', 'Concluído'),
        ('entregue', 'Entregue ao Cliente'),
    ]

    # Relações
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    equipamento = models.ForeignKey(Equipamento, on_delete=models.CASCADE)

    # Dados da OS
    data_abertura = models.DateTimeField(auto_now_add=True)
    defeito_relatado = models.TextField(help_text="Descrição do defeito pelo cliente.")
    status_atual = models.CharField(max_length=20, choices=STATUS_CHOICES, default='aberto')
    
    # Código único para consulta do Cliente
    # Usamos o UUID (Identificador Universalmente Único) e pegamos as 8 primeiras letras
    codigo_consulta = models.CharField(
        max_length=8, 
        unique=True, 
        editable=False, 
        default=uuid.uuid4().hex[:8].upper()
    )

    class Meta:
        verbose_name = "Ordem de Serviço"
        verbose_name_plural = "Ordens de Serviço"
        ordering = ['-data_abertura'] # Ordena pela mais recente

    def __str__(self):
        return f"OS #{self.id} - {self.cliente.nome}"


# --- 4. Modelo AtualizacaoStatus (Histórico de Mudanças) ---
class AtualizacaoStatus(models.Model):
    os = models.ForeignKey(OrdemDeServico, on_delete=models.CASCADE)
    data_atualizacao = models.DateTimeField(auto_now_add=True)
    novo_status = models.CharField(max_length=20, choices=OrdemDeServico.STATUS_CHOICES)
    observacoes = models.TextField(blank=True, help_text="Detalhes da atualização (ex: 'Diagnóstico: Placa-mãe danificada')")
    # Poderia ligar ao Técnico (User), mas vamos simplificar
    
    class Meta:
        verbose_name = "Atualização de Status"
        verbose_name_plural = "Atualizações de Status"
        ordering = ['data_atualizacao']

    def __str__(self):
        return f"OS #{self.os.id} - {self.get_novo_status_display()} em {self.data_atualizacao.strftime('%d/%m/%Y %H:%M')}"
# Create your models here.
