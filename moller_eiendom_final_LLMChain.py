import streamlit as st
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
import fitz  # PyMuPDF
import base64



# Funksjon for innlasting av pdf
def load_pdf_content(pdf_path):
    """Load and return the text content of a PDF document."""
    text = ''
    with fitz.open(pdf_path) as doc:
        for page in doc:
            text += page.get_text()
    return text

# Load PDF document content
pdf_path_leietakerhandbok_generell = 'leietakerhandbok-moller.pdf'
leietakerhandbok_generell = load_pdf_content(pdf_path_leietakerhandbok_generell)

pdf_path_harbitz_fellesarealer = 'Retningslinjer-for-bruk-av-fellesarealer.pdf'
veiledning_harbitz_fellesarealer = load_pdf_content(pdf_path_harbitz_fellesarealer)

pdf_path_harbitz_leietakerinfo = 'Informasjon til leietagere på Harbitz Torg - Harbitz Torg.pdf'
harbitz_leietakerinfo = load_pdf_content(pdf_path_harbitz_leietakerinfo)

pdf_path_brukerveiledning_hafslund = 'BRUKERVEILEDNING-Harbitz-Torg-Driftsteam-Hafslund.pdf'
brukerveiledning_hafslund = load_pdf_content(pdf_path_brukerveiledning_hafslund)



# def load_sitemap_docs(url_site_map):
#     sitemap_loader = SitemapLoader(web_path=url_site_map,      
#         # filter_urls=filter_urls
#         )
    
#     docs = sitemap_loader.load()
    
#     file1 = open("myfile.txt", 'a')
    
#     for i in range(len(docs)):
#         file1.write(docs[i].page_content + "\n\n")
    

# #Load url sitemap content
# url = "https://mollereiendom.no/"
# url_site_map = f"{url}/sitemap_index.xml"
# docs = load_sitemap_docs(url_site_map)
# print(docs)



# Sett opp Streamlit-sidekonfigurasjon
LOGO_IMAGE = "moller_eiendom_logo.png"
st.set_page_config(page_title="Møller Eiendoms leietakerchat", page_icon=LOGO_IMAGE, layout="wide")

st.markdown(
    """
    <style>
    .container {
        display: flex;
        align-items: center; /* Adjusts vertical alignment */
        border-bottom: 1px solid #ccc; /* Thin gray line */
        padding-bottom: 30px; /* Adds some space below the text and above the line */
        margin-bottom: 20px; /* Adds space below the line */
    }
    .logo-text {
        font-weight: 700 !important;
        font-size: 46px !important;
        color: #000000 !important;
    }
    .sub-text {
        font-weight: 300 !important;
        font-size: 32px !important;
        color: #000000 !important;
    }
    .logo-img {
        max-height: 80%; 
        max-width: 80%;
    }
    
    /* New style to reduce top padding */
    .main .block-container {
        padding-top: 50px !important; /* Reduces top padding. Adjust the value as needed */
    }
    
    </style>

    """,
    unsafe_allow_html=True
)

st.markdown(
    f"""
    <div class="container">
        <img class="logo-img" src="data:image/png;base64,{base64.b64encode(open(LOGO_IMAGE, "rb").read()).decode()}" style="width:200px; height:auto;">
        <div style="margin-left: 25px;">
            <p class="logo-text" style="margin-bottom: 0;">Ida, Møller Eiendoms assistent for leietakere</p>
            <p class="sub-text" style="margin-top: 0;">En assistent som kan svare på spørsmål fra leietakerhåndboken og annen leietakerinformasjon for Harbitz Torg, særlig rettet mot Hafslund</p>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)



#Systemmelding
prompt = PromptTemplate(
    input_variables=["chat_history", "question"],
    template="""
        You are mainly interacting in Norwegian.
        You are a helpful AI assistant talking with a human.
        If you do not know an answer, just say 'I don't know', do not make up an answer.
        Use this document as a basis to answer general questions about the lease agreement: """ + leietakerhandbok_generell + """
        Use this document to answer more specific questions about the lease agreement for Harbitz Torg: """ + harbitz_leietakerinfo + """
        Use this document to answer questions about the use of common areas of Harbitz Torg, especially for commersial use """ + veiledning_harbitz_fellesarealer + """
        Use this document to answer questions specifically about Hafslund's lease agreement at Harbitz Torg """ + brukerveiledning_hafslund + """
        Always cite the source of your answer.
        
        chat_history: {chat_history},
        Human: {question}
        AI:"""
)

# Initialiser ChatOpenAI-modellen, top_p? Hva er standardverdi?
API = st.secrets["API_KEY"]
chat = ChatOpenAI(temperature=0.5, model_name="gpt-4-0125-preview", openai_api_key=API, verbose=True)

#Initialiserer minne
memory=ConversationBufferMemory(memory_key="chat_history")

llm_chain = LLMChain(
    llm=chat,
    memory=memory,
    prompt=prompt
)

if "chat_history" not in st.session_state:
    st.session_state.chat_history=[]
else:
    for message in st.session_state.chat_history:
        memory.save_context({"input":message["Human"]},{"outputs":message["AI"]})

if "message" not in st.session_state:
    st.session_state.message = [{"role":"assistant","content":"Hei! Jeg er Ida, Møller Eiendoms assistent for leietakere. Hva kan jeg hjelpe deg med?"}]
for message1 in st.session_state.message:
    with st.chat_message(message1["role"]):
        st.markdown(message1["content"])

if prompt:=st.chat_input("Din forespørsel"):
        with st.chat_message("user"):
            st.markdown(prompt)
            st.session_state.message.append({"role":"user","content":prompt})
            
        with st.chat_message("assistant"):
                with st.spinner("Laster..."):
                    response=llm_chain.predict(question=prompt)
                    st.write(response)
        st.session_state.message.append({"role":"assistant","content":response})
        message={"Human":prompt,"AI":response}
        st.session_state.chat_history.append(message)
