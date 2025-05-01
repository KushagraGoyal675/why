from typing import List, Dict, Any, Optional
from datetime import datetime
from agents.judge_agent import JudgeAgent
from agents.lawyer_agent import LawyerAgent
from agents.witness_agent import WitnessAgent
from agents.clerk_agent import ClerkAgent

class Courtroom:
    def __init__(self, case_data: Dict[str, Any]):
        self.case_data = case_data
        self.judge = JudgeAgent(case_data.get("judge_data", {}))
        self.plaintiff_lawyer = LawyerAgent(case_data.get("plaintiff_lawyer_data", {}))
        self.defendant_lawyer = LawyerAgent(case_data.get("defendant_lawyer_data", {}))
        self.clerk = ClerkAgent()
        self.witnesses: List[WitnessAgent] = []
        self.current_stage = "pre_trial"
        self.proceedings: List[Dict[str, Any]] = []
        self.evidence: List[Dict[str, Any]] = []
        self.motions: List[Dict[str, Any]] = []
        self.orders: List[Dict[str, Any]] = []
        self.hearing_schedule: List[Dict[str, Any]] = []
        
        # Initialize witnesses
        for witness_data in case_data.get("witnesses", []):
            self.witnesses.append(WitnessAgent(witness_data))
        
        # Initialize case file
        self.clerk.manage_case_file(
            case_data["case_id"],
            "create",
            {
                "case_type": case_data.get("case_type"),
                "parties": case_data.get("parties"),
                "filing_date": datetime.now().isoformat(),
                "status": "pending"
            }
        )

    def conduct_hearing(self, hearing_type: str) -> Dict[str, Any]:
        """Conduct a court hearing"""
        hearing_record = {
            "hearing_id": f"HEAR-{self.case_data['case_id']}-{datetime.now().strftime('%Y%m%d')}",
            "type": hearing_type,
            "date": datetime.now().isoformat(),
            "stage": self.current_stage,
            "proceedings": []
        }
        
        # Record hearing in clerk's records
        self.clerk.record_proceedings(
            self.case_data["case_id"],
            {
                "type": hearing_type,
                "judge": self.judge.role,
                "parties": [self.plaintiff_lawyer.role, self.defendant_lawyer.role],
                "summary": f"Hearing for {hearing_type}",
                "next_hearing": None
            }
        )
        
        # Conduct hearing based on type
        if hearing_type == "pre_trial":
            hearing_record["proceedings"] = self._conduct_pre_trial_hearing()
        elif hearing_type == "evidence":
            hearing_record["proceedings"] = self._conduct_evidence_hearing()
        elif hearing_type == "arguments":
            hearing_record["proceedings"] = self._conduct_arguments_hearing()
        elif hearing_type == "judgment":
            hearing_record["proceedings"] = self._conduct_judgment_hearing()
        
        self.proceedings.append(hearing_record)
        return hearing_record

    def _conduct_pre_trial_hearing(self) -> List[Dict[str, Any]]:
        """Conduct pre-trial hearing"""
        proceedings = []
        
        # Case management
        case_management = self.judge.manage_case(self.case_data)
        proceedings.append({
            "type": "case_management",
            "content": case_management,
            "timestamp": datetime.now().isoformat()
        })
        
        # Initial arguments
        plaintiff_args = self.plaintiff_lawyer.prepare_legal_arguments(
            self.case_data["case_id"],
            "initial_pleadings"
        )
        defendant_args = self.defendant_lawyer.prepare_legal_arguments(
            self.case_data["case_id"],
            "initial_pleadings"
        )
        
        proceedings.extend([
            {
                "type": "plaintiff_arguments",
                "content": plaintiff_args,
                "timestamp": datetime.now().isoformat()
            },
            {
                "type": "defendant_arguments",
                "content": defendant_args,
                "timestamp": datetime.now().isoformat()
            }
        ])
        
        # Issue framing
        issues = self.judge.frame_issues(self.case_data)
        proceedings.append({
            "type": "issue_framing",
            "content": issues,
            "timestamp": datetime.now().isoformat()
        })
        
        return proceedings

    def _conduct_evidence_hearing(self) -> List[Dict[str, Any]]:
        """Conduct evidence hearing"""
        proceedings = []
        
        # Plaintiff's evidence
        for witness in self.witnesses:
            if witness.witness_data.get("side") == "plaintiff":
                # Direct examination
                questions = self.plaintiff_lawyer.prepare_witness_examination(
                    self.case_data["case_id"],
                    witness.witness_data
                )
                testimony = witness.provide_testimony(questions["prepared_questions"][0])
                
                proceedings.append({
                    "type": "plaintiff_witness_testimony",
                    "witness": witness.witness_data["name"],
                    "content": testimony,
                    "timestamp": datetime.now().isoformat()
                })
                
                # Cross examination
                cross_questions = self.defendant_lawyer.prepare_cross_examination(
                    self.case_data["case_id"],
                    witness.witness_data,
                    [{"question": questions["prepared_questions"][0], "answer": testimony}]
                )
                cross_testimony = witness.handle_cross_examination(
                    cross_questions["questions"][0],
                    [{"question": questions["prepared_questions"][0], "answer": testimony}]
                )
                
                proceedings.append({
                    "type": "cross_examination",
                    "witness": witness.witness_data["name"],
                    "content": cross_testimony,
                    "timestamp": datetime.now().isoformat()
                })
        
        # Defendant's evidence
        for witness in self.witnesses:
            if witness.witness_data.get("side") == "defendant":
                # Direct examination
                questions = self.defendant_lawyer.prepare_witness_examination(
                    self.case_data["case_id"],
                    witness.witness_data
                )
                testimony = witness.provide_testimony(questions["prepared_questions"][0])
                
                proceedings.append({
                    "type": "defendant_witness_testimony",
                    "witness": witness.witness_data["name"],
                    "content": testimony,
                    "timestamp": datetime.now().isoformat()
                })
                
                # Cross examination
                cross_questions = self.plaintiff_lawyer.prepare_cross_examination(
                    self.case_data["case_id"],
                    witness.witness_data,
                    [{"question": questions["prepared_questions"][0], "answer": testimony}]
                )
                cross_testimony = witness.handle_cross_examination(
                    cross_questions["questions"][0],
                    [{"question": questions["prepared_questions"][0], "answer": testimony}]
                )
                
                proceedings.append({
                    "type": "cross_examination",
                    "witness": witness.witness_data["name"],
                    "content": cross_testimony,
                    "timestamp": datetime.now().isoformat()
                })
        
        return proceedings

    def _conduct_arguments_hearing(self) -> List[Dict[str, Any]]:
        """Conduct final arguments hearing"""
        proceedings = []
        
        # Plaintiff's arguments
        plaintiff_args = self.plaintiff_lawyer.prepare_legal_arguments(
            self.case_data["case_id"],
            "final_arguments"
        )
        proceedings.append({
            "type": "plaintiff_arguments",
            "content": plaintiff_args,
            "timestamp": datetime.now().isoformat()
        })
        
        # Defendant's arguments
        defendant_args = self.defendant_lawyer.prepare_legal_arguments(
            self.case_data["case_id"],
            "final_arguments"
        )
        proceedings.append({
            "type": "defendant_arguments",
            "content": defendant_args,
            "timestamp": datetime.now().isoformat()
        })
        
        # Plaintiff's reply
        reply_args = self.plaintiff_lawyer.prepare_legal_arguments(
            self.case_data["case_id"],
            "reply_arguments"
        )
        proceedings.append({
            "type": "plaintiff_reply",
            "content": reply_args,
            "timestamp": datetime.now().isoformat()
        })
        
        return proceedings

    def _conduct_judgment_hearing(self) -> List[Dict[str, Any]]:
        """Conduct judgment hearing"""
        proceedings = []
        
        # Judge's analysis
        analysis = self.judge.analyze_case(self.case_data)
        proceedings.append({
            "type": "judge_analysis",
            "content": analysis,
            "timestamp": datetime.now().isoformat()
        })
        
        # Judgment delivery
        judgment = self.judge.deliver_judgment(self.case_data)
        proceedings.append({
            "type": "judgment",
            "content": judgment,
            "timestamp": datetime.now().isoformat()
        })
        
        # Record judgment
        self.clerk.manage_case_file(
            self.case_data["case_id"],
            "update",
            {
                "status": "decided",
                "judgment": judgment,
                "decision_date": datetime.now().isoformat()
            }
        )
        
        return proceedings

    def handle_motion(self, motion_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle a motion in court"""
        # Prepare motion
        if motion_data["filed_by"] == "plaintiff":
            motion = self.plaintiff_lawyer.prepare_motion(
                self.case_data["case_id"],
                motion_data["type"],
                motion_data["grounds"]
            )
        else:
            motion = self.defendant_lawyer.prepare_motion(
                self.case_data["case_id"],
                motion_data["type"],
                motion_data["grounds"]
            )
        
        # Record motion
        self.clerk.process_motion(self.case_data["case_id"], motion)
        self.motions.append(motion)
        
        # Judge's ruling
        ruling = self.judge.hear_motion(motion)
        
        # Update motion status
        motion["status"] = "granted" if ruling["decision"] == "granted" else "denied"
        motion["ruling"] = ruling
        
        return motion

    def handle_objection(self, objection_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle an objection in court"""
        # Prepare objection
        if objection_data["raised_by"] == "plaintiff":
            objection = self.plaintiff_lawyer.prepare_objection(
                self.case_data["case_id"],
                objection_data
            )
        else:
            objection = self.defendant_lawyer.prepare_objection(
                self.case_data["case_id"],
                objection_data
            )
        
        # Record objection
        self.clerk.handle_objection_recording(self.case_data["case_id"], objection)
        
        # Judge's ruling
        ruling = self.judge.rule_on_objection(objection)
        objection["ruling"] = ruling
        objection["status"] = "sustained" if ruling["decision"] == "sustained" else "overruled"
        
        return objection

    def schedule_hearing(self, hearing_data: Dict[str, Any]) -> Dict[str, Any]:
        """Schedule a court hearing"""
        hearing = self.clerk.handle_administrative_tasks("schedule_hearing", {
            "case_id": self.case_data["case_id"],
            "hearing_date": hearing_data["date"],
            "type": hearing_data["type"],
            "purpose": hearing_data["purpose"]
        })
        
        self.hearing_schedule.append(hearing)
        return hearing

    def process_evidence(self, evidence_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process evidence in court"""
        evidence = self.clerk.process_evidence(self.case_data["case_id"], evidence_data)
        self.evidence.append(evidence)
        return evidence

    def issue_order(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """Issue a court order"""
        order = {
            "order_id": f"ORDER-{self.case_data['case_id']}-{datetime.now().strftime('%Y%m%d')}",
            "type": order_data["type"],
            "content": order_data["content"],
            "issued_by": self.judge.role,
            "date": datetime.now().isoformat(),
            "status": "issued"
        }
        
        self.orders.append(order)
        self.clerk.manage_case_file(
            self.case_data["case_id"],
            "update",
            {"orders": self.orders}
        )
        
        return order

    def get_case_status(self) -> Dict[str, Any]:
        """Get current status of the case"""
        case_file = self.clerk.manage_case_file(self.case_data["case_id"], "retrieve", {})
        
        return {
            "case_id": self.case_data["case_id"],
            "status": case_file.get("status", "unknown"),
            "current_stage": self.current_stage,
            "next_hearing": self.hearing_schedule[-1] if self.hearing_schedule else None,
            "pending_motions": [m for m in self.motions if m["status"] == "pending"],
            "evidence_count": len(self.evidence),
            "witness_count": len(self.witnesses),
            "order_count": len(self.orders)
        } 