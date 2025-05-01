from typing import Dict, List, Any
from .agent_base import AgentBase
from llm.groq_api import groq_api

class PlaintiffAgent(AgentBase):
    def __init__(self, llm_provider: str = "Groq"):
        super().__init__("plaintiff", llm_provider)
    
    def generate_response(self, context: Dict[str, Any]) -> str:
        """Generate a response as the plaintiff"""
        prompt = self._build_prompt(context)
        result = groq_api.generate_response(prompt)
        if "error" in result:
            return f"Error generating response: {result['error']}"
        return result["response"]
    
    def _build_prompt(self, context: Dict[str, Any]) -> str:
        """Build a prompt for the LLM based on the context"""
        phase = context.get("phase", "")
        user_input = context.get("user_input", "")
        case = context.get("case", {})
        
        if phase == "opening":
            return f"""As a plaintiff's lawyer, prepare an opening statement in response to the defendant's statement:
            Defendant's Statement: {user_input}
            
            Case Details:
            - Type: {case.get('case_type', 'Unknown')}
            - Facts: {case.get('facts', [])}
            - Evidence: {case.get('evidence', [])}
            
            Provide a compelling opening statement that:
            1. Addresses the defendant's claims
            2. Presents our case strategy
            3. Sets the tone for our case
            4. Maintains professionalism and respect for the court"""
        
        # Generate examination questions
        elif phase == "examination":
            witness = context.get("witness", {})
            return f"Can you describe your relationship with the defendant and what happened on {witness.get('date', 'the day in question')}?"
        
        # Generate closing argument
        elif phase == "closing":
            return "In conclusion, the evidence clearly shows that the defendant breached the contract..."
        
        return "I object to that line of questioning."
    
    def analyze_case(self, case_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze the case from plaintiff's perspective"""
        return {
            "strengths": [
                "Clear breach of contract terms",
                "Documentary evidence available",
                "Witness testimony supporting our case"
            ],
            "weaknesses": [
                "Some missing documentation",
                "Potential credibility issues with one witness"
            ],
            "strategy": "Focus on the clear breach and damages suffered"
        }
    
    def prepare_arguments(self, case_data: Dict[str, Any]) -> List[str]:
        """Prepare arguments for the plaintiff's case"""
        return [
            "The defendant failed to deliver goods as per contract terms",
            "The plaintiff suffered financial losses due to the breach",
            "The defendant had no valid reason for non-performance",
            "The plaintiff is entitled to damages as per Section 73 of the Indian Contract Act"
        ] 