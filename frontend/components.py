import streamlit as st
from typing import Dict, Any, List
import time

class CourtroomUI:
    def __init__(self):
        self.inject_custom_css()
    
    def inject_custom_css(self):
        st.markdown(
            '''
            <style>
            body, .stApp {
                background-color: #18181b !important;
                color: #fff !important;
            }
            .courtroom-col {
                background: #23232a;
                border-radius: 12px;
                padding: 18px 12px 12px 12px;
                margin: 0 8px 12px 8px;
                min-height: 220px;
                box-shadow: 0 2px 8px #0002;
            }
            .courtroom-avatar {
                font-size: 2.5rem;
                margin-bottom: 8px;
            }
            .courtroom-name {
                font-weight: bold;
                color: #e10600;
                margin-bottom: 6px;
            }
            .chat-bubble {
                background: #222;
                border-radius: 10px;
                padding: 12px 16px;
                margin-bottom: 8px;
                color: #fff;
                font-size: 1.05rem;
                box-shadow: 0 1px 4px #0003;
            }
            .chat-bubble.judge { border-left: 5px solid #e10600; }
            .chat-bubble.plaintiff { border-left: 5px solid #1e90ff; }
            .chat-bubble.defendant { border-left: 5px solid #43a047; }
            .chat-bubble.witness { border-left: 5px solid #fbc02d; }
            .phase-banner {
                background: linear-gradient(90deg, #e10600 0%, #23232a 100%);
                color: #fff;
                font-size: 1.3rem;
                font-weight: bold;
                text-align: center;
                border-radius: 8px;
                margin: 18px 0 18px 0;
                padding: 10px 0;
                letter-spacing: 1px;
                box-shadow: 0 2px 8px #0002;
            }
            .speaking {
                box-shadow: 0 0 16px 4px #e10600cc !important;
                border: 2px solid #e10600 !important;
            }
            .transcript-sidebar {
                background: #23232a;
                border-radius: 10px;
                padding: 12px;
                margin-top: 10px;
                color: #fff;
                font-size: 1rem;
                max-height: 400px;
                overflow-y: auto;
            }
            </style>
            ''', unsafe_allow_html=True)
    
    def display_courtroom(self, simulation_state: Dict[str, Any], speaking_role: str = None):
        # Layout: Judge | Plaintiff Lawyer | Witness | Defendant Lawyer
        col_judge, col_plaintiff, col_witness, col_defendant = st.columns([1.2, 1.5, 1.2, 1.5])
        avatars = {
            "judge": "👨‍⚖️",
            "plaintiff": "🧑‍💼",
            "defendant": "🧑‍💼",
            "witness": "🧑‍🦳"
        }
        names = {
            "judge": "Judge",
            "plaintiff": "Plaintiff Lawyer",
            "defendant": "Defendant Lawyer",
            "witness": "Witness"
        }
        # Get last utterances for each role
        last_statements = self._get_last_statements(simulation_state.get('transcript', []))
        # Judge
        with col_judge:
            st.markdown(f'<div class="courtroom-col {"speaking" if speaking_role=="judge" else ""}">', unsafe_allow_html=True)
            st.markdown(f'<div class="courtroom-avatar">{avatars["judge"]}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="courtroom-name">{names["judge"]}</div>', unsafe_allow_html=True)
            if last_statements["judge"]:
                st.markdown(f'<div class="chat-bubble judge">{last_statements["judge"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="chat-bubble judge">...</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        # Plaintiff Lawyer
        with col_plaintiff:
            st.markdown(f'<div class="courtroom-col {"speaking" if speaking_role=="plaintiff" else ""}">', unsafe_allow_html=True)
            st.markdown(f'<div class="courtroom-avatar">{avatars["plaintiff"]}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="courtroom-name">{names["plaintiff"]}</div>', unsafe_allow_html=True)
            if last_statements["plaintiff"]:
                st.markdown(f'<div class="chat-bubble plaintiff">{last_statements["plaintiff"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="chat-bubble plaintiff">...</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        # Witness
        with col_witness:
            st.markdown(f'<div class="courtroom-col {"speaking" if speaking_role=="witness" else ""}">', unsafe_allow_html=True)
            st.markdown(f'<div class="courtroom-avatar">{avatars["witness"]}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="courtroom-name">{names["witness"]}</div>', unsafe_allow_html=True)
            if last_statements["witness"]:
                st.markdown(f'<div class="chat-bubble witness">{last_statements["witness"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="chat-bubble witness">...</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        # Defendant Lawyer
        with col_defendant:
            st.markdown(f'<div class="courtroom-col {"speaking" if speaking_role=="defendant" else ""}">', unsafe_allow_html=True)
            st.markdown(f'<div class="courtroom-avatar">{avatars["defendant"]}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="courtroom-name">{names["defendant"]}</div>', unsafe_allow_html=True)
            if last_statements["defendant"]:
                st.markdown(f'<div class="chat-bubble defendant">{last_statements["defendant"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="chat-bubble defendant">...</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
    
    def _get_last_statements(self, transcript: List[Dict[str, Any]]):
        # Find the last statement for each role
        last = {"judge": None, "plaintiff": None, "defendant": None, "witness": None}
        for entry in reversed(transcript):
            speaker = entry["speaker"].lower()
            if "judge" in speaker and not last["judge"]:
                last["judge"] = entry["content"]
            elif "plaintiff" in speaker and not last["plaintiff"]:
                last["plaintiff"] = entry["content"]
            elif "defendant" in speaker and not last["defendant"]:
                last["defendant"] = entry["content"]
            elif "witness" in speaker and not last["witness"]:
                last["witness"] = entry["content"]
        return last
    
    def display_transcript_sidebar(self, transcript: List[Dict[str, Any]]):
        st.markdown('<div class="transcript-sidebar"><b>Live Transcript</b><br>', unsafe_allow_html=True)
        for entry in transcript[-30:]:
            st.markdown(f'<span style="color:#e10600;font-weight:bold;">{entry["speaker"]}:</span> <span style="color:#fff;">{entry["content"]}</span><br>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    def display_phase_indicator(self, phase: str, phases: list = None):
        if phases is None:
            phases = [
                'opening',
                'examination',
                'evidence',
                'objection',
                'closing',
                'judgment',
                'completed'
            ]
            
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
        
        user_input = st.text_area(
            "Enter your opening statement:",
            key=f"opening_statement_{role.lower().replace(' ', '_')}"
        )
        col1, col2 = st.columns([1, 3])
        with col1:
            if st.button("Record Statement", key=f"record_statement_{role.lower().replace(' ', '_')}"):
                with st.spinner("Recording..."):
                    st.session_state.tts_engine.speak("Please deliver your opening statement.")
                    user_input = st.session_state.stt_engine.process_microphone_input()
                    st.success(f"Recorded: {user_input}")
        with col2:
            if st.button("Submit Opening Statement", key=f"submit_opening_{role.lower().replace(' ', '_')}"):
                if user_input:
                    return user_input
                else:
                    st.warning("Please enter your statement before submitting.")
        return None

    def display_phase_interface(self, phase: str, role: str):
        """Display the appropriate UI for the current phase and role."""
        if phase == 'opening':
            return self.display_opening_statement_form(role)
        elif phase == 'examination':
            return st.text_area(
                f"Enter your question for the witness:",
                key=f"examination_{role.lower().replace(' ', '_')}"
            )
        elif phase == 'evidence':
            return st.text_area(
                f"Describe the evidence you want to present:",
                key=f"evidence_{role.lower().replace(' ', '_')}"
            )
        elif phase == 'closing':
            return st.text_area(
                f"Enter your closing argument:",
                key=f"closing_{role.lower().replace(' ', '_')}"
            )
        else:
            st.info("This phase does not require user input.")
            return None

    def display_phase_banner(self, phase: str):
        st.markdown(f'<div class="phase-banner">Current Phase: {phase.title()}</div>', unsafe_allow_html=True) 