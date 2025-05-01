# utils/knowledge_base.py

import json
import os
from typing import Dict, Any, List, Optional

class KnowledgeBase:
    def __init__(self):
        self.precedents = []
        self.legal_principles = []
        self.load_knowledge_base()
        
    def load_knowledge_base(self):
        """Load legal knowledge from JSON files"""
        try:
            with open('data/precedents.json', 'r') as f:
                self.precedents = json.load(f)
        except FileNotFoundError:
            self.precedents = []
            
        try:
            with open('data/legal_principles.json', 'r') as f:
                self.legal_principles = json.load(f)
        except FileNotFoundError:
            self.legal_principles = []
            
    def get_section(self, section_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific legal section"""
        for principle in self.legal_principles:
            if principle.get('id') == section_id:
                return principle
        return None
        
    def search_principles(self, query: str) -> List[Dict[str, Any]]:
        """Search for legal principles matching the query"""
        return [
            principle for principle in self.legal_principles
            if query.lower() in principle.get('title', '').lower() or
            query.lower() in principle.get('description', '').lower()
        ]
        
    def get_relevant_precedents(self, case_type: str) -> List[Dict[str, Any]]:
        """Get precedents relevant to a case type"""
        return [
            precedent for precedent in self.precedents
            if case_type.lower() in precedent.get('case_type', '').lower()
        ]
        
    def add_precedent(self, precedent: Dict[str, Any]):
        """Add a new precedent"""
        self.precedents.append(precedent)
        self.save_knowledge_base()
        
    def add_legal_principle(self, principle: Dict[str, Any]):
        """Add a new legal principle"""
        self.legal_principles.append(principle)
        self.save_knowledge_base()
        
    def get_legal_advice(self, case_facts: Dict[str, Any]) -> Dict[str, Any]:
        """Get legal advice based on case facts"""
        relevant_sections = []
        applicable_precedents = []
        legal_principles = []
        
        # Find relevant sections
        for principle in self.legal_principles:
            if any(keyword in case_facts.get('description', '').lower()
                  for keyword in principle.get('keywords', [])):
                relevant_sections.append(principle)
                
        # Find applicable precedents
        applicable_precedents = self.get_relevant_precedents(case_facts.get('case_type', ''))
        
        # Extract legal principles
        for section in relevant_sections:
            legal_principles.extend(section.get('principles', []))
            
        return {
            'relevant_sections': relevant_sections,
            'applicable_precedents': applicable_precedents,
            'legal_principles': legal_principles
        }
        
    def save_knowledge_base(self):
        """Save the knowledge base to JSON files"""
        os.makedirs('data', exist_ok=True)
        
        with open('data/precedents.json', 'w') as f:
            json.dump(self.precedents, f, indent=4)
            
        with open('data/legal_principles.json', 'w') as f:
            json.dump(self.legal_principles, f, indent=4)

# Create a global instance
knowledge_base = KnowledgeBase()

def load_laws():
    """Load laws using the global knowledge base instance"""
    knowledge_base.load_knowledge_base()

def get_legal_advice(case_facts: Dict[str, Any]) -> Dict[str, Any]:
    """Get legal advice using the global knowledge base instance"""
    return knowledge_base.get_legal_advice(case_facts)
