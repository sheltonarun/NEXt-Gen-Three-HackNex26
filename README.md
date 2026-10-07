# 📊 Proof-Carrying Data Analyst

An AI agent system that answers questions about messy data and provides executable Python code as verifiable proof.

---

## 🏗️ Project Architecture & JSON Contract

The frontend (Streamlit), backend (FastAPI), and AI agent communicate using a unified JSON contract:

```json
{
  "status": "ok | cannot_determine",
  "answer": "the result",
  "assumptions": ["list of assumptions"],
  "code": "the python script as a string",
  "refusal_reason": "why it refused (if status is cannot_determine)",
  "verified": true | false
}
```

---

## 🎨 Frontend Setup (Streamlit UI)

The frontend application resides in `frontend/app.py`. It provides an interactive web interface to query the dataset, view proof code, and verify results.

### 🚀 Running Locally

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Launch Streamlit App**:
   ```bash
   streamlit run frontend/app.py
   ```

3. **Mock Mode vs Real Backend Mode**:
   - **Mock Mode (Default)**: Toggle ON in the sidebar to test UI features with preset response data without requiring backend servers.
   - **Real API Mode**: Toggle OFF in the sidebar and enter your FastAPI backend URL (e.g., `http://localhost:8000/analyze`).

---

## 🧪 Test Cases (`tests/questions.json`)

The `tests/questions.json` file contains 18 structured test questions categorized into:
- **Simple Answerable Questions**: Standard calculation queries.
- **Unit Mismatch Questions**: Queries requiring refused status due to mixed units (e.g., kg vs lbs).
- **Duplicate / Missing Data Questions**: Queries with data quality issues.
- **Trap Questions**: Unanswerable queries (e.g., predicting future data or missing exchange rates) where the agent MUST return `status: "cannot_determine"`.

---

## ☁️ Deploying to Streamlit Cloud

1. Push your changes to GitHub on your repository branch:
   ```bash
   git add .
   git commit -m "Add Streamlit frontend UI and test cases"
   git push origin frontend-work
   ```
2. Log into [Streamlit Community Cloud](https://share.streamlit.io/).
3. Click **New app** and select your GitHub repository branch (`frontend-work`).
4. Set Main file path to: `frontend/app.py`.
5. Click **Deploy!** 🚀
