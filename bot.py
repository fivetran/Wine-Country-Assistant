# *********************************************************
# CODE BLOCK 1: START STREAMLIT, INITIAL SETUP, UI CONFIG
# *********************************************************


import streamlit as st
from api import get_answer

# Initialize session state variables
if 'use_dataset_as_context' not in st.session_state:
    st.session_state['use_dataset_as_context'] = False

model = None

# UI Configuration
st.set_page_config(layout="wide")
st.title(":wine_glass: California Wine Country Visit Assistant :wine_glass:")
st.caption("0.5.5.3.8")

# Introductory text
st.write(
    """I'm an interactive California Wine Country Visit Assistant. A bit about me...I'm a RAG-based, Gen AI app **built with and powered by Fivetran, Databricks, Mosaic AI and Streamlit** and a custom, structured dataset!"""
)

st.caption(
    """Let me help plan your trip to California wine country. Using the dataset you just moved into the Databricks Lakehouse with Fivetran, I'll assist you with winery and vineyard information and provide visit recommendations from numerous models available in the Databricks Data Intelligence Platform (including DBRX Instruct). You can even pick the model you want to use or try out all the models. The dataset includes over **700 wineries and vineyards** across all CA wine-producing regions including the North Coast, Central Coast, Central Valley, South Coast and various AVAs sub-AVAs. Let's get started!"""
)

# *****************************************************************
# CODE BLOCK 2: USER INPUT MGMT, PROCESSING AND RESPONSE HANDLING
# *****************************************************************

# Initialize or retrieve the current user question
if 'user_question' not in st.session_state:
    st.session_state['user_question'] = ""

if 'reset_key' not in st.session_state:
    st.session_state['reset_key'] = 0

if st.button('Reset conversation', key='reset_conversation_button'):
    st.session_state['conversation_state'] = []
    st.session_state['user_question'] = ""
    checkbox_state = st.session_state['use_dataset_as_context']
    st.session_state['reset_key'] += 1
    st.session_state['use_dataset_as_context'] = checkbox_state
    st.experimental_rerun()

processing_placeholder = st.empty()
question = st.text_input(
    "", 
    value=st.session_state['user_question'], 
    placeholder="Message your personal CA Wine Country Visit Assistant...", 
    key=f"text_input_{st.session_state['reset_key']}", 
    label_visibility="collapsed"
)

# Handle user queries
if question:
    if 'user_question' not in st.session_state or st.session_state['user_question'] != question:
        st.session_state['user_question'] = question
        processing_placeholder.caption(f"I'm thinking about your question: {question}")
    processing_placeholder.empty()
    st.session_state['user_question'] = ""

# *****************************************************************
# CODE BLOCK 3: MODEL SELECTION AND DATA CONTEXT
# *****************************************************************

model = st.sidebar.selectbox('Select a Foundation Large Language Model:', (
    'databricks-dbrx-instruct',
    'databricks-meta-llama-3-70b-instruct',
    'databricks-mixtral-8x7b-instruct',
    'databricks-llama-2-70b-chat'
))

st.sidebar.checkbox(
    'Use your Fivetran dataset as context?', 
    value=st.session_state['use_dataset_as_context'], 
    key="dataset_context",
    on_change=lambda: st.session_state.update({'use_dataset_as_context': not st.session_state['use_dataset_as_context']})
)

st.sidebar.caption("""
I use **Databricks Mosaic AI** which provides instant access to industry-leading large language models (LLMs), including **DBRX Instruct**, trained by researchers at companies like Mistral, Meta and Databricks.

Mosaic AI also offers models that Databricks has fine-tuned for specific use cases. Since these LLMs are fully hosted and managed by Databricks, using them requires no setup. My data stays within Databricks, giving me the performance, scalability, and governance you expect.
""")

# **************************************************************************
# CODE BLOCK 4: ADDITIONAL UI ELEMENTS, CONVERSATION HISTORY INITIALIZATION
# **************************************************************************

st.sidebar.write("".join(["\n"]*12))
# TODO - update this image
url = 'https://i.imgur.com/9lS8Y34.png'

col1, col2, col3 = st.sidebar.columns([1,2,1.3])
with col2:
    st.image(url, width=150)

caption_col1, caption_col2, caption_col3 = st.sidebar.columns([0.22,2,0.005])
with caption_col2:
    st.caption("Fivetran, Databricks, Mosaic AI & Streamlit")

# Initialize conversation history
if 'conversation_state' not in st.session_state:
    st.session_state['conversation_state'] = []

conversation_state = st.session_state['conversation_state']

# **************************************************************************
# CODE BLOCK 5: INTERACTION LOGIC W/ MOSAIC AI AND CONVO HISTORY MGMT
# **************************************************************************

selection = ":green[**_I am_**]" if st.session_state['use_dataset_as_context'] else ":red[**_I am NOT_**]"
st.caption(f"Please note that {selection} using your Fivetran dataset as context. All models are very creative and can make mistakes. Consider checking important information before heading out to wine country.")

# Process user queries
if question:
    try:
        response = get_answer(st.session_state['use_dataset_as_context'], model, question)
        conversation_state.append((f"CA Wine Country Visit Assistant ({model}):", response))
        conversation_state.append(("You:", question))
    except Exception as e:
        st.warning(f"An error occurred while processing your question: {e}")

# Display conversation history
if conversation_state:
    for i in reversed(range(len(conversation_state))):
        label, message = conversation_state[i]
        if i % 2 == 0:
            st.markdown(f":wine_glass: **{label}**")
            st.info(message)
        else:
            st.markdown(f":question: **{label}**")
            st.success(message)

st.empty()
