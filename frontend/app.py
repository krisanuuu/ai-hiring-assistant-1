import streamlit as st
import requests
import pandas as pd

URL = "http://127.0.0.1:8000"

st.title("AI Hiring Assistant")

# -------------------------
# Upload
# -------------------------
files = st.file_uploader("Upload Resumes", accept_multiple_files=True)

if files:
    if st.button("Upload"):

        progress = st.progress(0)
        status = st.empty()

        try:
            # reset backend
            requests.post(f"{URL}/reset")

            # prepare ALL files for one request
            file_data = [
                ("files", (f.name, f.getvalue(), "application/pdf"))
                for f in files
            ]

            status.write("Uploading...")

            r = requests.post(
                f"{URL}/upload",
                files=file_data
            )

            if r.status_code == 200:
                progress.progress(100)
                status.write("✅ Upload complete")
                st.success("All resumes uploaded!")
            else:
                st.error(r.text)

        except Exception as e:
            st.error(str(e))

st.info(f"Total Resumes: {len(files) if files else 0}")

# -------------------------
# Job Description
# -------------------------
job = st.text_area("Job Description")

# -------------------------
# Analyze
# -------------------------
if st.button("Analyze"):
    try:
        if not job:
            st.warning("Enter job description first")
        else:
            r = requests.post(
                f"{URL}/analyze",
                params={"job_desc": job}
            )

            data = r.json()

            if "ranking" in data:
                df = pd.DataFrame(data["ranking"], columns=["Resume", "Match %"])
                st.dataframe(df)

                top = data["ranking"][0]
                st.success(f"🏆 Top Candidate: {top[0]} ({top[1]}%)")

            if "skills" in data:
                st.subheader("Skills per Candidate")
                st.write(data["skills"])

            if "details" in data:
                st.subheader("Match Details")

                for name, d in data["details"].items():
                    st.write(f"### {name}")
                    st.write("✅ Matched:", d["matched"])
                    st.write("❌ Missing:", d["missing"])

    except Exception as e:
        st.error(str(e))


# -------------------------
# Chat
# -------------------------
st.subheader("Chat")

q = st.text_input("Ask")

if st.button("Send"):
    try:
        if not q:
            st.warning("Type a question")
        else:
            r = requests.post(
                f"{URL}/chat",
                json={"question": q, "job_desc": job}
            )

            data = r.json()
            st.write(data.get("response", "No response"))

    except Exception as e:
        st.error(str(e))