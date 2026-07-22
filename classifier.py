import re
import json
import requests

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


def _call_openai_classify(bio, influencer_language, selected_language, selected_orientation, selected_niche, api_key):
    """Call OpenAI Chat Completions to get a semantic score and matched keywords.

    Returns (score:int, keywords:list[str], status:str) on success, otherwise raises.
    """
    if not api_key:
        raise ValueError("OpenAI API key required for LLM classification")

    prompt = (
        "You are an assistant that classifies social media influencer bios against given criteria.\n"
        "Given the influencer bio and the selected filters (language, orientation, niche), return a JSON object EXACTLY in the following format:\n"
        "{\n  \"score\": <integer 0-100>,\n  \"keywords\": [<list of matched keywords>],\n  \"status\": \"Excellent|Good|Average|Poor\"\n}\n"
        "Do not include any additional text. Use the following inputs:\n"
        f"BIO: \"{bio}\"\n"
        f"INFLUENCER_LANGUAGE: \"{influencer_language}\"\n"
        f"SELECTED_LANGUAGE: \"{selected_language}\"\n"
        f"SELECTED_ORIENTATION: \"{selected_orientation}\"\n"
        f"SELECTED_NICHE: \"{selected_niche}\"\n"
    )

    url = "https://api.openai.com/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": "You are a helpful, concise classifier."},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.0,
        "max_tokens": 200,
    }

    resp = requests.post(url, headers=headers, data=json.dumps(data), timeout=15)
    resp.raise_for_status()
    body = resp.json()
    content = body.get("choices", [{}])[0].get("message", {}).get("content", "")

    # Try to parse JSON directly from the model output
    try:
        parsed = json.loads(content)
        score = int(parsed.get("score", 0))
        keywords = parsed.get("keywords", []) or []
        status = parsed.get("status", "Poor")
        return score, keywords, status
    except Exception:
        # Fallback: attempt to extract digits and keywords via regex
        try:
            m = re.search(r"\"score\"\s*:\s*(\d{1,3})", content)
            score = int(m.group(1)) if m else 0
        except Exception:
            score = 0
        # keywords fallback: find words in square brackets
        kmatch = re.search(r"\[([^\]]+)\]", content)
        if kmatch:
            keywords = [k.strip().strip('\"') for k in kmatch.group(1).split(",")]
        else:
            keywords = []
        status = "Excellent" if score >= 80 else "Good" if score >= 60 else "Average" if score >= 40 else "Poor"
        return score, keywords, status


def classify_influencer_llm(
    bio,
    influencer_language,
    selected_language,
    selected_orientation,
    selected_niche,
    api_key=None,
):
    """Wrapper to call the LLM-based classifier; falls back to rule-based if LLM fails."""
    try:
        return _call_openai_classify(bio, influencer_language, selected_language, selected_orientation, selected_niche, api_key)
    except Exception:
        # If LLM fails for any reason, fall back to the deterministic classifier
        return classify_influencer(bio, influencer_language, selected_language, selected_orientation, selected_niche)
