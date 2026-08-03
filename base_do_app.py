import streamlit as st
import pandas as pd

st.set_page_config(page_title="Meu Portfólio de Investimentos", layout="wide")

st.title("Painel de Controle de Investimentos e Estudos")
st.markdown("Foco em: PETR4, BBSE3 e KNCR11")

if 'aportes' not in st.session_state:
    st.session_state.aportes = pd.DataFrame(columns=['Ativo', 'Quantidade', 'Preço Pago', 'Preço Atual', 'Data'])

if 'notas' not in st.session_state:
    st.session_state.notas = "Escreva aqui suas anotações sobre os estudos, teses de investimento ou metas para PETR4, BBSE3 e KNCR11."

st.sidebar.header("Registrar Novo Aporte")
ativo_escolhido = st.sidebar.selectbox("Ativo", ["PETR4", "BBSE3", "KNCR11"])
qtd_aporte = st.sidebar.number_input("Quantidade", min_value=1, step=1, value=1)
preco_pago = st.sidebar.number_input("Preço Pago por Unidade (R$)", min_value=0.01, format="%.2f", value=10.0)
preco_atual_input = st.sidebar.number_input("Preço Atual de Mercado (R$)", min_value=0.01, format="%.2f", value=10.0)
data_aporte = st.sidebar.date_input("Data do Aporte")

if st.sidebar.button("Adicionar Aporte"):
    novo_dado = pd.DataFrame({
        'Ativo': [ativo_escolhido],
        'Quantidade': [int(qtd_aporte)],
        'Preço Pago': [float(preco_pago)],
        'Preço Atual': [float(preco_atual_input)],
        'Data': [str(data_aporte)]
    })
    st.session_state.aportes = pd.concat([st.session_state.aportes, novo_dado], ignore_index=True)
    st.sidebar.success("Aporte registrado com sucesso!")
    st.rerun()

st.header("Resumo da Carteira")

if not st.session_state.aportes.empty:
    df = st.session_state.aportes.copy()
    
    df['Quantidade'] = pd.to_numeric(df['Quantidade'])
    df['Preço Pago'] = pd.to_numeric(df['Preço Pago'])
    df['Preço Atual'] = pd.to_numeric(df['Preço Atual'])
    
    df['Total Investido'] = df['Quantidade'] * df['Preço Pago']
    df['Valor Atual'] = df['Quantidade'] * df['Preço Atual']
    
    resumo = df.groupby('Ativo').agg(
        Quantidade_Total=('Quantidade', 'sum'),
        Total_Investido=('Total Investido', 'sum'),
        Valor_Atual=('Valor Atual', 'sum'),
        Preço_Atual_Ref=('Preço Atual', 'last')
    ).reset_index()
    
    resumo['Preço Médio'] = resumo['Total_Investido'] / resumo['Quantidade_Total']
    resumo['Lucro/Prejuízo (R$)'] = resumo['Valor_Atual'] - resumo['Total_Investido']
    resumo['Lucro/Prejuízo (%)'] = (resumo['Lucro/Prejuízo (R$)'] / resumo['Total_Investido']) * 100

    patrimonio_total = resumo['Valor_Atual'].sum()
    total_investido_geral = resumo['Total_Investido'].sum()
    lucro_geral = patrimonio_total - total_investido_geral
    
    m1, m2, m3 = st.columns(3)
    m1.metric("Patrimônio Total", f"R$ {patrimonio_total:,.2f}")
    m2.metric("Total Investido", f"R$ {total_investido_geral:,.2f}")
    m3.metric("Resultado Geral", f"R$ {lucro_geral:,.2f}", delta=f"{(lucro_geral/total_investido_geral)*100:.2f}%" if total_investido_geral > 0 else "0%")

    st.markdown("### Posição Consolidada por Ativo")
    st.dataframe(resumo[['Ativo', 'Quantidade_Total', 'Preço Médio', 'Preço_Atual_Ref', 'Valor_Atual', 'Lucro/Prejuízo (R$)']])

    st.markdown("### Alocação de Recursos")
    st.bar_chart(resumo.set_index('Ativo')['Valor_Atual'])

else:
    st.info("Nenhum aporte registrado ainda. Use a barra lateral à esquerda para cadastrar seus primeiros aportes.")

if not st.session_state.aportes.empty:
    st.markdown("---")
    st.header("Histórico Detalhado e Edição de Aportes")
    st.markdown("Aqui você pode editar qualquer linha diretamente, incluindo o preço pago e o preço atual de mercado.")
    
    st.session_state.aportes = st.data_editor(
        st.session_state.aportes, 
        num_rows="dynamic",
        key="editor_aportes"
    )

st.markdown("---")
st.header("Área de Anotações e Metas de Estudo")
st.session_state.notas = st.text_area("Bloco de Notas:", value=st.session_state.notas, height=200)
