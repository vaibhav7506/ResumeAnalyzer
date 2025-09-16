import os
import streamlit as st
from dotenv import load_dotenv
import google.generativeai as genai
from pdf2image import convert_from_path
import pytesseract
import pdfplumber
import time
from io import BytesIO

# Load environment variables
load_dotenv()

# Configure Google Gemini AI
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Custom CSS for modern design
def load_css():
    st.markdown("""
    <style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global Styles */
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #581c87 50%, #0f172a 100%);
        font-family: 'Inter', sans-serif;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Custom background pattern */
    .stApp::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-image: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%239C92AC' fill-opacity='0.05'%3E%3Cpath d='m36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
        opacity: 0.2;
        pointer-events: none;
        z-index: -1;
    }
    
    /* Main title */
    .main-title {
        text-align: center;
        margin-bottom: 2rem;
        padding: 2rem 0;
    }
    
    .title-container {
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 1rem;
        margin-bottom: 1rem;
    }
    
    .title-icon {
        background: linear-gradient(135deg, #a855f7, #ec4899);
        border-radius: 50%;
        padding: 12px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
    }
    
    .main-title h1 {
        background: linear-gradient(135deg, #a855f7, #ec4899, #a855f7);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 3.5rem;
        font-weight: 700;
        margin: 0;
        line-height: 1;
    }
    
    .subtitle {
        color: #cbd5e1;
        font-size: 1.2rem;
        font-weight: 400;
        max-width: 600px;
        margin: 0 auto;
        line-height: 1.6;
    }
    
    /* Glass card effect */
    .glass-card {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 20px;
        padding: 2rem;
        margin-bottom: 2rem;
        box-shadow: 0 20px 50px rgba(0, 0, 0, 0.3);
    }
    
    .section-title {
        color: white;
        font-size: 1.5rem;
        font-weight: 600;
        margin-bottom: 1.5rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    /* File uploader styling */
    .stFileUploader > div {
        background: rgba(30, 41, 59, 0.5);
        border: 2px dashed #64748b;
        border-radius: 15px;
        padding: 2rem;
        text-align: center;
        transition: all 0.3s ease;
    }
    
    .stFileUploader > div:hover {
        border-color: #a855f7;
        background: rgba(168, 85, 247, 0.1);
    }
    
    .stFileUploader label {
        color: white !important;
        font-weight: 500;
    }
    
    /* Text area styling */
    .stTextArea > div > div > textarea {
        background: rgba(30, 41, 59, 0.5) !important;
        border: 1px solid #475569 !important;
        border-radius: 15px !important;
        color: white !important;
        font-family: 'Inter', sans-serif !important;
        padding: 1rem !important;
    }
    
    .stTextArea > div > div > textarea:focus {
        border-color: #a855f7 !important;
        box-shadow: 0 0 0 3px rgba(168, 85, 247, 0.2) !important;
    }
    
    /* Button styling */
    .analyze-button {
        background: linear-gradient(135deg, #a855f7, #ec4899);
        color: white;
        border: none;
        border-radius: 15px;
        padding: 1rem 2rem;
        font-size: 1.1rem;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
        width: 100%;
        margin: 1rem 0;
        box-shadow: 0 10px 30px rgba(168, 85, 247, 0.3);
    }
    
    .analyze-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 15px 40px rgba(168, 85, 247, 0.4);
    }
    
    .analyze-button:disabled {
        background: linear-gradient(135deg, #475569, #64748b);
        cursor: not-allowed;
        transform: none;
    }
    
    /* Success/Warning messages */
    .stAlert > div {
        background: rgba(16, 185, 129, 0.1);
        border: 1px solid rgba(16, 185, 129, 0.3);
        border-radius: 10px;
        color: #10b981;
    }
    
    .stWarning > div {
        background: rgba(245, 158, 11, 0.1);
        border: 1px solid rgba(245, 158, 11, 0.3);
        border-radius: 10px;
        color: #f59e0b;
    }
    
    /* Analysis results */
    .analysis-results {
        background: rgba(30, 41, 59, 0.5);
        border-radius: 15px;
        padding: 2rem;
        color: #e2e8f0;
        line-height: 1.8;
        font-size: 1rem;
        white-space: pre-wrap;
        margin-top: 1rem;
    }
    
    /* Loading spinner */
    .loading-container {
        text-align: center;
        padding: 3rem;
        color: #cbd5e1;
    }
    
    .spinner {
        border: 4px solid rgba(168, 85, 247, 0.2);
        border-top: 4px solid #a855f7;
        border-radius: 50%;
        width: 50px;
        height: 50px;
        animation: spin 1s linear infinite;
        margin: 0 auto 1rem;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    /* Features list */
    .features-list {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 15px;
        padding: 1.5rem;
        margin-top: 2rem;
    }
    
    .feature-item {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        padding: 0.5rem 0;
        color: #cbd5e1;
    }
    
    .feature-icon {
        color: #10b981;
        font-size: 1.2rem;
    }
    
    /* Footer */
    .custom-footer {
        text-align: center;
        margin-top: 4rem;
        padding: 2rem 0;
        border-top: 1px solid rgba(255, 255, 255, 0.1);
        color: #94a3b8;
    }
    
    .footer-highlight {
        color: #a855f7;
        font-weight: 600;
    }
    
    /* Responsive */
    @media (max-width: 768px) {
        .main-title h1 {
            font-size: 2.5rem;
        }
        
        .glass-card {
            padding: 1.5rem;
        }
    }
    </style>
    """, unsafe_allow_html=True)

# Function to extract text from PDF
def extract_text_from_pdf(uploaded_file):
    text = ""
    try:
        # Save uploaded file temporarily
        with open("temp_resume.pdf", "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        # Try direct text extraction
        with pdfplumber.open("temp_resume.pdf") as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text

        if text.strip():
            return text.strip()
    except Exception as e:
        st.error(f"Direct text extraction failed: {e}")

    # Fallback to OCR for image-based PDFs
    st.info("Falling back to OCR for image-based PDF...")
    try:
        images = convert_from_path("temp_resume.pdf")
        for image in images:
            page_text = pytesseract.image_to_string(image)
            text += page_text + "\n"
    except Exception as e:
        st.error(f"OCR failed: {e}")

    # Clean up temp file
    if os.path.exists("temp_resume.pdf"):
        os.remove("temp_resume.pdf")
        
    return text.strip()

# Function to analyze resume
def analyze_resume(resume_text, job_description=None):
    if not resume_text:
        return {"error": "Resume text is required for analysis."}
    
    model = genai.GenerativeModel("gemini-1.5-flash")
    
    base_prompt = f"""
    You are an experienced HR with Technical Experience in the field of any one job role from Data Science, Data Analyst, DevOPS, Machine Learning Engineer, Prompt Engineer, AI Engineer, Full Stack Web Development, Big Data Engineering, Marketing Analyst, Human Resource Manager, Software Developer your task is to review the provided resume.
    Please share your professional evaluation on whether the candidate's profile aligns with the role. Also mention Skills he already have and suggest some skills to improve his resume, also suggest some course he might take to improve the skills. Highlight the strengths and weaknesses.

    Resume:
    {resume_text}
    """

    if job_description:
        base_prompt += f"""
        Additionally, compare this resume to the following job description:
        
        Job Description:
        {job_description}
        
        Highlight the strengths and weaknesses of the applicant in relation to the specified job requirements.
        """

    response = model.generate_content(base_prompt)
    return response.text.strip()

# Main Streamlit app
def main():
    # Set page config
    st.set_page_config(
        page_title="AI Resume Analyzer",
        page_icon="🧠",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    # Load custom CSS
    load_css()
    
    # Initialize session state
    if 'analysis_complete' not in st.session_state:
        st.session_state.analysis_complete = False
    if 'analysis_result' not in st.session_state:
        st.session_state.analysis_result = ""
    
    # Header
    st.markdown("""
    <div class="main-title">
        <div class="title-container">
            <div class="title-icon">🧠</div>
            <h1>AI Resume Analyzer</h1>
        </div>
        <p class="subtitle">
            Leverage cutting-edge AI to analyze your resume, identify strengths, and get personalized recommendations to boost your career prospects.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Main content
    col1, col2 = st.columns([1, 1], gap="large")
    
    with col1:
        # File Upload Section
        st.markdown("""
        <div class="glass-card">
            <h2 class="section-title">📁 Upload Resume</h2>
        </div>
        """, unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader(
            "Choose your PDF resume",
            type=["pdf"],
            help="Upload a PDF file of your resume for analysis"
        )
        
        if uploaded_file:
            st.success(f"✅ Resume uploaded successfully! ({uploaded_file.name})")
        else:
            st.warning("⚠️ Please upload a resume in PDF format.")
        
        # Job Description Section
        st.markdown("""
        <div class="glass-card">
            <h2 class="section-title">🎯 Job Description (Optional)</h2>
        </div>
        """, unsafe_allow_html=True)
        
        job_description = st.text_area(
            "Enter job description",
            placeholder="Paste the job description here to get targeted analysis...",
            height=200,
            help="Add a job description for more targeted analysis"
        )
        
        # Analyze Button
        st.markdown('<div style="margin-top: 2rem;"></div>', unsafe_allow_html=True)
        
        analyze_clicked = st.button(
            "✨ Analyze Resume",
            disabled=not uploaded_file,
            help="Click to start the AI analysis of your resume"
        )
    
    with col2:
        # Analysis Results Section
        st.markdown("""
        <div class="glass-card">
            <h2 class="section-title">📊 Analysis Results</h2>
        </div>
        """, unsafe_allow_html=True)
        
        if analyze_clicked and uploaded_file:
            # Show loading
            st.markdown("""
            <div class="loading-container">
                <div class="spinner"></div>
                <p>AI is analyzing your resume...</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Extract text and analyze
            with st.spinner("Processing..."):
                resume_text = extract_text_from_pdf(uploaded_file)
                if resume_text:
                    analysis = analyze_resume(resume_text, job_description)
                    st.session_state.analysis_result = analysis
                    st.session_state.analysis_complete = True
                    time.sleep(1)  # Small delay for better UX
                    st.rerun()
                else:
                    st.error("Failed to extract text from the PDF. Please try a different file.")
        
        elif st.session_state.analysis_complete and st.session_state.analysis_result:
            # Show results
            st.markdown(f"""
            <div class="analysis-results">
                {st.session_state.analysis_result}
            </div>
            """, unsafe_allow_html=True)
            
            # Reset button
            if st.button("🔄 Analyze Another Resume"):
                st.session_state.analysis_complete = False
                st.session_state.analysis_result = ""
                st.rerun()
        
        else:
            # Show features when no analysis
            st.markdown("""
            <div style="text-align: center; padding: 3rem 0; color: #94a3b8;">
                <div style="font-size: 4rem; margin-bottom: 1rem;">🏆</div>
                <p>Upload your resume and click analyze to see detailed insights and recommendations.</p>
            </div>
            
            <div class="features-list">
                <h3 style="color: white; margin-bottom: 1rem; font-size: 1.2rem;">What You'll Get:</h3>
                <div class="feature-item">
                    <span class="feature-icon">✅</span>
                    <span>Comprehensive skills assessment</span>
                </div>
                <div class="feature-item">
                    <span class="feature-icon">✅</span>
                    <span>Personalized improvement recommendations</span>
                </div>
                <div class="feature-item">
                    <span class="feature-icon">✅</span>
                    <span>Course and certification suggestions</span>
                </div>
                <div class="feature-item">
                    <span class="feature-icon">✅</span>
                    <span>Job role alignment analysis</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # Footer
    st.markdown("""
    <div class="custom-footer">
        <p>  
            Developed by <span class="footer-highlight">Vaibhav and Mohak</span>
        </p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()