# Frontier Run — Android + Gemini AI

This repository is for the Frontier Run Godot Android game and its Gemini-powered AI backend.

## Project source

The reviewed project archive is prepared in this ChatGPT conversation as `Frontier_Run_Android_Reviewed_Fixed.zip`. It contains the Godot project, Python AI server, Render deployment blueprint, and setup instructions.

## Deployment notes

- Configure `GEMINI_API_KEY` as a server-side environment variable. Do not commit secrets.
- Deploy `ai_server.py` using the included `render.yaml` and `requirements.txt`.
- Configure the Godot client to use the deployed HTTPS `/chat` endpoint before exporting the Android app.
- Android APK/AAB export and live Gemini connectivity still require testing.
