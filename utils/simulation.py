# utils/simulation.py

from agents.judge_agent import JudgeAgent
from agents.lawyer_agent import LawyerAgent
from agents.clerk_agent import ClerkAgent
from utils import knowledge_base
import streamlit as st
import random
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
from .knowledge_base import KnowledgeBase
from .tts import TTSEngine
from .stt import STTEngine
from agents.witness_agent import WitnessAgent
import json
import os

class Simulation:
    def __init__(self, case_data: Dict[str, Any]):
        self.case_data = case_data
        self.state = {
            'status': 'not_started',
            'current_phase': None,
            'transcript': [],
            'evidence_presented': [],
            'objections': [],
            'active_speaker': None
        }
        self.knowledge_base = knowledge_base.KnowledgeBase()
    
    def start(self):
        """Start the simulation"""
        self.state['status'] = 'in_progress'
        self.state['current_phase'] = 'opening'
        self.add_to_transcript("System", "Court is now in session")
        self.add_to_transcript("Judge", "Let the proceedings begin")
    
    def end(self):
        """End the simulation"""
        self.state['status'] = 'completed'
        self.add_to_transcript("Judge", "Court is adjourned")
    
    def add_to_transcript(self, speaker: str, content: str):
        """Add an entry to the transcript"""
        self.state['transcript'].append({
            'speaker': speaker,
            'content': content,
            'timestamp': datetime.now().isoformat()
        })
    
    def present_evidence(self, evidence_id: str, presenter: str):
        """Present evidence in court"""
        evidence = next(
            (e for e in self.case_data["evidence"] if e["id"] == evidence_id),
            None
        )
        
        if evidence:
            self.state['evidence_presented'].append({
                'evidence': evidence,
                'presented_by': presenter,
                'timestamp': datetime.now().isoformat()
            })
            self.add_to_transcript(presenter, f"Presenting evidence {evidence_id}: {evidence['description']}")
    
    def raise_objection(self, objector: str, reason: str):
        """Raise an objection"""
        objection = {
            'objector': objector,
            'reason': reason,
            'timestamp': datetime.now().isoformat(),
            'status': 'pending'
        }
        self.state['objections'].append(objection)
        self.add_to_transcript(objector, f"Objection! {reason}")
    
    def rule_on_objection(self, ruling: str):
        """Judge rules on the latest objection"""
        if self.state['objections']:
            latest_objection = self.state['objections'][-1]
            latest_objection['status'] = ruling
            self.add_to_transcript("Judge", f"Objection {ruling}")
    
    def get_state(self) -> Dict[str, Any]:
        """Get the current state of the simulation"""
        return {
            'status': self.state['status'],
            'current_phase': self.state['current_phase'],
            'transcript': self.state['transcript'],
            'evidence_presented': self.state['evidence_presented'],
            'objections': self.state['objections'],
            'active_speaker': self.state['active_speaker'],
            'case_info': self.case_data
        }
    
    def save_state(self, filepath: str):
        """Save the simulation state to a file"""
        state = self.get_state()
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w') as f:
            json.dump(state, f, indent=4)
    
    def load_state(self, filepath: str):
        """Load the simulation state from a file"""
        with open(filepath, 'r') as f:
            state = json.load(f)
        self.state = state
        self.case_data = state['case_info']

def run_simulation(case_data: dict, llm_provider: str = "OpenAI", user_role: str = None):
    """Run the courtroom simulation"""
    simulation = Simulation(case_data)
    return simulation.run_simulation()
