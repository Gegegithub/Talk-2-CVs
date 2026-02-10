"""
Interface Streamlit pour le Local Recruiter Assistant
Style inspiré de Gemini
"""
import streamlit as st
from pathlib import Path

from config.settings import DATA_DIR
from utils.pdf_processor import PDFProcessor
from utils.vector_store import get_vector_store

# Configuration de la page
st.set_page_config(
    page_title="Local Recruiter Assistant",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé style Gemini
st.markdown("""
<style>
    /* Masquer seulement le menu hamburger, pas le toggle sidebar */
    #MainMenu {visibility: hidden;}

    /* Container principal */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 0;
        max-width: 900px;
    }

    /* Zone de bienvenue centrée */
    .welcome-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        min-height: 50vh;
        text-align: center;
    }

    .welcome-icon {
        font-size: 3rem;
        margin-bottom: 1rem;
    }

    .welcome-title {
        font-size: 2.2rem;
        font-weight: 400;
        color: #E8EAED;
        margin-bottom: 0.5rem;
    }

    .welcome-subtitle {
        font-size: 2.2rem;
        font-weight: 400;
        color: #9AA0A6;
        margin-bottom: 2rem;
    }

    /* Boutons de suggestions */
    .suggestion-container {
        display: flex;
        flex-wrap: wrap;
        justify-content: center;
        gap: 0.75rem;
        margin-top: 1.5rem;
    }

    .stButton > button {
        background-color: #303134;
        color: #E8EAED;
        border: 1px solid #5F6368;
        border-radius: 24px;
        padding: 0.6rem 1.2rem;
        font-size: 0.9rem;
        transition: background-color 0.2s;
    }

    .stButton > button:hover {
        background-color: #3C4043;
        border-color: #8AB4F8;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #1E1E1E;
    }

    [data-testid="stSidebar"] .stMetric {
        background-color: #303134;
        padding: 1rem;
        border-radius: 12px;
    }

    /* Chat messages */
    .stChatMessage {
        background-color: transparent;
    }

    /* Source box */
    .source-box {
        background-color: #303134;
        padding: 1rem;
        border-radius: 12px;
        margin-top: 0.5rem;
    }

    /* Footer */
    .footer-text {
        text-align: center;
        color: #9AA0A6;
        font-size: 0.8rem;
        padding: 1rem;
    }
</style>
""", unsafe_allow_html=True)


def save_uploaded_file(uploaded_file) -> Path:
    """Sauvegarde un fichier uploadé dans le dossier data/"""
    file_path = DATA_DIR / uploaded_file.name
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return file_path


def ingest_single_pdf(pdf_path: Path) -> int:
    """Ingère un seul PDF et retourne le nombre de chunks"""
    processor = PDFProcessor()
    chunks = processor.process_pdf(pdf_path)

    if chunks:
        vectorstore = processor.vector_store.get_vectorstore()
        vectorstore.add_documents(chunks)

    return len(chunks)


# Sidebar - Statistiques (forcer l'affichage)
st.sidebar.title("📊 Base de CVs")

with st.sidebar:
    try:
        vector_store = get_vector_store()
        stats = vector_store.get_stats()

        col1, col2 = st.columns(2)
        with col1:
            st.metric("CVs indexés", stats["total_chunks"] // 5 or 0)  # Approximation
        with col2:
            status_emoji = "🟢" if stats["status"] == "ready" else "🔴"
            st.metric("Statut", status_emoji)

        if stats["total_chunks"] > 0:
            with st.expander("⚙️ Options"):
                if st.button("🗑️ Vider la base", use_container_width=True):
                    vector_store.reset()
                    st.rerun()

    except Exception as e:
        st.error(f"Erreur : {e}")

    st.divider()

    st.markdown("### 💡 Exemples")
    st.caption("• Qui maîtrise Python et SQL ?")
    st.caption("• Trouve un profil Data Engineer")
    st.caption("• Expérience en Machine Learning ?")

    st.divider()
    st.caption("🔒 100% Local - RGPD Compliant")
    st.caption("🤖 Ollama (Llama 3.1)")
    st.caption("💾 ChromaDB + LangChain")


# Initialiser l'historique
if "messages" not in st.session_state:
    st.session_state.messages = []

# Zone principale
if not st.session_state.messages:
    # Écran d'accueil style Gemini
    st.markdown("""
    <div class="welcome-container">
        <div class="welcome-icon">🎯</div>
        <div class="welcome-title">Bonjour,</div>
        <div class="welcome-subtitle">Trouvons le candidat idéal</div>
    </div>
    """, unsafe_allow_html=True)

    # Boutons de suggestions
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("🐍 Expert Python", use_container_width=True):
            st.session_state.suggestion = "Qui a de l'expérience en Python ?"
            st.rerun()

    with col2:
        if st.button("🤖 Machine Learning", use_container_width=True):
            st.session_state.suggestion = "Trouve les profils Machine Learning"
            st.rerun()

    with col3:
        if st.button("☁️ Cloud & DevOps", use_container_width=True):
            st.session_state.suggestion = "Qui maîtrise le Cloud ou DevOps ?"
            st.rerun()

    with col4:
        if st.button("📊 Data Engineer", use_container_width=True):
            st.session_state.suggestion = "Trouve un profil Data Engineer"
            st.rerun()

else:
    # Afficher l'historique des messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

            if message["role"] == "assistant" and "sources" in message:
                if message["sources"]:
                    with st.expander("📎 Sources consultées"):
                        for source in message["sources"]:
                            st.write(f"**{source['file']}** (chunk {source['chunk_id']})")
                            st.caption(source['preview'])

# Input utilisateur avec épingle pour fichiers
chat_input = st.chat_input(
    "Posez votre question ou attachez des CVs 📎",
    accept_file="multiple",
    file_type=["pdf"]
)

# Traiter une suggestion cliquée
if "suggestion" in st.session_state:
    prompt = st.session_state.suggestion
    del st.session_state.suggestion

    from agents.recruiter_rag import answer

    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("🔍 Recherche..."):
            try:
                result = answer(prompt, st.session_state.messages)
                response = result["answer"]
                sources = result.get("sources", [])

                st.markdown(response)

                if sources:
                    with st.expander("📎 Sources consultées"):
                        for source in sources:
                            st.write(f"**{source['file']}** (chunk {source['chunk_id']})")
                            st.caption(source['preview'])

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response,
                    "sources": sources
                })
            except Exception as e:
                st.error(f"❌ Erreur : {e}")

# Traiter l'input du chat
if chat_input:
    prompt = chat_input.text if hasattr(chat_input, 'text') else str(chat_input)
    files = chat_input.files if hasattr(chat_input, 'files') else None

    # Traiter les fichiers uploadés
    if files:
        total_chunks = 0
        file_names = []

        for uploaded_file in files:
            file_path = save_uploaded_file(uploaded_file)
            chunks_count = ingest_single_pdf(file_path)
            total_chunks += chunks_count
            file_names.append(uploaded_file.name)

        upload_msg = f"✅ {len(files)} CV(s) importé(s) : {', '.join(file_names)}"
        st.session_state.messages.append({"role": "assistant", "content": upload_msg})

        with st.chat_message("assistant"):
            st.success(upload_msg)

    # Traiter la question
    if prompt and prompt.strip():
        from agents.recruiter_rag import answer

        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("🔍 Recherche dans les CVs..."):
                try:
                    result = answer(prompt, st.session_state.messages)
                    response = result["answer"]
                    sources = result.get("sources", [])

                    st.markdown(response)

                    if sources:
                        with st.expander("📎 Sources consultées"):
                            for source in sources:
                                st.write(f"**{source['file']}** (chunk {source['chunk_id']})")
                                st.caption(source['preview'])

                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": response,
                        "sources": sources
                    })
                except Exception as e:
                    st.error(f"❌ Erreur : {e}")

    if files:
        st.rerun()
