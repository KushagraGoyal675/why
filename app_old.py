import streamlit as st

# Must be called before any other Streamlit commands
st.set_page_config(
    page_title="Lex Orion - Indian Court Simulator",
    page_icon=None,  # We'll update this once we have the logo
    layout="wide"
)

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
from frontend.components import CourtroomUI
from courtroom import create_simulation, CourtroomSimulationManager
from agents.plaintiff_agent import PlaintiffAgent
from agents.defendant_agent import DefendantAgent
from agents.judge_agent import JudgeAgent
from agents.witness_agent import WitnessAgent
from utils.tts import TTSEngine
from utils.stt import STTEngine

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
roles = ["Plaintiff Lawyer", "Defendant Lawyer", "Observer"]
if 'selected_role' not in st.session_state:
    st.session_state.selected_role = None
if not st.session_state.selected_role:
    st.subheader("Choose Your Role")
    
    # Visual role selection cards
    cols = st.columns(3)
    role_icons = {
        "Plaintiff Lawyer": "👨‍💼", 
        "Defendant Lawyer": "👩‍💼", 
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
<div style="text-align:center; margin-bottom:20px;">
    <h2 style="color:#e10600;">{case['title']}</h2>
    <p style="color:#fff;">{case['description']}</p>
</div>
""", unsafe_allow_html=True)

# Display the courtroom
frontend.display_courtroom(sim.get_simulation_state())

# Display the phase indicator
frontend.display_phase_indicator(phase)

# Handle user input based on the current phase and role
if st.session_state.selected_role == "Observer":
    # For observers, just show the transcript and auto-progress
    st.info("You are observing the case. The proceedings will progress automatically.")
    time.sleep(2)  # Add a small delay to make it feel more natural
                    st.rerun()
                else:
    # For lawyers, show the appropriate interface
    if phase == 'opening':
        if st.session_state.selected_role == "Plaintiff Lawyer":
            statement = frontend.display_phase_interface(phase, "Plaintiff Lawyer")
            if statement:
                sim.add_to_transcript("Plaintiff Lawyer", statement)
            st.rerun()
        elif st.session_state.selected_role == "Defendant Lawyer":
            statement = frontend.display_phase_interface(phase, "Defendant Lawyer")
            if statement:
                sim.add_to_transcript("Defendant Lawyer", statement)
                st.rerun()

elif phase == 'examination':
        if st.session_state.selected_role == "Plaintiff Lawyer":
            question = frontend.display_phase_interface(phase, "Plaintiff Lawyer")
            if question:
                sim.add_to_transcript("Plaintiff Lawyer", question)
                            st.rerun()
        elif st.session_state.selected_role == "Defendant Lawyer":
            question = frontend.display_phase_interface(phase, "Defendant Lawyer")
            if question:
                sim.add_to_transcript("Defendant Lawyer", question)
            st.rerun()

elif phase == 'evidence':
        if st.session_state.selected_role == "Plaintiff Lawyer":
            evidence = frontend.display_phase_interface(phase, "Plaintiff Lawyer")
            if evidence:
                sim.add_to_transcript("Plaintiff Lawyer", f"Presenting evidence: {evidence}")
                        st.rerun()
        elif st.session_state.selected_role == "Defendant Lawyer":
            evidence = frontend.display_phase_interface(phase, "Defendant Lawyer")
            if evidence:
                sim.add_to_transcript("Defendant Lawyer", f"Presenting evidence: {evidence}")
            st.rerun()

elif phase == 'closing':
        if st.session_state.selected_role == "Plaintiff Lawyer":
            closing = frontend.display_phase_interface(phase, "Plaintiff Lawyer")
            if closing:
                sim.add_to_transcript("Plaintiff Lawyer", closing)
                    st.rerun()
        elif st.session_state.selected_role == "Defendant Lawyer":
            closing = frontend.display_phase_interface(phase, "Defendant Lawyer")
            if closing:
                sim.add_to_transcript("Defendant Lawyer", closing)
            st.rerun()
    
# Update simulation state
simulation_state = sim.update()
st.session_state.current_phase = simulation_state['phase']

# Footer
        st.markdown("""
<div style="text-align:center; margin-top:50px; padding:20px; border-top:1px solid #333;">
    <p style="color:#666;">Indian Court Simulator - Educational Tool © 2024</p>
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
        user_input = st.text_area(
            "Enter your opening statement:",
            key=f"main_opening_statement_{simulation_state['role'].lower().replace(' ', '_')}"
        )
        if st.button("Submit Opening Statement", key=f"main_submit_opening_{simulation_state['role'].lower().replace(' ', '_')}"):
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