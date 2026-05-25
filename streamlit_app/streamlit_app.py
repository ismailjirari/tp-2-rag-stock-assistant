# streamlit_app/streamlit_app.py

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'app'))

import streamlit as st
from rag_pipeline import ask_question

# ─── Configuration Page ───────────────────────────────────────────────────────
st.set_page_config(
    page_title="RAG Stock Assistant – GOTS 7.0",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🌿 RAG Stock Assistant")
    st.markdown("---")
    st.markdown("### 📖 À propos")
    st.markdown("""
    Assistant IA basé sur le standard **GOTS 7.0**  
    (Global Organic Textile Standard).
    """)
    st.markdown("---")
    st.markdown("### 🛠️ Technologies")
    st.markdown("""
    - 🔍 **Qdrant** — Vector Database  
    - 🧠 **BAAI/bge-m3** — Embeddings  
    - 🤖 **Llama 3.3 70B** — OpenRouter  
    - 🎨 **Streamlit** — Interface  
    """)
    st.markdown("---")
    st.markdown("### ⚙️ Paramètres")
    top_k = st.slider("Nombre de sources", min_value=1, max_value=10, value=5)
    st.markdown("---")
    if st.button("🗑️ Vider l'historique", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# ─── Header ───────────────────────────────────────────────────────────────────
st.title("🌿 RAG Stock Assistant")
st.caption("Posez vos questions sur le Global Organic Textile Standard (GOTS 7.0)")
st.divider()

# ─── Initialisation session state ─────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

# ─── Message de bienvenue si historique vide ──────────────────────────────────
if not st.session_state.messages:
    with st.chat_message("assistant"):
        st.markdown("""
Bonjour ! 👋 Je suis votre assistant spécialisé sur le **standard GOTS 7.0**.

Vous pouvez me poser des questions comme :
- 🌱 *Quelles sont les fibres autorisées par GOTS ?*
- 📋 *Quelles sont les exigences de certification ?*
- 🧪 *Quels produits chimiques sont interdits ?*
- 👷 *Quelles sont les exigences sociales pour les travailleurs ?*
- 🏷️ *Comment fonctionne l'étiquetage GOTS ?*
        """)

# ─── Affichage historique ─────────────────────────────────────────────────────
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ─── Input utilisateur ────────────────────────────────────────────────────────
question = st.chat_input("💬 Posez votre question sur le standard GOTS...")

if question:
    # Afficher la question
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    # Générer la réponse
    with st.chat_message("assistant"):
        with st.spinner("🔍 Recherche et analyse en cours..."):
            try:
                result = ask_question(question, top_k=top_k)
                answer = result["answer"]
                sources = result["sources"]

                # Afficher la réponse
                st.markdown(answer)

                # Afficher les sources
                if sources:
                    with st.expander(f"📚 {len(sources)} source(s) utilisée(s)", expanded=False):
                        for i, src in enumerate(sources, 1):
                            col1, col2 = st.columns([1, 5])
                            with col1:
                                st.metric(label=f"Source {i}", value=f"{src['score']:.3f}")
                            with col2:
                                st.caption(src['chunk'][:300] + "...")
                            if i < len(sources):
                                st.divider()

                # Sauvegarder dans l'historique
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer
                })

            except Exception as e:
                error_msg = f"❌ Erreur : {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_msg
                })