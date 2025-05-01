import streamlit as st
from typing import Dict, Any
from .components import CourtroomUI
from .animations import CourtroomAnimation
from .proceeding_animations import CourtroomProceedingAnimation

class CourtroomFrontend:
    def __init__(self):
        self.ui = CourtroomUI()
        self.animation = CourtroomAnimation()
        self.proceeding_animation = CourtroomProceedingAnimation()
        
    def setup_page(self):
        """Setup the main page layout and configuration"""
        self.ui.setup_page_config()
        self.ui.inject_custom_css()
        
    def display_courtroom(self, simulation_state: Dict[str, Any]):
        """Display the main courtroom interface"""
        # Create two columns for the layout
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Display the courtroom animation
            self.animation.animate_phase(simulation_state.get('phase', 'opening'))
            
        with col2:
            # Display the transcript
            self.ui.display_transcript(
                simulation_state.get('transcript', []),
                simulation_state.get('role', 'Judge')
            )
            
    def display_phase_interface(self, phase: str, role: str):
        """Display the interface for the current phase"""
        self.proceeding_animation.animate_phase(phase, role)
        
        if phase == 'opening':
            self.ui.display_opening_statement_form(role)
        elif phase == 'examination':
            self.ui.display_witness_examination_form(role)
        elif phase == 'evidence':
            self.ui.display_evidence_form(role)
        elif phase == 'objection':
            self.ui.display_objection_form(role)
        elif phase == 'closing':
            self.ui.display_closing_argument_form(role)
        elif phase == 'judgment':
            self.ui.display_judgment_form(role)
            
    def display_phase_indicator(self, current_phase: str):
        """Display the current phase indicator"""
        self.ui.display_phase_indicator(current_phase)
        
    def display_error(self, error_message: str):
        """Display an error message"""
        st.error(error_message)
        
    def display_success(self, success_message: str):
        """Display a success message"""
        st.success(success_message)
        
    def display_warning(self, warning_message: str):
        """Display a warning message"""
        st.warning(warning_message)
        
    def display_info(self, info_message: str):
        """Display an info message"""
        st.info(info_message) 