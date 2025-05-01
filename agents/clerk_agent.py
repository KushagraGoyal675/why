# agents/clerk_agent.py

from typing import Dict, List, Any
from .agent_base import AgentBase
from utils import knowledge_base
import random
import json
import os
from datetime import datetime

class ClerkAgent(AgentBase):
    def __init__(self, llm_provider: str = "Groq"):
        super().__init__("clerk", llm_provider)
        self.role_prompt = (
            "You are a courtroom clerk. You assist by providing law sections or evidence on request. "
            "Do not argue or comment on the case. Maintain accurate records and ensure proper court procedures."
        )
        self.witnesses = []
        self.evidence = []
        self.transcript = []
        self.objections = []
        self.case_files = {}

    def generate_response(self, context: Dict[str, Any]) -> str:
        """Generate a response as the court clerk"""
        # Marking evidence
        if context.get("phase") == "evidence":
            evidence_id = context.get("evidence_id", "")
            return f"Evidence marked as Exhibit {evidence_id} for identification."
        
        # Calling witnesses
        elif context.get("phase") == "witness":
            witness_name = context.get("witness_name", "")
            return f"Calling {witness_name} to the stand."
        
        # Recording objections
        elif context.get("phase") == "objection":
            return "Objection noted for the record."
        
        return "The court is in session."
    
    def analyze_case(self, case_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze the case from clerk's perspective"""
        return {
            "documents": [
                "Summons",
                "Complaint",
                "Answer",
                "Evidence List",
                "Witness List"
            ],
            "procedural_steps": [
                "Filing of documents",
                "Service of process",
                "Pre-trial conference",
                "Trial proceedings",
                "Judgment entry"
            ],
            "timeline": {
                "filing_date": case_data.get("filing_date", ""),
                "trial_date": case_data.get("trial_date", ""),
                "deadlines": case_data.get("deadlines", [])
            }
        }
    
    def prepare_arguments(self, case_data: Dict[str, Any]) -> List[str]:
        """Prepare procedural arguments and documentation"""
        return [
            "All documents have been properly filed and served",
            "The case is ready for trial",
            "All necessary parties are present",
            "The court has jurisdiction over this matter"
        ]
    
    def manage_documents(self, document_type: str) -> str:
        """Manage court documents"""
        if document_type == "summons":
            return "Summons issued and ready for service."
        elif document_type == "judgment":
            return "Judgment prepared and ready for entry."
        return "Document processed and filed."
    
    def schedule_hearing(self, hearing_type: str) -> str:
        """Schedule court hearings"""
        if hearing_type == "pre_trial":
            return "Pre-trial conference scheduled for next month."
        elif hearing_type == "trial":
            return "Trial date set for three months from today."
        return "Hearing scheduled and notices issued."

    def manage_case_file(self, case_id: str, action: str, data: dict = None) -> dict:
        """Manage case files - create, update, or retrieve"""
        case_file_dir = os.path.join("data", "case_files")
        os.makedirs(case_file_dir, exist_ok=True)
        case_file_path = os.path.join(case_file_dir, f"{case_id}.json")

        if action == "create":
            if data is None:
                raise ValueError("Data required for creating case file")
            
            case_file = {
                "case_id": case_id,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "status": "active",
                **data
            }
            
            with open(case_file_path, "w") as f:
                json.dump(case_file, f, indent=4)
            
            self.case_files[case_id] = case_file
            return case_file

        elif action == "update":
            if not os.path.exists(case_file_path):
                raise FileNotFoundError(f"Case file {case_id} not found")
            
            with open(case_file_path, "r") as f:
                case_file = json.load(f)
            
            case_file.update(data or {})
            case_file["updated_at"] = datetime.now().isoformat()
            
            with open(case_file_path, "w") as f:
                json.dump(case_file, f, indent=4)
            
            self.case_files[case_id] = case_file
            return case_file

        elif action == "retrieve":
            if not os.path.exists(case_file_path):
                raise FileNotFoundError(f"Case file {case_id} not found")
            
            with open(case_file_path, "r") as f:
                case_file = json.load(f)
            
            self.case_files[case_id] = case_file
            return case_file

        else:
            raise ValueError(f"Invalid action: {action}")

    def get_law(self, act_name: str, section_number: int) -> str:
        section_text = knowledge_base.get_section_text(act_name, section_number)
        return f"{act_name} Section {section_number}:\n{section_text}" if section_text else "Section not found."

    def get_evidence(self, case_data: dict, exhibit_id: str) -> str:
        for item in case_data.get("evidence", []):
            if item["id"] == exhibit_id:
                self.evidence.append(item)
                return f"{exhibit_id}: {item['description']}"
        return f"Evidence {exhibit_id} not found."

    def generate_jury_pool(self) -> list:
        """Generate a pool of potential jurors"""
        num_pool = random.randint(20, 30)  # Generate 20-30 potential jurors
        return [
            {
                "id": i,
                "name": f"Juror {i}",
                "background": random.choice([
                    "Business professional",
                    "Teacher",
                    "Engineer",
                    "Healthcare worker",
                    "Retired",
                    "Student"
                ]),
                "bias_score": random.uniform(-0.5, 0.5)  # Random bias score between -0.5 and 0.5
            }
            for i in range(1, num_pool + 1)
        ]

    def get_witness(self, case_data: dict, side: str) -> dict:
        """Get a witness for the specified side"""
        witnesses = case_data.get("witnesses", [])
        side_witnesses = [w for w in witnesses if w.get("side") == side]
        
        if not side_witnesses:
            # Generate a default witness if none provided
            return {
                "name": f"{side.capitalize()} Witness",
                "background": f"Key witness for the {side}",
                "testimony": lambda question: f"I recall that {random.choice(['I saw', 'I heard', 'I know'])} {question}",
                "side": side
            }
        
        return random.choice(side_witnesses)

    def record_objection(self, objection: dict) -> None:
        """Record an objection in the court record"""
        self.objections.append({
            **objection,
            "timestamp": len(self.transcript)
        })

    def maintain_transcript(self, speaker: str, content: str) -> None:
        """Maintain the official court transcript"""
        self.transcript.append({
            "speaker": speaker,
            "content": content,
            "timestamp": len(self.transcript)
        })

    def prepare_court_documents(self, case_data: dict) -> dict:
        """Prepare necessary court documents"""
        return {
            "summons": f"Summons for Case {case_data.get('id', 'N/A')}",
            "complaint": case_data.get("plaintiff_statement", ""),
            "answer": case_data.get("defendant_statement", ""),
            "witness_list": [w["name"] for w in case_data.get("witnesses", [])],
            "evidence_list": [e["id"] for e in case_data.get("evidence", [])]
        }
