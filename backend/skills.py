SKILLS = [
    "python","java","c++","machine learning",
    "deep learning","nlp","sql","aws","docker"
]

def extract_skills(text):
    text = text.lower()
    return [s for s in SKILLS if s in text]
