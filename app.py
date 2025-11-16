import streamlit as st
import pdfplumber
import pandas as pd
import re
from io import BytesIO

st.title("PDF Check")

# --- Step 1: Input PPID list ---
st.header("1. Enter PPID List")
ppid_text = st.text_area("Paste PPIDs here (one per line)")

# --- Step 2: Upload PDF files ---
st.header("2. Upload PDF Files")
uploaded_pdfs = st.file_uploader("Upload PDFs", type="pdf", accept_multiple_files=True)

if st.button("Run Comparison"):
    if not ppid_text.strip():
        st.error("Please enter PPIDs.")
    elif not uploaded_pdfs:
        st.error("Please upload at least one PDF.")
    else:
        # Convert input PPIDs into list
        excel_numbers = [
            line.strip()
            for line in ppid_text.splitlines()
            if line.strip()
        ]

        # Extract numbers from PDFs
        pdf_numbers = []
        for pdf_file in uploaded_pdfs:
            try:
                with pdfplumber.open(pdf_file) as pdf:
                    for page in pdf.pages:
                        text = page.extract_text() or ""
                        matches = re.findall(r"_(.+?)_", text)
                        pdf_numbers.extend([m.strip() for m in matches])
            except Exception as e:
                st.warning(f"Could not process {pdf_file.name}: {e}")

        # Compare lists
        excel_set = set(excel_numbers)
        pdf_set = set(pdf_numbers)

        missing_from_pdf = sorted(list(excel_set - pdf_set))
        extra_in_pdf = sorted(list(pdf_set - excel_set))

        # Build results dataframe
        result_df = pd.DataFrame({
            "Missing from PDF": pd.Series(missing_from_pdf),
            "Extra in PDF": pd.Series(extra_in_pdf)
        })

        st.success("Comparison complete!")

        # Display results in browser
        st.dataframe(result_df)

        # Allow download as Excel
        output = BytesIO()
        result_df.to_excel(output, index=False)
        st.download_button(
            "Download Results as Excel",
            data=output.getvalue(),
            file_name="comparison_results.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

