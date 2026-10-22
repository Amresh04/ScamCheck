# ScamCheck
NOTE:_This website is totaly maide by Ai . only instructions ,workflow idea and prompt given by me .
ScamCheck is an independent, bilingual cyber-safety tool for checking suspicious messages, links, screenshots, and text-based PDF files. Its interface is available in English and Hindi. It is not a Government of India service.

Offline rules check English, Hindi, and common Hinglish fraud signals. Other languages require the optional Gemini service (`GEMINI_API_KEY`). When Gemini is configured, submitted text and extracted file text are sent to Google for analysis. Image OCR supports English and Hindi when the corresponding Tesseract language packs are installed. Text-based PDF extraction preserves Unicode text; scanned PDFs without selectable text are not supported yet. Do not submit passwords, OTPs, PINs, or other sensitive personal information.

Risk scores are indicators, not a guarantee that content is safe. The URL checker does not visit submitted URLs.

## Requirements

- Python 3.10 or newer
- Tesseract OCR installed and available on `PATH` for screenshot scanning. On Windows, the app also checks `C:\Program Files\Tesseract-OCR\tesseract.exe`. Install the English and Hindi language packs for both languages.
- A Gemini API key is optional. Rule-based scanning works without it.

## Run locally

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
python app.py
```

Open `http://127.0.0.1:5000`. Put credentials only in `.env`; do not commit that file.

## Production deployment

Run the WSGI app with a production server, for example on Linux:

```sh
gunicorn --workers 2 --bind 0.0.0.0:8000 app:app
```

Terminate HTTPS at a trusted reverse proxy, set `COOKIE_SECURE=true`, keep `FLASK_DEBUG=false`, and configure request timeouts and rate limits at the proxy. The built-in Flask development server is for local use only. Configure log collection and monitor the `/health` endpoint. `uploads/` is temporary processing storage and uploaded image files are removed after scanning; use encrypted ephemeral storage if the hosting platform requires a persistent filesystem.

## Supported input

- Message text: up to 20,000 characters.
- URL: up to 2,048 characters. The checker performs offline pattern analysis only.
- PNG, JPG/JPEG, or WEBP screenshot: up to 10 MB and 25 megapixels.
- PDF: up to 10 MB and 50 pages; requires selectable text (scanned image-only PDFs are not supported).

## Configuration

Copy `.env.example` to `.env` and set any required values. `GEMINI_MODEL` selects the Gemini model used for multilingual analysis. `OCR_LANGUAGES` selects installed Tesseract language packs, such as `eng,hin`. `LOG_LEVEL` accepts standard Python logging levels. Keep `.env`, uploaded content, and API credentials out of version control.
