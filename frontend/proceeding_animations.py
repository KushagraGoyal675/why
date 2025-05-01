import streamlit as st
from .animations import AnimationManager
import time

class CourtProceedingAnimations:
    def __init__(self):
        self.animation_manager = AnimationManager()

    def gavel_animation(self):
        """Displays a gavel animation effect."""
        st.markdown(
            """
            <div style='text-align: center; font-size: 2em; animation: gavel 1s;'>
                🔨
            </div>
            <style>
                @keyframes gavel {
                    0% { transform: rotate(0deg); }
                    25% { transform: rotate(-20deg); }
                    75% { transform: rotate(20deg); }
                    100% { transform: rotate(0deg); }
                }
            </style>
            """,
            unsafe_allow_html=True
        )
        time.sleep(1)

    def phase_transition_animation(self, from_phase: str, to_phase: str):
        """Animates the transition between court phases."""
        progress_text = f"Transitioning from {from_phase} to {to_phase}..."
        self.animation_manager.progress_bar_animation(
            progress_text,
            duration=2.0,
            on_complete=lambda: self.gavel_animation()
        )

    def evidence_presentation_animation(self, evidence_type: str):
        """Displays an animation for evidence presentation."""
        icon = "📄" if evidence_type == "document" else "🖼️" if evidence_type == "image" else "📹"
        st.markdown(
            f"""
            <div style='text-align: center; animation: present 1s;'>
                <div style='font-size: 3em;'>{icon}</div>
                <div style='font-size: 1.2em; color: #e10600;'>Presenting {evidence_type}</div>
            </div>
            <style>
                @keyframes present {{
                    from {{ transform: scale(0.5); opacity: 0; }}
                    to {{ transform: scale(1); opacity: 1; }}
                }}
            </style>
            """,
            unsafe_allow_html=True
        )
        time.sleep(1.5)

    def objection_animation(self, objection_type: str):
        """Displays an objection animation with the specified type."""
        st.markdown(
            f"""
            <div style='text-align: center; animation: objection 0.5s;'>
                <div style='font-size: 2em; color: #e10600; font-weight: bold;'>
                    OBJECTION!
                </div>
                <div style='font-size: 1.2em; color: #fff;'>
                    {objection_type}
                </div>
            </div>
            <style>
                @keyframes objection {{
                    0% {{ transform: scale(0.5); opacity: 0; }}
                    50% {{ transform: scale(1.2); }}
                    100% {{ transform: scale(1); opacity: 1; }}
                }}
            </style>
            """,
            unsafe_allow_html=True
        )
        time.sleep(1)

    def verdict_animation(self, verdict: str):
        """Displays an animation for the court's verdict."""
        icon = "⚖️"
        color = "#4CAF50" if verdict.lower() == "accepted" else "#e10600"
        
        st.markdown(
            f"""
            <div style='text-align: center;'>
                <div style='font-size: 3em; animation: verdict-icon 2s;'>{icon}</div>
                <div style='font-size: 2em; color: {color}; animation: verdict-text 1s;'>
                    {verdict.upper()}
                </div>
            </div>
            <style>
                @keyframes verdict-icon {{
                    0% {{ transform: translateY(-50px); opacity: 0; }}
                    100% {{ transform: translateY(0); opacity: 1; }}
                }}
                @keyframes verdict-text {{
                    0% {{ transform: scale(0.8); opacity: 0; }}
                    100% {{ transform: scale(1); opacity: 1; }}
                }}
            </style>
            """,
            unsafe_allow_html=True
        )
        time.sleep(2)

    def witness_transition_animation(self, witness_name: str):
        """Displays an animation for witness transitions."""
        st.markdown(
            f"""
            <div style='text-align: center;'>
                <div style='font-size: 1.5em; color: #fff;'>
                    Now calling to the stand
                </div>
                <div style='font-size: 2em; color: #e10600; margin-top: 10px; animation: witness 1s;'>
                    {witness_name}
                </div>
            </div>
            <style>
                @keyframes witness {{
                    from {{ transform: translateX(-100%); opacity: 0; }}
                    to {{ transform: translateX(0); opacity: 1; }}
                }}
            </style>
            """,
            unsafe_allow_html=True
        )
        time.sleep(1.5) 