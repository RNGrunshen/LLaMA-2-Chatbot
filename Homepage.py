import streamlit as st
# Streamlit页面配置
st.set_page_config(page_title="LLM", page_icon="🤖", layout="wide", initial_sidebar_state="expanded")

# Set the background image
# background-image: url("https://images.unsplash.com/photo-1542281286-9e0a16bb7366");
# background-size: 100vw 100vh;  # This sets the size to cover 100% of the viewport width and height
background_image = """
<style>
[data-testid="stAppViewContainer"] > .main {
    background-image: url("https://images.unsplash.com/photo-1542281286-9e0a16bb7366");
    background-size: cover;  
    background-position: center;  
    background-repeat: no-repeat;
}
</style>
"""

st.markdown(background_image, unsafe_allow_html=True)

input_style = """
<style>
input[type="text"] {
    background-color: transparent;
    color: #a19eae;  // This changes the text color inside the input box
}
div[data-baseweb="base-input"] {
    background-color: transparent !important;
}
[data-testid="stAppViewContainer"] {
    background-color: transparent !important;
}
</style>
"""
st.markdown(input_style, unsafe_allow_html=True)

# 从外部文件读取CSS样式
def load_css(file_name):
    with open(file_name, "r") as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# 加载CSS文件
load_css('style.css')


# 页面内容
st.markdown('<div class="container"><h1 class="typing-effect">Welcome to our LLaMA Chatbot!</h1></div>', unsafe_allow_html=True)
