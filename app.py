import streamlit as st
import tempfile
import os
from io import BytesIO
from dataclasses import dataclass
from typing import Optional

# Page config must be first Streamlit command
st.set_page_config(
    page_title="PDF Translator",
    page_icon="📄",
    layout="centered"
)


@dataclass
class TranslationConfig:
    """Configuration object that mimics CLI args for pipeline compatibility."""
    pdf: str
    source_lang: str
    target_lang: str
    model: str = "gpt-4o-mini"
    output: Optional[str] = None
    format: str = "both"
    resume: bool = False
    output_dir: str = "translation_cache"
    dpi: int = 200
    workers: int = 3
    sleep: float = 0.5


# Common languages
LANGUAGES = [
    "English", "Spanish", "French", "German", "Italian", "Portuguese",
    "Russian", "Japanese", "Chinese", "Korean", "Arabic", "Hindi",
    "Dutch", "Polish", "Swedish", "Turkish", "Greek", "Czech",
    "Serbian", "Croatian", "Bulgarian", "Romanian", "Hungarian"
]


def main():
    st.title("📄 PDF Translator")
    st.markdown("Translate PDF documents using AI vision technology")
    
    # Sidebar settings
    with st.sidebar:
        st.header("⚙️ Settings")
        
        model = st.selectbox(
            "Model",
            ["gpt-4o-mini", "gpt-4o"],
            help="gpt-4o-mini is faster and cheaper"
        )
        
        workers = st.slider(
            "Parallel Workers",
            min_value=1,
            max_value=5,
            value=3,
            help="More workers = faster, but higher API usage"
        )
        
        dpi = st.slider(
            "Image DPI",
            min_value=100,
            max_value=300,
            value=200,
            help="Higher DPI = better quality for scanned PDFs"
        )
        
        output_format = st.selectbox(
            "Output Format",
            ["both", "docx", "pdf"],
            help="Choose output file format(s)"
        )
    
    # Main content
    col1, col2 = st.columns(2)
    
    with col1:
        source_lang = st.selectbox(
            "Source Language",
            LANGUAGES,
            index=0
        )
    
    with col2:
        target_lang = st.selectbox(
            "Target Language",
            LANGUAGES,
            index=1
        )
    
    # File upload
    uploaded_file = st.file_uploader(
        "Upload PDF",
        type=["pdf"],
        help="Upload a PDF file to translate"
    )
    
    if uploaded_file:
        st.success(f"Uploaded: {uploaded_file.name} ({uploaded_file.size / 1024:.1f} KB)")
        
        # Translate button
        if st.button("🚀 Translate", type="primary", use_container_width=True):
            translate_document(
                uploaded_file=uploaded_file,
                source_lang=source_lang,
                target_lang=target_lang,
                model=model,
                workers=workers,
                dpi=dpi,
                output_format=output_format
            )


def translate_document(uploaded_file, source_lang, target_lang, model, workers, dpi, output_format):
    """Run the translation pipeline with progress updates."""
    
    # Import here to avoid circular imports and slow startup
    from pipeline import run_translation_pipeline
    
    # Create temp directory for processing
    with tempfile.TemporaryDirectory() as temp_dir:
        # Save uploaded file
        pdf_path = os.path.join(temp_dir, uploaded_file.name)
        with open(pdf_path, "wb") as f:
            f.write(uploaded_file.getvalue())
        
        # Output paths
        base_name = os.path.splitext(uploaded_file.name)[0]
        output_docx = os.path.join(temp_dir, f"{base_name}_translated.docx")
        output_pdf = os.path.join(temp_dir, f"{base_name}_translated.pdf")
        
        # Create config
        config = TranslationConfig(
            pdf=pdf_path,
            source_lang=source_lang,
            target_lang=target_lang,
            model=model,
            output=os.path.join(temp_dir, f"{base_name}_translated"),
            format=output_format,
            output_dir=os.path.join(temp_dir, "cache"),
            dpi=dpi,
            workers=workers
        )
        
        # Progress tracking
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        def update_progress(completed, total, result):
            progress = completed / total
            progress_bar.progress(progress)
            
            if "error" in result:
                status_text.warning(f"Page {result['page_num']}: Error - {result['error']}")
            else:
                status_text.info(f"Translated page {result['page_num']} of {total}")
        
        # Run translation
        try:
            with st.spinner("Loading and analyzing PDF..."):
                results = run_translation_pipeline(config, progress_callback=update_progress)
            
            progress_bar.progress(1.0)
            status_text.success(f"✅ Translation complete! {len(results)} pages processed.")
            
            # Download buttons
            st.markdown("### 📥 Download Results")
            
            col1, col2 = st.columns(2)
            
            if output_format in ("docx", "both") and os.path.exists(output_docx):
                with open(output_docx, "rb") as f:
                    docx_data = f.read()
                col1.download_button(
                    label="📄 Download DOCX",
                    data=docx_data,
                    file_name=f"{base_name}_translated.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True
                )
            
            if output_format in ("pdf", "both") and os.path.exists(output_pdf):
                with open(output_pdf, "rb") as f:
                    pdf_data = f.read()
                col2.download_button(
                    label="📕 Download PDF",
                    data=pdf_data,
                    file_name=f"{base_name}_translated.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            
            # Preview section
            if results:
                with st.expander("👀 Preview Translation", expanded=True):
                    page_nums = sorted([int(k) for k in results.keys()])
                    selected_page = st.selectbox(
                        "Select page to preview",
                        page_nums,
                        format_func=lambda x: f"Page {x}"
                    )
                    
                    if selected_page:
                        page_data = results[str(selected_page)]
                        
                        st.markdown(f"**Original ({source_lang}):**")
                        st.text_area(
                            "Original",
                            page_data.get("original", ""),
                            height=200,
                            label_visibility="collapsed"
                        )
                        
                        st.markdown(f"**Translation ({target_lang}):**")
                        st.text_area(
                            "Translation",
                            page_data.get("translated", ""),
                            height=200,
                            label_visibility="collapsed"
                        )
                        
        except Exception as e:
            st.error(f"❌ Translation failed: {str(e)}")
            st.exception(e)


if __name__ == "__main__":
    main()

