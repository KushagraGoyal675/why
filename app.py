import streamlit as st
import json
import os
import time
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import base64
from io import BytesIO
from typing import Dict, Any
# from frontend import CourtroomFrontend
from frontend.components import CourtroomUI
from frontend.animations import AnimationManager
from frontend.proceeding_animations import CourtProceedingAnimations
from courtroom import create_simulation, CourtroomSimulationManager
from agents.plaintiff_agent import PlaintiffAgent
from agents.defendant_agent import DefendantAgent
from agents.judge_agent import JudgeAgent
from agents.witness_agent import WitnessAgent
from utils.tts import TTSEngine
from utils.stt import STTEngine

# Must be called before any other Streamlit commands
st.set_page_config(
    page_title="Lex Orion - Indian Court Simulator",
    page_icon=None,  # We'll update this once we have the logo
    layout="wide"
)

# Display the logo using Streamlit's native st.image for debugging
st.image("logo.png", width=120)

def get_logo_base64(path="logo.png"):
    ext = os.path.splitext(path)[1].lower()
    mime = "image/png" if ext == ".png" else "image/jpeg" if ext in [".jpg", ".jpeg"] else "image/gif"
    with open(path, "rb") as f:
        data = f.read()
    return f"data:{mime};base64,{base64.b64encode(data).decode()}"

logo_data_uri = get_logo_base64("logo.png")
print("LOGO DATA URI (first 100 chars):", logo_data_uri[:100])

st.markdown(
    f'''
    <div style="display:flex;align-items:center;gap:16px;margin-bottom:24px;">
        <img src="{logo_data_uri}" alt="Lex Orion Logo" style="height:60px;">
        <span style="font-size:2.5rem;font-weight:bold;color:#e10600;letter-spacing:2px;">Lex Orion</span>
    </div>
    ''', unsafe_allow_html=True
)

# --- TTS VOICES AND FUNCTION (moved to top for global availability) ---
tts_voices = {
    "judge": {"language": "en", "slow": False},
    "plaintiff": {"language": "en", "slow": False},
    "defendant": {"language": "en", "slow": False},
    "witness": {"language": "en", "slow": False}
}

def play_tts(role, text):
    try:
        if not text or not isinstance(text, str):
            print(f"Invalid text for TTS: {text}")
            return False
        voice_settings = tts_voices.get(role, {"language": "en", "slow": False})
        print(f"Playing TTS for role {role} with text: {text[:100]}...")
        return st.session_state.tts_engine.speak(text, role=role, language=voice_settings["language"])
    except Exception as e:
        print(f"Error in play_tts: {str(e)}")
        return False

# Inject custom CSS for dark theme and branding
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
    .opening-statement h3 {
        color: #e10600 !important;
        margin-bottom: 10px;
    }
    .opening-statement p {
        color: #fff !important;
        margin: 0;
    }
    .phase-transition div {
        background-color: #444 !important;
        color: #fff !important;
    }
    .phase-transition div.active {
        background-color: #4CAF50 !important;
    }
    </style>
    ''', unsafe_allow_html=True)

# Initialize TTS and STT engines
if 'tts_engine' not in st.session_state:
    st.session_state.tts_engine = TTSEngine()
if 'stt_engine' not in st.session_state:
    st.session_state.stt_engine = STTEngine()

# Initialize animations
if 'courtroom_anim' not in st.session_state:
    st.session_state.courtroom_anim = AnimationManager()
if 'proceeding_anim' not in st.session_state:
    st.session_state.proceeding_anim = CourtProceedingAnimations()

# Initialize agents with proper configuration
if 'agents' not in st.session_state:
    judge_config = {
        'name': 'Justice Rao',
        'experience': '20 years',
        'specialization': 'Civil Law'
    }
    
    st.session_state.agents = {
        'plaintiff': PlaintiffAgent(),
        'defendant': DefendantAgent(),
        'judge': JudgeAgent(judge_config),
        'witness': WitnessAgent()
    }

# --- Login ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = None
if not st.session_state.logged_in:
    st.subheader("Login")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            if username == "admin" and password == "1234":
                st.session_state.logged_in = True
                st.session_state.username = username
                st.success("Login Successful! Welcome to the Indian Court Simulator.")
                time.sleep(1)
                st.rerun()
            else:
                st.error("Invalid username or password.")
    st.stop()

# --- Load cases from data/cases.json ---
def load_cases_from_json():
    cases_path = os.path.join("data", "cases.json")
    if not os.path.exists(cases_path):
        st.error("No cases.json file found in the data directory.")
        return []
    with open(cases_path, "r") as f:
        data = json.load(f)
        return data.get("cases", [])

def get_case_by_id(case_id):
    cases = load_cases_from_json()
    for case in cases:
        if case.get("case_id") == case_id:
            return case
    return None

# --- Case Selection ---
if 'selected_case_id' not in st.session_state:
    st.session_state.selected_case_id = None
if not st.session_state.selected_case_id:
    st.subheader("Select a Case")
    cases = load_cases_from_json()
    if not cases:
        st.stop()
    case_titles = [f"{case['case_id']}: {case['title']}" for case in cases]
    case_choice = st.selectbox("Choose a case", case_titles)
    if st.button("Confirm Case"):
        st.session_state.selected_case_id = case_choice.split(':')[0]
        st.rerun()
    st.stop()

case = get_case_by_id(st.session_state.selected_case_id)

# --- Role Selection ---
roles = ["Plaintiff Lawyer", "Defendant Lawyer", "Observer"]
if 'selected_role' not in st.session_state:
    st.session_state.selected_role = None
if not st.session_state.selected_role:
    st.subheader("Choose Your Role")
    
    # Visual role selection cards
    cols = st.columns(3)
    role_icons = {
        "Plaintiff Lawyer": "💼", 
        "Defendant Lawyer": "🧑‍💼", 
        "Observer": "👁️"
    }
    
    role_descs = {
        "Plaintiff Lawyer": "Represent the plaintiff, present evidence and arguments",
        "Defendant Lawyer": "Represent the defendant, present evidence and arguments",
        "Observer": "Watch the case proceedings automatically"
    }
    
    for i, role in enumerate(roles):
        with cols[i]:
            st.markdown(f"""
            <div style="border:1px solid #ddd; padding:15px; border-radius:5px; text-align:center; 
                      animation: fadeIn 0.5s {i*0.2}s; cursor:pointer; height:200px;">
                <h1>{role_icons[role]}</h1>
                <h4>{role}</h4>
                <p style="font-size:0.8em;">{role_descs[role]}</p>
            </div>
            """, unsafe_allow_html=True)
    
    role = st.selectbox("Select your role", roles)
    if st.button("Confirm Role"):
        st.session_state.selected_role = role
        st.success(f"You selected: {role}. Preparing the courtroom...")
        time.sleep(1)
        st.rerun()
    st.stop()

# --- Simulation Setup ---
if 'simulation' not in st.session_state:
    case_data = {
        "case_id": case["case_id"],
        "title": case["title"],
        "type": case["case_type"],
        "plaintiff": case["parties"]["plaintiff"],
        "defendant": case["parties"]["defendant"],
        "description": case["description"],
        "judge_data": {"name": "Justice Rao", "experience": "20 years", "specialization": "Civil Law"},
        "plaintiff_lawyer_data": {"name": "Adv. Mehta", "experience": "15 years", "specialization": "Contracts"},
        "defendant_lawyer_data": {"name": "Adv. Singh", "experience": "12 years", "specialization": "Contracts"},
        "witnesses": case["witnesses"],
        "evidence": case["evidence"]
    }
    
    st.session_state.simulation = create_simulation(case_data)
    st.session_state.simulation_state = 'not_started'
    st.session_state.transcript = []
    st.session_state.current_phase = 'opening'
    st.session_state.evidence_presented = []
    st.session_state.selected_witness = None
    st.session_state.current_speaker = None

sim: CourtroomSimulationManager = st.session_state.simulation

# --- Main Simulation UI ---
phases = [
    'opening',
    'examination_in_chief',
    'cross_examination',
    'evidence',
    'objection',
    'closing',
    'judgment',
    'completed'
]
phase = st.session_state.current_phase

# Header and Phase Banner
st.markdown(f"""
<div style="text-align:center; margin-bottom:20px;">
    <h2 style="color:#e10600;">{case['title']}</h2>
    <p style="color:#fff;">{case['description']}</p>
</div>
""", unsafe_allow_html=True)
courtroom_ui = CourtroomUI()
courtroom_ui.display_phase_banner(phase)

# --- Live Transcript Sidebar ---
transcript_placeholder = st.empty()
def render_transcript(transcript):
    transcript_html = '<div class="transcript-sidebar"><b>Live Transcript</b><br>'
    for entry in transcript[-30:]:
        transcript_html += f'<span style="color:#e10600;font-weight:bold;">{entry["speaker"]}:</span> <span style="color:#fff;">{entry["content"]}</span><br>'
    transcript_html += '</div>'
    return transcript_html
transcript = sim.get_simulation_state().get('transcript', [])
transcript_placeholder.markdown(render_transcript(transcript), unsafe_allow_html=True)

# --- Courtroom Display ---
speaking_role = st.session_state.get('current_speaker', None)
courtroom_ui.display_courtroom(sim.get_simulation_state(), speaking_role)

# --- Phase Logic ---
def next_phase(current):
    idx = phases.index(current)
    return phases[idx+1] if idx+1 < len(phases) else 'completed'

# --- Realistic Courtroom Flow ---
if st.session_state.selected_role == "Observer":
    # Opening Statements
    if phase == 'opening':
        st.info("AI agents are presenting opening statements...")
        if not st.session_state.get('opening_done', False):
            plaintiff_statement = sim.plaintiff_agent.generate_opening_statement(case)
            sim.add_to_transcript("Plaintiff Lawyer", plaintiff_statement)
            st.session_state.current_speaker = "plaintiff"
            play_tts("plaintiff", plaintiff_statement)
            time.sleep(2)
            st.session_state.opening_done = 'plaintiff'
            st.rerun()
        elif st.session_state.opening_done == 'plaintiff':
            defendant_statement = sim.defendant_agent.generate_opening_statement(case)
            sim.add_to_transcript("Defendant Lawyer", defendant_statement)
            st.session_state.current_speaker = "defendant"
            play_tts("defendant", defendant_statement)
            time.sleep(2)
            st.session_state.opening_done = 'done'
            st.rerun()
        else:
            st.session_state.current_phase = next_phase(phase)
            st.session_state.opening_done = False
            st.rerun()
    # Examination-in-Chief (Plaintiff's Witness)
    elif phase == 'examination_in_chief':
        st.info("Examination-in-Chief: Plaintiff Lawyer questions witness...")
        if not st.session_state.get('examination_done', False):
            witness = case["witnesses"][0] if case["witnesses"] else {"name": "Witness"}
            question = sim.plaintiff_agent.generate_question(witness)
            sim.add_to_transcript("Plaintiff Lawyer", question)
            st.session_state.current_speaker = "plaintiff"
            play_tts("plaintiff", question)
            time.sleep(2)
            st.session_state.examination_done = 'plaintiff_q'
            st.session_state.examination_question = question
            st.rerun()
        elif st.session_state.examination_done == 'plaintiff_q':
            witness = case["witnesses"][0] if case["witnesses"] else {"name": "Witness"}
            question = st.session_state.get('examination_question', '')
            answer = sim.witness_agent.give_testimony(question, case)
            sim.add_to_transcript("Witness", answer)
            st.session_state.current_speaker = "witness"
            play_tts("witness", answer)
            time.sleep(2)
            st.session_state.examination_done = 'done'
            st.rerun()
        else:
            st.session_state.current_phase = next_phase(phase)
            st.session_state.examination_done = False
            st.session_state.examination_question = ''
            st.rerun()
    # Cross-Examination (Defendant's turn)
    elif phase == 'cross_examination':
        st.info("Cross-Examination: Defendant Lawyer questions witness...")
        if not st.session_state.get('cross_done', False):
            witness = case["witnesses"][0] if case["witnesses"] else {"name": "Witness"}
            cross_question = sim.defendant_agent.generate_question(witness)
            sim.add_to_transcript("Defendant Lawyer", cross_question)
            st.session_state.current_speaker = "defendant"
            play_tts("defendant", cross_question)
            time.sleep(2)
            st.session_state.cross_done = 'defendant_q'
            st.session_state.cross_question = cross_question
            st.rerun()
        elif st.session_state.cross_done == 'defendant_q':
            witness = case["witnesses"][0] if case["witnesses"] else {"name": "Witness"}
            cross_question = st.session_state.get('cross_question', '')
            answer = sim.witness_agent.give_testimony(cross_question, case)
            sim.add_to_transcript("Witness", answer)
            st.session_state.current_speaker = "witness"
            play_tts("witness", answer)
            time.sleep(2)
            st.session_state.cross_done = 'done'
            st.rerun()
        else:
            st.session_state.current_phase = next_phase(phase)
            st.session_state.cross_done = False
            st.session_state.cross_question = ''
            st.rerun()
    # Evidence Presentation
    elif phase == 'evidence':
        st.info("AI agents are presenting evidence...")
        evidence_list = case["evidence"]
        if not st.session_state.get('evidence_done', False):
            if 'evidence_index' not in st.session_state:
                st.session_state.evidence_index = 0
                st.session_state.evidence_side = 'plaintiff'
            if st.session_state.evidence_side == 'plaintiff' and st.session_state.evidence_index < len(evidence_list):
                evidence = evidence_list[st.session_state.evidence_index]
                sim.add_to_transcript("Plaintiff Lawyer", f"Presenting evidence: {evidence}")
                st.session_state.current_speaker = "plaintiff"
                play_tts("plaintiff", str(evidence))
                time.sleep(2)
                st.session_state.evidence_index += 1
                st.rerun()
            elif st.session_state.evidence_side == 'plaintiff':
                st.session_state.evidence_index = 0
                st.session_state.evidence_side = 'defendant'
                st.rerun()
            elif st.session_state.evidence_side == 'defendant' and st.session_state.evidence_index < len(evidence_list):
                evidence = evidence_list[st.session_state.evidence_index]
                sim.add_to_transcript("Defendant Lawyer", f"Presenting evidence: {evidence}")
                st.session_state.current_speaker = "defendant"
                play_tts("defendant", str(evidence))
                time.sleep(2)
                st.session_state.evidence_index += 1
                st.rerun()
            else:
                st.session_state.evidence_done = True
                st.session_state.evidence_index = 0
                st.session_state.evidence_side = 'plaintiff'
                st.rerun()
        else:
            st.session_state.current_phase = next_phase(phase)
            st.session_state.evidence_done = False
            st.rerun()
    # Objections
    elif phase == 'objection':
        st.info("AI agents are raising objections...")
        if not st.session_state.get('objection_done', False):
            objection = "Objection, leading the witness!"
            sim.add_to_transcript("Defendant Lawyer", objection)
            st.session_state.current_speaker = "defendant"
            play_tts("defendant", objection)
            time.sleep(2)
            st.session_state.objection_done = 'raised'
            st.session_state.objection_text = objection  # Store objection in session state
            st.rerun()
        elif st.session_state.objection_done == 'raised':
            objection = st.session_state.get('objection_text', '')
            ruling = sim.judge_agent.rule_on_objection(objection)
            sim.add_to_transcript("Judge", ruling)
            st.session_state.current_speaker = "judge"
            play_tts("judge", ruling)
            time.sleep(2)
            st.session_state.objection_done = 'done'
            st.rerun()
        else:
            st.session_state.current_phase = next_phase(phase)
            st.session_state.objection_done = False
            st.session_state.objection_text = ''
            st.rerun()
    # Closing Arguments
    elif phase == 'closing':
        st.info("AI agents are presenting closing arguments...")
        if not st.session_state.get('closing_done', False):
            closing1 = sim.plaintiff_agent.generate_closing_argument(case)
            sim.add_to_transcript("Plaintiff Lawyer", closing1)
            st.session_state.current_speaker = "plaintiff"
            play_tts("plaintiff", closing1)
            time.sleep(2)
            st.session_state.closing_done = 'plaintiff'
            st.rerun()
        elif st.session_state.closing_done == 'plaintiff':
            closing2 = sim.defendant_agent.generate_closing_argument(case)
            sim.add_to_transcript("Defendant Lawyer", closing2)
            st.session_state.current_speaker = "defendant"
            play_tts("defendant", closing2)
            time.sleep(2)
            st.session_state.closing_done = 'done'
            st.rerun()
        else:
            st.session_state.current_phase = next_phase(phase)
            st.session_state.closing_done = False
            st.rerun()
    # Judgment
    elif phase == 'judgment':
        st.info("The judge is delivering the verdict...")
        if not st.session_state.get('judgment_done', False):
            judgment = sim.judge_agent.give_judgment(str(case))
            sim.add_to_transcript("Judge", judgment)
            st.session_state.current_speaker = "judge"
            play_tts("judge", judgment)
            time.sleep(2)
            st.session_state.judgment_done = True
            st.rerun()
        else:
            st.session_state.current_phase = next_phase(phase)
            st.session_state.judgment_done = False
            st.rerun()
    elif phase == 'completed':
        st.success("Case closed. Justice served!")
        st.session_state.current_speaker = None
else:
    st.warning("For the extreme AI simulation, only Observer mode is currently supported. Please restart and select Observer.")

# Footer
st.markdown("""
<div style="text-align:center; margin-top:50px; padding:20px; border-top:1px solid #333;">
    <p style="color:#666;">Indian Court Simulator - Educational Tool © 2024</p>
</div>
""", unsafe_allow_html=True) 