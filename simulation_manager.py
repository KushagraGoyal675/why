from typing import Dict, Any, List
from datetime import datetime
from agents.plaintiff_agent import PlaintiffAgent
from agents.defendant_agent import DefendantAgent
from agents.judge_agent import JudgeAgent
from agents.witness_agent import WitnessAgent

class SimulationManager:
    def __init__(self):
        self.current_phase = 'opening'
        self.current_role = 'Judge'
        self.transcript = []
        self.evidence_presented = []
        self.selected_witness = None
        self.current_speaker = None
        
        # Initialize agents
        self.plaintiff_agent = PlaintiffAgent()
        self.defendant_agent = DefendantAgent()
        self.judge_agent = JudgeAgent()
        self.witness_agent = WitnessAgent()
        
    def add_to_transcript(self, speaker: str, content: str):
        """Add an entry to the transcript"""
        self.transcript.append({
            'speaker': speaker,
            'content': content,
            'timestamp': datetime.now().strftime('%H:%M:%S')
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
            'witness': self.selected_witness
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
            'phase': self.current_phase,
            'role': self.current_role,
            'transcript': self.transcript,
            'evidence': self.evidence_presented,
            'witness': self.selected_witness,
            'speaker': self.current_speaker
        } 