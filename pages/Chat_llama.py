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
from langchain_core.messages import SystemMessage
from langchain_experimental.chat_models import Llama2Chat
from langchain_community.llms import LlamaCpp
from langchain import OpenAI, ConversationChain, LLMChain, PromptTemplate
from langchain.memory import ConversationBufferWindowMemory
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from openai import OpenAI

st.set_page_config(page_title="LLM", page_icon="🤖", layout="wide", initial_sidebar_state="expanded")
left, core, right = st.columns([1, 1, 1])
col1, col2 = st.columns(spec=2)
lleft, _, center, _, rright = st.columns([1, 1, 1, 1, 1])

max_length = left.slider(label="Max Length", min_value=0, max_value=4097, value=1024, step=1)
option = st.selectbox(
    'Choose an LLaMA model:',
    ('1: Name: llama-2-7b-chat.Q3_K_S.gguf; Size:2.95 GB; Max RAM required: 5.33 GB', 
     '2: Name: llama-2-7b-chat.Q5_K_M.gguf; Size:4.78 GB; Max RAM required: 7.28 GB GB',
     '3: Name: codellama-7b.Q4_K_M.gguf'
     )
)
top_p = core.slider(label="Accumulated Probability", min_value=0.0, max_value=1.0, value=0.8, step=0.01)
temp = right.slider(label="Temperature", min_value=0.0, max_value=1.0, value=0.6, step=0.01)
prompt_str = st.text_input(label="prompt", placeholder="prompt")

#**************************************************************************************************
hist = rright.checkbox("history memory activate")
vocie_hist = rright.checkbox("voice output activate")

def initialize_model(option, prompt_str, temperature=0.5, max_length=1024):
    """根据给定的prompt_str初始化对话模型和链"""
    template_messages = [
    SystemMessage(content=prompt_str),
    MessagesPlaceholder(variable_name="chat_history"),
    HumanMessagePromptTemplate.from_template("{text}"),]
    prompt_template = ChatPromptTemplate.from_messages(template_messages)
    
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    if option == '2: Name: llama-2-7b-chat.Q5_K_M.gguf; Size:4.78 GB; Max RAM required: 7.28 GB GB':
        model_path = "models/llama/llama-2-7b-chat.Q5_K_M.gguf"
    elif option == '1: Name: llama-2-7b-chat.Q3_K_S.gguf; Size:2.95 GB; Max RAM required: 5.33 GB': 
        model_path = "models/llama/llama-2-7b-chat.Q3_K_S.gguf"
    else:
         model_path = "models/llama/codellama-7b.Q4_K_M.gguf"
    llm = LlamaCpp(
    temperature=temperature,
    max_tokens=max_length,
    model_path=model_path,
    streaming=False,
    )
    model = Llama2Chat(llm=llm)
    chain = LLMChain(llm=model, prompt=prompt_template, memory=memory)
    return chain

def load_model(text, temp, max_length, prompt_str, option, bool_value=False, voice_bool=False):
    """根据条件加载或获取对话模型，处理输入并返回响应"""
    # 检查session_state中是否存在conversation实例，如果不存在或需要根据新的prompt_str重新创建，则进行初始化
    if 'conversation' not in st.session_state or (not bool_value) or prompt_str != st.session_state.get('last_prompt', ''):
        # 初始化对话模型
        st.session_state.conversation = initialize_model(option, prompt_str, temp, max_length)
        st.session_state['last_prompt'] = prompt_str  # 更新最后使用的提示词
    # 使用当前会话实例预测响应
    response = st.session_state.conversation.run(text=text)
    if voice_bool:
        client = OpenAI()
        response_voice = client.audio.speech.create(
        model="tts-1",
        voice='nova',
        input=response)
        return response_voice
    
    return response

def process_input(user_input, prompt_str, hist, temp, max_length, vocie_hist, option):

    last_exchange = st.session_state['history'][-1] if st.session_state['history'] else None
    if last_exchange is None or user_input != last_exchange['user']:
        response = load_model(user_input, temp, max_length, prompt_str, option, hist, vocie_hist)
        st.session_state['history'].append({'user': user_input, 'assistant': response})

def listen_and_convert(prompt_str, hist, temp, max_length, vocie_hist):
    r = sr.Recognizer()
    with sr.Microphone() as source:
        audio = r.listen(source)
    try:
        speech_text = r.recognize_google(audio, language='zh-CN')
        process_input(speech_text, prompt_str, hist, temp, max_length, vocie_hist)
    except Exception as e:
        st.error(str(e))

if center.button(label="🎤 Voice Input"):
    listen_and_convert(prompt_str, hist, temp, max_length, vocie_hist)

#**************************************************************************************************


if lleft.button(label="Clean the Session"):
    if 'history' in st.session_state:
        del st.session_state['history']
    if 'conversation' in st.session_state:
        del st.session_state['conversation']
    if 'last_prompt' in st.session_state:
        del st.session_state['last_prompt']



if 'history' not in st.session_state:
    st.session_state['history'] = []



def display_history():
    for exchange in st.session_state['history']:
        with st.chat_message(name="User"):
            st.markdown(exchange['user'])
        with st.chat_message(name="assistant"):
            if isinstance(exchange['assistant'], str):
                st.markdown(exchange['assistant'])
            else:
                audio_data = exchange['assistant']
                # 检查数据是否为HttpxBinaryResponseContent类型，如果是，则转换为二进制
                if isinstance(audio_data, openai._legacy_response.HttpxBinaryResponseContent):
                    # 转换数据格式
                    audio_data = audio_data.content  # 或者使用正确的方法来获取二进制数据
                # 使用转换后的二进制数据
                st.audio(audio_data, format='audio/mp3')

query = st.chat_input(placeholder="Please input your questions here...")

if query:
    process_input(query, prompt_str, hist, temp, max_length, vocie_hist, option)

if 'need_rerun' in st.session_state and st.session_state['need_rerun']:
    st.experimental_rerun()

display_history()
