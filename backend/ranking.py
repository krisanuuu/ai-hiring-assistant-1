import numpy as np
from embeddings import get_embedding

def compute_similarity(resumes, job_desc):
    job_vec = get_embedding(job_desc)
    results = []

    for name, text in resumes.items():
        res_vec = get_embedding(text)
        score = np.dot(res_vec, job_vec) / (
            np.linalg.norm(res_vec) * np.linalg.norm(job_vec)
        )
        results.append((name, float(score)))

    return sorted(results, key=lambda x: x[1], reverse=True)
