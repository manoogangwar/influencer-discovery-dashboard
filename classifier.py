import re

ORIENTATION_KEYWORDS = [
    "government",
    "government schemes",
    "pm yojana",
    "digital india",
    "make in india",
    "startup india",
    "skill india",
    "viksit bharat",
    "national development",
    "atmanirbhar bharat",
]


def normalize_text(value):
    text = str(value or "").strip().lower()
    text = re.sub(r"\s+", " ", text)
    return text


def classify_influencer(
    bio,
    influencer_language,
    selected_language,
    selected_orientation,
    selected_niche,
):
    bio_text = normalize_text(bio)
    selected_language = normalize_text(selected_language)
    selected_orientation = normalize_text(selected_orientation)
    selected_niche = normalize_text(selected_niche)
    influencer_language = normalize_text(influencer_language)

    score = 0
    matched_keywords = []

    # ---------- Niche Match (40) ----------
    if selected_niche:
        niche_terms = [term.strip() for term in re.split(r"[,-]", selected_niche) if term.strip()]
        niche_terms = [term for term in niche_terms if term]

        if niche_terms:
            match_count = 0
            for term in niche_terms:
                if term in bio_text:
                    matched_keywords.append(term)
                    match_count += 1

            score += int((match_count / len(niche_terms)) * 40)

    # ---------- Language Match (30) ----------
    if selected_language == "hindi & english":
        score += 30
    elif influencer_language == selected_language and selected_language in {"hindi", "english"}:
        score += 30

    # ---------- Orientation Match (30) ----------
    if selected_orientation == "any":
        score += 30
    else:
        for keyword in ORIENTATION_KEYWORDS:
            if keyword in bio_text:
                matched_keywords.append(keyword)
                score += 30
                break

    score = max(0, min(score, 100))

    if score >= 80:
        status = "Excellent"
    elif score >= 60:
        status = "Good"
    elif score >= 40:
        status = "Average"
    else:
        status = "Poor"

    matched_keywords = list(dict.fromkeys(matched_keywords))
    return score, matched_keywords, status
