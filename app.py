import os
from groq import Groq
import streamlit as st

# ---- HCI: basic page setup ----
st.set_page_config(
    page_title="Smart Calculator (Groq-powered)",
    page_icon="🧮",
    layout="centered"
)

st.title("🧮 Smart Calculator")
st.caption("A simple, beginner-friendly calculator with AI explanations (Groq LLM).")

st.markdown(
    """
    ### How to use
    1. Enter two numbers.
    2. Choose an operation.
    3. Click **Calculate** to see the result.
    4. (Optional) Click **Explain with AI** to get a step-by-step explanation.

    ---
    """
)

# ---- Helper functions ----

def create_groq_client():
    """Create a Groq client using the API key from environment variable."""
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        return None, "GROQ_API_KEY is missing. Set it in Colab secrets and environment."
    try:
        client = Groq(api_key=api_key)
        return client, None
    except Exception as e:
        return None, f"Error creating Groq client: {e}"

def calculate(a, b, op_label):
    """Perform the selected arithmetic operation."""
    if op_label == "Add (+)":
        return a + b, "+"
    elif op_label == "Subtract (-)":
        return a - b, "-"
    elif op_label == "Multiply (×)":
        return a * b, "×"
    elif op_label == "Divide (÷)":
        if b == 0:
            raise ZeroDivisionError("Cannot divide by zero.")
        return a / b, "÷"
    else:
        raise ValueError("Unknown operation selected.")

# ---- UI: Calculator Section (HCI: clear layout & controls) ----

st.header("1️⃣ Basic Calculator")

col1, col2 = st.columns(2)

with col1:
    num1 = st.number_input("First number", value=0.0, format="%.6f")
with col2:
    num2 = st.number_input("Second number", value=0.0, format="%.6f")

operation = st.radio(
    "Choose operation",
    ["Add (+)", "Subtract (-)", "Multiply (×)", "Divide (÷)"],
    horizontal=True
)

calc_button = st.button("✅ Calculate")

if "last_calc" not in st.session_state:
    st.session_state["last_calc"] = None

if calc_button:
    try:
        result, symbol = calculate(num1, num2, operation)
        st.success(f"Result: {num1} {symbol} {num2} = {result}")
        # Store last calculation in session state for AI explanation
        st.session_state["last_calc"] = {
            "num1": num1,
            "num2": num2,
            "symbol": symbol,
            "result": result,
        }
    except ZeroDivisionError as zde:
        st.error(f"⚠️ {zde}")
        st.session_state["last_calc"] = None
    except Exception as e:
        st.error(f"Unexpected error: {e}")
        st.session_state["last_calc"] = None

st.divider()

# ---- UI: AI Explanation Section (Groq) ----

st.header("2️⃣ Ask Groq to Explain the Calculation")

if st.session_state["last_calc"] is None:
    st.info("First perform a calculation above, then you can ask Groq to explain it.")
else:
    lc = st.session_state["last_calc"]
    default_prompt = (
        f"Explain step by step how to compute {lc['num1']} {lc['symbol']} {lc['num2']} "
        f"to get {lc['result']}. Use simple language for a beginner."
    )

    user_prompt = st.text_area(
        "Optional: customize the question you want to ask the AI",
        value=default_prompt,
        height=120
    )

    explain_button = st.button("🤖 Explain with AI (Groq)")

    if explain_button:
        client, err = create_groq_client()
        if err:
            st.error(f"❌ {err}")
        else:
            with st.spinner("Asking Groq to explain..."):
                try:
                    # Your exact Groq usage pattern
                    chat_completion = client.chat.completions.create(
                        messages=[
                            {
                                "role": "user",
                                "content": user_prompt,
                            }
                        ],
                        model="llama-3.3-70b-versatile",
                    )

                    explanation = chat_completion.choices[0].message.content
                    st.subheader("AI Explanation")
                    st.write(explanation)

                except Exception as e:
                    st.error(f"Error while contacting Groq: {e}")

st.caption(
    "Designed with basic HCI principles: clear labels, immediate feedback, simple layout, "
    "and helpful error messages."
)
