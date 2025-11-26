import os
import streamlit as st
from groq import Groq

# ---- Page Setup ----
st.set_page_config(
    page_title="Smart Calculator 🧮",
    page_icon="🧮",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🧮 Smart Calculator")
st.caption("A beginner-friendly calculator with AI explanations.")

# ---- Session State ----
if "history" not in st.session_state:
    st.session_state["history"] = []  # list of dicts: {expression, result}

if "last_calc" not in st.session_state:
    st.session_state["last_calc"] = None

# ---- Helper Functions ----
def create_groq_client():
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        return None, "GROQ_API_KEY is missing. Set it in Colab secrets and environment."
    try:
        client = Groq(api_key=api_key)
        return client, None
    except Exception as e:
        return None, f"Error creating Groq client: {e}"

def calculate(a, b, op_label):
    if op_label == "Add (+)": return a + b, "+"
    if op_label == "Subtract (-)": return a - b, "-"
    if op_label == "Multiply (×)": return a * b, "×"
    if op_label == "Divide (÷)":
        if b == 0: raise ZeroDivisionError("Cannot divide by zero.")
        return a / b, "÷"
    if op_label == "Power (a^b)": return a ** b, "^"
    if op_label == "Percentage (a% of b)": return (a / 100) * b, "% of"
    raise ValueError("Unknown operation selected.")

def add_to_history(expression, result):
    st.session_state["history"].insert(0, {"expression": expression, "result": result})
    st.session_state["history"] = st.session_state["history"][:10]

# ---- Sidebar: History ----
with st.sidebar:
    st.header("📜 Calculation History")
    if st.session_state["history"]:
        for item in st.session_state["history"]:
            st.write(f"{item['expression']} = **{item['result']}**")
    else:
        st.info("No calculations yet.")
    if st.button("🧹 Clear history"):
        st.session_state["history"] = []
        st.experimental_rerun()

# ---- Tabs for UI Sections ----
tab1, tab2, tab3 = st.tabs(["🧮 Basic Calculator", "🤖 AI Explanation", "📝 Natural Language Calculator"])

# ---- Tab 1: Basic Calculator ----
with tab1:
    st.subheader("1️⃣ Basic Calculator")
    col1, col2 = st.columns(2)
    with col1:
        num1 = st.number_input("First number", value=0.0, format="%.6f")
    with col2:
        num2 = st.number_input("Second number", value=0.0, format="%.6f")

    operation = st.selectbox("Choose operation", [
        "Add (+)", "Subtract (-)", "Multiply (×)", "Divide (÷)", "Power (a^b)", "Percentage (a% of b)"
    ])
    if st.button("✅ Calculate"):
        try:
            result, symbol = calculate(num1, num2, operation)
            expression = f"{num1} {symbol} {num2}" if symbol != "% of" else f"{num1}% of {num2}"
            st.success(f"Result: {expression} = {result}")
            st.session_state["last_calc"] = {"num1": num1, "num2": num2, "symbol": symbol, "result": result, "expression": expression}
            add_to_history(expression, result)
        except ZeroDivisionError as zde:
            st.error(f"⚠️ {zde}")
            st.session_state["last_calc"] = None
        except Exception as e:
            st.error(f"Unexpected error: {e}")
            st.session_state["last_calc"] = None

# ---- Tab 2: AI Explanation ----
with tab2:
    st.subheader("2️⃣ Ask Groq to Explain the Last Calculation")
    if st.session_state["last_calc"] is None:
        st.info("Perform a calculation first to get AI explanation.")
    else:
        lc = st.session_state["last_calc"]
        default_prompt = f"Explain step by step how to compute {lc['expression']} to get {lc['result']}. Use simple language."
        user_prompt = st.text_area("Optional: customize your question", value=default_prompt, height=120)
        if st.button("🤖 Explain with AI"):
            client, err = create_groq_client()
            if err:
                st.error(f"❌ {err}")
            else:
                with st.spinner("Asking Groq to explain..."):
                    try:
                        chat_completion = client.chat.completions.create(
                            messages=[{"role": "user", "content": user_prompt}],
                            model="llama-3.3-70b-versatile"
                        )
                        explanation = chat_completion.choices[0].message.content
                        st.subheader("AI Explanation")
                        st.write(explanation)
                    except Exception as e:
                        st.error(f"Error while contacting Groq: {e}")

# ---- Tab 3: Natural Language Calculator ----
with tab3:
    st.subheader("3️⃣ Natural Language Calculator (AI)")
    st.write("Type a math question in plain English. The AI will solve it and explain.")
    nl_question = st.text_input("Your question:", value="What is 12 divided by 3 plus 4?", placeholder="Type a math question...")
    if st.button("🧠 Ask AI to Calculate"):
        if not nl_question.strip():
            st.warning("Please enter a question first.")
        else:
            client, err = create_groq_client()
            if err:
                st.error(f"❌ {err}")
            else:
                with st.spinner("Asking Groq to solve..."):
                    try:
                        prompt = (
                            "You are a careful math tutor. Solve the following math question, "
                            "then give the final numeric answer and explain it step by step in simple language.\n\n"
                            f"Question: {nl_question}"
                        )
                        chat_completion = client.chat.completions.create(
                            messages=[{"role": "user", "content": prompt}],
                            model="llama-3.3-70b-versatile"
                        )
                        answer_text = chat_completion.choices[0].message.content
                        st.subheader("AI Answer")
                        st.write(answer_text)
                    except Exception as e:
                        st.error(f"Error while contacting Groq: {e}")

st.caption("Designed with clean layout, visible history, friendly messages, and step-by-step AI explanations.")
