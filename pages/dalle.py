import streamlit as st
import openai
import os
import speech_recognition as sr
from langchain.chat_models import ChatOpenAI
from langchain import LLMChain
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.prompts import (
    ChatPromptTemplate, 
    MessagesPlaceholder, 
    SystemMessagePromptTemplate, 
    HumanMessagePromptTemplate
)
from langchain import OpenAI, ConversationChain, LLMChain, PromptTemplate
from langchain.memory import ConversationBufferWindowMemory
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from openai import OpenAI
from io import BytesIO
from PIL import Image



os.environ["OPENAI_API_KEY"] = ''
st.set_page_config(page_title="LLM", page_icon="🤖", layout="wide", initial_sidebar_state="expanded")
left, core, right = st.columns([1, 1, 1])
col1, col2 = st.columns(spec=2)
lleft, _, center, _, _ = st.columns([1, 1, 1, 1, 1])
option = st.selectbox(
    'Choose an action:',
    ('Image Generation', 'Image Variations')
)
uploaded_file = st.file_uploader("Choose an image...", type=['png', 'jpg', 'jpeg'])

#**************************************************************************************************
def load_model(text: str, option, uploaded_file):
  os.environ["OPENAI_API_KEY"] = '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'
  client = OpenAI()
  if option == 'Image Generation':
    response = client.images.generate(
        model="dall-e-3",
        prompt= text,
        size="1024x1024",
        quality="standard",
        n=1,
    )
    return response.data[0].url
  
  elif option == 'Image Variations':
      response = client.images.create_variation(
        response_format = 'url',
        image=uploaded_file,
        n=2,
        size="1024x1024"
        )

      return response.data[0].url
#**************************************************************************************************


if lleft.button(label="Clean the Session"):
    if 'history' in st.session_state:
        del st.session_state['history']



if 'history' not in st.session_state:
    st.session_state['history'] = []

def listen_and_convert():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        audio = r.listen(source)
    try:
        speech_text = r.recognize_google(audio, language='zh-CN')
        process_input(speech_text)
    except Exception as e:
        st.error("Error recognizing speech: " + str(e))


center.button(label="🎤Voice", on_click=listen_and_convert)


def process_input(user_input, option, uploaded_file):
    last_exchange = st.session_state['history'][-1] if st.session_state['history'] else None
    if last_exchange is None or user_input != last_exchange['user']:
        if option =='Image Generation':
            response = load_model(user_input, option, uploaded_file)
            st.session_state['history'].append({'user': user_input, 'assistant': response, 'current_file':uploaded_file})
        if option == 'Image Variations':
            response = load_model(user_input, option, uploaded_file)
            st.session_state['history'].append({'user': uploaded_file, 'assistant': response, 'current_file':uploaded_file})
# 'Image Generation', 'Image Variations'
def display_history():
    for exchange in st.session_state['history']:
         # 如果是字符串，使用st.markdown()渲染文本
        with st.chat_message(name="User"):
            if isinstance(exchange['user'], str):
                st.markdown(exchange['user'])
            else:
                st.image(exchange['user'], width=256)
        with st.chat_message(name="Assistant"):
            st.image(exchange['assistant'], width=256)

query = st.chat_input(placeholder="Please input your questions here...")

# 'Image Generation', 'Image Variations'
if query and option =='Image Generation':
    process_input(query, option, None)

elif uploaded_file and option =='Image Variations' :
    process_input('', option, uploaded_file)

if 'need_rerun' in st.session_state and st.session_state['need_rerun']:
    st.experimental_rerun()

display_history()
