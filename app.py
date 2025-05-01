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
from frontend import CourtroomFrontend
from courtroom import create_simulation, CourtroomSimulationManager
from agents.plaintiff_agent import PlaintiffAgent
from agents.defendant_agent import DefendantAgent
from agents.judge_agent import JudgeAgent
from agents.witness_agent import WitnessAgent
from utils.tts import TTSEngine
from utils.stt import STTEngine

st.set_page_config(page_title="Lex Orion - Indian Court Simulator", page_icon="logo.png", layout="wide")

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
    <div style="display:flex;align-items:center;gap:16px;margin-bottom:24px;">
        <img src="logo.png" alt="Lex Orion Logo" style="height:60px;">
        <span style="font-size:2.5rem;font-weight:bold;color:#e10600;letter-spacing:2px;">Lex Orion</span>
    </div>
    ''', unsafe_allow_html=True)

# --- Animation Classes ---
class CourtroomAnimation:
    def __init__(self):
        self.characters = {
            "judge": {"position": (0.5, 0.15), "speaking": False},
            "plaintiff_lawyer": {"position": (0.2, 0.4), "speaking": False},
            "defendant_lawyer": {"position": (0.8, 0.4), "speaking": False},
            "witness": {"position": (0.5, 0.4), "speaking": False},
            "plaintiff": {"position": (0.1, 0.6), "speaking": False},
            "defendant": {"position": (0.9, 0.6), "speaking": False},
        }
        self.courtroom_bg = self.create_courtroom_bg()
        self.current_speaker = None
        self.animation_frames = []
        self.animation_speed = 0.5

    def create_courtroom_bg(self):
        """Create a simple courtroom background"""
        fig, ax = plt.subplots(figsize=(8, 4.8))  # Reduced size
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        
        # Draw judge bench
        ax.add_patch(plt.Rectangle((0.3, 0.05), 0.4, 0.1, color='brown'))
        
        # Draw witness stand
        ax.add_patch(plt.Rectangle((0.45, 0.35), 0.1, 0.1, color='brown'))
        
        # Draw lawyers' tables
        ax.add_patch(plt.Rectangle((0.1, 0.35), 0.2, 0.05, color='brown'))
        ax.add_patch(plt.Rectangle((0.7, 0.35), 0.2, 0.05, color='brown'))
        
        # Draw audience area
        ax.add_patch(plt.Rectangle((0.1, 0.6), 0.8, 0.3, color='lightgray', alpha=0.5))
        
        ax.axis('off')
        return fig

    def draw_character(self, ax, role, is_speaking=False):
        """Draw a character on the courtroom"""
        char_info = self.characters.get(role, {"position": (0.5, 0.5), "speaking": False})
        x, y = char_info["position"]
        
        # Body
        color = 'black' if role == 'judge' else 'navy' if 'lawyer' in role else 'darkgreen'
        ax.add_patch(plt.Circle((x, y), 0.05, color=color))
        
        # Head
        ax.add_patch(plt.Circle((x, y-0.07), 0.03, color='tan'))
        
        # Speech bubble if speaking
        if is_speaking:
            ax.annotate("Speaking", xy=(x, y-0.12), 
                        xytext=(x+0.15, y-0.15),
                        arrowprops=dict(arrowstyle="->", color='black'),
                        bbox=dict(boxstyle="round,pad=0.3", fc="yellow", alpha=0.7))

    def animate_phase(self, phase, speaking_role=None):
        """Animate the current phase of the trial"""
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        
        # Draw courtroom background
        ax.add_patch(plt.Rectangle((0, 0), 1, 1, color='#111', alpha=1.0))  # Dark background
        
        # Draw judge bench
        ax.add_patch(plt.Rectangle((0.3, 0.05), 0.4, 0.1, color='brown'))
        
        # Draw witness stand
        ax.add_patch(plt.Rectangle((0.45, 0.35), 0.1, 0.1, color='brown'))
        
        # Draw lawyers' tables
        ax.add_patch(plt.Rectangle((0.1, 0.35), 0.2, 0.05, color='brown'))
        ax.add_patch(plt.Rectangle((0.7, 0.35), 0.2, 0.05, color='brown'))
        
        # Draw audience area
        ax.add_patch(plt.Rectangle((0.1, 0.6), 0.8, 0.3, color='lightgray', alpha=0.5))
        
        # Draw phase-specific elements
        if phase == 'opening':
            ax.text(0.5, 0.9, "Opening Statements", ha='center', fontsize=14, 
                    bbox=dict(facecolor='#222', edgecolor='#e10600', alpha=0.9, 
                             boxstyle='round,pad=0.5'), color='#fff')
        elif phase == 'examination':
            ax.text(0.5, 0.9, "Witness Examination", ha='center', fontsize=14, bbox=dict(facecolor='white', alpha=0.5))
        elif phase == 'evidence':
            ax.text(0.5, 0.9, "Evidence Presentation", ha='center', fontsize=14, bbox=dict(facecolor='white', alpha=0.5))
            ax.add_patch(plt.Rectangle((0.45, 0.45), 0.1, 0.05, color='yellow', alpha=0.8))
        elif phase == 'objection':
            ax.text(0.5, 0.9, "Objection Phase", ha='center', fontsize=14, bbox=dict(facecolor='white', alpha=0.5))
            if speaking_role and 'lawyer' in speaking_role.lower():
                ax.text(0.5, 0.75, "OBJECTION!", ha='center', fontsize=16, color='red', weight='bold')
        elif phase == 'closing':
            ax.text(0.5, 0.9, "Closing Arguments", ha='center', fontsize=14, bbox=dict(facecolor='white', alpha=0.5))
        elif phase == 'judgment':
            ax.text(0.5, 0.9, "Judgment", ha='center', fontsize=14, bbox=dict(facecolor='white', alpha=0.5))
            ax.add_patch(plt.Rectangle((0.3, 0.02), 0.4, 0.13, color='brown', linewidth=3, edgecolor='gold'))
        elif phase == 'completed':
            ax.text(0.5, 0.9, "Case Closed", ha='center', fontsize=14, bbox=dict(facecolor='white', alpha=0.5))
            ax.text(0.5, 0.5, "JUSTICE SERVED", ha='center', fontsize=20, color='navy', weight='bold')
            
        # Draw characters
        for role, info in self.characters.items():
            self.draw_character(ax, role, is_speaking=(role.lower() == speaking_role.lower() if speaking_role else False))
            
        ax.axis('off')
        
        # Convert plot to image for Streamlit
        buf = BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        st.image(buf, use_column_width=True)
        plt.close(fig)
        
    def animate_confetti(self):
        """Display animated confetti for case completion"""
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        
        # Create and display confetti
        confetti_colors = ['red', 'blue', 'green', 'yellow', 'purple', 'orange']
        for _ in range(100):
            x = np.random.rand()
            y = np.random.rand()
            color = np.random.choice(confetti_colors)
            ax.add_patch(plt.Rectangle((x, y), 0.02, 0.01, color=color, alpha=0.7))
            
        ax.text(0.5, 0.5, "CASE CLOSED", ha='center', fontsize=24, color='navy', weight='bold')
        ax.axis('off')
        
        # Convert plot to image for Streamlit
        buf = BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        st.image(buf, use_column_width=True)
        plt.close(fig)
        
class CourtroomProceedingAnimation:
    def __init__(self):
        self.phase_animations = {
            'opening': self.animate_opening,
            'examination': self.animate_examination,
            'evidence': self.animate_evidence,
            'objection': self.animate_objection,
            'closing': self.animate_closing,
            'judgment': self.animate_judgment
        }
        
    def animate_opening(self, role):
        """Animation for opening statements"""
        st.markdown("""
        <div class="opening-statement">
            <h3>Opening Statements Phase</h3>
            <p>Present your opening statement to the court. Explain your client's position and what you intend to prove.</p>
        </div>
        """, unsafe_allow_html=True)
        
    def animate_examination(self, role):
        """Animation for witness examination"""
        st.markdown("""
        <style>
        @keyframes slideIn {
            from { transform: translateX(-100%); }
            to { transform: translateX(0); }
        }
        .examination {
            animation: slideIn 1s ease-out;
            padding: 10px;
            border-left: 4px solid #43A047;
            background-color: #E8F5E9;
        }
        </style>
        <div class="examination">
            <h3>Witness Examination Phase</h3>
            <p>Witnesses will now be called to testify and be examined by the lawyers.</p>
        </div>
        """, unsafe_allow_html=True)
        
    def animate_evidence(self, role):
        """Animation for evidence presentation"""
        st.markdown("""
        <style>
        @keyframes scaleIn {
            from { transform: scale(0); }
            to { transform: scale(1); }
        }
        .evidence {
            animation: scaleIn 1s ease-in-out;
            padding: 10px;
            border-left: 4px solid #FB8C00;
            background-color: #FFF3E0;
        }
        </style>
        <div class="evidence">
            <h3>Evidence Presentation Phase</h3>
            <p>The lawyers will now present and discuss key evidence in the case.</p>
        </div>
        """, unsafe_allow_html=True)
        
    def animate_objection(self, role):
        """Animation for objections"""
        st.markdown("""
        <style>
        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.05); }
            100% { transform: scale(1); }
        }
        .objection {
            animation: pulse 0.5s infinite;
            padding: 10px;
            border-left: 4px solid #E53935;
            background-color: #FFEBEE;
        }
        </style>
        <div class="objection">
            <h3>Objection Phase</h3>
            <p>Lawyers may raise objections to evidence or testimony that violates legal procedures.</p>
        </div>
        """, unsafe_allow_html=True)
        
    def animate_closing(self, role):
        """Animation for closing arguments"""
        st.markdown("""
        <style>
        @keyframes slideInFromBottom {
            from { transform: translateY(100%); opacity: 0; }
            to { transform: translateY(0); opacity: 1; }
        }
        .closing {
            animation: slideInFromBottom 1s ease-out;
            padding: 10px;
            border-left: 4px solid #7B1FA2;
            background-color: #F3E5F5;
        }
        </style>
        <div class="closing">
            <h3>Closing Arguments Phase</h3>
            <p>The lawyers will now present their final arguments summarizing their case.</p>
        </div>
        """, unsafe_allow_html=True)
        
    def animate_judgment(self, role):
        """Animation for judgment"""
        st.markdown("""
        <style>
        @keyframes glow {
            0% { box-shadow: 0 0 5px gold; }
            50% { box-shadow: 0 0 20px gold; }
            100% { box-shadow: 0 0 5px gold; }
        }
        .judgment {
            animation: glow 2s infinite;
            padding: 10px;
            border-left: 4px solid #FFC107;
            background-color: #FFF8E1;
        }
        </style>
        <div class="judgment">
            <h3>Judgment Phase</h3>
            <p>The judge will now deliver the final verdict based on the evidence and arguments presented.</p>
        </div>
        """, unsafe_allow_html=True)
        
    def animate_phase(self, phase, role=None):
        """Select and run the appropriate animation for the current phase"""
        if phase in self.phase_animations:
            self.phase_animations[phase](role)
        else:
            st.write(f"Phase: {phase}")

# --- Helper functions ---
def load_users():
    # Return a default user dict with admin/1234 if users.json is missing or removed
    return {"admin": {"password": "1234", "transcripts": []}}

def load_cases():
    with open('data/cases.json', 'r') as f:
        return json.load(f)["cases"]

def get_case_by_id(case_id):
    for case in load_cases():
        if case["case_id"] == case_id:
            return case
    return None

def get_speaker_role(role):
    """Convert UI role to character role for animation"""
    mapping = {
        "Judge": "judge",
        "Plaintiff Lawyer": "plaintiff_lawyer",
        "Defendant Lawyer": "defendant_lawyer",
        "Witness": "witness"
    }
    return mapping.get(role, None)

# --- Streamlit App ---

# Initialize TTS and STT engines
if 'tts_engine' not in st.session_state:
    st.session_state.tts_engine = TTSEngine()
if 'stt_engine' not in st.session_state:
    st.session_state.stt_engine = STTEngine()

# Initialize animations
if 'courtroom_anim' not in st.session_state:
    st.session_state.courtroom_anim = CourtroomAnimation()
if 'proceeding_anim' not in st.session_state:
    st.session_state.proceeding_anim = CourtroomProceedingAnimation()

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
            users = load_users()
            if username == "admin" and password == "1234":
                st.session_state.logged_in = True
                st.session_state.username = username
                # Add animation for successful login
                st.markdown("""
                <div style="text-align:center; animation: fadeIn 1s;">
                    <h3 style="color: green;">Login Successful!</h3>
                    <p>Welcome to the Indian Court Simulator</p>
                </div>
                """, unsafe_allow_html=True)
                time.sleep(1)  # Short delay for animation effect
                st.rerun()
            else:
                st.error("Invalid username or password.")
    st.stop()

# --- Case Selection ---
if 'selected_case_id' not in st.session_state:
    st.session_state.selected_case_id = None
if not st.session_state.selected_case_id:
    st.subheader("Select a Case")
    cases = load_cases()
    case_options = []
    
    # Create visual case cards
    cols = st.columns(3)
    for i, case in enumerate(cases):
        with cols[i % 3]:
            st.markdown(f"""
            <div style="border:1px solid #ddd; padding:10px; border-radius:5px; margin:5px; animation: fadeIn 1s {i*0.2}s;">
                <h4>{case['title']}</h4>
                <p><strong>Type:</strong> {case['case_type']}</p>
                <p><strong>Parties:</strong> {case['parties']['plaintiff']} vs. {case['parties']['defendant']}</p>
            </div>
            """, unsafe_allow_html=True)
    
    case_titles = [f"{case['case_id']}: {case['title']}" for case in cases]
    case_choice = st.selectbox("Choose a case", case_titles)
    if st.button("Confirm Case"):
        st.session_state.selected_case_id = case_choice.split(':')[0]
        st.rerun()
    st.stop()

case = get_case_by_id(st.session_state.selected_case_id)

# --- Role Selection ---
roles = ["Judge", "Plaintiff Lawyer", "Defendant Lawyer", "Witness"]
if 'selected_role' not in st.session_state:
    st.session_state.selected_role = None
if not st.session_state.selected_role:
    st.subheader("Choose Your Role")
    
    # Visual role selection cards
    cols = st.columns(4)
    role_icons = {
        "Judge": "⚖️", 
        "Plaintiff Lawyer": "👨‍💼", 
        "Defendant Lawyer": "👩‍💼", 
        "Witness": "👁️"
    }
    
    role_descs = {
        "Judge": "Preside over the court, rule on objections, and deliver the final judgment",
        "Plaintiff Lawyer": "Represent the plaintiff, present evidence and arguments",
        "Defendant Lawyer": "Represent the defendant, present evidence and arguments",
        "Witness": "Provide testimony when called upon by the lawyers"
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
        # Animation for role confirmation
        st.markdown(f"""
        <div style="text-align:center; animation: fadeIn 1s;">
            <h3>You selected: {role}</h3>
            <p>Preparing the courtroom...</p>
        </div>
        """, unsafe_allow_html=True)
        time.sleep(1)  # Short delay for animation effect
        st.rerun()
    st.stop()

# --- Simulation Setup ---
if 'simulation' not in st.session_state:
    # Prepare case_data for simulation manager
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
    
    # Initialize simulation with agents
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
    'examination',
    'evidence',
    'objection',
    'closing',
    'judgment',
    'completed'
]
phase = st.session_state.current_phase

# Header with phase indicator
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

# --- Draw courtroom animation ---
role_for_animation = get_speaker_role(st.session_state.selected_role)
st.session_state.courtroom_anim.animate_phase(phase, role_for_animation if st.session_state.current_speaker == role_for_animation else None)
st.session_state.proceeding_anim.animate_phase(phase, st.session_state.selected_role)

# Transcript in expandable section
with st.expander("Court Transcript", expanded=True):
    transcript = sim.get_state()['transcript']
    if transcript:
        for entry in transcript:
            # Only show agent responses for the user's role and LLM agent responses
            if entry['speaker'] == st.session_state.selected_role or entry['speaker'] in [
                'Judge', 'Plaintiff Lawyer', 'Defendant Lawyer', 'Witness']:
                # Use a dark background for transcript entries for contrast
                st.markdown(f"""
                <div style="background:#181818;padding:10px;border-radius:6px;margin-bottom:6px;">
                    <span style="color:#e10600;font-weight:bold;">{entry['speaker']}:</span>
                    <span style="color:#fff;">{entry['content']}</span>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("The court transcript will appear here as the case proceeds.")

# --- Role-Playing & Phase Actions ---
role = st.session_state.selected_role
user_input = None

# Main court action area
st.markdown("<hr>", unsafe_allow_html=True)
st.subheader("Your Actions")

if phase == 'opening':
    if role in ["Plaintiff Lawyer", "Defendant Lawyer"]:
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
                    # Set current speaker for animation
                    st.session_state.current_speaker = role_for_animation
                    
                    # Add user's input directly to transcript
                    sim.add_to_transcript(role, user_input)
                    
                    # Animate the speech
                    st.markdown(f"""
                    <div class="speaking-animation" style="padding: 10px; background-color: #222; border-radius: 5px;">
                        <strong>{role}:</strong> {user_input[:50]}...
                    </div>
                    """, unsafe_allow_html=True)
                    
                    time.sleep(1)  # Short delay for animation effect
                    
                    # Check if both lawyers have submitted opening statements
                    opening_count = 0
                    for entry in sim.get_state()['transcript']:
                        if 'Opening Statement' in entry['content']:
                            opening_count += 1
                    
                    if opening_count >= 2:
                        st.session_state.current_phase = 'examination'
                    
                    st.rerun()
                else:
                    st.warning("Please enter your statement before submitting.")
    
    elif role == "Judge":
        st.info("You are presiding over the opening statements. You may comment on the statements.")
        if st.button("Comment on Statement"):
            # Use judge agent to generate a response
            judge_agent = st.session_state.agents['judge']
            comment = judge_agent.comment_on_statement(sim.get_state()['transcript'][-1]['content'])
            sim.add_to_transcript("Judge", comment)
            st.rerun()
        
        if st.button("Proceed to Examination Phase"):
            st.session_state.current_phase = 'examination'
            st.rerun()
    
    elif role == "Witness":
        st.info("Witnesses are not active during opening statements. Please wait for your turn during the examination phase.")

elif phase == 'examination':
    if role in ["Plaintiff Lawyer", "Defendant Lawyer"]:
        st.markdown("""
        <div class="examination">
            <h3>Witness Examination Phase</h3>
            <p>You may now call and question witnesses to support your case.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Interactive witness selection
        witness_names = [w['name'] for w in case['witnesses']]
        witness_choice = st.selectbox("Choose a witness to examine", witness_names)
        question = st.text_area("Enter your question for the witness:")
        
        if st.button("Ask Question", key="ask_question"):
            if question and witness_choice:
                # Set current speaker for animation
                st.session_state.current_speaker = role_for_animation
                
                # Add question to transcript
                sim.add_to_transcript(role, f"Question to {witness_choice}: {question}")
                
                # Use witness agent to generate response
                witness_agent = st.session_state.agents['witness']
                response = witness_agent.respond_to_question(witness_choice, question, case)
                
                # Update current speaker for animation
                st.session_state.current_speaker = "witness"
                # Add witness response to transcript
                sim.add_to_transcript(f"Witness ({witness_choice})", response)
                st.rerun()
            else:
                st.warning("Please select a witness and enter a question.")
    
    elif role == "Judge":
        st.info("You are overseeing the witness examination. You may interrupt if necessary.")
        if st.button("Order Witness to Answer"):
            # Use judge agent to generate a response
            judge_agent = st.session_state.agents['judge']
            order = judge_agent.order_witness_to_answer()
            sim.add_to_transcript("Judge", order)
            st.rerun()
    
    elif role == "Witness":
        st.info("Please wait to be called to testify. Answer questions truthfully when asked.")

elif phase == 'evidence':
    if role in ["Plaintiff Lawyer", "Defendant Lawyer"]:
        st.markdown("""
        <div style="padding: 10px; background-color: #fff3e0; border-radius: 5px; animation: fadeIn 1s;">
            <h4>Evidence Presentation Phase</h4>
            <p>Present evidence to support your case.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Evidence selection with visual cards
        evidence_list = case['evidence']
        cols = st.columns(min(3, len(evidence_list)))
        for i, evidence in enumerate(evidence_list):
            with cols[i % 3]:
                st.markdown(f"""
                <div style="border:1px solid #ddd; padding:10px; border-radius:5px; text-align:center;">
                    <h4>📄</h4>
                    <p><strong>{evidence['title']}</strong></p>
                    <p style="font-size:0.8em;">{evidence['type']}</p>
                </div>
                """, unsafe_allow_html=True)
        
        evidence_choice = st.selectbox("Select evidence to present", [ev['title'] for ev in evidence_list])
        explanation = st.text_area("Explain the significance of this evidence:")
        
        col1, col2 = st.columns([1, 3])
        with col1:
            if st.button("Record Explanation"):
                with st.spinner("Recording..."):
                    st.session_state.tts_engine.speak("Please explain the significance of this evidence.")
                    explanation = st.session_state.stt_engine.process_microphone_input()
                    st.success(f"Recorded: {explanation}")
        with col2:
            if st.button("Present Evidence", key="present_evidence"):
                if explanation and evidence_choice:
                    # Set current speaker for animation
                    st.session_state.current_speaker = role_for_animation
                    # Find the selected evidence
                    selected_evidence = None
                    for ev in evidence_list:
                        if ev['title'] == evidence_choice:
                            selected_evidence = ev
                            break
                    
                    if selected_evidence:
                        # Animate evidence presentation
                        st.markdown(f"""
                        <div style="padding: 15px; background-color: #fffde7; border-radius: 5px; 
                                animation: scaleIn 1s; border: 2px dashed #ffa000;">
                            <h4>Evidence Presented: {selected_evidence['title']}</h4>
                            <p><strong>Type:</strong> {selected_evidence['type']}</p>
                            <p><strong>Description:</strong> {selected_evidence['description']}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Add to transcript
                        sim.add_to_transcript(role, f"Presenting evidence: {selected_evidence['title']} - {explanation}")
                        
                        # Add to presented evidence list
                        if selected_evidence not in st.session_state.evidence_presented:
                            st.session_state.evidence_presented.append(selected_evidence)
                        
                        time.sleep(1)  # Short delay for animation effect
                        st.rerun()
                else:
                    st.warning("Please select evidence and provide an explanation.")
        
        # Option to move to objection or closing phase
        if st.button("Conclude Evidence Phase"):
            st.session_state.current_phase = 'closing'
            st.rerun()
    
    elif role == "Judge":
        st.info("You are overseeing the evidence presentation. You may comment on the admissibility of evidence.")
        if st.button("Question Evidence Relevance"):
            sim.add_to_transcript("Judge", "The court questions the relevance of this evidence. Please explain further.")
            st.rerun()
        if st.button("Move to Closing Arguments"):
            st.session_state.current_phase = 'closing'
            st.rerun()
    
    elif role == "Witness":
        st.info("Witnesses are not active during evidence presentation unless called upon to verify evidence.")

elif phase == 'objection':
    if role in ["Plaintiff Lawyer", "Defendant Lawyer"]:
        st.markdown("""
        <div style="padding: 10px; background-color: #ffebee; border-radius: 5px; animation: pulse 1s infinite;">
            <h4>Objection Phase</h4>
            <p>You may raise objections to testimony or evidence.</p>
        </div>
        """, unsafe_allow_html=True)
        
        objection_reasons = [
            "Relevance",
            "Hearsay",
            "Leading the witness",
            "Speculation",
            "Lack of foundation",
            "Argumentative",
            "Asked and answered"
        ]
        
        objection_reason = st.selectbox("Select reason for objection", objection_reasons)
        objection_details = st.text_area("Explain your objection:")
        
        if st.button("Raise Objection", key="raise_objection"):
            if objection_details:
                # Dramatic animation for objection
                st.markdown("""
                <div style="text-align:center; animation: scaleIn 0.5s;">
                    <h2 style="color:red; font-weight:bold;">OBJECTION!</h2>
                </div>
                """, unsafe_allow_html=True)
                
                # Set current speaker for animation
                st.session_state.current_speaker = role_for_animation
                sim.add_to_transcript(role, f"Objection! {objection_reason}: {objection_details}")
                time.sleep(1)  # Short delay for animation effect
                st.rerun()
            else:
                st.warning("Please explain your objection before submitting.")
    
    elif role == "Judge":
        st.markdown("""
        <div style="padding: 10px; background-color: #e8eaf6; border-radius: 5px; animation: fadeIn 1s;">
            <h4>Ruling on Objection</h4>
            <p>You must rule on the objection raised.</p>
        </div>
        """, unsafe_allow_html=True)
        
        latest_entries = sim.get_state()['transcript'][-3:] if len(sim.get_state()['transcript']) >= 3 else sim.get_state()['transcript']
        objection_found = False
        
        for entry in latest_entries:
            if 'Objection!' in entry['content']:
                objection_found = True
                st.markdown(f"""
                <div style="padding: 10px; background-color: #f8f9fa; border-radius: 5px;">
                    <strong>{entry['speaker']}:</strong> {entry['content']}
                </div>
                """, unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Sustain Objection"):
                        # Set current speaker for animation
                        st.session_state.current_speaker = "judge"
                        sim.add_to_transcript("Judge", "Objection sustained.")
                        
                        # Animation for ruling
                        st.markdown("""
                        <div class="gavel-animation">
                            <span class="gavel">🔨</span>
                            <h3>Sustained</h3>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        time.sleep(1)  # Short delay for animation effect
                        st.session_state.current_phase = 'evidence'
                        st.rerun()
                with col2:
                    if st.button("Overrule Objection"):
                        # Set current speaker for animation
                        st.session_state.current_speaker = "judge"
                        sim.add_to_transcript("Judge", "Objection overruled. Please continue.")
                        
                        # Animation for ruling
                        st.markdown("""
                        <div class="gavel-animation">
                            <span class="gavel">🔨</span>
                            <h3>Overruled</h3>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        time.sleep(1)  # Short delay for animation effect
                        st.session_state.current_phase = 'evidence'
                        st.rerun()
        
        if not objection_found:
            st.info("No objections have been raised to rule on.")
            if st.button("Return to Evidence Phase"):
                st.session_state.current_phase = 'evidence'
                st.rerun()
    
    elif role == "Witness":
        st.info("Please wait while the objection is being handled by the court.")

elif phase == 'closing':
    if role in ["Plaintiff Lawyer", "Defendant Lawyer"]:
        st.markdown("""
        <div style="padding: 10px; background-color: #f3e5f5; border-radius: 5px; animation: fadeIn 1s;">
            <h4>Closing Arguments Phase</h4>
            <p>Present your final arguments summarizing your case.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Show evidence summary
        if st.session_state.evidence_presented:
            st.subheader("Evidence Presented")
            for ev in st.session_state.evidence_presented:
                st.markdown(f"""
                <div style="padding: 5px; background-color: #f5f5f5; border-radius: 5px; margin-bottom: 5px;">
                    <strong>{ev['title']}</strong> - {ev['type']}
                </div>
                """, unsafe_allow_html=True)
        
        closing_argument = st.text_area("Enter your closing argument:")
        
        col1, col2 = st.columns([1, 3])
        with col1:
            if st.button("Record Closing Argument"):
                with st.spinner("Recording..."):
                    st.session_state.tts_engine.speak("Please deliver your closing argument.")
                    closing_argument = st.session_state.stt_engine.process_microphone_input()
                    st.success(f"Recorded: {closing_argument}")
        with col2:
            if st.button("Submit Closing Argument", key="submit_closing"):
                if closing_argument:
                    # Set current speaker for animation
                    st.session_state.current_speaker = role_for_animation
                    sim.add_to_transcript(role, f"Closing Argument: {closing_argument}")
                    
                    # Animate the closing argument
                    st.markdown(f"""
                    <div class="speaking-animation" style="padding: 10px; background-color: #f3e5f5; border-radius: 5px;">
                        <strong>{role} Closing:</strong> {closing_argument[:50]}...
                    </div>
                    """, unsafe_allow_html=True)
                    
                    time.sleep(1)  # Short delay for animation effect
                    
                    # Check if both lawyers have submitted closing arguments
                    closing_count = 0
                    for entry in sim.get_state()['transcript']:
                        if 'Closing Argument:' in entry['content']:
                            closing_count += 1
                    
                    if closing_count >= 2:
                        st.session_state.current_phase = 'judgment'
                    
                    st.rerun()
                else:
                    st.warning("Please enter your closing argument before submitting.")
    
    elif role == "Judge":
        st.info("You are listening to the closing arguments. You will deliver judgment after both sides present.")
        if st.button("Move to Judgment Phase"):
            st.session_state.current_phase = 'judgment'
            st.rerun()
    
    elif role == "Witness":
        st.info("Witnesses are not active during closing arguments.")

elif phase == 'judgment':
    if role == "Judge":
        st.markdown("""
        <div class="judgment">
            <h3>Judgment Phase</h3>
            <p>Deliver your final verdict based on the evidence and arguments presented.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Use judge agent to analyze the case
        judge_agent = st.session_state.agents['judge']
        verdict = judge_agent.analyze_case(sim.get_state()['transcript'], case)
        
        if st.button("Pronounce Judgment"):
            # Set current speaker for animation
            st.session_state.current_speaker = "judge"
            sim.add_to_transcript("Judge", f"Final Judgment: {verdict}")
            st.session_state.current_phase = 'completed'
            st.rerun()
    
    else:
        st.info("Please wait for the judge to deliver the final judgment.")
        
        # Show a pulsing "Awaiting Judgment" animation
        st.markdown("""
        <div style="text-align:center; margin: 30px 0; animation: pulse 1.5s infinite;">
            <h3>Awaiting Final Judgment</h3>
            <div style="font-size: 40px;">⚖️</div>
        </div>
        """, unsafe_allow_html=True)

elif phase == 'completed':
    st.markdown("""
    <div style="text-align:center; animation: fadeIn 2s;">
        <h2 style="color: #1E3A8A;">Case Completed</h2>
        <div style="font-size: 50px; margin: 20px 0;">⚖️</div>
        <p style="font-size: 18px;">Justice has been served</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Display final judgment
    final_judgment = None
    for entry in reversed(sim.get_state()['transcript']):
        if 'Final Judgment' in entry['content']:
            final_judgment = entry
            break
    
    if final_judgment:
        st.markdown(f"""
        <div style="padding: 20px; background-color: #fff8e1; border-radius: 10px; border: 2px solid #ffd600; 
                  margin: 20px 0; animation: glow 3s infinite;">
            <h3>Final Verdict</h3>
            <p><strong>{final_judgment['speaker']}:</strong> {final_judgment['content']}</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Show confetti animation
    st.session_state.courtroom_anim.animate_confetti()
    
    # Option to start a new case
    if st.button("Start a New Case"):
        # Reset session state
        for key in ['selected_case_id', 'selected_role', 'simulation', 'current_phase', 
                    'transcript', 'evidence_presented', 'selected_witness', 'current_speaker']:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()

# --- Bottom navigation buttons ---
st.markdown("<hr>", unsafe_allow_html=True)
cols = st.columns(3)

# Save and load transcript functionality
with cols[0]:
    if st.button("Save Transcript"):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"transcript_{case['case_id']}_{timestamp}.json"
        
        # Save transcript data
        transcript_data = {
            "case_id": case["case_id"],
            "case_title": case["title"],
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "user_role": st.session_state.selected_role,
            "transcript": sim.get_state()['transcript']
        }
        
        # In a real app, this would save to a file or database
        st.json(transcript_data)
        st.success(f"Transcript saved as {filename}")

with cols[1]:
    if st.button("Help / Tutorial"):
        st.markdown("""
        ### Tutorial
        1. **Select your role**: Judge, lawyer, or witness
        2. **Navigate through phases**: Opening statements → Examination → Evidence → Objections → Closing → Judgment
        3. **Use the microphone**: Record your statements when available
        4. **View transcript**: Expand the transcript section to see the full court record
        
        ### Tips
        - Lawyers can present evidence, question witnesses, and raise objections
        - The judge controls the proceedings and delivers the final judgment
        - Witnesses provide testimony when questioned
        """)

with cols[2]:
    if st.button("Exit Simulation"):
        # Reset session state
        for key in ['selected_case_id', 'selected_role', 'simulation', 'current_phase', 
                    'transcript', 'evidence_presented', 'selected_witness', 'current_speaker']:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()

# --- Footer ---
st.markdown("""
<div style="text-align:center; margin-top: 30px; padding: 10px; background-color: #f1f1f1; border-radius: 5px;">
    <p>Indian Court Simulator - Educational Tool © 2024</p>
</div>
""", unsafe_allow_html=True)

def main():
    # Initialize the frontend
    frontend = CourtroomFrontend()
    frontend.setup_page()
    
    # Initialize the simulation manager
    if 'sim' not in st.session_state:
        # Load case data
        case_data = {
            'title': 'Sample Case',
            'description': 'A sample case for testing the court simulator',
            'plaintiff': {
                'name': 'John Doe',
                'claims': ['Breach of contract', 'Financial damages']
            },
            'defendant': {
                'name': 'Jane Smith',
                'defenses': ['No breach occurred', 'No damages suffered']
            },
            'witnesses': [
                {
                    'name': 'Witness 1',
                    'role': 'Expert',
                    'testimony': 'Expert analysis of the contract'
                }
            ],
            'evidence': [
                {
                    'id': 'E1',
                    'type': 'Document',
                    'description': 'Contract agreement'
                }
            ]
        }
        st.session_state.sim = create_simulation(case_data)
    
    # Get the current simulation state
    sim = st.session_state.sim
    simulation_state = sim.get_simulation_state()
    
    # Display the main courtroom interface
    frontend.display_courtroom(simulation_state)
    
    # Display the current phase interface
    frontend.display_phase_interface(simulation_state['phase'], simulation_state['role'])
    
    # Display the phase indicator
    frontend.display_phase_indicator(simulation_state['phase'])
    
    # Handle user input based on the current phase
    if simulation_state['phase'] == 'opening':
        user_input = st.text_area("Enter your opening statement:")
        if st.button("Submit Opening Statement"):
            if user_input:
                sim.add_to_transcript(simulation_state['role'], user_input)
                frontend.display_success("Opening statement submitted successfully!")
            else:
                frontend.display_warning("Please enter your opening statement.")
    
    # Add similar handlers for other phases...
    
    # Display the footer
    st.markdown("""
    <div style="text-align:center; margin-top: 30px; padding: 10px; background-color: #f1f1f1; border-radius: 5px;">
        <p>Indian Court Simulator - Educational Tool © 2024</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()