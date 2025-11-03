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

# Menu: incluir CONSULTAR/EDITAR (único item para essa funcionalidade)
menu = st.sidebar.radio("Menu", ["Visão Geral", "Inserir Dados", "Consultar/Editar", "Transformar", "Visualizar"])

# -------------------------
# VISÃO GERAL
# -------------------------
if menu == "Visão Geral":
    st.subheader("Resumo do Banco de Dados")
    try:
        total = coll.count_documents({})
    except Exception as e:
        total = 0
        st.error(f"Erro ao conectar ao MongoDB: {e}")
    st.metric("Total de pedidos", total)
    if st.button("Popular com dados de exemplo (300)"):
        populate(300)
        st.success("Banco populado com sucesso!")

# -------------------------
# INSERIR DADOS
# -------------------------
import uuid

if menu == "Inserir Dados":
    st.subheader("Inserção manual")
    name = st.text_input("Nome do cliente")
    email = st.text_input("E-mail")
    total_val = st.number_input("Valor total", 0.0, step=0.01)
    category = st.selectbox("Categoria (opcional)", ["Eletrônicos", "Moda", "Casa", "Beleza", "Esportes"])

    if st.button("Salvar pedido"):
        order_id = str(uuid.uuid4())[:8]  # 🔹 gera ID único e curto, ex: "a1b2c3d4"
        doc = {
            "order_id": order_id,
            "customer": {"name": name or "Anon", "email": email or ""},
            "items": [{
                "sku": f"SKU-{order_id}",
                "name": "Item Exemplo",
                "category": category,
                "price": float(total_val or 0),
                "quantity": 1
            }],
            "order_total": float(total_val or 0),
            "order_date": datetime.now(),
            "status": "processing",
            "shipping_region": ""
        }
        coll.insert_one(doc)
        st.success(f"Pedido inserido com sucesso! (ID: {order_id})")


# -------------------------
# CONSULTAR / EDITAR
# -------------------------
if menu == "Consultar/Editar":
    st.header("🔍 Consulta, edição e exclusão de pedidos")

    # ----------------------------
    # MODO AVANÇADO: edição em massa (checkbox)
    # ----------------------------
    if st.checkbox("Editar dados diretamente (modo avançado)"):
        st.subheader("✏️ Edição em massa (primeiros 50 documentos)")
        data = list(coll.find().sort("order_date", -1).limit(50))
        if data:
            df_bulk = pd.json_normalize(data)
            # Colunas editáveis
            cols_to_edit = ["order_id", "customer.name", "customer.email", "order_total", "status"]
            # Garantir colunas existentes
            for c in cols_to_edit:
                if c not in df_bulk.columns:
                    df_bulk[c] = ""
            # Exibir data editor (planilha)
            edited_df = st.data_editor(
                df_bulk[cols_to_edit],
                num_rows="fixed",
                use_container_width=True,
                key="bulk_editor"
            )

            if st.button("💾 Salvar alterações em massa"):
                updated = 0
                for _, row in edited_df.iterrows():
                    order_id = row.get("order_id")
                    if not order_id:
                        continue
                    coll.update_one(
                        {"order_id": order_id},
                        {"$set": {
                            "customer.name": row.get("customer.name", "") or "",
                            "customer.email": row.get("customer.email", "") or "",
                            "order_total": float(row.get("order_total") or 0),
                            "status": row.get("status", "") or ""
                        }}
                    )
                    updated += 1
                st.success(f"Alterações em massa salvas: {updated} documentos atualizados.")
        else:
            st.info("Ainda não há documentos no banco para editar em massa.")

    st.markdown("---")

    # ----------------------------
    # BUSCAR PEDIDOS ESPECÍFICOS
    # ----------------------------
    st.subheader("🔎 Buscar pedidos específicos")
    search_term = st.text_input("Pesquisar por order_id, e-mail ou status (ex: delivered)", key="search_input")

    if st.button("Pesquisar"):
        if search_term.strip() == "":
            docs = list(coll.find().sort("order_date", -1).limit(20))
        else:
            docs = list(
                coll.find({
                    "$or": [
                        {"order_id": search_term},
                        {"customer.email": search_term},
                        {"status": search_term}
                    ]
                }).sort("order_date", -1).limit(200)
            )

        if docs:
            df = pd.json_normalize(docs)
            if "order_date" in df.columns:
                df["order_date"] = pd.to_datetime(df["order_date"])
            # Mostrar tabela resultado (somente leitura)
            st.dataframe(
                df[["order_id", "customer.name", "customer.email", "order_total", "status", "order_date"]].fillna(""),
                use_container_width=True
            )
        else:
            st.info("Nenhum pedido encontrado com o termo pesquisado.")

    st.markdown("---")

    # ----------------------------
    # EDIÇÃO DOS ÚLTIMOS PEDIDOS INSERIDOS (modo planilha)
    # ----------------------------
    st.subheader("🛠️ Editar os últimos pedidos inseridos (10)")

    last_docs = list(coll.find().sort("order_date", -1).limit(10))
    if last_docs:
        df_last = pd.json_normalize(last_docs)
        # Garantir colunas necessárias
        for c in ["order_id", "customer.name", "customer.email", "order_total", "status"]:
            if c not in df_last.columns:
                df_last[c] = ""

        st.info("Edite diretamente na tabela abaixo (célula-a-célula). Depois clique em 'Salvar alterações nos últimos pedidos'.")
        df_editable = st.data_editor(
            df_last[["order_id", "customer.name", "customer.email", "order_total", "status"]],
            num_rows="fixed",
            use_container_width=True,
            key="last_editor"
        )

        if st.button("💾 Salvar alterações nos últimos pedidos"):
            updated_last = 0
            for _, row in df_editable.iterrows():
                order_id = row.get("order_id")
                if not order_id:
                    continue
                coll.update_one(
                    {"order_id": order_id},
                    {"$set": {
                        "customer.name": row.get("customer.name", "") or "",
                        "customer.email": row.get("customer.email", "") or "",
                        "order_total": float(row.get("order_total") or 0),
                        "status": row.get("status", "") or ""
                    }}
                )
                updated_last += 1
            st.success(f"Alterações salvas com sucesso! {updated_last} pedidos atualizados.")
    else:
        st.warning("Ainda não há pedidos recentes no banco para editar.")

    st.markdown("---")

    # ----------------------------
    # EXCLUSÃO DE PEDIDO ESPECÍFICO
    # ----------------------------
    st.subheader("❌ Excluir pedido pelo order_id")
    delete_id = st.text_input("Digite o order_id para excluir um pedido específico:", key="delete_input")
    if st.button("Excluir pedido"):
        if delete_id.strip() == "":
            st.error("Por favor, informe um order_id válido.")
        else:
            result = coll.delete_one({"order_id": delete_id})
            if result.deleted_count > 0:
                st.success("Pedido excluído com sucesso! 🗑️")
            else:
                st.error("Pedido não encontrado. Verifique o order_id digitado.")

# -------------------------
# TRANSFORMAR (concatenar)
# -------------------------
if menu == "Transformar":
    st.subheader("Concatenar nome e e-mail")
    if st.button("Executar concatenação"):
        result = coll.update_many({}, [{"$set": {"customer.full_name_email": {"$concat": ["$customer.name", " - ", {"$ifNull": ["$customer.email", ""]}]}}}])
        st.success(f"Atualizados {result.modified_count} documentos.")

# -------------------------
# VISUALIZAR
# -------------------------
if menu == "Visualizar":
    st.subheader("Visualização por status")
    data = list(coll.find())
    if data:
        df = pd.json_normalize(data)
        if "order_total" in df.columns:
            # converter order_total para numérico, ignorando NaN
            df["order_total"] = pd.to_numeric(df["order_total"], errors="coerce").fillna(0)
            fig = px.histogram(df, x="order_total", nbins=12, title="Distribuição dos Valores de Pedido")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Nenhum valor de pedido disponível para visualização.")
    else:
        st.info("Banco vazio. Popule dados para ver gráficos.")
