# Text-to-Speech Integration

The AI Summarizer includes a simplified text-to-speech feature that reads summary text aloud using the browser's built-in speech synthesis.

## TTS Engine

### **Browser TTS (Web Speech API)**
- **Pros**: No server processing, works offline, fast response
- **Cons**: Voice quality varies by browser/device
- **Best for**: Simple, reliable text-to-speech

## Features

- **🔊 Speak Button**: Click to hear the summary read aloud
- **⏯️ Playback Control**: Start/stop speech playback
- **🎯 One-Click**: Simple, single-button interface

## Usage

1. Generate a summary using either text or URL input
2. Once the summary appears, click the "🔊 Speak" button
3. The summary will be read aloud using your browser's voice
4. Click "Stop" to interrupt playback

## Technical Implementation

### Client-Side Components
- JavaScript TTS controller using Web Speech API
- Automatic voice selection (prefers English female voices)
- Simple start/stop functionality

### Browser Compatibility

Browser TTS works in all modern browsers:
- Chrome/Chromium (recommended)
- Firefox
- Safari
- Edge
- Mobile browsers

Voice quality and available voices vary by browser and operating system.

## Configuration

The system uses the browser's default TTS settings:
- Speed: 0.9x (slightly slower than default)
- Pitch: Normal (1.0)
- Volume: 80%

Automatically selects the best available English voice.

## Error Handling

- Graceful fallback if TTS is not supported
- User-friendly error messages
- Automatic voice selection