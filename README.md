---
title: Speech to Text Backend
emoji: 🎙️
colorFrom: indigo
colorTo: purple
sdk: docker
app_port: 7860
pinned: false
---

# Speech to Text Backend

A high-performance Flask + faster-whisper Docker backend optimized for running on Hugging Face Spaces.

## Features
- Baked-in Whisper model for instant cold-starts
- 2 OMP/CPU threads optimization to prevent container thrashing
- Secure CORS and CSP headers
