# Deploy the Frontier Run Gemini AI server

This API runs separately from the Godot game. Never put your Gemini API key in the game or commit it to GitHub.

## Deploy on Render
1. Create a Web Service connected to this repository.
2. Build command: `pip install -r requirements.txt`
3. Start command: `python ai_server.py`
4. Add `GEMINI_API_KEY` in Render Environment settings.
5. Optionally set `GEMINI_MODEL=gemini-2.5-flash`.
6. Deploy, then check `https://YOUR-SERVICE.onrender.com/health`.

The chat endpoint is `POST /chat`. Update the Godot game's `AI_SERVER_URL` to your deployed HTTPS URL plus `/chat`.

Free hosting can sleep when idle. Test the server and game in Godot before release. The in-memory rate limit is basic; add stronger authentication before a public launch.
