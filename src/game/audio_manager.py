"""
Audio management system for Claw Machine Game.
Handles background music and sound effects playback.
"""
import pygame
import os


def _resolve_audio_path(filename):
    """Helper: Resolve absolute path to audio file in assets/audio/"""
    # Get the project root (three levels up from this file: game/audio_manager.py -> game/ -> src/ -> root/)
    base_path = os.path.dirname(os.path.abspath(__file__))
    audio_path = os.path.join(base_path, "..", "..", "assets", "audio", filename)
    return os.path.normpath(audio_path)


def play_soundtrack(volume=0.5):
    """
    Plays the main game soundtrack (soundtrack.ogg) in an infinite loop.
    
    Args:
        volume (float): Volume level (0.0 to 1.0). Default 0.5.
    
    Notes:
        Uses pygame.mixer.music for seamless looping.
        Plays at 1x speed (pygame doesn't support speed adjustment).
        To play at different speeds, pre-process the audio file externally.
    """
    soundtrack_path = _resolve_audio_path("soundtrack.ogg")
    
    # Stop any currently playing music
    pygame.mixer.music.stop()
    
    # Load and play
    pygame.mixer.music.load(soundtrack_path)
    pygame.mixer.music.set_volume(volume)
    pygame.mixer.music.play(-1)  # -1 = loop indefinitely


def play_audio(name, volume=1.0):
    """
    Plays a one-shot sound effect from assets/audio/ at 1x speed.
    
    Args:
        name (str): Name of the audio file (without extension).
                   Examples: "homens-verde", "me-solta", "vai-comendo"
        volume (float): Volume level (0.0 to 1.0). Default 1.0.
    
    Returns:
        pygame.mixer.Channel: The channel playing the sound, or None if failed.
    
    Example:
        play_audio("homens-verde")  # Plays assets/audio/homens-verde.ogg
        play_audio("me-solta", volume=0.8)
    
    Notes:
        - Uses pygame.mixer.Sound for independent sound effect playback
        - Does not interfere with background music
        - Automatically finds available channel
        - Sound plays once and stops (no looping)
    """
    audio_path = _resolve_audio_path(f"{name}.ogg")
    
    # Check if file exists
    if not os.path.exists(audio_path):
        print(f"Warning: Audio file not found: {audio_path}")
        return None
    
    try:
        # Load and play sound effect
        sound = pygame.mixer.Sound(audio_path)
        sound.set_volume(volume)
        channel = sound.play()  # Play once
        return channel
    except pygame.error as e:
        print(f"Error playing audio '{name}': {e}")
        return None


def stop_soundtrack(fadeout_ms=1000):
    """
    Stops the currently playing soundtrack with optional fade-out.
    
    Args:
        fadeout_ms (int): Fade-out duration in milliseconds. Default 1000ms.
    """
    pygame.mixer.music.fadeout(fadeout_ms)
