import logging
import streamlit as st

from config import DEFAULT_CATALOGUE, POLICY
from core import ProductStore, answer_query, load_catalogue, load_policy

logging.basicConfig(level=logging.INFO)

st.set_page_config(page_title="TrustCart AI", page_icon="🛍️", layout="wide")

st.markdown("""
<style>
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
    }
    .hero {
        padding: 18px 22px;
        border-radius: 14px;
        background: linear-gradient(135deg, #182848, #4b6cb7);
        color: white;
        margin-bottom: 18px;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
    <h2 style="margin: 0; color: white;">TrustCart AI</h2>
    <p style="margin: 6px 0 0; color: #e2e8f0;">
        Grounded Conversational Shopping Assistant that Doesn't Lie
    </p>
</div>
""", unsafe_allow_html=True)


@st.cache_resource(show_spinner="Validating official catalogue and policy...")
def init_store():
    products = load_catalogue(DEFAULT_CATALOGUE)
    policy = load_policy(POLICY)
    index = ProductStore(products)
    return products, index, policy


with st.sidebar:
    st.header("Settings")
    if st.button("Reset conversation"):
        st.session_state["messages"] = []
        st.session_state["history"] = []
        st.rerun()

    st.markdown("---")
    st.markdown("**Synthetic catalogue grounded: 1 October 2026**")
    st.caption("Answers reflect strict catalogue constraint checks and cited policy verification.")

try:
    products, index, policy = init_store()
except FileNotFoundError:
    st.error("Default data files are not configured.")
    st.info("Copy catalogue.csv and policy.md from the challenge pack into FULL_CODE/data/.")
    st.stop()

st.caption(f"Validated records: {len(products):,} products • {len(policy)} policy subsections")
st.session_state.setdefault("messages", [])
st.session_state.setdefault("history", [])

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["text"])

prompt = st.chat_input("Ask about products, price, stock or store policy...", max_chars=500)
if prompt:
    st.session_state.messages.append({"role": "user", "text": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Checking catalogue evidence..."):
            answer = answer_query(prompt, st.session_state.history, products, index, policy)
        st.markdown(answer.answer_text)

        if answer.cited_product_ids:
            st.markdown("**Product IDs:**")
            for product_id in answer.cited_product_ids:
                st.write(product_id)

    st.session_state.messages.append({"role": "assistant", "text": answer.answer_text})
    st.session_state.history.append((prompt, answer.answer_text))

if not st.session_state.messages:
    st.markdown("### Try these questions")
    st.write("- `65W charger dikhao`")
    st.write("- `What is the return window?`")
    st.write("- `Do you sell iPhones?`")
    st.write("- `Sanchayo NimbusMax steel container set stock me hai?`")
