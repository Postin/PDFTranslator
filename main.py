from cli import build_cli_parser
from vision_pipeline import run_vision_translation_pipeline
from loader import pdf_type_detector
from loader.pdf_type_detector import is_scanned_pdf


def main():
    parser = build_cli_parser()
    args = parser.parse_args()

    # figure out which pipeline to use (digital vs scanned pdf)
    pdf_path = args['pdf']

    if is_scanned_pdf(pdf_path):
        print("Detected scanned/image-based PDF → using image conversion")
        run_vision_translation_pipeline(args)
    else:
        print("Detected digital/text-based PDF → extracting text directly")


if __name__ == "__main__":
    main()
