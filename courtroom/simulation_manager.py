from typing import Dict, Any, List
from datetime import datetime
import json
import os
from utils.knowledge_base import KnowledgeBase
from agents.judge_agent import JudgeAgent
from agents.plaintiff_agent import PlaintiffAgent
from agents.defendant_agent import DefendantAgent
from agents.witness_agent import WitnessAgent
import streamlit as st

class CourtroomSimulationManager:
    def __init__(self, case_data: Dict[str, Any]):
        self.case_data = case_data
        self.transcript = []
        self.current_phase = 'opening'
        self.evidence_presented = []
        self.selected_witness = None
        self.current_speaker = None
        self.auto_progress = True  # Enable automatic progression
        
        # Initialize agents with case data
        self.plaintiff_agent = PlaintiffAgent()
        self.defendant_agent = DefendantAgent()
        self.judge_agent = JudgeAgent()
        self.witness_agent = WitnessAgent()
        
        # Analyze the case
        self.plaintiff_analysis = self.plaintiff_agent.analyze_case(case_data)
        self.defendant_analysis = self.defendant_agent.analyze_case(case_data)
        
    def add_to_transcript(self, speaker: str, content: str):
        """Add an entry to the transcript"""
        self.transcript.append({
            'speaker': speaker,
            'content': content,
            'timestamp': datetime.now().strftime("%H:%M:%S")
        })
        
    def get_transcript(self) -> List[Dict[str, str]]:
        """Get the current transcript"""
        return self.transcript
        
    def get_current_phase(self) -> str:
        """Get the current phase of the simulation"""
        return self.current_phase
        
    def get_current_role(self) -> str:
        """Get the current role in the simulation"""
        return self.current_role
        
    def set_current_phase(self, phase: str):
        """Set the current phase of the simulation"""
        self.current_phase = phase
        
    def set_current_role(self, role: str):
        """Set the current role in the simulation"""
        self.current_role = role
        
    def get_agent(self, role: str):
        """Get the appropriate agent for the given role"""
        if role == 'Plaintiff':
            return self.plaintiff_agent
        elif role == 'Defendant':
            return self.defendant_agent
        elif role == 'Judge':
            return self.judge_agent
        elif role == 'Witness':
            return self.witness_agent
        else:
            raise ValueError(f"Unknown role: {role}")
            
    def process_user_input(self, role: str, input_text: str) -> str:
        """Process user input and get agent response"""
        agent = self.get_agent(role)
        context = {
            'phase': self.current_phase,
            'transcript': self.transcript,
            'evidence': self.evidence_presented,
            'witness': self.selected_witness,
            'case_data': self.case_data
        }
        return agent.generate_response(context)
        
    def add_evidence(self, evidence: Dict[str, Any]):
        """Add evidence to the simulation"""
        self.evidence_presented.append(evidence)
        
    def set_witness(self, witness: Dict[str, Any]):
        """Set the current witness"""
        self.selected_witness = witness
        
    def get_simulation_state(self) -> Dict[str, Any]:
        """Get the current state of the simulation"""
        return {
            'transcript': self.transcript,
            'phase': self.current_phase,
            'evidence_presented': self.evidence_presented,
            'selected_witness': self.selected_witness,
            'current_speaker': self.current_speaker,
            'auto_progress': self.auto_progress
        }
        
    def get_case_summary(self) -> Dict[str, Any]:
        """Get a summary of the case"""
        return {
            'title': self.case_data.get('title', ''),
            'description': self.case_data.get('description', ''),
            'plaintiff_analysis': self.plaintiff_analysis,
            'defendant_analysis': self.defendant_analysis
        }
        
    def progress_phase(self):
        """Progress to the next phase of the trial"""
        phases = [
            'opening',
            'examination',
            'evidence',
            'objection',
            'closing',
            'judgment',
            'completed'
        ]
        current_index = phases.index(self.current_phase)
        if current_index < len(phases) - 1:
            self.current_phase = phases[current_index + 1]
            return True
        return False
    
    def handle_automatic_progression(self):
        """Handle automatic progression of the case"""
        if not self.auto_progress:
            return
            
        if self.current_phase == 'opening':
            # Automatically generate opening statements
            plaintiff_agent = st.session_state.agents['plaintiff']
            defendant_agent = st.session_state.agents['defendant']
            
            plaintiff_statement = plaintiff_agent.generate_opening_statement(self.case_data)
            defendant_statement = defendant_agent.generate_opening_statement(self.case_data)
            
            self.add_to_transcript("Plaintiff Lawyer", plaintiff_statement)
            self.add_to_transcript("Defendant Lawyer", defendant_statement)
            self.progress_phase()
            
        elif self.current_phase == 'examination':
            # Automatically handle witness examination
            if not self.selected_witness:
                # Select first witness
                self.selected_witness = self.case_data['witnesses'][0]
                self.add_to_transcript("Judge", f"Calling {self.selected_witness['name']} to the stand.")
            
            # Generate examination questions and answers
            plaintiff_agent = st.session_state.agents['plaintiff']
            defendant_agent = st.session_state.agents['defendant']
            
            question = plaintiff_agent.generate_question(self.selected_witness)
            answer = self.selected_witness['testimony']
            
            self.add_to_transcript("Plaintiff Lawyer", question)
            self.add_to_transcript("Witness", answer)
            
            # Cross-examination
            question = defendant_agent.generate_question(self.selected_witness)
            answer = self.selected_witness['testimony']
            
            self.add_to_transcript("Defendant Lawyer", question)
            self.add_to_transcript("Witness", answer)
            
            self.progress_phase()
            
        elif self.current_phase == 'evidence':
            # Automatically present evidence
            if not self.evidence_presented:
                for evidence in self.case_data['evidence']:
                    self.add_to_transcript("Plaintiff Lawyer", f"Presenting evidence: {evidence['description']}")
                    self.evidence_presented.append(evidence)
            
            self.progress_phase()
            
        elif self.current_phase == 'closing':
            # Automatically generate closing arguments
            plaintiff_agent = st.session_state.agents['plaintiff']
            defendant_agent = st.session_state.agents['defendant']
            
            plaintiff_closing = plaintiff_agent.generate_closing_argument(self.case_data)
            defendant_closing = defendant_agent.generate_closing_argument(self.case_data)
            
            self.add_to_transcript("Plaintiff Lawyer", plaintiff_closing)
            self.add_to_transcript("Defendant Lawyer", defendant_closing)
            self.progress_phase()
            
        elif self.current_phase == 'judgment':
            # Automatically generate judgment
            judge_agent = st.session_state.agents['judge']
            judgment = judge_agent.give_judgment(str(self.case_data))
            self.add_to_transcript("Judge", judgment)
            self.progress_phase()
    
    def update(self):
        """Update the simulation state"""
        self.handle_automatic_progression()
        return self.get_simulation_state()

def create_simulation(case_data: Dict[str, Any]) -> CourtroomSimulationManager:
    """Create a new courtroom simulation"""
    return CourtroomSimulationManager(case_data) 