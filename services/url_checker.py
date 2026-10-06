import re
import ipaddress
from urllib.parse import urlparse


SUSPICIOUS_WORDS = [
    "login",
    "signin",
    "verify",
    "verification",
    "secure",
    "security",
    "update",
    "kyc",
    "bank",
    "wallet",
    "payment",
    "pay",
    "refund",
    "reward",
    "prize",
    "winner",
    "claim",
    "gift",
    "support",
    "account",
    "confirm",
    "password",
    "otp"
]

URL_SHORTENERS = [
    "bit.ly",
    "tinyurl.com",
    "t.co",
    "goo.gl",
    "is.gd",
    "cutt.ly",
    "rb.gy",
    "shorturl.at",
    "tiny.one",
    "rebrand.ly"
]

TRUSTED_DOMAINS = [
    "google.com",
    "youtube.com",
    "wikipedia.org",
    "github.com",
    "microsoft.com",
    "apple.com",
    "amazon.in",
    "amazon.com",
    "sbi.co.in",
    "rbi.org.in",
    "gov.in",
    "india.gov.in"
]


def get_risk_level(score):
    if score >= 70:
        return "High Risk"
    if score >= 40:
        return "Suspicious"
    return "Safe"


def normalize_url(url):
    url = (url or "").strip()

    if not url:
        return ""

    if not re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*://", url):
        url = "http://" + url

    return url


def is_ip_address(hostname):
    try:
        ipaddress.ip_address(hostname)
        return True
    except ValueError:
        return False


def is_trusted_domain(hostname):
    hostname = (hostname or "").lower().strip(".")

    for trusted_domain in TRUSTED_DOMAINS:
        if hostname == trusted_domain or hostname.endswith("." + trusted_domain):
            return True

    return False


def check_url_security(url):
    """
    Check a URL using offline security rules.
    This function does not open the URL or make a request to it.

    Returns a consistent dictionary for CyberSaathi's risk engine.
    """
    original_url = (url or "").strip()
    normalized_url = normalize_url(original_url)

    if not normalized_url:
        return {
            "risk_score": 0,
            "risk_level": "Safe",
            "is_safe": False,
            "normalized_url": "",
            "domain": "",
            "reasons": ["No URL was provided."],
            "recommendations": ["Enter a valid website address to scan."],
            "suspicious_signals": []
        }

    try:
        parsed = urlparse(normalized_url)
        hostname = (parsed.hostname or "").lower().strip(".")
        scheme = (parsed.scheme or "").lower()
        path_and_query = f"{parsed.path}?{parsed.query}".lower()

    except Exception:
        return {
            "risk_score": 85,
            "risk_level": "High Risk",
            "is_safe": False,
            "normalized_url": normalized_url,
            "domain": "",
            "reasons": ["The URL format could not be read safely."],
            "recommendations": [
                "Do not open this link.",
                "Ask the sender for an official website address."
            ],
            "suspicious_signals": ["Invalid URL format"]
        }

    score = 0
    reasons = []
    suspicious_signals = []

    if scheme not in ["http", "https"]:
        score += 60
        reasons.append("The URL uses an unsupported or potentially unsafe protocol.")
        suspicious_signals.append("Unsafe protocol")

    if not hostname:
        score += 80
        reasons.append("The URL does not contain a valid website domain.")
        suspicious_signals.append("Missing domain")

    if scheme == "http":
        score += 15
        reasons.append("The URL uses HTTP instead of encrypted HTTPS.")
        suspicious_signals.append("HTTP instead of HTTPS")

    if "@" in normalized_url:
        score += 30
        reasons.append("The URL contains '@', which can hide the real destination domain.")
        suspicious_signals.append("Contains @ symbol")

    if hostname and is_ip_address(hostname):
        score += 35
        reasons.append("The URL uses an IP address instead of a normal domain name.")
        suspicious_signals.append("IP address used as domain")

    if hostname and hostname.startswith("xn--"):
        score += 25
        reasons.append("The domain uses punycode, which can sometimes imitate trusted websites.")
        suspicious_signals.append("Punycode domain")

    if hostname and len(hostname) > 55:
        score += 10
        reasons.append("The domain name is unusually long.")
        suspicious_signals.append("Very long domain")

    if normalized_url.count(".") >= 5:
        score += 10
        reasons.append("The URL has many subdomains, which can hide the real domain.")
        suspicious_signals.append("Many subdomains")

    if len(normalized_url) > 150:
        score += 10
        reasons.append("The URL is unusually long.")
        suspicious_signals.append("Very long URL")

    if hostname and hostname in URL_SHORTENERS:
        score += 20
        reasons.append("The URL uses a shortened-link service, so the final destination is hidden.")
        suspicious_signals.append("URL shortener")

    url_text = (hostname + " " + path_and_query).lower()

    matched_words = []
    for word in SUSPICIOUS_WORDS:
        if word in url_text:
            matched_words.append(word)

    if matched_words:
        score += min(len(matched_words) * 6, 24)
        reasons.append(
            "The URL contains sensitive or scam-related words: "
            + ", ".join(sorted(set(matched_words))) + "."
        )
        suspicious_signals.append("Suspicious URL words")

    if re.search(r"[^a-zA-Z0-9.-]", hostname or ""):
        score += 12
        reasons.append("The domain contains unusual characters.")
        suspicious_signals.append("Unusual domain characters")

    trusted_domain = hostname and is_trusted_domain(hostname)

    if trusted_domain and scheme == "https":
        score = max(0, score - 15)
        reasons.append("The domain matches a known trusted-domain pattern.")

    score = min(score, 100)
    risk_level = get_risk_level(score)

    if risk_level == "High Risk":
        recommendations = [
            "Do not open this link or enter any personal information.",
            "Do not provide OTP, password, PIN, CVV, bank details, or UPI PIN.",
            "Open the organization’s official website manually instead of using this link.",
            "Report or block the sender if the link was unsolicited."
        ]
    elif risk_level == "Suspicious":
        recommendations = [
            "Do not enter passwords, OTPs, bank details, or payment information.",
            "Verify the domain through the official website or official mobile app.",
            "Avoid clicking the link until you confirm the sender and destination."
        ]
    else:
        recommendations = [
            "No strong offline risk indicators were found.",
            "Still verify unexpected links before entering personal or financial information.",
            "Use official websites or apps for important banking and account actions."
        ]

    if not reasons:
        reasons = [
            "No strong suspicious URL patterns were found by the offline checker."
        ]

    return {
        "risk_score": score,
        "risk_level": risk_level,
        "is_safe": score < 40,
        "normalized_url": normalized_url,
        "domain": hostname,
        "reasons": reasons,
        "recommendations": recommendations,
        "suspicious_signals": suspicious_signals
    }