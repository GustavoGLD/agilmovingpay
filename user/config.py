from typing import Literal
from sqlalchemy import URL
from models import HydraItem

APP_NAME = 'Siscof - AgilMovingPay'

log_level: Literal[
    "ERROR", "WARNING", "INFO", "DEBUG", "TRACE"
] = "DEBUG"

pages: list[HydraItem] = [
    {
        'icon': "💸",
        'label': "Contabilidade e Finanças",
        'submenu': [{
            'icon': "🤝",
            'label': "Acordo",
            "metadata": {
                "table": "acordo",
                "func": "update_table"
            }}, {
            'icon': "📅",
            'label': "Agenda Financeira",
            "metadata": {
                "table": "agenda_financeira",
                "func": "update_table"
            }}, {
            'icon': "📊",
            'label': "Ajustes Não Contabilizados",
            "metadata": {
                "table": "ajustes_nao_contabilizados",
                "func": "update_table"
            }}, {
            'icon': "💳",
            'label': "Conta",
            "metadata": {
                "table": "conta",
                "func": "update_table"
            }}, {
            'icon': "💳",
            'label': "Conta Contábil",
            "metadata": {
                "table": "conta_contabil",
                "func": "update_table"
            }}, {
            'icon': "📅",
            'label': "Data Banco",
            "metadata": {
                "table": "dt_banco",
                "func": "update_table"
            }}, {
            'icon': "💸",
            'label': "Lançamentos Contábeis",
            "metadata": {
                "table": "lancamentos_contabeis",
                "func": "update_table"
            }}, {
            'icon': "💸",
            'label': "Mov Contábil",
            "metadata": {
                "table": "mov_contabil",
                "func": "update_table"
            }}, {
            'icon': "💸",
            'label': "Mov Corte",
            "metadata": {
                "table": "mov_corte",
                "func": "update_table"
            }}, {
            'icon': "📊",
            'label': "Resumo Movto Contábil",
            "metadata": {
                "table": "resumo_movto_contabil",
                "func": "update_table"
            }}, {
            'icon': "🤝",
            'label': "Evento compra",
            "metadata": {
                "table": "t_eventocompra",
                "func": "update_table"
            }}, {
            'icon': "🤝",
            'label': "Evento Compra Não Contabilizado",
            "metadata": {
                "table": "t_eventocompra_nao_contabilizado",
                "func": "update_table"
            }}, {
            'icon': "💸",
            'label': "Lancamento Contabil",
            "metadata": {
                "table": "t_lancamentocontabil",
                "func": "update_table"
            }}, {
            'icon': "💸",
            'label': "Parcela Aberta",
            "metadata": {
                "table": "t_parcelaaberta",
                "func": "update_table"
            }}, {
            'icon': "💸",
            'label': "Transação Contabil Portador",
            "metadata": {
                "table": "t_transacaocontabilportador",
                "func": "update_table"
            }}, {
            'icon': "❌",
            'label': "Transação Não Emite Extrato",
            "metadata": {
                "table": "t_transacaonaoemiteextrato",
                "func": "update_table"
            }}, {
            'icon': "📊",
            'label': "View Movto Contabil",
            "metadata": {
                "table": "view_movto_contabil",
                "func": "update_table"
            }},
        ]
    },
    {
        'icon': "🤝",
        'label': "Compras e Faturamento",
        'submenu': [{
            'icon': "🤝",
            'label': "Carteira",
            "metadata": {
                "table": "carteira",
                "func": "update_table"
            }}, {
            'icon': "📅",
            'label': "Compras Int Saques",
            "metadata": {
                "table": "compras_int_saques",
                "func": "update_table"
            }}, {
            'icon': "📅",
            'label': "Compras Nacionais",
            "metadata": {
                "table": "compras_nacionais",
                "func": "update_table"
            }}, {
            'icon': "🤝",
            'label': "Evento",
            "metadata": {
                "table": "evento",
                "func": "update_table"
            }}, {
            'icon': "💳",
            'label': "Fatura",
            "metadata": {
                "table": "fatura",
                "func": "update_table"
            }}, {
            'icon': "💸",
            'label': "Faturamento",
            "metadata": {
                "table": "faturamento",
                "func": "update_table"
            }}, {
            'icon': "💸",
            'label': "Faturas Contas",
            "metadata": {
                "table": "faturas_contas",
                "func": "update_table"
            }},
        ]
    },
    {
        'icon': "📈",
        'label': "Outros",
        'submenu': [{
            'icon': "📅",
            'label': "Feriados",
            "metadata": {
                "table": "feriados",
                "func": "update_table"
            }}, {
            'icon': "💸",
            'label': "Interface Contabil",
            "metadata": {
                "table": "interface_contabil",
                "func": "update_table"
            }}, {
            'icon': "💸",
            'label': "Interface Contabil 1",
            "metadata": {
                "table": "interface_contabil_1",
                "func": "update_table"
            }}, {
            'icon': "💳",
            'label': "Pagamentos",
            "metadata": {
                "table": "pagamentos",
                "func": "update_table"
            }}, {
            'icon': "💳",
            'label': "Saldo",
            "metadata": {
                "table": "saldo",
                "func": "update_table"
            }}, {
            'icon': "💸",
            'label': "Trx Agillitas Rendimento",
            "metadata": {
                "table": "trx_agillitas_rendimento",
                "func": "update_table"
            }}, {
            'icon': "💸",
            'label': "Vl Dolar",
            "metadata": {
                "table": "vl_dolar",
                "func": "update_table"
            }},
        ]
    }
]

