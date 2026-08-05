import streamlit as st
import pandas as pd
import yfinance as yf
from supabase import create_client

st.set_page_config(page_title="Meu Portfólio de Investimentos", layout="wide")

# Configuração direta para teste e funcionamento imediato
SUPABASE_URL = "https://gmpqpiagdnebzafjiogn.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImdtcXBwaWFnZG5lYnphZmppb2duIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODU3ODI4NjMsImV4cCI6MjEwMTM1ODg2M30.xDk4lPnIK0oKjEwK2d4oidMQFt67CDoSzJapRkiUlLA"

@st.cache_resource
def init_connection():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

try:
    supabase = init_connection()
except Exception as e:
    st.error(f"Erro ao conectar no banco: {e}")

st.title("Painel de Controle de Investimentos e Estudos")
st.markdown("Foco em: PETR4, BBSE3 e KNCR11 com salvamento automático na nuvem")

if 'notas' not in st.session_state:
    st.session_state.notas = "Escreva aqui suas anotações sobre os estudos, teses de investimento ou metas para PETR4, BBSE3 e KNCR11."

def carregar_aportes():
    try:
        response = supabase.table("aportes").select("*").execute()
        data = response.data
        if data:
            df = pd.DataFrame(data)
            return df
    except:
        pass
    return pd.DataFrame(columns=['id', 'ativo', 'quantidade', 'preco_pago', 'data'])

df_aportes = carregar_aportes()

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

# Criando as abas de navegação principais
aba_dashboard, aba_aportes, aba_notas = st.tabs(["Dashboard Geral", "Cadastrar & Histórico de Aportes", "Anotações e Estudos"])

# ==================== ABA 1: DASHBOARD ====================
with aba_dashboard:
    st.header("Dashboard de Desempenho")

    if not df_aportes.empty and 'quantidade' in df_aportes.columns:
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
        
        # Métricas principais do Dashboard (Cards superiores)
        m1, m2, m3 = st.columns(3)
        m1.metric("Patrimônio Total", f"R$ {patrimonio_total:,.2f}")
        m2.metric("Total Investido", f"R$ {total_investido_geral:,.2f}")
        m3.metric("Resultado Geral", f"R$ {lucro_geral:,.2f}", delta=f"{(lucro_geral/total_investido_geral)*100:.2f}%" if total_investido_geral > 0 else "0%")

        st.markdown("---")
        st.subheader("Posição Consolidada por Ativo")
        st.dataframe(resumo[['ativo', 'Quantidade_Total', 'Preço Médio', 'Preço Atual', 'Valor Atual', 'Lucro/Prejuízo (R$)']], use_container_width=True)

        st.markdown("---")
        st.subheader("Dashboard de Alocação por Ativo")
        
        # Novo formato de Dashboard: Linhas de progresso e métricas visuais por ativo (Sem gráficos complexos)
        for _, row in resumo.iterrows():
            percentual = (row['Valor Atual'] / patrimonio_total * 100) if patrimonio_total > 0 else 0
            col_info1, col_info2 = st.columns([1, 3])
            with col_info1:
                st.markdown(f"**{row['ativo']}**")
                st.text(f"R$ {row['Valor Atual']:,.2f}")
            with col_info2:
                st.progress(int(percentual) if percentual <= 100 else 100, text=f"Alocação: {percentual:.1f}% do portfólio")

    else:
        st.info("Nenhum dado cadastrado para exibir no dashboard. Vá até a aba de Aportes para registrar suas compras.")

# ==================== ABA 2: APORTES ====================
with aba_aportes:
    st.header("Gerenciamento de Aportes")
    
    col_form, col_tabela = st.columns([1, 2])
    
    with col_form:
        st.subheader("Registrar Novo Aporte")
        ativo_escolhido = st.selectbox("Ativo", ["PETR4", "BBSE3", "KNCR11"], key="form_ativo")
        qtd_aporte = st.number_input("Quantidade", min_value=1, step=1, value=1, key="form_qtd")
        preco_pago = st.number_input("Preço Pago por Unidade (R$)", min_value=0.01, format="%.2f", value=10.0, key="form_preco")
        data_aporte = st.date_input("Data do Aporte", key="form_data")

        if st.button("Adicionar Aporte na Nuvem", use_container_width=True):
            try:
                novo_registro = {
                    "ativo": str(ativo_escolhido),
                    "quantidade": int(qtd_aporte),
                    "preco_pago": float(preco_pago),
                    "data": str(data_aporte)
                }
                supabase.table("aportes").insert(novo_registro).execute()
                st.success("Aporte salvo com sucesso!")
                st.rerun()
            except Exception as e:
                st.error(f"Erro ao salvar: {e}")

    with col_tabela:
        st.subheader("Histórico Detalhado de Aportes")
        if not df_aportes.empty:
            st.dataframe(df_aportes, use_container_width=True)
        else:
            st.info("Nenhum aporte registrado ainda.")

# ==================== ABA 3: ANOTAÇÕES ====================
with aba_notas:
    st.header("Área de Anotações e Metas de Estudo")
    st.markdown("Use este espaço livre para registrar suas teses de investimento, lembretes e planos para PETR4, BBSE3 e KNCR11.")
    st.session_state.notas = st.text_area("Bloco de Notas:", value=st.session_state.notas, height=300)
