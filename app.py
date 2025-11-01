import streamlit as st
import pandas as pd
from utils import get_collection
from bson.objectid import ObjectId
import plotly.express as px
from datetime import datetime
from populate_db import populate

st.set_page_config(page_title="E-Shop Brasil - Data Manager", layout="wide")
coll = get_collection()
st.title("E-Shop Brasil — Gerenciamento e Análise (MongoDB + Streamlit)")

menu = st.sidebar.radio("Menu", ["Visão Geral", "Inserir Dados", "Consultar", "Transformar", "Visualizar"])

if menu == "Visão Geral":
    st.subheader("Resumo do Banco de Dados")
    total = coll.count_documents({})
    st.metric("Total de pedidos", total)
    if st.button("Popular com dados de exemplo (300)"):
        populate(300)
        st.success("Banco populado com sucesso!")

if menu == "Inserir Dados":
    st.subheader("Inserção manual")
    name = st.text_input("Nome do cliente")
    email = st.text_input("E-mail")
    total = st.number_input("Valor total", 0.0)
    if st.button("Salvar pedido"):
        coll.insert_one({"customer": {"name": name, "email": email}, "order_total": total, "order_date": datetime.now()})
        st.success("Pedido inserido.")

if menu == "Consultar":
    st.subheader("Consultar pedidos")
    q = st.text_input("Buscar por nome ou e-mail")
    if q:
        data = list(coll.find({"$or": [{"customer.name": q}, {"customer.email": q}]}))
    else:
        data = list(coll.find().limit(50))
    if data:
        df = pd.json_normalize(data)
        st.dataframe(df)

if menu == "Transformar":
    st.subheader("Concatenar nome e e-mail")
    if st.button("Executar concatenação"):
        result = coll.update_many({}, [{"$set": {"customer.full_name_email": {"$concat": ["$customer.name", " - ", "$customer.email"]}}}])
        st.success(f"Atualizados {result.modified_count} documentos.")

if menu == "Visualizar":
    st.subheader("Visualização por status")
    data = list(coll.find())
    if data:
        df = pd.json_normalize(data)
        if "order_total" in df.columns:
            fig = px.histogram(df, x="order_total", nbins=10, title="Distribuição dos Valores de Pedido")
            st.plotly_chart(fig)
