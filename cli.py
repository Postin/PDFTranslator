import argparse


def build_cli_parser():
    parser = argparse.ArgumentParser(
        description="📘 Translate scanned PDF books using GPT-4o vision"
    )
    parser.add_argument("--pdf", type=str, required=True, help="Path to input scanned PDF")
    parser.add_argument("--lang", type=str, default="both", choices=["english", "srpski", "both"], help="Translation output")
    parser.add_argument("--model", type=str, default="gpt-4o", help="OpenAI model to use (e.g. gpt-4o, gpt-4o-mini)")
    parser.add_argument("--font", type=str, default="fonts/DejaVuSans.ttf", help="Path to UTF-8 TTF font file")
    parser.add_argument("--font-name", type=str, default="DejaVuSans", help="Font internal name")
    parser.add_argument("--to-pdf", action="store_true", help="Export to PDF")
    parser.add_argument("--to-docx", action="store_true", help="Export to Word DOCX")
    parser.add_argument("--resume", action="store_true", help="Resume from previously translated pages")
    parser.add_argument("--output-dir", type=str, default=None, help="Override output path (by default uses data/<bookname>/translated_pages)")
    parser.add_argument("--dpi", type=int, default=200, help="Resolution for image rendering")
    parser.add_argument("--sleep", type=float, default=1.5, help="Sleep between GPT calls (to avoid rate limits)")
    return parser