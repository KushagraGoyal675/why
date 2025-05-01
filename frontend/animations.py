# This file is intentionally left blank to prevent import errors.

import streamlit as st
import time
from typing import Optional, Callable

class AnimationManager:
    @staticmethod
    def fade_in_text(text: str, delay: float = 0.05):
        """Creates a fade-in animation effect for text using Streamlit's empty placeholder."""
        placeholder = st.empty()
        for i in range(len(text) + 1):
            placeholder.markdown(
                f"""
                <div style='opacity: 1; transition: opacity 0.5s;'>
                    {text[:i]}
                </div>
                """,
                unsafe_allow_html=True
            )
            time.sleep(delay)
        return placeholder

    @staticmethod
    def typewriter_effect(text: str, delay: float = 0.05):
        """Creates a typewriter effect for text using Streamlit's empty placeholder."""
        placeholder = st.empty()
        for i in range(len(text) + 1):
            placeholder.markdown(f"{''.join(text[:i])}_")
            time.sleep(delay)
        placeholder.markdown(text)
        return placeholder

    @staticmethod
    def progress_bar_animation(
        title: str,
        duration: float = 3.0,
        on_complete: Optional[Callable] = None
    ):
        """Displays an animated progress bar with optional completion callback."""
        progress_text = title
        progress_bar = st.progress(0)
        
        for i in range(101):
            progress_bar.progress(i)
            time.sleep(duration / 100)
        
        if on_complete:
            on_complete()
        
        return progress_bar

    @staticmethod
    def flash_message(message: str, duration: float = 1.0, style: str = "info"):
        """Displays a temporary flash message with specified style."""
        placeholder = st.empty()
        
        if style == "success":
            placeholder.success(message)
        elif style == "error":
            placeholder.error(message)
        elif style == "warning":
            placeholder.warning(message)
        else:
            placeholder.info(message)
            
        time.sleep(duration)
        placeholder.empty()

    @staticmethod
    def slide_transition(old_content: str, new_content: str, direction: str = "left"):
        """Creates a sliding transition effect between two pieces of content."""
        if direction not in ["left", "right"]:
            direction = "left"
            
        slide_direction = "translateX(-100%)" if direction == "left" else "translateX(100%)"
        
        st.markdown(
            f"""
            <div style='position: relative; overflow: hidden;'>
                <div style='transform: {slide_direction}; transition: transform 0.5s;'>
                    {old_content}
                </div>
                <div style='position: absolute; top: 0; left: 0; transform: translateX(0); transition: transform 0.5s;'>
                    {new_content}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        time.sleep(0.5) 