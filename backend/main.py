from fastapi import FastAPI, UploadFile, File
from typing import List
import os
import pdfplumber
from sentence_transformers import SentenceTransformer, util

# -------------------------
# App init
# -------------------------
app = FastAPI()

UPLOAD_FOLDER = "data"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

stored_data = []

model = SentenceTransformer("all-MiniLM-L6-v2")

# -------------------------
# Extract text
# -------------------------
def extract_text(path):
    text = ""
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
    return text.lower()

# -------------------------
# Extract skills
# -------------------------
def extract_skills(text):
    keywords = [
        "python","java","sql","html","css","javascript",
        "react","node","communication","teamwork",
        "leadership","problem solving","adaptability"
    ]
    return [k for k in keywords if k in text]

# -------------------------
# Upload MULTIPLE resumes
# -------------------------
@app.post("/upload")
async def upload(files: List[UploadFile] = File(...)):
    global stored_data

    results = []

    for file in files:
        content = await file.read()
        path = os.path.join(UPLOAD_FOLDER, file.filename)

        with open(path, "wb") as f:
            f.write(content)

        text = extract_text(path)
        embedding = model.encode(text, convert_to_tensor=True)
        skills = extract_skills(text)

        stored_data.append({
            "name": file.filename,
            "text": text,
            "embedding": embedding,
            "skills": skills
        })

        results.append(file.filename)

    return {"message": "Uploaded", "files": results}

# -------------------------
# Reset
# -------------------------
@app.post("/reset")
def reset():
    global stored_data
    stored_data = []
    return {"message": "reset done"}

# -------------------------
# Analyze
# -------------------------
@app.post("/analyze")
def analyze(job_desc: str):

    if not stored_data:
        return {"error": "No resumes uploaded"}

    job_embedding = model.encode(job_desc, convert_to_tensor=True)

    ranking = []
    skills_map = {}
    match_details = {}

    job_words = set(job_desc.lower().split())

    for r in stored_data:
        score = util.cos_sim(job_embedding, r["embedding"]).item()
        percent = round(score * 100, 2)

        ranking.append((r["name"], percent))
        skills_map[r["name"]] = r["skills"]

        resume_words = set(r["text"].split())

        matched = list(job_words & resume_words)
        missing = list(job_words - resume_words)

        match_details[r["name"]] = {
            "matched": matched[:10],
            "missing": missing[:10]
        }

    ranking.sort(key=lambda x: x[1], reverse=True)

    return {
        "ranking": ranking,
        "skills": skills_map,
        "details": match_details
    }

# -------------------------
# Chat (LOCAL AI - NO API)
# -------------------------
@app.post("/chat")
def chat(data: dict):

    question = data.get("question", "").lower()
    job_desc = data.get("job_desc", "")

    if not stored_data:
        return {"response": "Upload resumes first."}

    job_embedding = model.encode(job_desc, convert_to_tensor=True)

    scores = []

    for r in stored_data:
        score = util.cos_sim(job_embedding, r["embedding"]).item()
        scores.append((r, score))

    scores.sort(key=lambda x: x[1], reverse=True)

    # -----------------------------
    # BEST
    # -----------------------------
    if "best" in question:
        best = scores[0][0]
        return {
            "response": f"🏆 Best candidate: {best['name']}\nSkills: {', '.join(best['skills'])}"
        }

    # -----------------------------
    # COMPARE
    # -----------------------------
    elif "compare" in question:
        if len(scores) < 2:
            return {"response": "Need at least 2 resumes."}

        a, b = scores[0][0], scores[1][0]

        return {
            "response": f"""
📊 Comparison:

{a['name']} → {', '.join(a['skills'])}
{b['name']} → {', '.join(b['skills'])}

👉 {a['name']} is better based on job similarity.
"""
        }

    # -----------------------------
    # WHY
    # -----------------------------
    elif "why" in question or "reason" in question:
        best = scores[0][0]

        return {
            "response": f"""
🧠 Reasoning:

{best['name']} is best because:
- Matches job description closely
- Has relevant skills: {', '.join(best['skills'])}
- Higher similarity score
"""
        }

    # -----------------------------
    # DEFAULT
    # -----------------------------
    else:
        best = scores[0][0]
        return {
            "response": f"Best candidate is {best['name']}. Ask 'why' or 'compare'."
        }