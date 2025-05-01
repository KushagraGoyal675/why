import streamlit as st
from typing import Dict, Any
import time

class CourtroomUI:
    def __init__(self):
        self.setup_page_config()
        self.inject_custom_css()
    
    def setup_page_config(self):
        st.set_page_config(
            page_title="Lex Orion - Indian Court Simulator",
            page_icon="logo.png",
            layout="wide"
        )
    
    def inject_custom_css(self):
        st.markdown(
            '''
            <style>
            body, .stApp {
                background-color: #111 !important;
                color: #fff !important;
            }
            .stApp {
                background: #111 !important;
            }
            .stButton>button, .stTextInput>div>input, .stTextArea>div>textarea, .stSelectbox>div>div>div>div {
                background: #222 !important;
                color: #fff !important;
                border: 2px solid #e10600 !important;
                border-radius: 8px !important;
            }
            .stButton>button:hover {
                background: #e10600 !important;
                color: #fff !important;
                border: 2px solid #fff !important;
            }
            .stProgress > div > div > div > div {
                background-color: #e10600 !important;
            }
            .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4, .stMarkdown h5, .stMarkdown h6 {
                color: #e10600 !important;
            }
            .stAlert, .stSuccess, .stInfo, .stWarning, .stError {
                background: #222 !important;
                color: #fff !important;
                border-left: 5px solid #e10600 !important;
            }
            .stSidebar {
                background: #181818 !important;
                color: #fff !important;
            }
            .stSidebar .stHeader {
                color: #e10600 !important;
            }
            .stSidebar .stSubheader {
                color: #fff !important;
            }
            .stSidebar .stMarkdown {
                color: #fff !important;
            }
            .stSidebar .stTextInput>div>input, .stSidebar .stTextArea>div>textarea, .stSidebar .stSelectbox>div>div>div>div {
                background: #222 !important;
                color: #fff !important;
                border: 2px solid #e10600 !important;
                border-radius: 8px !important;
            }
            .stSidebar .stButton>button {
                background: #e10600 !important;
                color: #fff !important;
                border: 2px solid #fff !important;
            }
            .stSidebar .stButton>button:hover {
                background: #fff !important;
                color: #e10600 !important;
                border: 2px solid #e10600 !important;
            }
            .stMarkdown {
                color: #fff !important;
            }
            .opening-statement {
                background-color: #111 !important;
                color: #e10600 !important;
                border-left: 4px solid #e10600 !important;
                padding: 20px;
                margin: 10px 0;
                border-radius: 5px;
            }
            .phase-transition div {
                background-color: #444 !important;
                color: #fff !important;
            }
            .phase-transition div.active {
                background-color: #4CAF50 !important;
            }
            </style>
            <div style="display:flex;align-items:center;gap:16px;margin-bottom:24px;">
                <img src="logo.png" alt="Lex Orion Logo" style="height:60px;">
                <span style="font-size:2.5rem;font-weight:bold;color:#e10600;letter-spacing:2px;">Lex Orion</span>
            </div>
            ''', unsafe_allow_html=True)
    
    def display_transcript(self, transcript: list, selected_role: str):
        with st.expander("Court Transcript", expanded=True):
            if transcript:
                for entry in transcript:
                    if entry['speaker'] == selected_role or entry['speaker'] in [
                        'Judge', 'Plaintiff Lawyer', 'Defendant Lawyer', 'Witness']:
                        st.markdown(f"""
                        <div style="background:#181818;padding:10px;border-radius:6px;margin-bottom:6px;">
                            <span style="color:#e10600;font-weight:bold;">{entry['speaker']}:</span>
                            <span style="color:#fff;">{entry['content']}</span>
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.info("The court transcript will appear here as the case proceeds.")
    
    def display_phase_indicator(self, phase: str, phases: list):
        st.markdown(f"""
        <div class="phase-transition">
            <h2>Current Phase: {phase.title()}</h2>
            <div style="background-color: #444; border-radius: 10px; padding: 5px;">
                <div style="display: flex; justify-content: space-between;">
                    {"".join([f'<div class="{ "active" if p == phase else "" }" style="padding: 5px; border-radius: 5px; background-color: {"#4CAF50" if p == phase else "#444"}; flex: 1; margin: 0 2px; text-align: center;">{p.title()}</div>' for p in phases])}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    def display_opening_statement_form(self, role: str):
        st.markdown("""
        <div class="opening-statement">
            <h3>Opening Statements Phase</h3>
            <p>Present your opening statement to the court. Explain your client's position and what you intend to prove.</p>
        </div>
        """, unsafe_allow_html=True)
        
        user_input = st.text_area("Enter your opening statement:")
        col1, col2 = st.columns([1, 3])
        with col1:
            if st.button("Record Statement"):
                with st.spinner("Recording..."):
                    st.session_state.tts_engine.speak("Please deliver your opening statement.")
                    user_input = st.session_state.stt_engine.process_microphone_input()
                    st.success(f"Recorded: {user_input}")
        with col2:
            if st.button("Submit Opening Statement", key="submit_opening"):
                if user_input:
                    return user_input
                else:
                    st.warning("Please enter your statement before submitting.")
        return None 