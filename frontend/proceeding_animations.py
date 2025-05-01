import streamlit as st

class CourtroomProceedingAnimation:
    def __init__(self):
        self.phase_animations = {
            'opening': self.animate_opening,
            'examination': self.animate_examination,
            'evidence': self.animate_evidence,
            'objection': self.animate_objection,
            'closing': self.animate_closing,
            'judgment': self.animate_judgment
        }
        
    def animate_opening(self, role):
        """Animation for opening statements"""
        st.markdown("""
        <div class="opening-statement">
            <h3>Opening Statements Phase</h3>
            <p>Present your opening statement to the court. Explain your client's position and what you intend to prove.</p>
        </div>
        """, unsafe_allow_html=True)
        
    def animate_examination(self, role):
        """Animation for witness examination"""
        st.markdown("""
        <style>
        @keyframes slideIn {
            from { transform: translateX(-100%); }
            to { transform: translateX(0); }
        }
        .examination {
            animation: slideIn 1s ease-out;
            padding: 10px;
            border-left: 4px solid #43A047;
            background-color: #E8F5E9;
        }
        </style>
        <div class="examination">
            <h3>Witness Examination Phase</h3>
            <p>Witnesses will now be called to testify and be examined by the lawyers.</p>
        </div>
        """, unsafe_allow_html=True)
        
    def animate_evidence(self, role):
        """Animation for evidence presentation"""
        st.markdown("""
        <style>
        @keyframes scaleIn {
            from { transform: scale(0); }
            to { transform: scale(1); }
        }
        .evidence {
            animation: scaleIn 1s ease-in-out;
            padding: 10px;
            border-left: 4px solid #FB8C00;
            background-color: #FFF3E0;
        }
        </style>
        <div class="evidence">
            <h3>Evidence Presentation Phase</h3>
            <p>The lawyers will now present and discuss key evidence in the case.</p>
        </div>
        """, unsafe_allow_html=True)
        
    def animate_objection(self, role):
        """Animation for objections"""
        st.markdown("""
        <style>
        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.05); }
            100% { transform: scale(1); }
        }
        .objection {
            animation: pulse 0.5s infinite;
            padding: 10px;
            border-left: 4px solid #E53935;
            background-color: #FFEBEE;
        }
        </style>
        <div class="objection">
            <h3>Objection Phase</h3>
            <p>Lawyers may raise objections to evidence or testimony that violates legal procedures.</p>
        </div>
        """, unsafe_allow_html=True)
        
    def animate_closing(self, role):
        """Animation for closing arguments"""
        st.markdown("""
        <style>
        @keyframes slideInFromBottom {
            from { transform: translateY(100%); opacity: 0; }
            to { transform: translateY(0); opacity: 1; }
        }
        .closing {
            animation: slideInFromBottom 1s ease-out;
            padding: 10px;
            border-left: 4px solid #7B1FA2;
            background-color: #F3E5F5;
        }
        </style>
        <div class="closing">
            <h3>Closing Arguments Phase</h3>
            <p>The lawyers will now present their final arguments summarizing their case.</p>
        </div>
        """, unsafe_allow_html=True)
        
    def animate_judgment(self, role):
        """Animation for judgment"""
        st.markdown("""
        <style>
        @keyframes glow {
            0% { box-shadow: 0 0 5px gold; }
            50% { box-shadow: 0 0 20px gold; }
            100% { box-shadow: 0 0 5px gold; }
        }
        .judgment {
            animation: glow 2s infinite;
            padding: 10px;
            border-left: 4px solid #FFC107;
            background-color: #FFF8E1;
        }
        </style>
        <div class="judgment">
            <h3>Judgment Phase</h3>
            <p>The judge will now deliver the final verdict based on the evidence and arguments presented.</p>
        </div>
        """, unsafe_allow_html=True)
        
    def animate_phase(self, phase, role=None):
        """Select and run the appropriate animation for the current phase"""
        if phase in self.phase_animations:
            self.phase_animations[phase](role)
        else:
            st.write(f"Phase: {phase}") 