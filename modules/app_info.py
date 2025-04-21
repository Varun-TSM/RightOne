import streamlit as st

def show_notice_box():
    st.markdown("""
    <div style="
        border: 2px dotted rgba(100, 100, 100, 0.4);
        background-color: rgba(200, 200, 200, 0.1);
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 20px;
    ">
        <h4 style="margin-top: 0;"><i class="fas fa-cogs"></i> Tool Guide</h4>
        <ol style="padding-left: 20px; margin-top: 10px;">
            <li>Upload a valid ZIP file containing multiple resumes.</li>
            <li>Submit one batch per job description.</li>
            <li>Do not include sensitive personal data.</li>
            <li>System extracts key resume information automatically.</li>
            <li>Top matching resumes are recommended using embeddings.</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)
