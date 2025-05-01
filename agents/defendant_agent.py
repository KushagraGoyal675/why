from typing import Dict, List, Any
from .agent_base import AgentBase
from llm.groq_api import groq_api

class DefendantAgent(AgentBase):
    def __init__(self, llm_provider: str = "Groq"):
        super().__init__("defendant", llm_provider)
    
    def generate_response(self, context: Dict[str, Any]) -> str:
        """Generate a response as the defendant"""
        prompt = self._build_prompt(context)
        result = groq_api.generate_response(prompt)
        if "error" in result:
            return f"Error generating response: {result['error']}"
        return result["response"]
    
    def analyze_case(self, case_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze the case from defendant's perspective"""
        prompt = f"""Analyze this case from the defendant's perspective:
        Case Type: {case_data.get('case_type', 'Unknown')}
        Key Facts: {case_data.get('facts', [])}
        Plaintiff's Claims: {case_data.get('plaintiff_claims', [])}
        Evidence: {case_data.get('evidence', [])}
        
        Provide a detailed analysis including:
        1. Key strengths in our defense
        2. Potential weaknesses to address
        3. Recommended defense strategy
        4. Key legal arguments to make
        5. Evidence to emphasize
        6. Potential counter-arguments to prepare for
        
        Format the response as a structured analysis."""
        
        analysis = self._generate_llm_response(prompt)
        return self._parse_analysis(analysis)
    
    def prepare_arguments(self, case_data: Dict[str, Any]) -> List[str]:
        """Prepare arguments for the defendant's case"""
        prompt = f"""Based on this case data, prepare strong arguments for the defense:
        Case Type: {case_data.get('case_type', 'Unknown')}
        Key Facts: {case_data.get('facts', [])}
        Plaintiff's Claims: {case_data.get('plaintiff_claims', [])}
        Evidence: {case_data.get('evidence', [])}
        
        Generate a list of compelling arguments that:
        1. Challenge the plaintiff's claims
        2. Present alternative interpretations
        3. Highlight weaknesses in plaintiff's case
        4. Support our position with evidence
        5. Address potential counter-arguments
        
        Format as a numbered list of arguments."""
        
        arguments = self._generate_llm_response(prompt)
        return self._parse_arguments(arguments)
    
    def _build_prompt(self, context: Dict[str, Any]) -> str:
        """Build a detailed prompt for the defendant's response"""
        phase = context.get("phase", "")
        witness = context.get("witness", {})
        previous_exchange = context.get("previous_exchange", "")
        
        if phase == "opening":
            return f"""As the defendant's attorney, deliver an opening statement that:
            1. Clearly states our position
            2. Challenges the plaintiff's claims
            3. Outlines our key arguments
            4. Sets the tone for our defense
            5. Maintains professionalism and credibility
            
            Previous exchange: {previous_exchange}
            
            Craft a compelling opening statement."""
        
        elif phase == "examination":
            return f"""As the defendant's attorney, prepare a cross-examination question for the witness:
            Witness: {witness.get('name', 'Unknown')}
            Witness Role: {witness.get('role', 'Unknown')}
            Previous Testimony: {witness.get('previous_testimony', '')}
            
            Craft a strategic question that:
            1. Challenges the witness's credibility
            2. Exposes inconsistencies
            3. Supports our defense
            4. Is legally appropriate
            5. Advances our case strategy
            
            Previous exchange: {previous_exchange}
            
            Generate a single, focused question."""
        
        elif phase == "closing":
            return f"""As the defendant's attorney, deliver a closing argument that:
            1. Summarizes key points in our favor
            2. Highlights weaknesses in plaintiff's case
            3. Reinforces our strongest arguments
            4. Appeals to the judge's sense of justice
            5. Concludes with a clear request for judgment
            
            Previous exchange: {previous_exchange}
            
            Craft a persuasive closing argument."""
        
        return f"""As the defendant's attorney, respond to this situation:
        Phase: {phase}
        Context: {context}
        Previous exchange: {previous_exchange}
        
        Generate a professional and strategic response.""" 