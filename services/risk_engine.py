import re


HINDI_REASON_TRANSLATIONS = {
    "The message requests an OTP, verification code, or security code.": "संदेश में OTP या गुप्त कोड मांगा गया है।",
    "The message requests sensitive login, card, or banking information.": "संदेश में पासवर्ड, PIN या बैंक/कार्ड की जानकारी मांगी गई है।",
    "The message uses urgency or pressure tactics.": "संदेश में जल्दी करने का दबाव बनाया गया है।",
    "The message threatens account blocking, suspension, or closure.": "संदेश में खाता बंद या ब्लॉक होने की धमकी दी गई है।",
    "The message asks you to click a link or verify account details.": "संदेश में लिंक खोलने या खाते की जानकारी देने को कहा गया है।",
    "The message contains a lottery, prize, reward, or winner claim.": "संदेश में इनाम या लॉटरी जीतने का दावा है।",
    "The message mentions KYC verification, which is commonly used in scams.": "संदेश में KYC अपडेट करने को कहा गया है। पहले आधिकारिक माध्यम से पुष्टि करें।",
    "The message includes a payment, UPI, transfer, or fee request.": "संदेश में पैसे भेजने या भुगतान करने को कहा गया है।",
    "The message contains a web link that should be verified.": "संदेश में एक लिंक है। उसे खोलने से पहले जांचें।",
    "The URL uses HTTP instead of encrypted HTTPS.": "इस लिंक में सुरक्षित HTTPS के बजाय HTTP है।",
    "The URL contains '@', which can hide the real destination domain.": "इस लिंक में @ का निशान है, जो असली वेबसाइट का पता छिपा सकता है।",
    "The URL uses an IP address instead of a normal domain name.": "यह लिंक सामान्य वेबसाइट नाम के बजाय IP पते का उपयोग करता है।",
    "The domain uses punycode, which can sometimes imitate trusted websites.": "वेबसाइट का नाम नकली वेबसाइट जैसा दिख सकता है। ध्यान से जांचें।",
    "The domain name is unusually long.": "वेबसाइट का पता असामान्य रूप से लंबा है।",
    "The URL has many subdomains, which can hide the real domain.": "इस लिंक में कई उप-डोमेन हैं; असली वेबसाइट का पता ध्यान से देखें।",
    "The URL is unusually long.": "यह लिंक असामान्य रूप से लंबा है।",
    "The URL uses a shortened-link service, so the final destination is hidden.": "यह छोटा लिंक है और खोलने से पहले असली वेबसाइट का पता नहीं दिखता।",
    "The URL contains unusual characters.": "वेबसाइट के पते में अजीब अक्षर हैं।",
    "The URL uses an unsupported or potentially unsafe protocol.": "यह लिंक असुरक्षित तरीके का उपयोग कर सकता है। इसे न खोलें।",
    "The URL does not contain a valid website domain.": "इस लिंक में वेबसाइट का सही पता नहीं मिला।",
    "The URL format could not be read safely.": "लिंक का पता सुरक्षित तरीके से पढ़ा नहीं जा सका।",
    "The domain matches a known trusted-domain pattern.": "वेबसाइट का नाम एक जाने-पहचाने डोमेन जैसा है, लेकिन फिर भी सावधान रहें।"
}


def translate_reasons_to_hindi(reasons):
    return list(dict.fromkeys(
        HINDI_REASON_TRANSLATIONS[reason]
        for reason in reasons
        if reason in HINDI_REASON_TRANSLATIONS
    ))


def get_risk_level(score):
    if score >= 70:
        return "High Risk"
    if score >= 40:
        return "Suspicious"
    return "Safe"


def ensure_list(value):
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]

    if isinstance(value, str) and value.strip():
        return [value.strip()]

    return []


def extract_score(result):
    if not isinstance(result, dict):
        return 0

    value = result.get(
        "risk_score",
        result.get("score", result.get("final_score", 0))
    )

    try:
        return max(0, min(100, int(float(value))))
    except (ValueError, TypeError):
        return 0


def extract_reasons(result):
    if not isinstance(result, dict):
        return []

    reasons = []

    for key in ["reasons", "risk_reasons", "warnings", "explanation_en"]:
        value = result.get(key)
        for item in ensure_list(value):
            if item not in reasons:
                reasons.append(item)

    return reasons


def extract_recommendations(result):
    if not isinstance(result, dict):
        return []

    recommendations = []

    for key in ["recommendations", "advice", "suggestions"]:
        value = result.get(key)
        for item in ensure_list(value):
            if item not in recommendations:
                recommendations.append(item)

    return recommendations


def analyze_message(text):
    """
    Simple local message analysis.
    This supports the AI analyzer and also works when no Gemini API key exists.
    """
    normalized_text = (text or "").lower()

    if not normalized_text.strip():
        return {
            "risk_score": 0,
            "risk_level": "Safe",
            "reasons": ["No text was provided for message analysis."],
            "reasons_hi": ["जांच के लिए कोई संदेश नहीं दिया गया।"],
            "recommendations": ["Enter text before scanning."]
        }

    score = 0
    reasons = []

    rule_groups = [
        (
            ["otp", "one time password", "verification code", "ओटीपी", "वन टाइम पासवर्ड", "सत्यापन कोड", "गुप्त कोड"],
            35,
            "The message requests an OTP, verification code, or security code."
        ),
        (
            ["password", "pin", "cvv", "card number", "atm card", "पासवर्ड", "पिन", "सीवीवी", "कार्ड नंबर", "एटीएम कार्ड"],
            30,
            "The message requests sensitive login, card, or banking information."
        ),
        (
            ["urgent", "immediately", "act now", "last chance", "within 24 hours", "तुरंत", "अभी", "जल्दी करें", "आज ही", "अंतिम मौका", "abhi turant", "jaldi karo", "last chance"],
            15,
            "The message uses urgency or pressure tactics."
        ),
        (
            ["account blocked", "account suspended", "account will be closed", "खाता बंद", "खाता ब्लॉक", "खाता निलंबित", "बैंक खाता बंद", "khata band", "account band ho jayega", "sim band", "सिम बंद", "बिजली कटेगी"],
            20,
            "The message threatens account blocking, suspension, or closure."
        ),
        (
            ["click here", "click the link", "open the link", "verify your account", "यहां क्लिक", "लिंक खोलें", "खाता सत्यापित", "वेरिफाई करें", "link kholo", "verify karo"],
            15,
            "The message asks you to click a link or verify account details."
        ),
        (
            ["lottery", "winner", "claim reward", "claim prize", "you have won", "लॉटरी", "इनाम", "पुरस्कार", "आप जीत गए", "ईनाम", "inaam", "aap jeet gaye"],
            20,
            "The message contains a lottery, prize, reward, or winner claim."
        ),
        (
            ["kyc update", "update kyc", "complete kyc", "केवाईसी अपडेट", "केवाईसी पूरा", "केवाईसी अपडेट करें"],
            15,
            "The message mentions KYC verification, which is commonly used in scams."
        ),
        (
            ["upi", "send money", "transfer money", "processing fee", "refund fee", "पैसे भेजें", "भुगतान करें", "पैसा ट्रांसफर", "रिफंड शुल्क", "यूपीआई पिन", "paise bheje", "paisa transfer", "payment karo", "fees do"],
            15,
            "The message includes a payment, UPI, transfer, or fee request."
        )
    ]

    for keywords, points, reason in rule_groups:
        if any(keyword in normalized_text for keyword in keywords):
            score += points
            reasons.append(reason)

    if re.search(r"(https?://|www\.)", normalized_text):
        score += 10
        reasons.append("The message contains a web link that should be verified.")

    score = min(score, 100)
    risk_level = get_risk_level(score)

    if risk_level == "High Risk":
        recommendations = [
            "Do not click links or download files from this message.",
            "Do not share OTP, password, PIN, CVV, card details, or bank details.",
            "Verify through an official website or official customer-care number.",
            "Block and report the sender if the message is unsolicited."
        ]
    elif risk_level == "Suspicious":
        recommendations = [
            "Verify the message independently before taking any action.",
            "Use an official website or app rather than opening the message link.",
            "Do not share personal, banking, or login information."
        ]
    else:
        recommendations = [
            "No strong suspicious message patterns were found.",
            "Continue following normal cyber-safety practices."
        ]

    if not reasons:
        reasons = ["No strong message-based scam indicators were found."]

    reasons_hi = [HINDI_REASON_TRANSLATIONS[reason] for reason in reasons if reason in HINDI_REASON_TRANSLATIONS]
    if not reasons_hi:
        reasons_hi = ["जांच में धोखाधड़ी के स्पष्ट संकेत नहीं मिले, फिर भी सावधान रहें।"]

    if risk_level == "High Risk":
        recommendations_hi = [
            "लिंक न खोलें और पैसे न भेजें।",
            "OTP, PIN, पासवर्ड या बैंक की जानकारी किसी को न बताएं।",
            "बैंक या संस्था से उसके आधिकारिक नंबर पर पुष्टि करें।"
        ]
    elif risk_level == "Suspicious":
        recommendations_hi = [
            "कुछ भी करने से पहले संदेश भेजने वाले की पुष्टि करें।",
            "लिंक से मिली वेबसाइट पर निजी या बैंक की जानकारी न डालें।"
        ]
    else:
        recommendations_hi = [
            "गुप्त कोड या बैंक की जानकारी किसी को न बताएं।",
            "अचानक आए संदेश की आधिकारिक माध्यम से पुष्टि करें।"
        ]

    return {
        "risk_score": score,
        "risk_level": risk_level,
        "reasons": reasons,
        "reasons_hi": reasons_hi,
        "recommendations": recommendations,
        "recommendations_hi": recommendations_hi
    }


def compute_final_risk(ai_result=None, message_result=None, url_result=None):
    """
    Combines results from:
    - ai_analyzer.py
    - analyze_message()
    - url_checker.py

    Returns one final result for the CyberSaathi frontend.
    """
    ai_result = ai_result if isinstance(ai_result, dict) else {}
    message_result = message_result if isinstance(message_result, dict) else {}
    url_result = url_result if isinstance(url_result, dict) else {}

    ai_score = extract_score(ai_result)
    message_score = extract_score(message_result)
    url_score = extract_score(url_result)

    available_scores = [ai_score, message_score]

    if url_result:
        available_scores.append(url_score)

    highest_score = max(available_scores) if available_scores else 0
    average_score = round(sum(available_scores) / len(available_scores)) if available_scores else 0

    final_score = max(highest_score, average_score)

    if ai_score >= 70 and message_score >= 70:
        final_score = min(100, final_score + 10)

    if url_result and url_score >= 70:
        final_score = min(100, final_score + 10)

    final_score = max(0, min(100, final_score))
    risk_level = get_risk_level(final_score)

    reasons = []
    recommendations = []

    for result in [ai_result, message_result, url_result]:
        for reason in extract_reasons(result):
            if reason not in reasons:
                reasons.append(reason)

        for recommendation in extract_recommendations(result):
            if recommendation not in recommendations:
                recommendations.append(recommendation)

    if not reasons:
        reasons = ["No strong cyber-risk signals were detected."]

    if not recommendations:
        recommendations = [
            "Do not share OTPs, passwords, PINs, CVV numbers, or bank details.",
            "Verify unexpected messages and links through official channels."
        ]

    if risk_level == "High Risk":
        safety_message = (
            "High-risk indicators were detected. Do not interact with this content "
            "until you verify it through an official source."
        )
    elif risk_level == "Suspicious":
        safety_message = (
            "Some suspicious indicators were detected. Verify the content "
            "independently before clicking links or sharing information."
        )
    else:
        safety_message = (
            "No strong risk indicators were detected. This is not a guarantee of safety, "
            "so remain careful with unexpected requests."
        )

    return {
        "risk_score": final_score,
        "risk_level": risk_level,
        "reasons": reasons[:10],
        "recommendations": recommendations[:8],
        "safety_message": safety_message,
        "component_scores": {
            "ai_analysis": ai_score,
            "message_analysis": message_score,
            "url_analysis": url_score if url_result else None
        }
    }
