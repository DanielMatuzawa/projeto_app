import streamlit as st
import pandas as pd
import yfinance as yf


# =====================================
# CONFIGURAÇÃO
# =====================================

st.set_page_config(
    page_title="Meu Portfólio de Investimentos",
    layout="wide"
)


st.title("📈 Painel de Controle de Investimentos")
st.markdown(
    "Carteira monitorada: **PETR4 | BBSE3 | KNCR11**"
)



# =====================================
# FUNÇÃO PARA BUSCAR COTAÇÕES
# =====================================

def buscar_cotacao(ativo):

    try:

        ticker = ativo + ".SA"

        acao = yf.Ticker(ticker)

        preco = acao.fast_info["last_price"]

        return round(preco,2)


    except:

        return None



# =====================================
# MEMÓRIA
# =====================================

if "aportes" not in st.session_state:

    st.session_state.aportes = pd.DataFrame(
        columns=[
            "Ativo",
            "Quantidade",
            "Preço Pago",
            "Data"
        ]
    )



if "notas" not in st.session_state:

    st.session_state.notas = (
        "Anotações sobre estudos, "
        "teses e metas."
    )



# =====================================
# ATUALIZAÇÃO DAS COTAÇÕES
# =====================================

st.sidebar.header("📡 Mercado")


if st.sidebar.button(
    "Atualizar Cotações"
):

    st.session_state.cotacoes = {}


    for ativo in [
        "PETR4",
        "BBSE3",
        "KNCR11"
    ]:

        st.session_state.cotacoes[ativo] = buscar_cotacao(
            ativo
        )


    st.sidebar.success(
        "Cotações atualizadas!"
    )



if "cotacoes" not in st.session_state:

    st.session_state.cotacoes = {

        "PETR4": buscar_cotacao("PETR4"),
        "BBSE3": buscar_cotacao("BBSE3"),
        "KNCR11": buscar_cotacao("KNCR11")

    }



# =====================================
# SIDEBAR - APORTE
# =====================================


st.sidebar.header(
    "💰 Registrar Aporte"
)


ativo = st.sidebar.selectbox(
    "Ativo",
    [
        "PETR4",
        "BBSE3",
        "KNCR11"
    ]
)


quantidade = st.sidebar.number_input(
    "Quantidade",
    min_value=1,
    value=1
)


preco_pago = st.sidebar.number_input(
    "Preço pago por unidade",
    min_value=0.01,
    value=10.00,
    format="%.2f"
)


data = st.sidebar.date_input(
    "Data do aporte"
)



if st.sidebar.button(
    "Adicionar Aporte"
):


    novo = pd.DataFrame({

        "Ativo":[ativo],

        "Quantidade":[quantidade],

        "Preço Pago":[preco_pago],

        "Data":[str(data)]

    })


    st.session_state.aportes = pd.concat(

        [
            st.session_state.aportes,
            novo
        ],

        ignore_index=True

    )


    st.sidebar.success(
        "Aporte registrado!"
    )


    st.rerun()



# =====================================
# DASHBOARD
# =====================================


st.header(
    "📊 Resumo da Carteira"
)



if not st.session_state.aportes.empty:


    df = st.session_state.aportes.copy()



    df["Preço Atual"] = df["Ativo"].apply(

        lambda x:
        st.session_state.cotacoes.get(x)

    )


    df["Investido"] = (

        df["Quantidade"]
        *
        df["Preço Pago"]

    )



    df["Valor Atual"] = (

        df["Quantidade"]
        *
        df["Preço Atual"]

    )



    df["Resultado"] = (

        df["Valor Atual"]
        -
        df["Investido"]

    )



    resumo = df.groupby(
        "Ativo"
    ).agg(

        Quantidade=("Quantidade","sum"),

        Investido=("Investido","sum"),

        Atual=("Valor Atual","sum"),

        Resultado=("Resultado","sum")

    ).reset_index()



    resumo["Rentabilidade %"] = (

        resumo["Resultado"]
        /
        resumo["Investido"]
        *
        100

    )



    patrimonio = resumo["Atual"].sum()

    investido = resumo["Investido"].sum()

    lucro = patrimonio-investido



    c1,c2,c3 = st.columns(3)



    c1.metric(

        "Patrimônio Atual",

        f"R$ {patrimonio:,.2f}"

    )


    c2.metric(

        "Total Investido",

        f"R$ {investido:,.2f}"

    )


    c3.metric(

        "Resultado",

        f"R$ {lucro:,.2f}",

        delta=f"{lucro/investido*100:.2f}%"

    )



    st.subheader(
        "Posição dos Ativos"
    )


    st.dataframe(

        resumo,

        use_container_width=True

    )



    st.subheader(
        "Distribuição da Carteira"
    )


    st.bar_chart(

        resumo.set_index("Ativo")["Atual"]

    )



else:


    st.info(
        "Cadastre seu primeiro aporte."
    )



# =====================================
# EDIÇÃO
# =====================================


st.divider()


st.header(
    "✏️ Histórico de Aportes"
)


st.session_state.aportes = st.data_editor(

    st.session_state.aportes,

    num_rows="dynamic",

    use_container_width=True

)



# =====================================
# NOTAS
# =====================================


st.divider()


st.header(
    "📚 Estudos e Teses"
)


st.session_state.notas = st.text_area(

    "Anotações",

    value=st.session_state.notas,

    height=250

)
