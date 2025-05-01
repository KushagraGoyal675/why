# agents/judge_agent.py

from typing import Dict, Any, List
from .agent_base import AgentBase

class JudgeAgent(AgentBase):
    def __init__(self, llm_provider: str = "Groq"):
        super().__init__("judge", llm_provider)
        self.config = {
            "name": "Justice Rao",
            "experience": "20 years",
            "specialization": "Civil Law"
        }
    
    def generate_response(self, context: Dict[str, Any]) -> str:
        """Generate a response as the judge"""
        prompt = self._build_prompt(context)
        return self._generate_llm_response(prompt)
    
    def analyze_case(self, case_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze the case from judge's perspective"""
        return {
            "legal_issues": self._identify_legal_issues(case_data),
            "key_evidence": self._evaluate_evidence(case_data),
            "witness_credibility": self._assess_witness_credibility(case_data),
            "precedents": self._find_relevant_precedents(case_data),
            "recommendations": self._generate_recommendations(case_data)
        }
    
    def prepare_arguments(self, case_data: Dict[str, Any]) -> List[str]:
        """Prepare arguments for the judge's ruling"""
        return [
            "The evidence presented must be evaluated for relevance and reliability",
            "Witness credibility is a crucial factor in determining the truth",
            "Legal principles must be applied consistently",
            "Precedents should guide but not dictate the outcome",
            "The burden of proof must be properly allocated"
        ]
    
    def rule_on_objection(self, objection: str) -> str:
        """Rule on an objection raised in court"""
        context = {
            "phase": "objection",
            "objection": objection,
            "previous_exchange": ""
        }
        return self.generate_response(context)
        
    def give_judgment(self, case_summary: str) -> str:
        """Provide final judgment on the case"""
        context = {
            "phase": "judgment",
            "case_summary": case_summary,
            "previous_exchange": ""
        }
        return self.generate_response(context)
    
    def _build_prompt(self, context: Dict[str, Any]) -> str:
        """Build a detailed prompt for the judge's response"""
        phase = context.get("phase", "")
        previous_exchange = context.get("previous_exchange", "")
        
        if phase == "objection":
            objection = context.get("objection", "")
            return f"""As the presiding judge, rule on this objection:
            Objection: {objection}
            
            Previous Exchange: {previous_exchange}
            
            Guidelines for your ruling:
            1. Consider the legal basis for the objection
            2. Evaluate the impact on the proceedings
            3. Maintain fairness to both parties
            4. Provide clear reasoning for your decision
            5. Keep the proceedings moving efficiently
            
            Generate a professional and reasoned ruling."""
            
        elif phase == "judgment":
            case_summary = context.get("case_summary", "")
            return f"""As the presiding judge, deliver your final judgment:
            Case Summary: {case_summary}
            
            Previous Exchange: {previous_exchange}
            
            Guidelines for your judgment:
            1. Evaluate all evidence presented
            2. Consider witness credibility
            3. Apply relevant legal principles
            4. Reference applicable precedents
            5. Provide clear reasoning
            6. Ensure justice is served
            
            Generate a comprehensive and fair judgment."""
        
        return f"""As the presiding judge, respond to this situation:
        Phase: {phase}
        Context: {context}
        Previous Exchange: {previous_exchange}
        
        Generate a professional and appropriate response."""
    
    def _identify_legal_issues(self, case_data: Dict[str, Any]) -> List[str]:
        """Identify key legal issues in the case"""
        return [
            "Jurisdiction and venue",
            "Applicable laws and statutes",
            "Burden of proof",
            "Admissibility of evidence",
            "Procedural matters"
        ]
    
    def _evaluate_evidence(self, case_data: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate the evidence presented in the case"""
        return {
            "strength": 0.8,  # Default score
            "reliability": 0.7,
            "relevance": 0.9,
            "key_pieces": [],
            "gaps": []
        }
    
    def _assess_witness_credibility(self, case_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess the credibility of witnesses"""
        return {
            "overall_credibility": 0.75,  # Default score
            "consistency": 0.8,
            "bias_assessment": [],
            "reliability_factors": []
        }
    
    def _find_relevant_precedents(self, case_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find relevant legal precedents"""
        return [
            {
                "case_name": "Sample Precedent",
                "relevance": 0.85,
                "key_points": [],
                "application": "Similar facts and legal issues"
            }
        ]
    
    def _generate_recommendations(self, case_data: Dict[str, Any]) -> List[str]:
        """Generate recommendations for the case"""
        return [
            "Consider additional evidence if available",
            "Evaluate witness credibility carefully",
            "Apply relevant legal principles consistently",
            "Ensure procedural fairness",
            "Maintain clear record of proceedings"
        ]
