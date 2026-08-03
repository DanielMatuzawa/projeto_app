import streamlit as st
import pandas as pd

# Configuração da página
st.set_page_config(page_title="Meu Portfólio de Investimentos", layout="wide")

st.title("Painel de Controle de Investimentos e Estudos")
st.markdown("Foco em: **PETR4**, **BBSE3** e **KNCR11**")

# Inicializar dados na sessão (para salvar enquanto o app estiver aberto)
if 'aportes' not in st.session_state:
    st.session_state.aportes = pd.DataFrame(columns=['Ativo', 'Quantidade', 'Preço Unitário', 'Valor Total', 'Data'])

if 'notas' not in st.session_state:
    st.session_state.notas = "Escreva aqui suas anotações sobre os estudos, teses de investimento ou metas para PETR4, BBSE3 e KNCR11."

# ----------------------------------------------------
# 1. REGISTRO DE APORTES
# ----------------------------------------------------
st.sidebar.header("Registrar Novo Aporte")
ativo_escolhido = st.sidebar.selectbox("Ativo", ["PETR4", "BBSE3", "KNCR11"])
qtd_aporte = st.sidebar.number_input("Quantidade", min_value=1, step=1)
preco_aporte = st.sidebar.number_input("Preço Unitário (R$)", min_value=0.01, format="%.2f")
data_aporte = st.sidebar.date_input("Data do Aporte")

if st.sidebar.button("Adicionar Aporte"):
    valor_total = qtd_aporte * preco_aporte
    novo_dado = pd.DataFrame({
        'Ativo': [ativo_escolhido],
        'Quantidade': [qtd_aporte],
        'Preço Unitário': [preco_aporte],
        'Valor Total': [valor_total],
        'Data': [data_aporte]
    })
    st.session_state.aportes = pd.concat([st.session_state.aportes, novo_dado], ignore_index=True)
    st.sidebar.success("Aporte registrado com sucesso!")

# ----------------------------------------------------
# 2. CONSOLIDAÇÃO DA CARTEIRA
# ----------------------------------------------------
st.header("Resumo da Carteira")

if not st.session_state.aportes.empty:
    # Agrupar por ativo para calcular quantidade total e preço médio ponderado
    df = st.session_state.aportes
    resumo = df.groupby('Ativo').agg(
        Quantidade_Total=('Quantidade', 'sum'),
        Total_Investido=('Valor Total', 'sum')
    ).reset_index()
    
    resumo['Preço Médio'] = resumo['Total_Investido'] / resumo['Quantidade_Total']
    
    # Preços atuais simulados/editáveis (você pode ajustar aqui ou digitar o preço de mercado atual)
    st.markdown("### Defina os Preços Atuais de Mercado")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        preco_petr4 = st.number_input("Preço Atual PETR4", value=35.00, format="%.2f")
    with col2:
        preco_bbse3 = st.number_input("Preço Atual BBSE3", value=33.00, format="%.2f")
    with col3:
        preco_kncr11 = st.number_input("Preço Atual KNCR11", value=100.00, format="%.2f")
        
    precos_atuais = {'PETR4': preco_petr4, 'BBSE3': preco_bbse3, 'KNCR11': preco_kncr11}
    resumo['Preço Atual'] = resumo['Ativo'].map(precos_atuais)
    resumo['Valor Atual'] = resumo['Quantidade_Total'] * resumo['Preço Atual']
    resumo['Lucro/Prejuízo (R$)'] = resumo['Valor Atual'] - resumo['Total_Investido']
    resumo['Lucro/Prejuízo (%)'] = (resumo['Lucro/Prejuízo (R$)'] / resumo['Total_Investido']) * 100

    # Exibindo métricas gerais
    patrimonio_total = resumo['Valor Atual'].sum()
    total_investido_geral = resumo['Total_Investido'].sum()
    lucro_geral = patrimonio_total - total_investido_geral
    
    m1, m2, m3 = st.columns(3)
    m1.metric("Patrimônio Total", f"R$ {patrimonio_total:,.2f}")
    m2.metric("Total Investido", f"R$ {total_investido_geral:,.2f}")
    m3.metric("Resultado Geral", f"R$ {lucro_geral:,.2f}", delta=f"{(lucro_geral/total_investido_geral)*100:.2f}%" if total_investido_geral > 0 else "0%")

    st.markdown("### Posição por Ativo")
    st.dataframe(resumo[['Ativo', 'Quantidade_Total', 'Preço Médio', 'Preço Atual', 'Valor Atual', 'Lucro/Prejuízo (R$)']])

    # Gráfico simples de alocação
    st.markdown("### Alocação de Recursos")
    st.bar_chart(resumo.set_index('Ativo')['Valor Atual'])

else:
    st.info("Nenhum aporte registrado ainda. Use a barra lateral à esquerda para cadastrar seus primeiros aportes em PETR4, BBSE3 ou KNCR11.")

# ----------------------------------------------------
# 3. ÁREA DE ANOTAÇÕES E ESTUDOS
# ----------------------------------------------------
st.markdown("---")
st.header("Área de Anotações e Metas de Estudo")

st.session_state.notas = st.text_area("Bloco de Notas (Anote teses, dividendos esperados, regras de aporte):", value=st.session_state.notas, height=200)

# ----------------------------------------------------
# 4. HISTÓRICO DE APORTES
# ----------------------------------------------------
if not st.session_state.aportes.empty:
    st.markdown("---")
    st.header("Histórico Detalhado de Aportes")
    st.dataframe(st.session_state.aportes)
