def neuro_decision(sentiment, score, keywords, time_hour, source_reputation):
    weight = 0
    weight += score * 2
    if sentiment == "positive":
        weight += 1
    if "rally" in keywords:
        weight += 1
    if time_hour in range(8, 12):  # Sabah saatleri
        weight += 0.5
    if source_reputation == "high":
        weight += 1
    return "AL" if weight >= 3.5 else "SAT" if weight <= -2 else "BEKLE"
