import argparse


def build_cli_parser():
    parser = argparse.ArgumentParser(
        description="Translate PDF documents (regular or scanned) using GPT-4o-mini vision"
    )
    parser.add_argument(
        "--pdf",
        type=str,
        required=True,
        help="Path to input PDF file"
    )
    parser.add_argument(
        "--source-lang",
        type=str,
        required=True,
        help="Source language (e.g., English, German, Japanese)"
    )
    parser.add_argument(
        "--target-lang",
        type=str,
        required=True,
        help="Target language (e.g., Serbian, Spanish, French)"
    )
    parser.add_argument(
        "--model",
        type=str,
        default="gpt-4o-mini",
        help="OpenAI model to use (default: gpt-4o-mini)"
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Output file path (default: <pdf_name>_translated.docx)"
    )
    parser.add_argument(
        "--format",
        type=str,
        choices=["docx", "pdf", "both"],
        default="docx",
        help="Output format: docx, pdf, or both (default: docx)"
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Resume from previously translated pages"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="translation_cache",
        help="Cache directory for intermediate files"
    )
    parser.add_argument(
        "--dpi",
        type=int,
        default=200,
        help="Resolution for image rendering (for scanned PDFs)"
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=3,
        help="Number of parallel workers for translation (default: 3)"
    )
    parser.add_argument(
        "--sleep",
        type=float,
        default=0.5,
        help="Sleep between API calls to avoid rate limits (default: 0.5)"
    )
    return parser
