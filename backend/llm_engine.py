def analyze_candidates(ranking, skills_map, question):
    q = question.lower()

    if "best" in q:
        name, score = ranking[0]
        skills = ", ".join(skills_map[name])
        return f"{name} is the best candidate with score {score:.2f}. Skills: {skills}"

    if "compare" in q and len(ranking) >= 2:
        a, b = ranking[0], ranking[1]
        return f"{a[0]} ({a[1]:.2f}) is better than {b[0]} ({b[1]:.2f})"

    if "why" in q:
        name, score = ranking[0]
        skills = ", ".join(skills_map[name])
        return f"{name} is ranked highest due to strong match and skills: {skills}"

    return "Ask about best candidate, comparison, or reasoning."
