import os
import logging
import uuid

from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from werkzeug.utils import secure_filename

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

from services.ai_analyzer import analyze_text_with_ai
from services.url_checker import check_url_security
from services.risk_engine import compute_final_risk, analyze_message, translate_reasons_to_hindi
from services.ocr import extract_text_from_image
from services.pdf_reader import extract_text_from_pdf


app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates"),
    static_folder=os.path.join(BASE_DIR, "static")
)

app.config.update(
    # Leave room for multipart boundaries around a file capped at 10 MiB.
    MAX_CONTENT_LENGTH=11 * 1024 * 1024,
    JSON_SORT_KEYS=False,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=os.getenv("COOKIE_SECURE", "false").lower() == "true",
)
logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO").upper())
logger = logging.getLogger("scamcheck")

UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
ALLOWED_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.after_request
def add_security_headers(response):
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "DENY")
    response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
    response.headers.setdefault("Permissions-Policy", "camera=(), microphone=(), geolocation=()")
    response.headers.setdefault("Content-Security-Policy", "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; base-uri 'self'; frame-ancestors 'none'; form-action 'self'; object-src 'none'")
    response.headers.setdefault("Cache-Control", "no-store" if request.path == "/scan" else "no-cache")
    return response


def allowed_image_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_IMAGE_EXTENSIONS
    )


def ensure_list(value):
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]

    if isinstance(value, str) and value.strip():
        return [value.strip()]

    return []


def normalize_final_result(result, ai_result=None, message_result=None):
    """
    Guarantees a consistent response for the frontend,
    even if one service returns different key names.
    """
    if not isinstance(result, dict):
        result = {}

    score = result.get(
        "risk_score",
        result.get("score", result.get("final_score", 0))
    )

    try:
        score = int(float(score))
    except (TypeError, ValueError):
        score = 0

    score = max(0, min(100, score))

    risk_level = result.get(
        "risk_level",
        result.get("label", result.get("status", ""))
    )

    if not risk_level:
        if score >= 70:
            risk_level = "High Risk"
        elif score >= 40:
            risk_level = "Suspicious"
        else:
            risk_level = "Safe"

    reasons = ensure_list(
        result.get(
            "reasons",
            result.get("risk_reasons", result.get("warnings", []))
        )
    )

    recommendations = ensure_list(
        result.get(
            "recommendations",
            result.get("advice", result.get("suggestions", []))
        )
    )

    if not reasons:
        reasons = ["No detailed risk signals were returned by the scanner."]

    if not recommendations:
        recommendations = [
            "Do not share OTPs, passwords, PINs, CVV numbers, or bank details.",
            "Verify unexpected messages and links using official channels."
        ]

    ai_has_language_output = "Gemini" in str((ai_result or {}).get("analysis_source", ""))
    reasons_hi = (
        ensure_list((ai_result or {}).get("reasons_hi")) if ai_has_language_output
        else translate_reasons_to_hindi(reasons) + ensure_list((message_result or {}).get("reasons_hi"))
    ) or ensure_list((ai_result or {}).get("reasons_hi")) or [
        "जांच में मिले संकेतों को ध्यान से पढ़ें। संदेह हो तो लिंक न खोलें और पैसे न भेजें।"
    ]
    if ai_has_language_output:
        recommendations_hi = ensure_list((ai_result or {}).get("recommendations_hi"))
    elif score >= 70:
        recommendations_hi = [
            "लिंक न खोलें और पैसे न भेजें।",
            "OTP, PIN, पासवर्ड या बैंक की जानकारी किसी को न बताएं।",
            "बैंक या संस्था से उसके आधिकारिक नंबर पर पुष्टि करें।"
        ]
    elif score >= 40:
        recommendations_hi = [
            "कुछ भी करने से पहले संदेश या लिंक की आधिकारिक माध्यम से पुष्टि करें।",
            "लिंक पर बैंक या निजी जानकारी न डालें।"
        ]
    else:
        recommendations_hi = [
            "गुप्त कोड या बैंक की जानकारी किसी को न बताएं।",
            "अचानक आए संदेश की आधिकारिक माध्यम से पुष्टि करें।"
        ]

    return {
        "risk_score": score,
        "risk_level": str(risk_level),
        "reasons": reasons,
        "recommendations": recommendations,
        "safety_message": result.get("safety_message", ""),
        "reasons_hi": reasons_hi[:10],
        "recommendations_hi": recommendations_hi[:8],
        "explanation_hi": str((ai_result or {}).get("explanation_hi", ""))
        if ai_has_language_output and (ai_result or {}).get("risk_level") == risk_level else ""
    }


@app.route("/")
def home():
    return render_template("index.html", page="home")


@app.route("/message")
def message_tool():
    return render_template("index.html", page="message")


@app.route("/url")
def url_tool():
    return render_template("index.html", page="url")


@app.route("/pdf")
def pdf_tool():
    return render_template("index.html", page="pdf")


@app.route("/screenshot")
def screenshot_tool():
    return render_template("index.html", page="image")


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


@app.route("/scan", methods=["POST"])
def scan():
    scan_type = request.form.get("scan_type", "").strip().lower()

    try:
        # ---------------- MESSAGE SCAN ----------------
        if scan_type == "message":
            message = request.form.get("message", "").strip()

            if not message:
                return jsonify({
                    "success": False,
                    "error": "Please enter a message before scanning."
                }), 400

            if len(message) > 20000:
                return jsonify({"success": False, "error": "Messages must be 20,000 characters or fewer."}), 413

            ai_result = analyze_text_with_ai(message)
            message_result = analyze_message(message)

            final_result = compute_final_risk(
                ai_result=ai_result,
                message_result=message_result,
                url_result=None
            )

            return jsonify({
                "success": True,
                "scan_type": "message",
                "input_text": message,
                "ai_result": ai_result,
                "message_result": message_result,
                "final_result": normalize_final_result(final_result, ai_result, message_result)
            })

        # ---------------- URL SCAN ----------------
        if scan_type == "url":
            url = request.form.get("url", "").strip()

            if not url:
                return jsonify({
                    "success": False,
                    "error": "Please enter a URL before scanning."
                }), 400

            if len(url) > 2048:
                return jsonify({"success": False, "error": "URLs must be 2,048 characters or fewer."}), 400

            url_result = check_url_security(url)
            ai_result = analyze_text_with_ai(url)
            message_result = analyze_message(url)

            final_result = compute_final_risk(
                ai_result=ai_result,
                message_result=message_result,
                url_result=url_result
            )

            return jsonify({
                "success": True,
                "scan_type": "url",
                "input_url": url,
                "url_result": url_result,
                "ai_result": ai_result,
                "message_result": message_result,
                "final_result": normalize_final_result(final_result, ai_result, message_result)
            })

        # ---------------- IMAGE SCAN ----------------
        if scan_type == "image":
            if "image" not in request.files:
                return jsonify({
                    "success": False,
                    "error": "Please select an image before scanning."
                }), 400

            image_file = request.files["image"]

            if image_file.filename == "":
                return jsonify({
                    "success": False,
                    "error": "No image file was selected."
                }), 400

            if not allowed_image_file(image_file.filename):
                return jsonify({
                    "success": False,
                    "error": "Only PNG, JPG, JPEG, and WEBP images are supported."
                }), 400

            safe_filename = secure_filename(image_file.filename)
            if not safe_filename:
                return jsonify({"success": False, "error": "The image filename is invalid."}), 400

            unique_filename = f"{uuid.uuid4().hex}_{safe_filename}"
            image_path = os.path.join(app.config["UPLOAD_FOLDER"], unique_filename)

            try:
                image_file.save(image_path)
                if os.path.getsize(image_path) > 10 * 1024 * 1024:
                    return jsonify({"success": False, "error": "Image uploads must be 10 MB or smaller."}), 413

                # Check the actual file format; extensions and browser MIME types are untrusted.
                from PIL import Image, UnidentifiedImageError
                try:
                    with Image.open(image_path) as uploaded_image:
                        if uploaded_image.format not in {"PNG", "JPEG", "WEBP"}:
                            return jsonify({"success": False, "error": "The uploaded file is not a supported PNG, JPG, or WEBP image."}), 400
                        if uploaded_image.width * uploaded_image.height > 25_000_000:
                            return jsonify({"success": False, "error": "The image dimensions are too large. Use an image under 25 megapixels."}), 400
                        uploaded_image.verify()
                except (UnidentifiedImageError, OSError):
                    return jsonify({"success": False, "error": "The uploaded file is not a valid image."}), 400

                extracted_text = extract_text_from_image(image_path)

                if not extracted_text or not extracted_text.strip():
                    return jsonify({
                        "success": False,
                        "error": "No readable text was found in the image. Use a clearer image or screenshot."
                    }), 400

                ai_result = analyze_text_with_ai(extracted_text)
                message_result = analyze_message(extracted_text)

                final_result = compute_final_risk(
                    ai_result=ai_result,
                    message_result=message_result,
                    url_result=None
                )

                return jsonify({
                    "success": True,
                    "scan_type": "image",
                    "original_filename": safe_filename,
                    "extracted_text": extracted_text,
                    "ai_result": ai_result,
                    "message_result": message_result,
                    "final_result": normalize_final_result(final_result, ai_result, message_result)
                })

            finally:
                if os.path.exists(image_path):
                    os.remove(image_path)

        if scan_type == "pdf":
            pdf_file = request.files.get("pdf")
            if not pdf_file or not pdf_file.filename:
                return jsonify({"success": False, "error": "Choose a PDF file first."}), 400
            safe_filename = secure_filename(pdf_file.filename)
            if not safe_filename.lower().endswith(".pdf"):
                return jsonify({"success": False, "error": "Please choose a PDF file."}), 400

            pdf_path = os.path.join(app.config["UPLOAD_FOLDER"], f"{uuid.uuid4().hex}_{safe_filename}")
            try:
                pdf_file.save(pdf_path)
                if os.path.getsize(pdf_path) > 10 * 1024 * 1024:
                    return jsonify({"success": False, "error": "PDF files must be 10 MB or smaller."}), 413
                with open(pdf_path, "rb") as uploaded_pdf:
                    if not uploaded_pdf.read(5).startswith(b"%PDF-"):
                        return jsonify({"success": False, "error": "This file does not look like a valid PDF."}), 400

                try:
                    extracted_text = extract_text_from_pdf(pdf_path)
                except ValueError as error:
                    return jsonify({"success": False, "error": str(error)}), 400

                ai_result = analyze_text_with_ai(extracted_text)
                message_result = analyze_message(extracted_text)
                final_result = compute_final_risk(ai_result, message_result, None)
                normalized_result = normalize_final_result(final_result, ai_result, message_result)

                return jsonify({
                    "success": True,
                    "scan_type": "pdf",
                    "original_filename": safe_filename,
                    "extracted_text": extracted_text,
                    "final_result": normalized_result
                })
            finally:
                if os.path.exists(pdf_path):
                    os.remove(pdf_path)

        return jsonify({
            "success": False,
            "error": "Invalid scan type. Choose Message, URL, Image, or PDF."
        }), 400

    except Exception:
        logger.exception("Scan failed (type=%s)", scan_type)

        return jsonify({
            "success": False,
            "error": "The scan could not be completed. Please try again later."
        }), 500


@app.errorhandler(413)
def file_too_large(error):
    return jsonify({
        "success": False,
        "error": "The request is too large. Upload a file no larger than 10 MB."
    }), 413


if __name__ == "__main__":
    app.run(debug=os.getenv("FLASK_DEBUG", "false").lower() == "true")
