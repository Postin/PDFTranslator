# PDF Translator - Task Runner
# Install just: https://github.com/casey/just

# Default recipe - show help
default:
    @just --list

# Install dependencies
install:
    pip install -r requirements.txt

# Run the web UI
web:
    streamlit run app.py

# Run CLI translation (requires arguments)
translate pdf source target:
    python main.py --pdf {{pdf}} --source-lang {{source}} --target-lang {{target}} --format both

# Run CLI with resume
resume pdf source target:
    python main.py --pdf {{pdf}} --source-lang {{source}} --target-lang {{target}} --resume --format both

# Quick translate English to Spanish
en2es pdf:
    python main.py --pdf {{pdf}} --source-lang English --target-lang Spanish --format both

# Quick translate English to Serbian  
en2sr pdf:
    python main.py --pdf {{pdf}} --source-lang English --target-lang Serbian --format both

# Clean cache and output files
clean:
    rm -rf translation_cache/
    rm -f *_translated.docx *_translated.pdf

# Clean everything including venv
clean-all: clean
    rm -rf .venv/ __pycache__/ */__pycache__/

# Setup project from scratch
setup:
    python -m venv .venv
    .venv/bin/pip install -r requirements.txt
    @echo "Setup complete! Activate with: source .venv/bin/activate"
    @echo "Then run: just web"

# Check if .env exists
check-env:
    @test -f .env || (echo "ERROR: .env file not found. Create it with your OPENAI_API_KEY" && exit 1)
    @echo ".env file found ✓"

# Run web UI with env check
run: check-env web

# Show translation cache status
status:
    @echo "=== Translation Cache ==="
    @test -f translation_cache/translation_cache.json && cat translation_cache/translation_cache.json | python -c "import sys,json; d=json.load(sys.stdin); print(f'Pages cached: {len(d)}')" || echo "No cache found"
    @echo ""
    @echo "=== Cached Images ==="
    @ls -la translation_cache/images/ 2>/dev/null || echo "No images cached"

