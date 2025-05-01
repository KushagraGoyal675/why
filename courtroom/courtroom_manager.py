from typing import Dict, Any, List
from datetime import datetime
import json
import os
from utils import knowledge_base, simulation, tts, stt

class CourtroomManager:
    def __init__(self, case_data: Dict[str, Any]):
        self.case_data = case_data
        self.knowledge_base = knowledge_base.KnowledgeBase()
        self.tts_engine = tts.TTSEngine()
        self.stt_engine = stt.STTEngine()
        
        # Initialize state
        self.state = {
            'status': 'not_started',
            'current_phase': None,
            'transcript': [],
            'evidence_presented': [],
            'objections': [],
            'active_speaker': None,
            'case_info': case_data
        }
    
    def start_hearing(self):
        """Start the court hearing"""
        self.state['status'] = 'in_progress'
        self.state['current_phase'] = 'opening'
        self._add_to_transcript("System", "Court is now in session")
        self._speak_as_judge("Let the proceedings begin")
    
    def end_hearing(self):
        """End the court hearing"""
        self.state['status'] = 'completed'
        self._speak_as_judge("Court is adjourned")
    
    def _add_to_transcript(self, speaker: str, content: str):
        """Add an entry to the transcript"""
        self.state['transcript'].append({
            'speaker': speaker,
            'content': content,
            'timestamp': datetime.now().isoformat()
        })
    
    def _speak_as_judge(self, text: str):
        """Have the judge speak and add to transcript"""
        self.tts_engine.speak(text)
        self._add_to_transcript("Judge", text)
    
    def examine_witness(self, witness_id: str):
        """Examine a witness"""
        witness = next(
            (w for w in self.case_data["witnesses"] if w["witness_id"] == witness_id),
            None
        )
        
        if witness:
            self.state['active_speaker'] = witness["name"]
            self._add_to_transcript("System", f"Examining witness: {witness['name']}")
    
    def present_evidence(self, evidence_id: str):
        """Present evidence in court"""
        evidence = next(
            (e for e in self.case_data["evidence"] if e["id"] == evidence_id),
            None
        )
        
        if evidence:
            self.state['evidence_presented'].append({
                'evidence': evidence,
                'presented_by': 'Lawyer',
                'timestamp': datetime.now().isoformat()
            })
            self._add_to_transcript("Lawyer", f"Presenting evidence {evidence_id}: {evidence['description']}")
    
    def handle_objection(self, objector: str, reason: str):
        """Handle an objection"""
        objection = {
            'objector': objector,
            'reason': reason,
            'timestamp': datetime.now().isoformat(),
            'status': 'pending'
        }
        self.state['objections'].append(objection)
        self._add_to_transcript(objector, f"Objection! {reason}")
    
    def process_voice_command(self, audio_data: bytes) -> str:
        """Process voice commands"""
        command = self.stt_engine.process_audio(audio_data)
        return command
    
    def get_state(self) -> Dict[str, Any]:
        """Get the current state"""
        return self.state
    
    def save_state(self, filepath: str):
        """Save the state to a file"""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w') as f:
            json.dump(self.state, f, indent=4)
    
    def load_state(self, filepath: str):
        """Load the state from a file"""
        with open(filepath, 'r') as f:
            self.state = json.load(f)
        self.case_data = self.state['case_info'] 