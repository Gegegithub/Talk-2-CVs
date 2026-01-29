import streamlit as st
from rag_core import answer

# Configuration de la page
st.set_page_config(
    page_title="RAG Multimodal - Gemini",
    
    layout="wide"
)

# CSS personnalisé
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        background: linear-gradient(90deg, #4285F4, #EA4335, #FBBC05, #34A853);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        padding: 1rem 0;
    }
    .sub-header {
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
    }
    .response-box {
        background-color: #f0f7ff;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #4285F4;
        min-height: 200px;
    }
    .score-card {
        background-color: #fff;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #e0e0e0;
        margin-bottom: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<p class="main-header">RAG Multimodal</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Gemini + pgvector | Recherche intelligente sur vos documents</p>', unsafe_allow_html=True)

# Barre de recherche centrée
col1, col2, col3 = st.columns([1, 3, 1])
with col2:
    query = st.text_input("", placeholder="Posez votre question ici...", label_visibility="collapsed")
    search_button = st.button(" Rechercher", use_container_width=True, type="primary")

# Résultats
if search_button and query:
    with st.spinner('Recherche en cours...'):
        resp, rows = answer(query, k=5)

        st.markdown("---")

        # Layout deux colonnes : Réponse à gauche, Sources à droite
        col_left, col_right = st.columns([3, 2])

        # Colonne gauche : Réponse
        with col_left:
            st.markdown("###  Réponse")
            st.markdown(f'<div class="response-box">{resp}</div>', unsafe_allow_html=True)

        # Colonne droite : Sources et scores
        with col_right:
            st.markdown("###  Sources & Scores")

            for i, (src, chunk, modality, score) in enumerate(rows):
                icon = "📄" if modality == "text" else "🖼️"
                filename = src.split('/')[-1].split('\\')[-1]

                # Score avec barre de progression
                st.markdown(f"**{icon} Source {i+1}:** {filename}")
                st.progress(float(score), text=f"Pertinence: {score:.1%}")

                with st.expander("Voir l'extrait"):
                    st.caption(f"Type: {modality.upper()}")
                    st.info(chunk[:300] + "..." if len(chunk) > 300 else chunk)

                st.markdown("")

# Footer
st.markdown("---")
st.markdown(
    '<p style="text-align: center; color: #888; font-size: 0.8rem;">Powered by Gemini + pgvector</p>',
    unsafe_allow_html=True
)
