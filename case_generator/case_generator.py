from typing import List, Dict, Any, Optional
from datetime import datetime
import random
import json

class CaseGenerator:
    def __init__(self):
        self.case_types = [
            "Contract Dispute",
            "Property Dispute",
            "Family Law",
            "Consumer Protection",
            "Commercial Dispute",
            "Tort Claim",
            "Injunction Suit",
            "Specific Performance",
            "Partition Suit",
            "Recovery Suit"
        ]
        
        self.legal_issues = {
            "Contract Dispute": [
                "Breach of Contract",
                "Specific Performance",
                "Damages",
                "Rescission",
                "Quantum Meruit"
            ],
            "Property Dispute": [
                "Ownership Dispute",
                "Easement Rights",
                "Partition",
                "Encroachment",
                "Adverse Possession"
            ],
            "Family Law": [
                "Divorce",
                "Maintenance",
                "Custody",
                "Property Division",
                "Alimony"
            ],
            "Consumer Protection": [
                "Defective Goods",
                "Deficient Services",
                "Unfair Trade Practices",
                "Compensation",
                "Refund"
            ],
            "Commercial Dispute": [
                "Partnership Dispute",
                "Shareholder Rights",
                "Company Law",
                "Insolvency",
                "Arbitration"
            ]
        }
        
        self.evidence_types = [
            "Documentary Evidence",
            "Electronic Evidence",
            "Expert Opinion",
            "Photographic Evidence",
            "Audio-Visual Evidence",
            "Forensic Evidence",
            "Medical Reports",
            "Financial Records",
            "Property Documents",
            "Witness Statements"
        ]
        
        self.witness_types = [
            "Fact Witness",
            "Expert Witness",
            "Character Witness",
            "Document Witness",
            "Eye Witness"
        ]

    def generate_case(self, case_type: Optional[str] = None) -> Dict[str, Any]:
        """Generate a complete civil case"""
        if not case_type:
            case_type = random.choice(self.case_types)
        elif case_type not in self.case_types:
            raise ValueError(f"Invalid case type: {case_type}")
        
        case_id = f"CIV-{datetime.now().strftime('%Y%m%d')}-{random.randint(1000, 9999)}"
        
        # Generate parties first
        parties = self._generate_parties()
        
        # Generate case data
        case_data = {
            "case_id": case_id,
            "case_type": case_type,
            "filing_date": datetime.now().isoformat(),
            "status": "pending",
            "parties": parties,
            "facts": self._generate_facts(case_type),
            "legal_issues": self._generate_legal_issues(case_type),
            "relief_sought": self._generate_relief_sought(case_type),
            "evidence": self._generate_evidence(case_type),
            "witnesses": self._generate_witnesses(case_type),
            "judge_data": self._generate_judge_data(),
            "plaintiff_lawyer_data": self._generate_lawyer_data("plaintiff"),
            "defendant_lawyer_data": self._generate_lawyer_data("defendant")
        }
        
        return case_data

    def _generate_parties(self) -> Dict[str, Any]:
        """Generate parties to the case"""
        return {
            "plaintiff": {
                "name": f"Party-{random.randint(1, 1000)}",
                "type": random.choice(["Individual", "Company", "Partnership", "Trust"]),
                "address": f"Address-{random.randint(1, 100)}",
                "contact": f"Contact-{random.randint(1000000000, 9999999999)}"
            },
            "defendant": {
                "name": f"Party-{random.randint(1001, 2000)}",
                "type": random.choice(["Individual", "Company", "Partnership", "Trust"]),
                "address": f"Address-{random.randint(101, 200)}",
                "contact": f"Contact-{random.randint(1000000000, 9999999999)}"
            }
        }

    def _generate_facts(self, case_type: str) -> List[str]:
        """Generate case facts based on case type"""
        facts = []
        
        if case_type == "Contract Dispute":
            facts.extend([
                "Parties entered into a written agreement",
                "Agreement specified terms and conditions",
                "One party failed to perform obligations",
                "Other party suffered losses",
                "Notice was served before filing suit"
            ])
        elif case_type == "Property Dispute":
            facts.extend([
                "Dispute over property ownership",
                "Property documents exist",
                "Possession is in question",
                "Boundary dispute exists",
                "Previous attempts at resolution failed"
            ])
        elif case_type == "Family Law":
            facts.extend([
                "Marriage certificate exists",
                "Parties have been separated",
                "Children are involved",
                "Property needs division",
                "Maintenance is required"
            ])
        elif case_type == "Consumer Protection":
            facts.extend([
                "Consumer purchased goods/services",
                "Defect/deficiency discovered",
                "Complaint filed with seller",
                "No satisfactory response received",
                "Consumer suffered damages"
            ])
        elif case_type == "Commercial Dispute":
            facts.extend([
                "Business agreement exists",
                "Breach of terms occurred",
                "Financial losses incurred",
                "Notice of dispute sent",
                "Negotiations failed"
            ])
        elif case_type == "Tort Claim":
            facts.extend([
                "Wrongful act committed",
                "Damages suffered",
                "Causation established",
                "Medical reports available",
                "Police report filed"
            ])
        elif case_type == "Injunction Suit":
            facts.extend([
                "Imminent threat exists",
                "Irreparable harm likely",
                "No adequate remedy at law",
                "Balance of convenience favors",
                "Status quo needs preservation"
            ])
        elif case_type == "Specific Performance":
            facts.extend([
                "Valid contract exists",
                "Breach occurred",
                "Monetary compensation inadequate",
                "Performance possible",
                "Plaintiff ready and willing"
            ])
        elif case_type == "Partition Suit":
            facts.extend([
                "Joint ownership exists",
                "Share determined",
                "Physical division possible",
                "Co-owners not cooperating",
                "Revenue records available"
            ])
        elif case_type == "Recovery Suit":
            facts.extend([
                "Debt/money due",
                "Demand notice sent",
                "Payment not received",
                "Interest accruing",
                "Supporting documents exist"
            ])
        else:
            facts.extend([
                "Cause of action exists",
                "Jurisdiction established",
                "Notice period completed",
                "Documents available",
                "Witnesses identified"
            ])
        
        return facts

    def _generate_legal_issues(self, case_type: str) -> List[str]:
        """Generate legal issues based on case type"""
        if case_type == "Contract Dispute":
            issues = [
                "Breach of Contract",
                "Specific Performance",
                "Damages",
                "Rescission",
                "Quantum Meruit"
            ]
        elif case_type == "Property Dispute":
            issues = [
                "Ownership Dispute",
                "Easement Rights",
                "Partition",
                "Encroachment",
                "Adverse Possession"
            ]
        elif case_type == "Family Law":
            issues = [
                "Divorce",
                "Maintenance",
                "Custody",
                "Property Division",
                "Alimony"
            ]
        elif case_type == "Consumer Protection":
            issues = [
                "Defective Goods",
                "Deficient Services",
                "Unfair Trade Practices",
                "Compensation",
                "Refund"
            ]
        elif case_type == "Commercial Dispute":
            issues = [
                "Partnership Dispute",
                "Shareholder Rights",
                "Company Law",
                "Insolvency",
                "Arbitration"
            ]
        elif case_type == "Tort Claim":
            issues = [
                "Negligence",
                "Damages",
                "Liability",
                "Causation",
                "Duty of Care"
            ]
        elif case_type == "Injunction Suit":
            issues = [
                "Irreparable Injury",
                "Balance of Convenience",
                "Prima Facie Case",
                "Status Quo",
                "Public Interest"
            ]
        elif case_type == "Specific Performance":
            issues = [
                "Contract Validity",
                "Readiness and Willingness",
                "Alternative Remedy",
                "Time Essence",
                "Part Performance"
            ]
        elif case_type == "Partition Suit":
            issues = [
                "Share Determination",
                "Property Valuation",
                "Physical Division",
                "Sale Proceeds",
                "Possession"
            ]
        elif case_type == "Recovery Suit":
            issues = [
                "Debt Existence",
                "Interest Rate",
                "Payment History",
                "Limitation Period",
                "Security Interest"
            ]
        else:
            issues = [
                "Jurisdiction",
                "Cause of Action",
                "Limitation",
                "Relief",
                "Costs"
            ]
        
        # Ensure we don't try to sample more items than available
        k = min(random.randint(2, 4), len(issues))
        return random.sample(issues, k=k)

    def _generate_relief_sought(self, case_type: str) -> List[str]:
        """Generate relief sought based on case type"""
        reliefs = []
        
        if case_type == "Contract Dispute":
            reliefs.extend([
                "Specific Performance",
                "Damages",
                "Injunction",
                "Costs"
            ])
        elif case_type == "Property Dispute":
            reliefs.extend([
                "Declaration of Title",
                "Possession",
                "Permanent Injunction",
                "Mesne Profits"
            ])
        elif case_type == "Family Law":
            reliefs.extend([
                "Divorce",
                "Maintenance",
                "Custody",
                "Property Division"
            ])
        elif case_type == "Consumer Protection":
            reliefs.extend([
                "Refund",
                "Compensation",
                "Replacement",
                "Costs"
            ])
        elif case_type == "Commercial Dispute":
            reliefs.extend([
                "Injunction",
                "Damages",
                "Specific Performance",
                "Costs"
            ])
        elif case_type == "Tort Claim":
            reliefs.extend([
                "Compensation",
                "Injunction",
                "Damages",
                "Costs"
            ])
        elif case_type == "Injunction Suit":
            reliefs.extend([
                "Temporary Injunction",
                "Permanent Injunction",
                "Damages",
                "Costs"
            ])
        elif case_type == "Specific Performance":
            reliefs.extend([
                "Specific Performance",
                "Damages",
                "Injunction",
                "Costs"
            ])
        elif case_type == "Partition Suit":
            reliefs.extend([
                "Partition",
                "Possession",
                "Mesne Profits",
                "Costs"
            ])
        elif case_type == "Recovery Suit":
            reliefs.extend([
                "Recovery of Money",
                "Interest",
                "Costs"
            ])
        else:
            # Default reliefs for unknown case types
            reliefs.extend([
                "Damages",
                "Injunction",
                "Costs"
            ])
        
        # Ensure we don't try to sample more items than available
        k = min(random.randint(1, 3), len(reliefs))
        return random.sample(reliefs, k=k)

    def _generate_evidence(self, case_type: str) -> List[Dict[str, Any]]:
        """Generate evidence based on case type"""
        evidence = []
        num_evidence = random.randint(3, 6)
        
        for _ in range(num_evidence):
            evidence.append({
                "type": random.choice(self.evidence_types),
                "description": f"Evidence related to {case_type}",
                "date": datetime.now().isoformat(),
                "source": random.choice(["Plaintiff", "Defendant", "Court", "Third Party"]),
                "relevance": random.choice(["Direct", "Circumstantial", "Corroborative"])
            })
        
        return evidence

    def _generate_witnesses(self, case_type: str) -> List[Dict[str, Any]]:
        """Generate witnesses based on case type"""
        witnesses = []
        num_witnesses = random.randint(2, 4)
        
        for i in range(num_witnesses):
            witness_type = random.choice(self.witness_types)
            witness_id = f"W{i+1}"
            
            witness = {
                "witness_id": witness_id,
                "name": f"Witness-{random.randint(1, 1000)}",
                "type": witness_type,
                "credibility": random.choice(["High", "Medium", "Low"]),
                "relation": random.choice(["Independent", "Related to Plaintiff", "Related to Defendant"]),
                "testimony_topics": self._generate_testimony_topics(case_type, witness_type)
            }
            witnesses.append(witness)
        
        return witnesses

    def _generate_testimony_topics(self, case_type: str, witness_type: str) -> List[str]:
        """Generate testimony topics based on case type and witness type"""
        topics = []
        
        if witness_type == "Fact Witness":
            if case_type == "Contract Dispute":
                topics = [
                    "Contract Formation",
                    "Terms Discussion",
                    "Performance Issues",
                    "Communication History"
                ]
            elif case_type == "Property Dispute":
                topics = [
                    "Property Boundaries",
                    "Possession History",
                    "Construction Activities",
                    "Neighbor Relations"
                ]
            else:
                topics = [
                    "Factual Background",
                    "Timeline of Events",
                    "Direct Observations",
                    "Related Communications"
                ]
        elif witness_type == "Expert Witness":
            if case_type == "Contract Dispute":
                topics = [
                    "Industry Standards",
                    "Market Practices",
                    "Damage Assessment",
                    "Technical Specifications"
                ]
            elif case_type == "Property Dispute":
                topics = [
                    "Property Valuation",
                    "Construction Standards",
                    "Land Survey",
                    "Development Regulations"
                ]
            else:
                topics = [
                    "Professional Opinion",
                    "Technical Analysis",
                    "Industry Standards",
                    "Best Practices"
                ]
        elif witness_type == "Character Witness":
            topics = [
                "Personal Knowledge",
                "Past Interactions",
                "Reputation",
                "Professional Conduct"
            ]
        elif witness_type == "Document Witness":
            topics = [
                "Document Authenticity",
                "Record Keeping",
                "Document History",
                "Filing Systems"
            ]
        elif witness_type == "Eye Witness":
            topics = [
                "Direct Observation",
                "Event Details",
                "Physical Description",
                "Environmental Conditions"
            ]
        else:
            topics = [
                "General Knowledge",
                "Relevant Facts",
                "Personal Observations",
                "Supporting Information"
            ]
        
        # Select 2-3 topics
        k = min(random.randint(2, 3), len(topics))
        return random.sample(topics, k=k)

    def _generate_judge_data(self) -> Dict[str, Any]:
        """Generate judge data"""
        return {
            "name": f"Judge-{random.randint(1, 100)}",
            "experience": f"{random.randint(5, 30)} years",
            "specialization": random.choice(["Civil", "Commercial", "Family"]),
            "court": f"District Court {random.randint(1, 50)}",
            "bench": random.choice(["Principal", "Additional", "Senior"])
        }

    def _generate_lawyer_data(self, side: str) -> Dict[str, Any]:
        """Generate lawyer data"""
        return {
            "name": f"Lawyer-{side}-{random.randint(1, 100)}",
            "specialization": random.choice(["Civil Litigation", "Commercial", "Family"]),
            "experience": f"{random.randint(3, 25)} years",
            "firm": f"Law Firm {random.randint(1, 50)}",
            "success_rate": random.randint(60, 95),
            "style": random.choice(["Aggressive", "Diplomatic", "Technical", "Persuasive"])
        }

    def generate_multiple_cases(self, num_cases: int) -> List[Dict[str, Any]]:
        """Generate multiple cases"""
        return [self.generate_case() for _ in range(num_cases)]

    def save_case_to_file(self, case_data: Dict[str, Any], filename: str):
        """Save case data to a file"""
        with open(filename, 'w') as f:
            json.dump(case_data, f, indent=4)

    def load_case_from_file(self, filename: str) -> Dict[str, Any]:
        """Load case data from a file"""
        with open(filename, 'r') as f:
            return json.load(f)

    def generate_case_summary(self, case_data: Dict[str, Any]) -> str:
        """Generate a summary of the case"""
        summary = f"""
        Case Summary for {case_data['case_id']}
        
        Case Type: {case_data['case_type']}
        Filing Date: {case_data['filing_date']}
        Status: {case_data['status']}
        
        Parties:
        - Plaintiff: {case_data['parties']['plaintiff']['name']}
        - Defendant: {case_data['parties']['defendant']['name']}
        
        Legal Issues:
        {chr(10).join(f'- {issue}' for issue in case_data['legal_issues'])}
        
        Relief Sought:
        {chr(10).join(f'- {relief}' for relief in case_data['relief_sought'])}
        
        Evidence Count: {len(case_data['evidence'])}
        Witness Count: {len(case_data['witnesses'])}
        """
        
        return summary 