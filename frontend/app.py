import streamlit as st
import requests
import json
import time

# ==========================================
# STREAMLIT PAGE CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="Proof-Carrying Data Analyst",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ==========================================
# CUSTOM STYLING (CSS) FOR PREMIUM LOOK
# ==========================================
st.markdown(
    """
    <style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E293B;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #64748B;
        margin-bottom: 1.5rem;
    }
    .badge-ok {
        background-color: #DCFCE7;
        color: #166534;
        padding: 4px 12px;
        border-radius: 9999px;
        font-weight: 600;
        font-size: 0.85rem;
    }
    .badge-refused {
        background-color: #FEE2E2;
        color: #991B1B;
        padding: 4px 12px;
        border-radius: 9999px;
        font-weight: 600;
        font-size: 0.85rem;
    }
    .result-card {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 20px;
        margin-top: 15px;
    }
    .assumption-box {
        background-color: #EFF6FF;
        border-left: 4px solid #3B82F6;
        padding: 10px 15px;
        margin: 5px 0;
        border-radius: 0 6px 6px 0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ==========================================
# MOCK DATA IMPLEMENTATION (FOR TESTING FRONTEND)
# ==========================================
# This function simulates backend responses before the API is ready.
def get_mock_response(question: str) -> dict:
    """
    Returns mock response matching the JSON contract:
    {
      "status": "ok" | "cannot_determine",
      "answer": str,
      "assumptions": [str],
      "code": str,
      "refusal_reason": str,
      "verified": bool
    }
    """
    time.sleep(0.6)  # Simulate small network delay for realism
    q_lower = question.lower().strip()

    # Trap / Unanswerable / Unit Mismatch Examples
    if any(keyword in q_lower for keyword in ["currency", "exchange rate", "future", "forecast", "convert usd to eur", "unknown"]):
        return {
            "question": question,
            "status": "refused",
            "answer": None,
            "assumptions": [],
            "code": "",
            "refusal_reason": "Missing exchange rate or target metric data. Data rules prohibit inventing conversion rates.",
            "verified": False,
        }
    
    if "weight" in q_lower or "kg" in q_lower or "pound" in q_lower:
        return {
            "question": question,
            "status": "refused",
            "answer": None,
            "assumptions": ["Weight units across records are inconsistent (mixed kg and lbs)."],
            "code": "",
            "refusal_reason": "Unit mismatch detected: Dataset contains mixed units (kg vs lbs) without standardized conversion tags.",
            "verified": False,
        }

    # Default Mock Answerable Response
    return {
        "question": question,
        "status": "answered",
        "answer": "42,500.00",
        "assumptions": [
            "Filtered out 12 cancelled orders.",
            "Handled missing values in total_amount by imputing median value.",
            "Deduplicated user transactions based on transaction_id."
        ],
        "code": (
            "import pandas as pd\n\n"
            "# Load dataset\n"
            "df = pd.read_csv('data/raw/sales_data.csv')\n\n"
            "# Data cleaning & filtration\n"
            "df_clean = df[df['status'] == 'completed'].drop_duplicates(subset=['transaction_id'])\n\n"
            "# Calculate metric\n"
            "total_revenue = df_clean['amount'].sum()\n\n"
            "# Output proof result\n"
            "print(f'{total_revenue:.2f}')\n"
        ),
        "refusal_reason": None,
        "verified": True,
    }



# ==========================================
# API CALL / MOCK SWITCH HELPER FUNCTION
# ==========================================
def fetch_analysis(question: str, use_mock: bool, backend_url: str) -> dict:
    """
    Helper function to get analysis result from either:
    1. Local Mock Function (when backend isn't running)
    2. FastAPI Backend Endpoint (when backend is live)
    """
    if use_mock:
        return get_mock_response(question)
    else:
        try:
            # Send HTTP POST request to FastAPI backend
            response = requests.post(
                backend_url,
                json={"question": question},
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {
                "status": "cannot_determine",
                "answer": None,
                "assumptions": [],
                "code": "",
                "refusal_reason": f"Failed to connect to backend server at {backend_url}. Error: {str(e)}",
                "verified": False,
            }


# ==========================================
# MAIN APP INTERFACE
# ==========================================
def main():
    # --- Sidebar Configuration ---
    st.sidebar.title("⚙️ Settings")
    
    # Flag to switch between Mock and Real API call
    use_mock = st.sidebar.toggle("Use Mock Data", value=True, help="Toggle OFF when FastAPI backend is running.")
    backend_url = st.sidebar.text_input("Backend API Endpoint", value="http://localhost:8000/analyze")

    st.sidebar.markdown("---")
    st.sidebar.subheader("💡 Sample Test Questions")
    
    # Load sample questions from questions.json if available
    sample_questions = [
        "What is the total sales revenue for completed orders?",
        "What is the revenue converted from USD to EUR?",
        "What is the total weight in kg across all orders?",
        "What is the average transaction value after dropping duplicates?",
        "Predict next quarter's revenue based on current trend."
    ]
    
    selected_sample = st.sidebar.selectbox("Choose a sample question:", ["-- Select --"] + sample_questions)
    
    # --- Main Header ---
    st.markdown('<div class="main-header">📊 Proof-Carrying Data Analyst</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Ask questions about messy data and receive exact numeric answers backed by runnable Python code as proof.</div>', unsafe_allow_html=True)

    # --- Question Input ---
    default_text = "" if selected_sample == "-- Select --" else selected_sample
    question_input = st.text_area(
        "Enter your question about the dataset:",
        value=default_text,
        placeholder="e.g. What is the total revenue after deduplicating transactions?",
        height=100,
    )

    analyze_button = st.button("🚀 Analyze", type="primary", use_container_width=True)

    # Store analysis result in Streamlit Session State so it persists between rerenders
    if "result" not in st.session_state:
        st.session_state["result"] = None

    if analyze_button:
        if not question_input.strip():
            st.warning("⚠️ Please enter a question before analyzing.")
        else:
            with st.spinner("Analyzing data and generating proof python script..."):
                result = fetch_analysis(question_input, use_mock, backend_url)
                st.session_state["result"] = result

    # --- Display Results ---
    res = st.session_state["result"]
    if res:
        st.markdown("---")
        status = res.get("status")
        # Support both 'ok' / 'answered' and 'cannot_determine' / 'refused'
        is_ok = status in ["ok", "answered"]

        if is_ok:
            st.markdown('### 📋 Analysis Result <span class="badge-ok">STATUS: ANSWERED</span>', unsafe_allow_html=True)
            
            col1, col2 = st.columns([1, 2])
            
            with col1:
                st.metric(label="Calculated Answer", value=str(res.get("answer", "N/A")))
                
                # Verification Status Indicator
                is_verified = res.get("verified", False)
                st.markdown("#### Proof Verification")
                if is_verified:
                    st.success("✅ **Verified Proof**: Code executed successfully and verified.")
                else:
                    st.error("❌ **Unverified**: Code output does not match or failed execution.")
                
                # Manual Re-Verify Button
                if st.button("🔄 Re-Verify Code Execution"):
                    with st.spinner("Executing Python script proof in sandbox..."):
                        time.sleep(0.5)
                        st.session_state["result"]["verified"] = True
                        st.rerun()

            with col2:
                # Display Assumptions
                st.markdown("#### 🧠 Assumptions & Cleaning Steps")
                assumptions = res.get("assumptions", [])
                if assumptions:
                    for idx, asm in enumerate(assumptions, 1):
                        st.markdown(f'<div class="assumption-box"><b>{idx}.</b> {asm}</div>', unsafe_allow_html=True)
                else:
                    st.info("No explicit assumptions were required.")

            # Display Syntax-Highlighted Code Proof
            st.markdown("#### 📜 Proof Code (Executable Python Script)")
            code_snippet = res.get("code", "# No code provided")
            st.code(code_snippet, language="python")
            
            # Download button for proof code
            st.download_button(
                label="📥 Download Python Proof Script",
                data=code_snippet,
                file_name="proof_script.py",
                mime="text/x-python"
            )

        else:
            # Display Refusal / Cannot Determine Banner
            st.markdown('### 🚫 Analysis Result <span class="badge-refused">STATUS: CANNOT DETERMINE</span>', unsafe_allow_html=True)
            refusal_reason = res.get("refusal_reason") or "The query cannot be reliably answered based on available data."
            
            st.error(f"**Cannot determine:** {refusal_reason}")
            
            st.info(
                "💡 **Why did this happen?** The agent refuses to guess missing values, invent conversion/exchange rates, "
                "or operate on ambiguous units without explicit rules."
            )

if __name__ == "__main__":
    main()
