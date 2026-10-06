import os

from PIL import Image, ImageOps, ImageEnhance, UnidentifiedImageError
import pytesseract


TESSERACT_WINDOWS_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


def configure_tesseract():
    """
    Configure Tesseract on Windows only when the common installation path exists.
    If Tesseract is already available in PATH, this does not cause any issue.
    """
    if os.path.exists(TESSERACT_WINDOWS_PATH):
        pytesseract.pytesseract.tesseract_cmd = TESSERACT_WINDOWS_PATH


def clean_extracted_text(text):
    lines = []

    for line in (text or "").splitlines():
        cleaned_line = " ".join(line.split())

        if cleaned_line:
            lines.append(cleaned_line)

    return "\n".join(lines).strip()


def prepare_image_for_ocr(image):
    """
    Improve an uploaded screenshot/image before OCR:
    - fixes phone-image rotation using EXIF data
    - converts it to grayscale
    - enlarges small images for better text recognition
    - improves contrast
    """
    image = ImageOps.exif_transpose(image)
    image = image.convert("RGB")

    width, height = image.size

    if width < 1400:
        scale = 2
        image = image.resize(
            (width * scale, height * scale),
            Image.Resampling.LANCZOS
        )

    grayscale_image = ImageOps.grayscale(image)
    enhanced_image = ImageEnhance.Contrast(grayscale_image).enhance(2.0)

    return enhanced_image


def extract_text_from_image(image_path):
    """
    Extract readable text from an image file using Tesseract OCR.

    Args:
        image_path: Full path of PNG, JPG, JPEG, or WEBP image.

    Returns:
        Extracted text as a string.

    Raises:
        RuntimeError: When the image is invalid or Tesseract is unavailable.
    """
    if not image_path:
        raise RuntimeError("No image path was provided for OCR.")

    if not os.path.exists(image_path):
        raise RuntimeError("The uploaded image file could not be found.")

    configure_tesseract()

    try:
        requested_languages = [
            item.strip() for item in os.getenv("OCR_LANGUAGES", "eng,hin").split(",")
            if item.strip()
        ]
        try:
            available_languages = set(pytesseract.get_languages(config=""))
            selected_languages = [
                language for language in requested_languages
                if language in available_languages
            ]
            language = "+".join(selected_languages) or "eng"
        except pytesseract.TesseractNotFoundError:
            language = "eng"

        with Image.open(image_path) as image:
            prepared_image = prepare_image_for_ocr(image)

            extracted_text = pytesseract.image_to_string(
                prepared_image,
                lang=language,
                config="--oem 3 --psm 6"
            )

            return clean_extracted_text(extracted_text)

    except pytesseract.TesseractNotFoundError:
        raise RuntimeError(
            "Tesseract OCR is not installed or is not configured correctly. "
            "Install Tesseract OCR, then restart Flask."
        )

    except UnidentifiedImageError:
        raise RuntimeError(
            "The uploaded file is not a readable image. "
            "Please upload a PNG, JPG, JPEG, or WEBP image."
        )

    except Exception as error:
        raise RuntimeError(f"OCR failed: {error}")
