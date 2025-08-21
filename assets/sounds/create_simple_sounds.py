#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
إنشاء نغمات بسيطة للإشعارات بدون مكتبات خارجية
"""

import wave
import math
import struct

def create_tone(frequency, duration, sample_rate=22050, amplitude=0.3):
    """إنشاء نغمة بسيطة"""
    frames = []
    for i in range(int(duration * sample_rate)):
        # حساب القيمة الصوتية
        value = amplitude * math.sin(2 * math.pi * frequency * i / sample_rate)
        
        # تطبيق fade in/out للنعومة
        fade_frames = int(0.05 * sample_rate)  # 50ms
        if i < fade_frames:
            value *= i / fade_frames
        elif i > int(duration * sample_rate) - fade_frames:
            remaining = int(duration * sample_rate) - i
            value *= remaining / fade_frames
            
        # تحويل إلى 16-bit integer
        frames.append(struct.pack('<h', int(value * 32767)))
    
    return b''.join(frames)

def save_wav_file(filename, audio_data, sample_rate=22050):
    """حفظ البيانات الصوتية كملف WAV"""
    with wave.open(filename, 'wb') as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(audio_data)

def create_notification_sounds():
    """إنشاء جميع نغمات الإشعارات"""
    
    print("جاري إنشاء نغمات الإشعارات...")
    
    # نغمة النجاح - نغمة لطيفة صاعدة
    success_parts = [
        create_tone(523, 0.1),  # C5
        create_tone(659, 0.1),  # E5  
        create_tone(784, 0.1)   # G5
    ]
    save_wav_file("notification_success.wav", b''.join(success_parts))
    print("✓ تم إنشاء نغمة النجاح")
    
    # نغمة التحذير - نغمة متوسطة
    warning_parts = [
        create_tone(440, 0.12),  # A4
        create_tone(523, 0.12)   # C5
    ]
    save_wav_file("notification_warning.wav", b''.join(warning_parts))
    print("✓ تم إنشاء نغمة التحذير")
    
    # نغمة الخطأ - نغمة هابطة
    error_parts = [
        create_tone(523, 0.08),  # C5
        create_tone(440, 0.08),  # A4
        create_tone(349, 0.12)   # F4
    ]
    save_wav_file("notification_error.wav", b''.join(error_parts))
    print("✓ تم إنشاء نغمة الخطأ")
    
    # نغمة المعلومات - نغمة بسيطة وهادئة
    info_data = create_tone(523, 0.15)  # C5
    save_wav_file("notification_info.wav", info_data)
    print("✓ تم إنشاء نغمة المعلومات")
    
    print("\n🎵 تم إنشاء جميع نغمات الإشعارات بنجاح!")

if __name__ == "__main__":
    try:
        create_notification_sounds()
    except Exception as e:
        print(f"❌ خطأ في إنشاء النغمات: {e}")