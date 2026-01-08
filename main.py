from cli import build_cli_parser


def main():
    parser = build_cli_parser()
    args = parser.parse_args()
    
    from pipeline import run_translation_pipeline
    run_translation_pipeline(args)


if __name__ == "__main__":
    main()
