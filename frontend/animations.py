import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
from io import BytesIO
from PIL import Image

class CourtroomAnimation:
    def __init__(self):
        self.characters = {
            "judge": {"position": (0.5, 0.15), "speaking": False},
            "plaintiff_lawyer": {"position": (0.2, 0.4), "speaking": False},
            "defendant_lawyer": {"position": (0.8, 0.4), "speaking": False},
            "witness": {"position": (0.5, 0.4), "speaking": False},
            "plaintiff": {"position": (0.1, 0.6), "speaking": False},
            "defendant": {"position": (0.9, 0.6), "speaking": False},
        }
        self.courtroom_bg = self.create_courtroom_bg()
        self.current_speaker = None
        self.animation_frames = []
        self.animation_speed = 0.5

    def create_courtroom_bg(self):
        """Create a simple courtroom background"""
        fig, ax = plt.subplots(figsize=(8, 4.8))
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        
        # Draw judge bench
        ax.add_patch(plt.Rectangle((0.3, 0.05), 0.4, 0.1, color='brown'))
        
        # Draw witness stand
        ax.add_patch(plt.Rectangle((0.45, 0.35), 0.1, 0.1, color='brown'))
        
        # Draw lawyers' tables
        ax.add_patch(plt.Rectangle((0.1, 0.35), 0.2, 0.05, color='brown'))
        ax.add_patch(plt.Rectangle((0.7, 0.35), 0.2, 0.05, color='brown'))
        
        # Draw audience area
        ax.add_patch(plt.Rectangle((0.1, 0.6), 0.8, 0.3, color='lightgray', alpha=0.5))
        
        ax.axis('off')
        return fig

    def draw_character(self, ax, role, is_speaking=False):
        """Draw a character on the courtroom"""
        char_info = self.characters.get(role, {"position": (0.5, 0.5), "speaking": False})
        x, y = char_info["position"]
        
        # Body
        color = 'black' if role == 'judge' else 'navy' if 'lawyer' in role else 'darkgreen'
        ax.add_patch(plt.Circle((x, y), 0.05, color=color))
        
        # Head
        ax.add_patch(plt.Circle((x, y-0.07), 0.03, color='tan'))
        
        # Speech bubble if speaking
        if is_speaking:
            ax.annotate("Speaking", xy=(x, y-0.12), 
                        xytext=(x+0.15, y-0.15),
                        arrowprops=dict(arrowstyle="->", color='black'),
                        bbox=dict(boxstyle="round,pad=0.3", fc="yellow", alpha=0.7))

    def animate_phase(self, phase, speaking_role=None):
        """Animate the current phase of the trial"""
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        
        # Draw courtroom background
        ax.add_patch(plt.Rectangle((0, 0), 1, 1, color='#111', alpha=1.0))
        
        # Draw judge bench
        ax.add_patch(plt.Rectangle((0.3, 0.05), 0.4, 0.1, color='brown'))
        
        # Draw witness stand
        ax.add_patch(plt.Rectangle((0.45, 0.35), 0.1, 0.1, color='brown'))
        
        # Draw lawyers' tables
        ax.add_patch(plt.Rectangle((0.1, 0.35), 0.2, 0.05, color='brown'))
        ax.add_patch(plt.Rectangle((0.7, 0.35), 0.2, 0.05, color='brown'))
        
        # Draw audience area
        ax.add_patch(plt.Rectangle((0.1, 0.6), 0.8, 0.3, color='lightgray', alpha=0.5))
        
        # Draw phase-specific elements
        if phase == 'opening':
            ax.text(0.5, 0.9, "Opening Statements", ha='center', fontsize=14, 
                    bbox=dict(facecolor='#222', edgecolor='#e10600', alpha=0.9, 
                             boxstyle='round,pad=0.5'), color='#fff')
        elif phase == 'examination':
            ax.text(0.5, 0.9, "Witness Examination", ha='center', fontsize=14, 
                    bbox=dict(facecolor='white', alpha=0.5))
        elif phase == 'evidence':
            ax.text(0.5, 0.9, "Evidence Presentation", ha='center', fontsize=14, 
                    bbox=dict(facecolor='white', alpha=0.5))
            ax.add_patch(plt.Rectangle((0.45, 0.45), 0.1, 0.05, color='yellow', alpha=0.8))
        elif phase == 'objection':
            ax.text(0.5, 0.9, "Objection Phase", ha='center', fontsize=14, 
                    bbox=dict(facecolor='white', alpha=0.5))
            if speaking_role and 'lawyer' in speaking_role.lower():
                ax.text(0.5, 0.75, "OBJECTION!", ha='center', fontsize=16, color='red', weight='bold')
        elif phase == 'closing':
            ax.text(0.5, 0.9, "Closing Arguments", ha='center', fontsize=14, 
                    bbox=dict(facecolor='white', alpha=0.5))
        elif phase == 'judgment':
            ax.text(0.5, 0.9, "Judgment", ha='center', fontsize=14, 
                    bbox=dict(facecolor='white', alpha=0.5))
            ax.add_patch(plt.Rectangle((0.3, 0.02), 0.4, 0.13, color='brown', linewidth=3, edgecolor='gold'))
        elif phase == 'completed':
            ax.text(0.5, 0.9, "Case Closed", ha='center', fontsize=14, 
                    bbox=dict(facecolor='white', alpha=0.5))
            ax.text(0.5, 0.5, "JUSTICE SERVED", ha='center', fontsize=20, color='navy', weight='bold')
            
        # Draw characters
        for role, info in self.characters.items():
            self.draw_character(ax, role, is_speaking=(role.lower() == speaking_role.lower() if speaking_role else False))
            
        ax.axis('off')
        
        # Convert plot to image for Streamlit
        buf = BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        st.image(buf, use_column_width=True)
        plt.close(fig)
        
    def animate_confetti(self):
        """Display animated confetti for case completion"""
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        
        # Create and display confetti
        confetti_colors = ['red', 'blue', 'green', 'yellow', 'purple', 'orange']
        for _ in range(100):
            x = np.random.rand()
            y = np.random.rand()
            color = np.random.choice(confetti_colors)
            ax.add_patch(plt.Rectangle((x, y), 0.02, 0.01, color=color, alpha=0.7))
            
        ax.text(0.5, 0.5, "CASE CLOSED", ha='center', fontsize=24, color='navy', weight='bold')
        ax.axis('off')
        
        # Convert plot to image for Streamlit
        buf = BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        st.image(buf, use_column_width=True)
        plt.close(fig) 