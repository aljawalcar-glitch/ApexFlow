#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
مولد النغمات البسيطة للإشعارات
Simple notification sound generator
"""

import numpy as np
import wave
import os

def generate_tone(frequency, duration, sample_rate=44100, amplitude=0.3):
    """توليد نغمة بسيطة"""
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    # استخدام موجة جيبية ناعمة
    wave_data = amplitude * np.sin(2 * np.pi * frequency * t)
    
    # إضافة تأثير fade in/out للنعومة
    fade_samples = int(0.05 * sample_rate)  # 50ms fade
    if len(wave_data) > 2 * fade_samples:
        # Fade in
        wave_data[:fade_samples] *= np.linspace(0, 1, fade_samples)
        # Fade out
        wave_data[-fade_samples:] *= np.linspace(1, 0, fade_samples)
    
    return wave_data

def save_wav(filename, data, sample_rate=44100):
    """حفظ البيانات الصوتية كملف WAV"""
    # تحويل إلى 16-bit integers
    data_int = np.int16(data * 32767)
    
    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(data_int.tobytes())

def generate_notification_sounds():
    """توليد جميع نغمات الإشعارات"""
    
    # نغمة النجاح - نغمة صاعدة لطيفة
    success_data = np.concatenate([
        generate_tone(523, 0.1),  # C5
        generate_tone(659, 0.1),  # E5
        generate_tone(784, 0.15)  # G5
    ])
    save_wav("notification_success.wav", success_data)
    
    # نغمة التحذير - نغمة متوسطة
    warning_data = np.concatenate([
        generate_tone(440, 0.15),  # A4
        generate_tone(523, 0.15)   # C5
    ])
    save_wav("notification_warning.wav", warning_data)
    
    # نغمة الخطأ - نغمة هابطة
    error_data = np.concatenate([
        generate_tone(523, 0.1),  # C5
        generate_tone(440, 0.1),  # A4
        generate_tone(349, 0.15)  # F4
    ])
    save_wav("notification_error.wav", error_data)
    
    # نغمة المعلومات - نغمة بسيطة
    info_data = generate_tone(523, 0.2)  # C5
    save_wav("notification_info.wav", info_data)
    
    print("تم إنشاء جميع ملفات النغمات بنجاح!")

if __name__ == "__main__":
    try:
        generate_notification_sounds()
    except ImportError:
        print("تحتاج إلى تثبيت numpy لإنشاء النغمات:")
        print("pip install numpy")
    except Exception as e:
        print(f"خطأ في إنشاء النغمات: {e}")