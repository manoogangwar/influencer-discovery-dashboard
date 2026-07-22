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
    "atmanirbhar bharat"
]


def classify_influencer(
    bio,
    influencer_language,
    selected_language,
    selected_orientation,
    selected_niche
):

    bio = str(bio).lower()

    score = 0
    matched = []

    # ---------- Niche Match (40) ----------
    if selected_niche.strip():

        words = selected_niche.lower().split()

        count = 0

        for word in words:

            if word in bio:
                matched.append(word)
                count += 1

        if len(words) > 0:
            score += int((count / len(words)) * 40)

    # ---------- Language Match (30) ----------

    if selected_language == "Hindi & English":
        score += 30

    elif influencer_language.lower() == selected_language.lower():
        score += 30

    # ---------- Orientation Match (30) ----------

    if selected_orientation == "Any":

        score += 30

    else:

        for keyword in ORIENTATION_KEYWORDS:

            if keyword in bio:

                score += 30
                matched.append(keyword)
                break

    # ---------- Status ----------

    if score >= 80:
        status = "Excellent"

    elif score >= 60:
        status = "Good"

    elif score >= 40:
        status = "Average"

    else:
        status = "Poor"

    return score, matched, status