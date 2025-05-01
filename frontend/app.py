import streamlit as st
from .components import CourtroomUI
from .animations import AnimationManager
from .proceeding_animations import CourtProceedingAnimations
from typing import Dict, Any

class CourtroomFrontend:
    def __init__(self):
        self.ui = CourtroomUI()
        self.animations = AnimationManager()
        self.proceeding_animations = CourtProceedingAnimations()
    
    def setup_page(self):
        """Setup the page styling"""
        self.ui.inject_custom_css()
    
    def display_courtroom(self, simulation_state: Dict[str, Any]):
        """Display the main courtroom interface"""
        # Display the transcript
        self.ui.display_transcript(
            simulation_state.get('transcript', []),
            simulation_state.get('selected_role', '')
        )
    
    def display_phase_interface(self, phase: str, role: str):
        """Display the interface for the current phase"""
        if phase == 'opening':
            self.ui.display_opening_statement_form(role)
        # Add other phase interfaces here
    
    def display_phase_indicator(self, current_phase: str):
        """Display the current phase indicator"""
        phases = [
            'opening',
            'examination',
            'evidence',
            'objection',
            'closing',
            'judgment',
            'completed'
        ]
        self.ui.display_phase_indicator(current_phase, phases)
    
    def display_error(self, error_message: str):
        """Display an error message"""
        self.animations.flash_message(error_message, style="error")
    
    def display_success(self, message: str):
        """Display a success message"""
        self.animations.flash_message(message, style="success")
    
    def display_warning(self, message: str):
        """Display a warning message"""
        self.animations.flash_message(message, style="warning")
    
    def animate_phase_transition(self, from_phase: str, to_phase: str):
        """Animate the transition between phases"""
        self.proceeding_animations.phase_transition_animation(from_phase, to_phase)
    
    def animate_evidence_presentation(self, evidence_type: str):
        """Animate evidence presentation"""
        self.proceeding_animations.evidence_presentation_animation(evidence_type)
    
    def animate_objection(self, objection_type: str):
        """Animate an objection"""
        self.proceeding_animations.objection_animation(objection_type)
    
    def animate_verdict(self, verdict: str):
        """Animate the verdict"""
        self.proceeding_animations.verdict_animation(verdict)
    
    def animate_witness_transition(self, witness_name: str):
        """Animate witness transition"""
        self.proceeding_animations.witness_transition_animation(witness_name) 