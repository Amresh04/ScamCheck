"""Safe, bounded text extraction for text-based PDF documents."""

try:
    from pypdf import PdfReader
except ImportError:
    PdfReader = None


MAX_PDF_PAGES = 50
MAX_EXTRACTED_CHARACTERS = 20000
MAX_PAGE_CONTENT_BYTES = 25 * 1024 * 1024


def extract_text_from_pdf(pdf_path):
    try:
        if PdfReader is None:
            raise ValueError(
                "PDF scanning needs an extra package. In PowerShell, run "
                "python -m pip install -r requirements.txt, then restart Cyber Suraksha Saathi."
            )
        document = PdfReader(pdf_path, strict=False)
        if document.is_encrypted:
            raise ValueError("This PDF is password protected. Please upload an unlocked copy.")
        if len(document.pages) == 0:
            raise ValueError("This PDF has no pages.")
        if len(document.pages) > MAX_PDF_PAGES:
            raise ValueError("This PDF has too many pages. Please upload a file with 50 pages or fewer.")

        sections = []
        remaining = MAX_EXTRACTED_CHARACTERS
        for page_number, page in enumerate(document.pages, start=1):
            content_stream = page.get_contents()
            if content_stream and len(content_stream.get_data()) > MAX_PAGE_CONTENT_BYTES:
                raise ValueError("This PDF page is too large to check safely. Please use a smaller PDF.")
            page_text = (page.extract_text() or "").strip()
            if page_text and remaining:
                page_text = page_text[:remaining]
                sections.append(f"[Page {page_number}]\n{page_text}")
                remaining -= len(page_text)

        text = "\n\n".join(sections).strip()
        if not text:
            raise ValueError(
                "We could not read selectable text in this PDF. It may be a scanned document. "
                "For now, use a clear screenshot instead."
            )
        return text[:MAX_EXTRACTED_CHARACTERS]
    except ValueError:
        raise
    except Exception as error:
        raise ValueError("This PDF could not be opened. Please choose a valid, non-damaged PDF.") from error
