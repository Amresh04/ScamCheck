const tabButtons = document.querySelectorAll(".tab-button");
const scanPanels = document.querySelectorAll(".scan-panel");

const scanForm = document.getElementById("scanForm");
const scanTypeInput = document.getElementById("scanType");

const messageInput = document.getElementById("messageInput");
const urlInput = document.getElementById("urlInput");
const imageInput = document.getElementById("imageInput");
const pdfInput = document.getElementById("pdfInput");
const selectedImageName = document.getElementById("selectedImageName");
const selectedPdfName = document.getElementById("selectedPdfName");
const fileUploadBox = document.querySelector(".file-upload-box");

const scanButton = document.getElementById("scanButton");
const scanButtonIcon = document.getElementById("scanButtonIcon");
const scanButtonText = document.getElementById("scanButtonText");

const resultSection = document.getElementById("resultSection");
const riskBadge = document.getElementById("riskBadge");
const scoreCircle = document.getElementById("scoreCircle");
const riskScore = document.getElementById("riskScore");
const riskTitle = document.getElementById("riskTitle");
const riskSummary = document.getElementById("riskSummary");

const reasonsList = document.getElementById("reasonsList");
const recommendationsList = document.getElementById("recommendationsList");
const reasonsListHi = document.getElementById("reasonsListHi");
const recommendationsListHi = document.getElementById("recommendationsListHi");

const extractedTextCard = document.getElementById("extractedTextCard");
const extractedText = document.getElementById("extractedText");
const rawResponse = document.getElementById("rawResponse");
let currentLanguage = "en";
let latestResult = null;
let latestError = null;

const translations = {
    en: {
        brand: "ScamCheck", tagline: "Check before you trust", independent: "Independent safety tool",
        alertTitle: "Fraud safety alert", alertBody: "A real bank or official will never ask for your OTP, UPI PIN, or password. Do not rush to pay or install an app; verify using a number you already trust.",
        eyebrow: "INDIA · ONLINE SAFETY", heroTitle: "Stop. Check. Then act.", heroBody: "Not sure about a message or link? Check it here before you reply, click, or send money.",
        navHome: "Home", navUrl: "URL", navMessage: "Message", navPdf: "PDF",
        messageHeroTitle: "Check a message", messageHeroBody: "Paste a message or SMS here. We will look for common signs of fraud.",
        urlHeroTitle: "Check a link", urlHeroBody: "Paste a suspicious website address here. We check its address without opening it.",
        pdfHeroTitle: "Check a PDF", pdfHeroBody: "Choose a PDF notice, bill, or offer. We will look at its readable text.",
        imageHeroTitle: "Check a screenshot", imageHeroBody: "Choose a clear picture of a suspicious message to check its text.",
        toolsLabel: "QUICK HELP", toolsTitle: "What would you like to check?", toolsHelp: "Choose one option. We will guide you step by step.",
        homeUrlTitle: "Check a link", homeUrlBody: "Paste a website link that looks suspicious.", homeMessageTitle: "Check a message", homeMessageBody: "Check a text, SMS, or chat message.",
        homePdfTitle: "Check a PDF", homePdfBody: "Choose a notice, bill, or offer PDF.", homeImageTitle: "Check a screenshot", homeImageBody: "Choose a picture of a suspicious message.",
        notOfficial: "An independent public safety tool. This is not an official Government of India website.", tabMessage: "Message", tabLink: "Link", tabImage: "Screenshot", tabPdf: "PDF file",
        messageTitle: "Check a message", messageHelp: "Paste the message you received. You can use Hindi or English.", messageLabel: "Paste message here", messagePlaceholder: "Example: Your bank account will close today. Send your OTP now.", messageNote: "Never paste your real password, OTP, PIN, or bank details.",
        linkTitle: "Check a link", linkHelp: "Paste the full link here. We do not open the link.", linkLabel: "Paste link here", linkNote: "We check the link address without visiting the website.",
        imageTitle: "Check a screenshot", imageHelp: "Choose a clear screenshot of the message. Hindi and English text work best.", imageLabel: "Choose screenshot", imageChoose: "Tap to choose a screenshot", imageLimit: "PNG, JPG or WEBP · Up to 10 MB", imageNote: "Text is read from the screenshot to look for warning signs. Hindi reading needs Hindi OCR language data installed.",
        pdfTitle: "Check a PDF file", pdfHelp: "Choose a PDF message, bill, notice, or offer to check its readable text.", pdfLabel: "Choose PDF file", pdfNote: "PDFs in different languages can be checked. Image-only scanned PDFs cannot be read yet.",
        scanButton: "Check now", languageCapability: "English, Hindi and common Hinglish warnings are checked offline. Other languages need the optional AI service.", privacyNote: "If AI checking is enabled, text you submit may be sent to Google. Do not enter passwords, OTPs, or bank details.", reportLabel: "YOUR CHECK RESULT", reportTitle: "Safety check", waiting: "Ready to check", waitingHelp: "Your result and next steps will appear here.", scoreDescription: "A higher score means more warning signs were found. It does not prove a scam.", whyResult: "Why are we showing this?", nextSteps: "What should I do?", extractedTitle: "Text read from your file", technical: "View technical details",
        tipsLabel: "STAY SAFE", tipsTitle: "Simple ways to avoid online fraud", footerBrand: "ScamCheck · Independent online safety tool", footerDisclaimer: "This tool can miss fraud. When in doubt, do not click or send money."
    },
    hi: {
        brand: "ScamCheck", tagline: "भरोसा करने से पहले जांचें", independent: "स्वतंत्र सुरक्षा टूल",
        alertTitle: "धोखाधड़ी से सावधान", alertBody: "बैंक या सरकारी अधिकारी बनकर कोई फोन करे तब भी OTP, UPI PIN या पासवर्ड न बताएं। पैसे भेजने की जल्दी न करें। पहले पुराने या आधिकारिक नंबर से खुद पुष्टि करें।",
        eyebrow: "भारत · ऑनलाइन सुरक्षा", heroTitle: "रुकें। जांचें। फिर कदम उठाएं।", heroBody: "किसी संदेश या लिंक पर शक है? जवाब देने, खोलने या पैसे भेजने से पहले यहां जांचें।",
        navHome: "मुख्य पृष्ठ", navUrl: "लिंक", navMessage: "संदेश", navPdf: "PDF",
        messageHeroTitle: "संदेश की जांच करें", messageHeroBody: "संदेश या SMS यहां डालें। हम धोखाधड़ी के आम संकेत देखेंगे।",
        urlHeroTitle: "लिंक की जांच करें", urlHeroBody: "संदेह वाला वेबसाइट पता यहां डालें। हम उसे खोले बिना जांचते हैं।",
        pdfHeroTitle: "PDF की जांच करें", pdfHeroBody: "नोटिस, बिल या ऑफर की PDF चुनें। हम उसमें लिखे शब्दों की जांच करेंगे।",
        imageHeroTitle: "स्क्रीनशॉट की जांच करें", imageHeroBody: "संदेह वाले संदेश की साफ तस्वीर चुनें। हम उसमें लिखे शब्द जांचेंगे।",
        toolsLabel: "जल्दी मदद", toolsTitle: "आप क्या जांचना चाहते हैं?", toolsHelp: "एक विकल्प चुनें। हम आसान तरीके से मदद करेंगे।",
        homeUrlTitle: "लिंक जांचें", homeUrlBody: "संदेह वाला वेबसाइट लिंक डालें।", homeMessageTitle: "संदेश जांचें", homeMessageBody: "SMS या चैट में मिले संदेश की जांच करें।",
        homePdfTitle: "PDF जांचें", homePdfBody: "नोटिस, बिल या ऑफर की PDF चुनें।", homeImageTitle: "स्क्रीनशॉट जांचें", homeImageBody: "संदेह वाले संदेश की तस्वीर चुनें।",
        notOfficial: "यह एक स्वतंत्र जन-जागरूकता टूल है। यह भारत सरकार की आधिकारिक वेबसाइट नहीं है।", tabMessage: "संदेश", tabLink: "लिंक", tabImage: "स्क्रीनशॉट", tabPdf: "PDF फ़ाइल",
        messageTitle: "संदेश की जांच करें", messageHelp: "आपको मिला संदेश यहां डालें। हिंदी या अंग्रेज़ी में लिख सकते हैं।", messageLabel: "संदेश यहां डालें", messagePlaceholder: "उदाहरण: आपका बैंक खाता बंद हो जाएगा। अभी OTP भेजें।", messageNote: "अपना असली पासवर्ड, OTP, PIN या बैंक की जानकारी यहां न डालें।",
        linkTitle: "लिंक की जांच करें", linkHelp: "पूरा लिंक यहां डालें। हम लिंक को खोलते नहीं हैं।", linkLabel: "लिंक यहां डालें", linkNote: "हम वेबसाइट पर जाए बिना लिंक पते की जांच करते हैं।",
        imageTitle: "स्क्रीनशॉट की जांच करें", imageHelp: "संदेश का साफ स्क्रीनशॉट चुनें। हिंदी और अंग्रेज़ी सबसे अच्छे काम करते हैं।", imageLabel: "स्क्रीनशॉट चुनें", imageChoose: "स्क्रीनशॉट चुनने के लिए यहां दबाएं", imageLimit: "PNG, JPG या WEBP · अधिकतम 10 MB", imageNote: "स्क्रीनशॉट से लिखे शब्द पढ़े जाएंगे। हिंदी पढ़ने के लिए हिंदी OCR भाषा डेटा इंस्टॉल होना चाहिए।",
        pdfTitle: "PDF फ़ाइल की जांच करें", pdfHelp: "संदेश, बिल, नोटिस या ऑफर वाली PDF चुनें।", pdfLabel: "PDF फ़ाइल चुनें", pdfNote: "अलग-अलग भाषाओं की PDF जांची जा सकती हैं। फोटो/स्कैन वाली PDF अभी नहीं पढ़ी जा सकती।",
        scanButton: "अभी जांचें", languageCapability: "बिना AI सेवा के हिंदी, अंग्रेज़ी और आम हिंग्लिश संकेत जांचे जाते हैं। दूसरी भाषाओं के लिए वैकल्पिक AI सेवा चाहिए।", privacyNote: "AI जांच चालू होने पर आपका लिखा टेक्स्ट Google को भेजा जा सकता है। पासवर्ड, OTP या बैंक की जानकारी न डालें।", reportLabel: "आपकी जांच का नतीजा", reportTitle: "सुरक्षा जांच", waiting: "जांच के लिए तैयार", waitingHelp: "नतीजा और आगे क्या करना है, यहां दिखेगा।", scoreDescription: "बड़ा नंबर मतलब ज्यादा खतरे के संकेत मिले। यह धोखाधड़ी का पक्का सबूत नहीं है।", whyResult: "यह नतीजा क्यों दिखा?", nextSteps: "अब मुझे क्या करना चाहिए?", extractedTitle: "फ़ाइल से पढ़ा गया टेक्स्ट", technical: "तकनीकी जानकारी देखें",
        tipsLabel: "सुरक्षित रहें", tipsTitle: "ऑनलाइन धोखाधड़ी से बचने के आसान तरीके", footerBrand: "ScamCheck · स्वतंत्र ऑनलाइन सुरक्षा टूल", footerDisclaimer: "यह टूल हर धोखाधड़ी नहीं पहचान सकता। शक हो तो लिंक न खोलें और पैसे न भेजें।"
    }
};

function applyLanguage(language) {
    currentLanguage = language === "hi" ? "hi" : "en";
    document.documentElement.lang = currentLanguage;
    document.querySelectorAll("[data-i18n]").forEach((element) => {
        const value = translations[currentLanguage][element.dataset.i18n];
        if (value) element.textContent = value;
    });
    document.querySelectorAll("[data-i18n-placeholder]").forEach((element) => {
        const value = translations[currentLanguage][element.dataset.i18nPlaceholder];
        if (value) element.placeholder = value;
    });
    const tips = currentLanguage === "hi" ? [
        ["गुप्त कोड किसी से साझा न करें", "OTP, पासवर्ड, UPI PIN, ATM PIN, CVV या कार्ड नंबर किसी को न बताएं।"],
        ["लिंक खोलने से पहले जांचें", "डर, जल्दी, इनाम या खाता बंद होने की धमकी देने वाले संदेशों से सावधान रहें।"],
        ["आधिकारिक माध्यम अपनाएं", "संदेश के लिंक पर भरोसा करने के बजाय आधिकारिक ऐप खोलें या वेबसाइट खुद लिखें।"],
        ["अलग पासवर्ड और दोहरी सुरक्षा रखें", "हर खाते के लिए अलग मजबूत पासवर्ड रखें। अतिरिक्त साइन-इन सुरक्षा चालू करें और अनजान अनुरोध मंजूर न करें।"],
        ["पैसे भेजने से पहले रुकें", "भुगतान की मांग की पुष्टि पुराने/पहचाने हुए नंबर पर करें। इनाम या नौकरी पाने के लिए फीस न दें।"],
        ["फोन और कंप्यूटर अपडेट रखें", "सुरक्षा अपडेट लगाएं, स्क्रीन लॉक रखें और अनजान फाइलें न खोलें।"],
        ["भेजने वाले और लिंक को जांचें", "वेबसाइट के नाम की वर्तनी देखें। ताला निशान या लोगो अकेले भरोसे का सबूत नहीं है।"],
        ["धोखा हो जाए तो जल्दी कदम उठाएं", "बातचीत रोकें। पैसे या खाते का खतरा हो तो बैंक को उसके आधिकारिक नंबर से बताएं और संदेश रिपोर्ट करें।"]
    ] : [
        ["Never share secret codes", "Never share an OTP, password, UPI PIN, ATM PIN, CVV, or card number."],
        ["Check before opening links", "Be careful with messages that create fear, urgency, prizes, or account-blocking threats."],
        ["Use official channels", "Open the official app or type its website yourself instead of trusting a message link."],
        ["Use different passwords and two-step security", "Use a strong, different password for each account. Turn on extra sign-in checks and deny sign-ins you did not start."],
        ["Pause before sending money", "Verify payment requests using a number you already know. Never pay to receive a prize or job."],
        ["Keep your devices updated", "Install security updates, use a screen lock, and do not open unexpected files."],
        ["Check the sender and link", "Check the spelling of website names. A padlock or familiar logo alone does not prove it is genuine."],
        ["Act quickly if you are targeted", "Stop replying. If money or an account is at risk, contact your bank using its official number and report the message."]
    ];
    document.querySelectorAll(".tip-card").forEach((card, index) => {
        card.querySelector("h3").textContent = tips[index][0];
        card.querySelector("p").textContent = tips[index][1];
    });
    const toggle = document.getElementById("languageToggle");
    toggle.textContent = currentLanguage === "en" ? "हिन्दी" : "English";
    toggle.setAttribute("aria-label", currentLanguage === "en" ? "हिन्दी में देखें" : "View in English");
    document.querySelector('[role="tablist"]').setAttribute("aria-label", currentLanguage === "en" ? "Choose what you want to check" : "क्या जांचना है चुनें");
    if (scanForm.getAttribute("aria-busy") !== "true") {
        scanButtonText.textContent = scanTypeInput.value === "pdf"
            ? (currentLanguage === "hi" ? "PDF जांचें" : "Check PDF")
            : translations[currentLanguage].scanButton;
    }
    renderLocalizedResults();
    if (latestError) renderLocalizedError();
}

document.getElementById("languageToggle").addEventListener("click", () => {
    applyLanguage(currentLanguage === "en" ? "hi" : "en");
});
applyLanguage("en");


tabButtons.forEach((button) => {
    button.addEventListener("click", () => {
        const selectedTab = button.dataset.tab;

        tabButtons.forEach((tab) => {
            tab.classList.remove("active");
            tab.setAttribute("aria-selected", "false");
            tab.tabIndex = -1;
        });

        scanPanels.forEach((panel) => {
            panel.classList.remove("active");
            panel.hidden = true;
        });

        button.classList.add("active");
        button.setAttribute("aria-selected", "true");
        button.tabIndex = 0;

        const selectedPanel = document.getElementById(`${selectedTab}Panel`);

        if (selectedPanel) {
            selectedPanel.classList.add("active");
            selectedPanel.hidden = false;
        }

        scanTypeInput.value = selectedTab;

        if (selectedTab === "pdf") {
            scanButton.disabled = false;
            scanButtonIcon.textContent = "📄";
            scanButtonText.textContent = currentLanguage === "hi" ? "PDF जांचें" : "Check PDF";
        } else {
            scanButton.disabled = false;
            scanButtonIcon.textContent = "🔍";
            scanButtonText.textContent = translations[currentLanguage].scanButton;
        }
    });

    button.addEventListener("keydown", (event) => {
        const currentIndex = Array.from(tabButtons).indexOf(button);
        let nextIndex = currentIndex;
        if (event.key === "ArrowRight" || event.key === "ArrowDown") {
            nextIndex = (currentIndex + 1) % tabButtons.length;
        } else if (event.key === "ArrowLeft" || event.key === "ArrowUp") {
            nextIndex = (currentIndex - 1 + tabButtons.length) % tabButtons.length;
        } else if (event.key === "Home") {
            nextIndex = 0;
        } else if (event.key === "End") {
            nextIndex = tabButtons.length - 1;
        } else {
            return;
        }
        event.preventDefault();
        tabButtons[nextIndex].click();
        tabButtons[nextIndex].focus();
    });
});


imageInput.addEventListener("change", () => {
    if (imageInput.files.length > 0) {
        const file = imageInput.files[0];

        selectedImageName.textContent =
            currentLanguage === "hi"
                ? `चुनी गई तस्वीर: ${file.name} (${formatFileSize(file.size)})`
                : `Selected image: ${file.name} (${formatFileSize(file.size)})`;
    } else {
        selectedImageName.textContent = "";
    }
});

pdfInput.addEventListener("change", () => {
    selectedPdfName.textContent = pdfInput.files.length ? pdfInput.files[0].name : "";
});

["dragenter", "dragover"].forEach((eventName) => {
    fileUploadBox.addEventListener(eventName, (event) => {
        event.preventDefault();
        fileUploadBox.classList.add("is-dragging");
    });
});

["dragleave", "drop"].forEach((eventName) => {
    fileUploadBox.addEventListener(eventName, (event) => {
        event.preventDefault();
        fileUploadBox.classList.remove("is-dragging");
    });
});

fileUploadBox.addEventListener("drop", (event) => {
    const [file] = event.dataTransfer.files;
    if (!file) return;

    const transfer = new DataTransfer();
    transfer.items.add(file);
    imageInput.files = transfer.files;
    imageInput.dispatchEvent(new Event("change", { bubbles: true }));
});


scanForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const scanType = scanTypeInput.value;

    if (!validateInput(scanType)) {
        return;
    }

    const formData = new FormData(scanForm);

    setLoadingState(true);

    if (scanType === "pdf") {
        showTemporaryResult(
            currentLanguage === "hi" ? "PDF की जांच हो रही है" : "Checking the PDF",
            currentLanguage === "hi" ? "फ़ाइल के लिखे हुए शब्द पढ़े जा रहे हैं।" : "We are reading the text in your file."
        );
    } else {
        showTemporaryResult(
            currentLanguage === "hi" ? "जांच हो रही है" : "Checking this content",
            currentLanguage === "hi" ? "धोखाधड़ी के संकेत देखे जा रहे हैं।" : "We are checking for common fraud warning signs."
        );
    }

    const controller = new AbortController();
    const timeout = window.setTimeout(() => controller.abort(), 60000);

    try {
        const response = await fetch("/scan", {
            method: "POST",
            body: formData,
            signal: controller.signal
        });
        window.clearTimeout(timeout);

        let data;

        try {
            data = await response.json();
        } catch (jsonError) {
            throw new Error(
                "The server did not return valid JSON. Check the Flask terminal for an error."
            );
        }

        if (!response.ok || !data.success) {
            throw new Error(data.error || "The scan could not be completed.");
        }

        displayResult(data);
    } catch (error) {
        displayError(error.name === "AbortError"
            ? "The scan took too long. Please try again with a smaller image or shorter message."
            : (error.message || "The scan could not be completed."));
    } finally {
        window.clearTimeout(timeout);
        setLoadingState(false);
    }
});


function validateInput(scanType) {
    if (scanType === "message" && !messageInput.value.trim()) {
        displayError("Please enter a message before scanning.");
        return false;
    }

    if (scanType === "url" && !urlInput.value.trim()) {
        displayError("Please enter a URL before scanning.");
        return false;
    }

    if (scanType === "image" && imageInput.files.length === 0) {
        displayError("Please select an image before scanning.");
        return false;
    }

    if (scanType === "image" && imageInput.files[0].size > 10 * 1024 * 1024) {
        displayError(currentLanguage === "hi" ? "तस्वीर 10 MB या उससे छोटी चुनें।" : "Choose an image that is 10 MB or smaller.");
        return false;
    }

    if (scanType === "pdf" && !pdfInput.files.length) {
        displayError(currentLanguage === "hi" ? "पहले PDF फ़ाइल चुनें।" : "Choose a PDF file first.");
        return false;
    }
    if (scanType === "pdf" && pdfInput.files[0].size > 10 * 1024 * 1024) {
        displayError(currentLanguage === "hi" ? "PDF फ़ाइल 10 MB या उससे छोटी चुनें।" : "Choose a PDF file that is 10 MB or smaller.");
        return false;
    }

    return true;
}


function setLoadingState(isLoading) {
    scanButton.disabled = isLoading;
    scanForm.setAttribute("aria-busy", String(isLoading));

    if (isLoading) {
        scanButtonIcon.textContent = "⏳";
        scanButtonText.textContent = currentLanguage === "hi" ? "जांच हो रही है…" : "Checking…";
    } else if (scanTypeInput.value === "pdf") {
        scanButtonIcon.textContent = "📄";
        scanButtonText.textContent = currentLanguage === "hi" ? "PDF जांचें" : "Check PDF";
    } else {
        scanButtonIcon.textContent = "🔍";
        scanButtonText.textContent = translations[currentLanguage].scanButton;
    }
}


function showTemporaryResult(title, summary) {
    latestResult = null;
    latestError = null;
    resultSection.classList.remove("hidden");

    riskBadge.textContent = "Scanning";
    riskBadge.className = "risk-badge scanning";

    scoreCircle.className = "score-circle safe";

    riskScore.textContent = "...";
    riskTitle.textContent = title;
    riskSummary.textContent = summary;

    updateList(reasonsList, ["Please wait while the check is in progress."]);
    updateList(recommendationsList, ["Do not click the link or send money while the check is in progress."]);
    updateList(reasonsListHi, ["जांच पूरी होने तक रुकें।"]);
    updateList(recommendationsListHi, ["जांच पूरी होने तक लिंक न खोलें और पैसे न भेजें।"]);
    reasonsList.classList.toggle("hidden", currentLanguage === "hi");
    recommendationsList.classList.toggle("hidden", currentLanguage === "hi");
    reasonsListHi.classList.toggle("hidden", currentLanguage !== "hi");
    recommendationsListHi.classList.toggle("hidden", currentLanguage !== "hi");

    extractedTextCard.classList.add("hidden");
    rawResponse.textContent = "";

    resultSection.scrollIntoView({
        behavior: "smooth",
        block: "start"
    });
}


function displayResult(data) {
    const finalResult = data.final_result || {};
    latestResult = { data, finalResult };
    latestError = null;

    const score = getScore(finalResult);
    const level = getRiskLevel(finalResult, score);

    const reasons = getArrayValue(finalResult, [
        "reasons",
        "risk_reasons",
        "warnings"
    ]);

    const recommendations = getArrayValue(finalResult, [
        "recommendations",
        "advice",
        "suggestions"
    ]);

    riskScore.textContent = score;
    riskTitle.textContent = localizedRisk(level);
    riskSummary.textContent = currentLanguage === "hi"
        ? (finalResult.explanation_hi || summaryHindi(score))
        : buildSummary(data, finalResult, level, score);

    setRiskVisuals(level, score);

    updateList(
        reasonsList,
        reasons.length > 0
            ? reasons
            : ["The scan completed, but no detailed risk reasons were returned."]
    );

    updateList(
        recommendationsList,
        recommendations.length > 0
            ? recommendations
            : getDefaultRecommendations(level)
    );

    if (["image", "pdf"].includes(data.scan_type) && data.extracted_text) {
        extractedText.textContent = data.extracted_text;
        extractedTextCard.classList.remove("hidden");
    } else {
        extractedText.textContent = "";
        extractedTextCard.classList.add("hidden");
    }

    rawResponse.textContent = JSON.stringify(data, null, 2);
    renderLocalizedResults();

    resultSection.classList.remove("hidden");

    resultSection.scrollIntoView({
        behavior: "smooth",
        block: "start"
    });
}


function displayError(message) {
    latestResult = null;
    latestError = message;
    resultSection.classList.remove("hidden");

    riskBadge.textContent = currentLanguage === "hi" ? "त्रुटि" : "Error";
    riskBadge.className = "risk-badge error";

    scoreCircle.className = "score-circle error";

    riskScore.textContent = "!";
    riskTitle.textContent = currentLanguage === "hi" ? "जांच पूरी नहीं हो सकी" : "The check could not be completed";
    riskSummary.textContent = currentLanguage === "hi" ? (translateKnownError(message) || `जांच नहीं हो सकी: ${message}`) : message;

    updateList(reasonsList, [message]);

    updateList(recommendationsList, [
        "Check your connection and try again.",
        "For images, use a clear PNG, JPG, or WEBP file smaller than 10 MB.",
        "Avoid sharing sensitive information while troubleshooting."
    ]);
    updateList(reasonsListHi, [translateKnownError(message) || "जांच पूरी नहीं हो सकी। कृपया फिर कोशिश करें।"]);
    updateList(recommendationsListHi, ["लिंक न खोलें और पैसे न भेजें।", "फाइल या जानकारी दोबारा जांचकर फिर कोशिश करें।"]);

    extractedTextCard.classList.add("hidden");
    rawResponse.textContent = "";
    renderLocalizedError();
}

function renderLocalizedError() {
    if (!latestError) return;
    const showHindi = currentLanguage === "hi";
    riskBadge.textContent = showHindi ? "त्रुटि" : "Error";
    riskTitle.textContent = showHindi ? "जांच पूरी नहीं हो सकी" : "The check could not be completed";
    riskSummary.textContent = showHindi ? translateKnownError(latestError) : latestError;
    reasonsList.classList.toggle("hidden", showHindi);
    recommendationsList.classList.toggle("hidden", showHindi);
    reasonsListHi.classList.toggle("hidden", !showHindi);
    recommendationsListHi.classList.toggle("hidden", !showHindi);
}


function getScore(result) {
    const possibleKeys = ["risk_score", "score", "final_score", "risk"];

    for (const key of possibleKeys) {
        const value = result[key];

        if (typeof value === "number") {
            return Math.max(0, Math.min(100, Math.round(value)));
        }

        if (typeof value === "string" && value.trim() !== "") {
            const numericValue = Number(value);

            if (!Number.isNaN(numericValue)) {
                return Math.max(0, Math.min(100, Math.round(numericValue)));
            }
        }
    }

    return 0;
}


function getRiskLevel(result, score) {
    const possibleKeys = [
        "risk_level",
        "label",
        "status",
        "assessment",
        "verdict"
    ];

    for (const key of possibleKeys) {
        if (result[key]) {
            return String(result[key]);
        }
    }

    if (score >= 70) {
        return "High Risk";
    }

    if (score >= 40) {
        return "Suspicious";
    }

    return "Safe";
}


function getArrayValue(result, keys) {
    for (const key of keys) {
        const value = result[key];

        if (Array.isArray(value)) {
            return value
                .map((item) => String(item).trim())
                .filter((item) => item !== "");
        }

        if (typeof value === "string" && value.trim()) {
            return [value.trim()];
        }
    }

    return [];
}


function buildSummary(data, finalResult, level, score) {
    if (finalResult.safety_message) {
        return finalResult.safety_message;
    }

    if (data.scan_type === "message") {
        return `The message was assessed as ${level} with a risk score of ${score}/100.`;
    }

    if (data.scan_type === "url") {
        const domain = data.url_result && data.url_result.domain
            ? ` Domain checked: ${data.url_result.domain}.`
            : "";

        return `The submitted URL was assessed as ${level} with a risk score of ${score}/100.${domain}`;
    }

    if (data.scan_type === "image") {
        return `Text was extracted from the image and assessed as ${level} with a risk score of ${score}/100.`;
    }

    if (data.scan_type === "pdf") {
        return `Text was read from the PDF and assessed as ${level} with a risk score of ${score}/100.`;
    }

    return `ScamCheck found a ${level} rating with a risk score of ${score}/100.`;
}


function setRiskVisuals(level, score) {
    const normalizedLevel = level.toLowerCase();

    let circleClass = "safe";

    if (
        score >= 70 ||
        normalizedLevel.includes("high") ||
        normalizedLevel.includes("danger")
    ) {
        circleClass = "high-risk";
    } else if (
        score >= 40 ||
        normalizedLevel.includes("suspicious") ||
        normalizedLevel.includes("medium")
    ) {
        circleClass = "suspicious";
    }

    riskBadge.textContent = localizedRisk(level);
    riskBadge.className = `risk-badge ${circleClass}`;

    scoreCircle.className = `score-circle ${circleClass}`;
}

function localizedRisk(level) {
    if (currentLanguage !== "hi") return level;
    if (level.toLowerCase().includes("high")) return "खतरा ज्यादा";
    if (level.toLowerCase().includes("suspicious")) return "सावधानी रखें";
    return "कम खतरे के संकेत";
}

function summaryHindi(score) {
    if (score >= 70) return "कई गंभीर खतरे के संकेत मिले हैं। लिंक न खोलें, पैसे न भेजें और कोई गुप्त जानकारी न दें।";
    if (score >= 40) return "कुछ संदेह के संकेत मिले हैं। आगे बढ़ने से पहले आधिकारिक नंबर या ऐप से पुष्टि करें।";
    return "जांच में कम खतरे के संकेत मिले हैं। इसका मतलब पूरी सुरक्षा की गारंटी नहीं है; सावधान रहें।";
}

function renderLocalizedResults() {
    if (!latestResult) return;
    const { data, finalResult } = latestResult;
    const showHindi = currentLanguage === "hi";
    const englishReasons = getArrayValue(finalResult, ["reasons", "risk_reasons", "warnings"]);
    const englishAdvice = getArrayValue(finalResult, ["recommendations", "advice", "suggestions"]);
    const hindiReasons = getArrayValue(finalResult, ["reasons_hi"]);
    const hindiAdvice = getArrayValue(finalResult, ["recommendations_hi"]);
    reasonsList.classList.toggle("hidden", showHindi);
    recommendationsList.classList.toggle("hidden", showHindi);
    reasonsListHi.classList.toggle("hidden", !showHindi);
    recommendationsListHi.classList.toggle("hidden", !showHindi);
    updateList(reasonsList, englishReasons.length ? englishReasons : ["No detailed warning signs were returned."]);
    updateList(recommendationsList, englishAdvice.length ? englishAdvice : getDefaultRecommendations(getRiskLevel(finalResult, getScore(finalResult))));
    updateList(reasonsListHi, hindiReasons.length ? hindiReasons : ["कुछ जोखिम संकेतों की जांच की गई। संदेह हो तो कार्रवाई से पहले पुष्टि करें।"]);
    updateList(recommendationsListHi, hindiAdvice.length ? hindiAdvice : ["OTP, PIN, पासवर्ड या बैंक की जानकारी किसी को न बताएं।", "भुगतान या लिंक पर कार्रवाई से पहले आधिकारिक माध्यम से पुष्टि करें।"]);
    riskTitle.textContent = localizedRisk(getRiskLevel(finalResult, getScore(finalResult)));
    riskSummary.textContent = showHindi
        ? (finalResult.explanation_hi || summaryHindi(getScore(finalResult)))
        : buildSummary(data, finalResult, getRiskLevel(finalResult, getScore(finalResult)), getScore(finalResult));
    riskBadge.textContent = localizedRisk(getRiskLevel(finalResult, getScore(finalResult)));
}

function translateKnownError(message) {
    const known = {
        "Please enter a message before scanning.": "जांचने के लिए संदेश यहां डालें।",
        "Please enter a URL before scanning.": "जांचने के लिए लिंक यहां डालें।",
        "Please select an image before scanning.": "पहले स्क्रीनशॉट चुनें।",
        "Choose a PDF file first.": "पहले PDF फ़ाइल चुनें।",
        "PDF files must be 10 MB or smaller.": "PDF फ़ाइल 10 MB या उससे छोटी होनी चाहिए।",
        "The scan could not be completed. Please try again later.": "जांच पूरी नहीं हो सकी। थोड़ी देर बाद फिर कोशिश करें।",
        "This file does not look like a valid PDF.": "यह सही PDF फ़ाइल नहीं लगती।",
        "This PDF could not be opened. Please choose a valid, non-damaged PDF.": "यह PDF नहीं खुली। सही और बिना खराबी वाली फ़ाइल चुनें।"
    };
    return known[message] || "जांच पूरी नहीं हो सकी। कृपया सही संदेश या फ़ाइल चुनकर फिर कोशिश करें।";
}


function getDefaultRecommendations(level) {
    const normalizedLevel = level.toLowerCase();

    if (
        normalizedLevel.includes("high") ||
        normalizedLevel.includes("danger")
    ) {
        return [
            "Do not click links, open attachments, or reply to the sender.",
            "Do not share OTP, password, PIN, CVV, card number, bank details, or UPI PIN.",
            "Verify using the organization’s official website, app, or customer-care number.",
            "Block and report suspicious senders or messages."
        ];
    }

    if (
        normalizedLevel.includes("suspicious") ||
        normalizedLevel.includes("medium")
    ) {
        return [
            "Verify the message or link independently before taking action.",
            "Do not enter personal, financial, or login information.",
            "Use official apps or manually typed official websites."
        ];
    }

    return [
        "No strong warning signs were found, but stay cautious.",
        "Never share secret security codes or financial information.",
        "Verify unexpected requests through official channels."
    ];
}


function updateList(listElement, items) {
    listElement.replaceChildren();

    items.forEach((item) => {
        const listItem = document.createElement("li");
        listItem.textContent = item;
        listElement.appendChild(listItem);
    });
}


function formatFileSize(bytes) {
    if (bytes < 1024) {
        return `${bytes} bytes`;
    }

    if (bytes < 1024 * 1024) {
        return `${(bytes / 1024).toFixed(1)} KB`;
    }

    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}
