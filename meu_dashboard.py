from pathlib import Path

import streamlit as st
import pandas as pd

# ---------------- FASE 1 ----------------
st.title('Dashboard de Vendas')

# caminho relativo ao proprio arquivo .py
# no streamlit cloud o app roda a partir da raiz do repo, entao so 'vendas.csv' nao acharia o arquivo
CAMINHO_CSV = Path(__file__).parent / 'vendas.csv'


# guarda o dataframe na memoria, so le o csv de novo se o argumento mudar
@st.cache_data
def carregar_dados(caminho):
    df = pd.read_csv(caminho, parse_dates=['data'])
    return df


df = carregar_dados(CAMINHO_CSV)

# ---------------- FASE 2 ----------------
st.sidebar.title('Filtros')

lista_categorias = sorted(df['categoria'].unique())

# default = todas marcadas, senao o painel abre vazio
categorias_selecionadas = st.sidebar.multiselect(
    'Selecione as Categorias',
    options=lista_categorias,
    default=lista_categorias,
)

# regra de ouro: o retorno do widget filtra o dataframe
# isin() = true pras linhas cuja categoria esta na lista (igual mascara do numpy)
df_filtrado = df[df['categoria'].isin(categorias_selecionadas)]

# se desmarcar tudo, avisa e para o script aqui
if df_filtrado.empty:
    st.warning('Selecione pelo menos uma categoria.')
    st.stop()

# ---------------- FASE 3 ----------------
receita_calculada = df_filtrado['receita'].sum()
total_pedidos = df_filtrado['id_pedido'].nunique()

col1, col2 = st.columns([1, 1])

# obs: o parametro certo do st.metric e value=, nao valor=
with col1:
    st.metric(label='Receita Total', value=f'R$ {receita_calculada:,.2f}')

with col2:
    st.metric(label='Total de Pedidos', value=total_pedidos)

aba1, aba2 = st.tabs(['Evolução Mensal', 'Tabela de Dados'])

with aba1:
    # agrupa ANTES de plotar: 500 linhas viram 12 pontos (um por mes)
    # to_period('M') transforma a data em ano-mes, astype(str) deixa legivel no eixo
    dados_agrupados = (
        df_filtrado
        .groupby(df_filtrado['data'].dt.to_period('M').astype(str))['receita']
        .sum()
    )
    dados_agrupados.index.name = 'mes'
    st.area_chart(dados_agrupados)

with aba2:
    # tabela interativa: da pra rolar e ordenar clicando na coluna
    st.dataframe(df_filtrado, hide_index=True)

    # to_csv sem caminho devolve texto, encode transforma em bytes pro download
    csv = df_filtrado.to_csv(index=False).encode('utf-8')
    st.download_button(
        label='Baixar CSV',
        data=csv,
        file_name='vendas_filtradas.csv',
        mime='text/csv',
    )
