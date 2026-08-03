import streamlit as st
import pandas as pd
import yfinance as yf
from supabase import create_client

st.set_page_config(page_title="Meu Portfólio de Investimentos", layout="wide")

# Configuração de Conexão com o Supabase com as suas chaves
SUPABASE_URL = "https://gmpqpiagdnebzafjiogn.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImdtcXBwaWFnZG5lYnphZmppb2duIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODU3ODI4NjMsImV4cCI6MjEwMTM1ODg2M30.xDk4lPnIK0oKjEwK2d4oidMQFt67CDoSzJapRkiUlLA"

@st.cache_resource
def init_connection():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = init_connection()

st.title("Painel de Controle de Investimentos e Estudos")
st.markdown("Foco em: PETR4, BBSE3 e KNCR11 com salvamento automático na nuvem")

if 'notas' not in st.session_state:
    st.session_state.notas = "Escreva aqui suas anotações sobre os estudos, teses de investimento ou metas para PETR4, BBSE3 e KNCR11."

# Função para carregar os aportes direto do Supabase
def carregar_aportes():
    try:
        response = supabase.table("aportes").select("*").execute()
        data = response.data
        if data:
            df = pd.DataFrame(data)
            colunas_desejadas = ['id', 'ativo', 'quantidade', 'preco_pago', 'data']
            for col in colunas_desejadas:
                if col not in df.columns:
                    df[col] = None
            return df
    except:
        pass
    return pd.DataFrame(columns=['id', 'ativo', 'quantidade', 'preco_pago', 'data'])

df_aportes = carregar_aportes()

# Função para buscar o preço atual na B3 via Yahoo Finance
def obter_preco_atual(ticker_simbolo):
    try:
        ticker = yf.Ticker(ticker_simbolo)
        dados = ticker.history(period="1d")
        if not dados.empty:
            return float(dados['Close'].iloc[-1])
    except:
        pass
    return 0.0

tickers_map = {
    "PETR4": "PETR4.SA",
    "BBSE3": "BBSE3.SA",
    "KNCR11": "KNCR11.SA"
}

st.sidebar.header("Registrar Novo Aporte")
ativo_escolhido = st.sidebar.selectbox("Ativo", ["PETR4", "BBSE3", "KNCR11"])
qtd_aporte = st.sidebar.number_input("Quantidade", min_value=1, step=1, value=1)
preco_pago = st.sidebar.number_input("Preço Pago por Unidade (R$)", min_value=0.01, format="%.2f", value=10.0)
data_aporte = st.sidebar.date_input("Data do Aporte")

if st.sidebar.button("Adicionar Aporte"):
    novo_registro = {
        "ativo": ativo_escolhido,
        "quantidade": int(qtd_aporte),
        "preco_pago": float(preco_pago),
        "data": str(data_aporte)
    }
    supabase.table("aportes").insert(novo_registro).execute()
    st.sidebar.success("Aporte salvo na nuvem com sucesso!")
    st.rerun()

st.header("Resumo da Carteira com Preços em Tempo Real")

if not df_aportes.empty:
    df = df_aportes.copy()
    
    df['quantidade'] = pd.to_numeric(df['quantidade'])
    df['preco_pago'] = pd.to_numeric(df['preco_pago'])
    df['Total Investido'] = df['quantidade'] * df['preco_pago']
    
    resumo = df.groupby('ativo').agg(
        Quantidade_Total=('quantidade', 'sum'),
        Total_Investido=('Total Investido', 'sum')
    ).reset_index()
    
    resumo['Preço Médio'] = resumo['Total_Investido'] / resumo['Quantidade_Total']
    
    precos_atuais = {}
    for ativo in resumo['ativo']:
        simbolo_yahoo = tickers_map.get(ativo)
        precos_atuais[ativo] = obter_preco_atual(simbolo_yahoo)
        
    resumo['Preço Atual'] = resumo['ativo'].map(precos_atuais)
    resumo['Valor Atual'] = resumo['Quantidade_Total'] * resumo['Preço Atual']
    resumo['Lucro/Prejuízo (R$)'] = resumo['Valor Atual'] - resumo['Total_Investido']
    resumo['Lucro/Prejuízo (%)'] = (resumo['Lucro/Prejuízo (R$)'] / resumo['Total_Investido']) * 100

    patrimonio_total = resumo['Valor Atual'].sum()
    total_investido_geral = resumo['Total_Investido'].sum()
    lucro_geral = patrimonio_total - total_investido_geral
    
    m1, m2, m3 = st.columns(3)
    m1.metric("Patrimônio Total", f"R$ {patrimonio_total:,.2f}")
    m2.metric("Total Investido", f"R$ {total_investido_geral:,.2f}")
    m3.metric("Resultado Geral", f"R$ {lucro_geral:,.2f}", delta=f"{(lucro_geral/total_investido_geral)*100:.2f}%" if total_investido_geral > 0 else "0%")

    st.markdown("### Posição Consolidada por Ativo")
    st.dataframe(resumo[['ativo', 'Quantidade_Total', 'Preço Médio', 'Preço Atual', 'Valor Atual', 'Lucro/Prejuízo (R$)']])

    st.markdown("### Alocação de Recursos")
    st.bar_chart(resumo.set_index('ativo')['Valor Atual'])

else:
    st.info("Nenhum aporte registrado na nuvem ainda. Use a barra lateral à esquerda para cadastrar.")

if not df_aportes.empty:
    st.markdown("---")
    st.header("Histórico Detalhado de Aportes")
    st.dataframe(df_aportes[['id', 'ativo', 'quantidade', 'preco_pago', 'data']])

st.markdown("---")
st.header("Área de Anotações e Metas de Estudo")
st.session_state.notas = st.text_area("Bloco de Notas:", value=st.session_state.notas, height=200)
