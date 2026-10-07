# 📊 Proof-Carrying Data Analyst (HackNex26 - PS08)

An AI Agent framework that answers quantitative questions on messy datasets and ships **executable, standalone Python scripts** as mathematical proof.

---

## 🎯 Project Overview

Messy data often leads to hallucinated or unverifiable AI answers. The **Proof-Carrying Data Analyst** guarantees correctness by enforcing a strict proof contract:
- Every numeric answer must ship with a **standalone Python script** that loads the raw CSV data, executes data cleaning/filtration, and prints the exact numeric result to `stdout`.
- The system **never invents missing data, conversion factors, or exchange rates**. If a query is ambiguous, missing required data, or requests future projections, it **refuses** with an explicit reason.

### 📜 Shared JSON Contract (`AgentResult`)
All communication between Frontend, Backend, and Agent uses the standardized schema defined in `agent/schema.py`:

```json
{
  "question": "What is the total revenue from all completed orders?",
  "status": "answered",
  "answer": "42500.00",
  "assumptions": [
    "Filtered out 12 cancelled orders.",
    "Deduplicated user transactions based on transaction_id."
  ],
  "code": "import pandas as pd\ndf = pd.read_csv('data/raw/sales_data.csv')\nprint(df[df['status'] == 'completed']['amount'].sum())",
  "refusal_reason": null,
  "verified": true
}
```

---

## ⚙️ Setup Instructions

### Prerequisites
- **Python 3.10+**
- `git`

### Installation Steps

1. **Clone the repository**:
   ```bash
   git clone https://github.com/sheltonarun/NEXt-Gen-Three-HackNex26.git
   cd NEXt-Gen-Three-HackNex26
   ```

2. **Create and activate a virtual environment**:
   ```bash
   # Windows (PowerShell)
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1

   # Linux/macOS
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install required dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables**:
   Copy `.env.example` to `.env` and add your LLM API keys:
   ```bash
   cp .env.example .env
   ```
   Add key inside `.env`:
   ```env
   LLM_API_KEY=your_llm_api_key_here
   ```

---

## 🚀 How to Run Frontend & Backend

### 1. Running the Streamlit Frontend UI
Start the Streamlit application:
```bash
streamlit run frontend/app.py
```
Open your browser at **`http://localhost:8501`**.

> 💡 **Mock Mode vs Live API Mode**:
> - **Mock Mode (Default)**: Use the `Use Mock Data Mode` toggle in the sidebar to test UI features and preset responses offline without starting the backend server.
> - **Live API Mode**: Turn OFF mock mode in the sidebar and ensure your FastAPI backend endpoint is set to `http://localhost:8000/analyze`.

### 2. Running the FastAPI Backend Server
Start the FastAPI server using `uvicorn`:
```bash
uvicorn backend.main:app --reload --port 8000
```
The API interactive docs will be available at **`http://localhost:8000/docs`**.

---

## 🧪 How to Run the Test Suite

The test suite evaluates answer correctness, proof code execution, unit mismatch handling, and trap question refusal.

1. **Run Verifier Unit Tests**:
   ```bash
   python -m unittest tests/test_verifier.py
   ```

2. **Run Pytest (All Tests)**:
   ```bash
   pytest tests/
   ```

3. **Run Full Evaluation Matrix on `tests/questions.json`**:
   ```bash
   python tests/run_eval.py
   ```

---

## 💡 Sample Questions & Expected Outputs

### Sample 1: Answerable Query (Status: `answered`)
- **Input Question**: `"What is the total revenue from all completed orders?"`
- **Expected Output JSON**:
  ```json
  {
    "question": "What is the total revenue from all completed orders?",
    "status": "answered",
    "answer": "42500.00",
    "assumptions": [
      "Filtered out cancelled and pending order records.",
      "Deduplicated transactions using transaction_id."
    ],
    "code": "import pandas as pd\n\ndf = pd.read_csv('data/raw/sales_data.csv')\ndf_clean = df[df['status'] == 'completed'].drop_duplicates(subset=['transaction_id'])\nprint(f'{df_clean[\"amount\"].sum():.2f}')\n",
    "refusal_reason": null,
    "verified": true
  }
  ```

---

### Sample 2: Trap / Unanswerable Query (Status: `refused`)
- **Input Question**: `"Convert total sales from USD to EUR when exchange rate is not provided in dataset."`
- **Expected Output JSON**:
  ```json
  {
    "question": "Convert total sales from USD to EUR when exchange rate is not provided in dataset.",
    "status": "refused",
    "answer": null,
    "assumptions": [],
    "code": "",
    "refusal_reason": "Missing currency conversion rates. Data integrity rules prohibit inventing exchange rates without explicit exchange rate tables.",
    "verified": false
  }
  ```

---

### Sample 3: Unit Mismatch Query (Status: `refused`)
- **Input Question**: `"What is the total weight of all shipped packages combined?"`
- **Expected Output JSON**:
  ```json
  {
    "question": "What is the total weight of all shipped packages combined?",
    "status": "refused",
    "answer": null,
    "assumptions": [
      "Package weights contain mixed metric (kg) and imperial (lbs) units."
    ],
    "code": "",
    "refusal_reason": "Unit mismatch detected: Dataset contains mixed units (kg vs lbs) without standardized conversion tags.",
    "verified": false
  }
  ```
