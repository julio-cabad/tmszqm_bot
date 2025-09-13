#!/usr/bin/env python3
"""
Test script for sound alerts
"""

import os
import time

def test_sound_alerts():
    """Test the sound alert system"""
    print("🔊 Testing Sound Alerts...")
    
    print("🟢 Testing BUY/LONG alert...")
    try:
        os.system("afplay sounds/super_alert.wav")
    except:
        print("❌ Custom sound failed, trying system sound...")
        os.system("afplay /System/Library/Sounds/Glass.aiff")
    
    time.sleep(2)
    
    print("🔴 Testing SELL/SHORT alert...")
    try:
        os.system("afplay sounds/error_alert.wav")
    except:
        print("❌ Custom sound failed, trying system sound...")
        os.system("afplay /System/Library/Sounds/Basso.aiff")
    
    print("✅ Sound test completed!")

if __name__ == "__main__":
    test_sound_alerts()