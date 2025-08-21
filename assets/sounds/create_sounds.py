#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import wave
import math
import struct

def create_tone(frequency, duration, sample_rate=22050, amplitude=0.3):
    frames = []
    for i in range(int(duration * sample_rate)):
        value = amplitude * math.sin(2 * math.pi * frequency * i / sample_rate)
        
        fade_frames = int(0.05 * sample_rate)
        if i < fade_frames:
            value *= i / fade_frames
        elif i > int(duration * sample_rate) - fade_frames:
            remaining = int(duration * sample_rate) - i
            value *= remaining / fade_frames
            
        frames.append(struct.pack('<h', int(value * 32767)))
    
    return b''.join(frames)

def save_wav_file(filename, audio_data, sample_rate=22050):
    with wave.open(filename, 'wb') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(audio_data)

def create_notification_sounds():
    print("Creating notification sounds...")
    
    # Success sound
    success_parts = [
        create_tone(523, 0.1),
        create_tone(659, 0.1),
        create_tone(784, 0.1)
    ]
    save_wav_file("notification_success.wav", b''.join(success_parts))
    print("Success sound created")
    
    # Warning sound
    warning_parts = [
        create_tone(440, 0.12),
        create_tone(523, 0.12)
    ]
    save_wav_file("notification_warning.wav", b''.join(warning_parts))
    print("Warning sound created")
    
    # Error sound
    error_parts = [
        create_tone(523, 0.08),
        create_tone(440, 0.08),
        create_tone(349, 0.12)
    ]
    save_wav_file("notification_error.wav", b''.join(error_parts))
    print("Error sound created")
    
    # Info sound
    info_data = create_tone(523, 0.15)
    save_wav_file("notification_info.wav", info_data)
    print("Info sound created")
    
    print("All notification sounds created successfully!")

if __name__ == "__main__":
    try:
        create_notification_sounds()
    except Exception as e:
        print(f"Error creating sounds: {e}")