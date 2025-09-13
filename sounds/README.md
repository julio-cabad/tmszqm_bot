# Spartan Trading System - Sound Files

This directory contains audio alert files for the Spartan Trading System.

## Required Sound Files

Place the following WAV files in this directory for audio alerts:

### Signal Alerts
- `super_alert.wav` - Super Bullish/Bearish signals (high priority)
- `strong_alert.wav` - Strong signals (medium priority)  
- `medium_alert.wav` - Medium signals (low priority)

### System Alerts
- `error_alert.wav` - System errors and connection issues
- `warning_alert.wav` - Rate limits and warnings

## Sound File Requirements

- Format: WAV (recommended) or MP3
- Sample Rate: 22050 Hz or higher
- Channels: Mono or Stereo
- Duration: 1-3 seconds (short and clear)

## Creating Sound Files

You can:
1. Download free sound effects from freesound.org
2. Use text-to-speech tools to create voice alerts
3. Record your own alert sounds
4. Use system notification sounds

## Example Commands to Create Simple Beep Sounds

If you have `sox` installed:

```bash
# Super alert (high pitch, urgent)
sox -n super_alert.wav synth 0.5 sine 1000 vol 0.7

# Strong alert (medium pitch)
sox -n strong_alert.wav synth 0.3 sine 800 vol 0.6

# Medium alert (lower pitch)
sox -n medium_alert.wav synth 0.2 sine 600 vol 0.5

# Error alert (warning tone)
sox -n error_alert.wav synth 0.8 sine 400 vol 0.8

# Warning alert (gentle beep)
sox -n warning_alert.wav synth 0.3 sine 500 vol 0.4
```

## Testing Sounds

The monitoring system will automatically detect and use sound files placed in this directory. If a sound file is missing, the system will log a warning but continue to function normally.