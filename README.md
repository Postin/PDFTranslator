# PDF Translator

A powerful CLI and web-based tool for translating PDF documents using OpenAI's GPT-4o vision models. Supports both regular text-based PDFs and scanned documents.

## Features

- **Language Agnostic**: Translate between any language pair supported by GPT-4o
- **Smart PDF Detection**: Automatically detects text-based vs scanned PDFs
- **Parallel Processing**: Translate multiple pages simultaneously for faster results
- **Resume Support**: Interrupt and resume translations without losing progress
- **Dual Output**: Generate both DOCX and PDF with original + translated text
- **Web Interface**: User-friendly Streamlit UI with drag-and-drop upload
- **Retry Logic**: Automatic exponential backoff for API failures

## Installation

### Prerequisites

- Python 3.9+
- OpenAI API key

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd PDFTranslator
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file with your OpenAI API key:
```bash
echo "OPENAI_API_KEY=your-api-key-here" > .env
```

## Quick Start

### Easiest Way - Run Script
```bash
# macOS/Linux
./run.sh

# Windows
run.bat
```

### Using Just (Task Runner)
If you have [just](https://github.com/casey/just) installed:
```bash
just              # Show all available commands
just web          # Launch web UI
just translate doc.pdf English Spanish
just en2es doc.pdf   # Quick English → Spanish
just status       # Show cache status
just clean        # Clear cache
```

### Direct Commands
```bash
# Web UI
streamlit run app.py

# CLI
python main.py --pdf doc.pdf --source-lang English --target-lang Spanish
```

## Usage

### Command Line Interface

Basic translation:
```bash
python main.py --pdf document.pdf --source-lang English --target-lang Spanish
```

Full options:
```bash
python main.py \
  --pdf document.pdf \
  --source-lang English \
  --target-lang Spanish \
  --model gpt-4o-mini \
  --workers 3 \
  --format both \
  --output my_translation \
  --dpi 200
```

#### CLI Arguments

| Argument | Required | Default | Description |
|----------|----------|---------|-------------|
| `--pdf` | Yes | - | Path to input PDF file |
| `--source-lang` | Yes | - | Source language (e.g., English, German, Japanese) |
| `--target-lang` | Yes | - | Target language (e.g., Spanish, Serbian, French) |
| `--model` | No | `gpt-4o-mini` | OpenAI model (`gpt-4o-mini` or `gpt-4o`) |
| `--output` | No | `<pdf_name>_translated` | Output file path (without extension) |
| `--format` | No | `docx` | Output format: `docx`, `pdf`, or `both` |
| `--workers` | No | `3` | Number of parallel translation workers |
| `--resume` | No | `false` | Resume from previously cached translations |
| `--output-dir` | No | `translation_cache` | Directory for cache and intermediate files |
| `--dpi` | No | `200` | Image resolution for scanned PDF pages |
| `--sleep` | No | `0.5` | Delay between API calls (seconds) |

### Web Interface

Launch the Streamlit web UI:
```bash
streamlit run app.py
```

Then open your browser to `http://localhost:8501`

The web interface provides:
- Drag-and-drop PDF upload
- Language selection dropdowns
- Real-time translation progress
- Preview of translated pages
- Download buttons for DOCX and PDF

## Output Format

The translated documents contain both original and translated text in a sequential layout:

```
═══════════════════════════════════════
               Page 1
═══════════════════════════════════════

Original (English)
──────────────────
[Original text from the PDF...]

──────────────────────────────────────

Translation (Spanish)
─────────────────────
[Translated text...]

═══════════════════════════════════════
```

## How It Works

1. **PDF Analysis**: The tool analyzes each page to determine if it's text-based or scanned
2. **Text Extraction**: 
   - Text-based pages: Direct text extraction using PyMuPDF (fast, no API cost)
   - Scanned pages: Rendered to images and processed with GPT-4o vision
3. **Translation**: GPT-4o-mini translates the content while preserving structure
4. **Caching**: Results are cached to JSON for resume support
5. **Export**: Final documents generated in DOCX and/or PDF format

## Project Structure

```
PDFTranslator/
├── app.py                 # Streamlit web interface
├── main.py                # CLI entry point
├── cli.py                 # CLI argument parser
├── pipeline.py            # Main translation pipeline
├── config.py              # Configuration and API key loading
├── requirements.txt       # Python dependencies
├── .env                   # API keys (create this file)
├── fonts/
│   └── DejaVuSans.ttf     # Unicode font for PDF export
├── loader/
│   └── image_loader.py    # PDF loading and page analysis
├── translator/
│   └── vision_translator.py  # GPT-4o translation functions
├── exporter/
│   ├── docx_exporter.py   # Word document export
│   └── pdf_exporter.py    # PDF export
└── utils/
    ├── retry.py           # Exponential backoff decorator
    └── parallel.py        # Parallel processing utilities
```

## Examples

### Translate a German book to English
```bash
python main.py --pdf german_novel.pdf --source-lang German --target-lang English --format both
```

### Translate a scanned Japanese document with higher quality
```bash
python main.py --pdf scan.pdf --source-lang Japanese --target-lang English --dpi 300 --model gpt-4o
```

### Resume an interrupted translation
```bash
python main.py --pdf large_book.pdf --source-lang French --target-lang Spanish --resume
```

### Fast translation with more workers
```bash
python main.py --pdf report.pdf --source-lang English --target-lang Chinese --workers 5
```

## Cost Estimation

Approximate costs per page (as of 2024):

| Model | Text Page | Scanned Page |
|-------|-----------|--------------|
| gpt-4o-mini | ~$0.001 | ~$0.003 |
| gpt-4o | ~$0.01 | ~$0.03 |

*Actual costs depend on page content length.*

## Troubleshooting

### API Rate Limits
If you encounter rate limit errors, reduce the number of workers:
```bash
python main.py --pdf doc.pdf --source-lang English --target-lang Spanish --workers 1 --sleep 2
```

### Unicode Characters Not Displaying in PDF
Ensure the `fonts/DejaVuSans.ttf` file exists. The PDF exporter will fall back to Helvetica (no Unicode) if the font is missing.

### Out of Memory for Large PDFs
Process in batches by using page ranges (feature coming soon) or reduce DPI:
```bash
python main.py --pdf large.pdf --source-lang English --target-lang Spanish --dpi 150
```

## License

MIT License

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

