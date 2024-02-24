# from streamlit.runtime.scriptrunner import add_script_run_ctx,get_script_run_ctx
import concurrent.futures
import streamlit as st
from gtts import gTTS
import requests
import time
import io


# parameter
if "lang_list" not in st.session_state:
    st.session_state.lang_list = ["中文-zh","English-en","日本語-ja","Русский язык-ru","Deutsch-de","Français-fr","중국어-ko"]
if "lang" not in st.session_state:
    st.session_state.lang = st.session_state.lang_list[0]
if "file" not in st.session_state:
    st.session_state.file = None
if "text" not in st.session_state:
    st.session_state.text = ""
if "text_audio" not in st.session_state:
    st.session_state.text_audio = None
if "choice" not in st.session_state:
    st.session_state.choice = True
if "tts_choice" not in st.session_state:
    st.session_state.tts_choice_list = ["google","Genshin Impact"]
    st.session_state.tts_choice = st.session_state.tts_choice_list[0]
    st.session_state.GenshinImpactRole_list = ["阿贝多","埃洛伊","艾尔海森","安柏","八重神子","芭芭拉","白术","班尼特","北斗","达达利亚","迪奥娜","迪卢克","迪希雅","多莉","珐露珊","菲米尼","菲谢尔","枫原万叶","芙宁娜","甘雨","胡桃","荒泷一斗","嘉明","九条裟罗","久岐忍","卡维","凯亚","坎蒂丝","柯莱","可莉","刻晴","莱欧斯利","莱依拉","雷电将军","雷泽","丽莎","林尼","琳妮特","流浪者","鹿野院平藏","罗莎莉亚","米卡","莫娜","那维莱特","纳西妲","娜维娅","妮露","凝光","诺艾尔","七七","绮良良","琴","赛诺","砂糖","珊瑚宫心海","申鹤","神里绫华","神里绫人","提纳里","托马","温迪","五郎","夏洛蒂","夏沃蕾","闲云","香菱","宵宫","魈","辛焱","行秋","烟绯","瑶瑶","夜兰","优菈","云堇","早柚","钟离","重云"]
    st.session_state.GenshinImpactRole = st.session_state.GenshinImpactRole_list[0]

# show page
header = st.empty()
show_input = st.container()
show_result = st.container()


# function

@st.cache_data
def tts_google(text, lang):
    try:
        tts = gTTS(text=text,lang=lang)
        speach_BytesIO = io.BytesIO()
        tts.write_to_fp(speach_BytesIO)
        return speach_BytesIO
    except Exception as e:
        st.error(f"Error converting text to speech: {e}")
        return False

@st.cache_data
def tts_GenshinImpact(text, role):
    try:
        url = "http://ovoa.cc/api/yuanshen.php"
        params = {
            "message": text,
            "key": "123456",
            "figure": role
        }
        response = requests.get(url, params=params)
        tts = response.content
        speach_BytesIO = io.BytesIO()
        speach_BytesIO.write(tts)
        return speach_BytesIO
    except Exception as e:
        st.error(f"Error converting text to speech: {e}")
        return False

@st.cache_data
def merge_audio(audio_list):
    final_audio = io.BytesIO()
    for audio in audio_list:
        if audio is False:
            continue
        audio.seek(0)
        final_audio.write(audio.read())
    final_audio.seek(0)
    return final_audio

def text2speech():
    paragraph = list(filter(None, st.session_state.text.splitlines()))
    if st.session_state.tts_choice == st.session_state.tts_choice_list[0]:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures= [executor.submit(tts_google, content, st.session_state.lang[-2:]) for content in paragraph]
            paragraph_audio = [future.result() for future in futures]
    elif st.session_state.tts_choice == st.session_state.tts_choice_list[1]:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures= [executor.submit(tts_GenshinImpact, content, st.session_state.GenshinImpactRole) for content in paragraph]
            paragraph_audio = [future.result() for future in futures]
    st.session_state.text_audio = merge_audio(paragraph_audio)

# mount

def get_file():
    if st.session_state.file:
        st.session_state.text = st.session_state.file.getvalue().decode("utf-8")
def change_choice():
    st.session_state.choice = not st.session_state.choice

def get_paramater():
    st.session_state.tts_choice = st.session_state.tts_choice
    st.session_state.choice = st.session_state.choice
    st.session_state.lang = st.session_state.lang
    st.session_state.text = st.session_state.text
    st.session_state.file = st.session_state.file
    st.session_state.text_audio = st.session_state.text_audio
    st.session_state.GenshinImpactRole = st.session_state.GenshinImpactRole
    

# setting
with st.sidebar:
    st.session_state.choice = st.toggle("File || Input",value=st.session_state.choice,on_change=change_choice)
    st.session_state.tts_choice = st.selectbox("Choose TTS Source",st.session_state.tts_choice_list,on_change=get_paramater)
    if st.session_state.tts_choice == st.session_state.tts_choice_list[0]:
        st.session_state.lang = st.selectbox("Language",st.session_state.lang_list,on_change=get_paramater)
    elif st.session_state.tts_choice == st.session_state.tts_choice_list[1]:
        st.session_state.GenshinImpactRole = st.selectbox("Role",st.session_state.GenshinImpactRole_list,on_change=get_paramater)

# logic
if st.session_state.choice:
    if st.session_state.tts_choice == st.session_state.tts_choice_list[0]:
        header.write("<h2> Input-"+st.session_state.lang[:-3]+"</h2>",unsafe_allow_html=True)
    else:
        header.write("<h2> Input-"+st.session_state.GenshinImpactRole+"</h2>",unsafe_allow_html=True)
    text = st.chat_input("Send your text")
    if text:
        st.session_state.text = text
        start = time.time()
        text2speech()
        end = time.time()
        st.write(f"cost:",end-start)
    with show_result:
        if st.session_state.text_audio:
            st.audio(st.session_state.text_audio.getvalue())
            with st.container():
                st.write(st.session_state.text)

else:
    header.write("<h2> File-"+st.session_state.lang[:-3]+"</h2>",unsafe_allow_html=True)
    with show_input:
        st.session_state.file = st.file_uploader("Upload your file",type=["txt"],label_visibility="collapsed")
        st.button("Convert",use_container_width=True,key="convert",type="primary")
        if st.session_state.get("convert"):
            start = time.time()
            get_file()
            text2speech()
            end = time.time()
            st.write(f"cost:",end-start)
    with show_result:
        if st.session_state.text_audio:
            st.audio(st.session_state.text_audio.getvalue())
            with st.container():
                st.write(st.session_state.text)
get_paramater()