import sys
import os
import streamlit as st
import shutil
from PIL import Image
import base64
import pandas as pd
from fpdf import FPDF
import io

sys.path.append(os.path.abspath("."))

from rag.doc_loader import load_documents, split_documents
from models.ollama_integration import get_validated_response


st.set_page_config(page_title="ContraSage", layout="centered")

logo_path = os.path.join("logo", "ContraSageLogo.png")
if os.path.exists(logo_path):
    st.markdown(
        f"<div style='text-align: center;'><img src='data:image/png;base64,{base64.b64encode(open(logo_path, 'rb').read()).decode()}' width='400'/></div>",
        unsafe_allow_html=True
    )

st.markdown(
    """
    <div style='position: fixed; bottom: 15px; right: 25px; background-color: rgba(255,255,255,0.05); 
                padding: 12px 18px; border-radius: 10px; font-size: 0.85rem; line-height: 1.6; 
                box-shadow: 0 0 10px rgba(0,0,0,0.2); text-align: left;'>
        <div>👤 <b>Vansh Kumar</b></div>
        <div>🎓 IIT Gandhinagar</div>
        <div>💼 AI & Data Science Intern @ Tata Communications</div>
        <div>📧 <a href='mailto:kumar.vansh@iitgn.ac.in' style='color:#56b0f9;'>kumar.vansh@iitgn.ac.in</a></div>
        <div>🔗 
            <a href='https://www.linkedin.com/in/vansh-ai/' target='_blank' style='color:#56b0f9;'>LinkedIn</a> |
            <a href='https://github.com/VanshOnGit' target='_blank' style='color:#56b0f9;'>GitHub</a>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

st.title("🧠 ContraSage – AI-Powered Contradiction Detector")
st.markdown("Upload multiple documents and detect contradictions with your custom query.")


def extract_filename(text):
    import re
    match = re.search(r"\(([^()]+\.md)\)", text)
    return match.group(1).strip() if match else "uploaded file"

def strip_filename(text):
    return text.strip()

def prepare_export_data(conflict_pairs):
    rows = []
    for idx, pair in enumerate(conflict_pairs, start=1):
        rows.append({
            "Contradiction #": idx,
            "Text 1": strip_filename(pair['text_1']),
            "File 1": extract_filename(pair['text_1']),
            "Text 2": strip_filename(pair['text_2']),
            "File 2": extract_filename(pair['text_2']),
            "Reason": pair['reason']
        })
    return pd.DataFrame(rows)

def generate_pdf(df):
    def safe(text):
        return text.encode("latin-1", "ignore").decode("latin-1")

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    for index, row in df.iterrows():
        pdf.multi_cell(0, 10, f"Contradiction {row['Contradiction #']}")
        pdf.multi_cell(0, 10, f"Text 1 ({row['File 1']}): {safe(row['Text 1'])}")
        pdf.multi_cell(0, 10, f"Text 2 ({row['File 2']}): {safe(row['Text 2'])}")
        pdf.multi_cell(0, 10, f"Reason: {safe(row['Reason'])}")
        pdf.ln()

    output = io.BytesIO()
    pdf.output(name=output)


    return output.getvalue()


uploaded_files = st.file_uploader(
    "Upload documents (.pdf, .txt, .md)",
    type=["pdf", "txt", "md"],
    accept_multiple_files=True,
)

question = st.text_input("Ask your contradiction-related question:")
run_check = st.button("🔍 Run Contradiction Check")

if run_check:
    if not uploaded_files:
        st.warning("Please upload at least one document.")
    elif not question.strip():
        st.warning("Please enter a valid question.")
    else:
        with st.spinner("Analyzing documents..."):
            data_dir = "./data"
            if os.path.exists(data_dir):
                shutil.rmtree(data_dir)
            os.makedirs(data_dir)

            for file in uploaded_files:
                with open(os.path.join(data_dir, file.name), "wb") as f:
                    f.write(file.read())

            docs = load_documents(data_dir)
            chunks = split_documents(docs)
            full_context = "\n\n".join(chunk.page_content for chunk in chunks)
            result = get_validated_response(full_context, question)

        st.success("Contradiction analysis completed.")
        st.subheader("Results")

        if result["conflict_found"]:
            count = len(result["conflict_pairs"])
            label = "Contradiction" if count == 1 else "Contradictions"
            st.markdown(f"### ❗ {count} {label} Found")

            for idx, pair in enumerate(result["conflict_pairs"], start=1):
                st.markdown(f"""
**🔹 Contradiction {idx}:**

> **Text 1 ({extract_filename(pair['text_1'])})**: {strip_filename(pair['text_1']).replace(f'({extract_filename(pair["text_1"])})', '').strip()}

> **Text 2 ({extract_filename(pair['text_2'])})**: {strip_filename(pair['text_2']).replace(f'({extract_filename(pair["text_2"])})', '').strip()}

Reason: {pair['reason']}

---
""")

            df = prepare_export_data(result["conflict_pairs"])

            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Export to CSV",
                data=csv,
                file_name="contradictions.csv",
                mime="text/csv",
            
            )

        else:
            st.markdown("✅ No contradictions found.")
