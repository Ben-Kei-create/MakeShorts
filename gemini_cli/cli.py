import argparse
from gemini_cli.api import GeminiAPI
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description="Gemini CLI for MakeShorts")
    parser.add_argument("--person", required=True, help="対象人物名（例：ウォルト・ディズニー）")
    parser.add_argument("--task", choices=["script", "thumbnail", "seo"], default="script")
    parser.add_argument("--section", default="第1章")
    parser.add_argument("--length", type=int, default=1100)
    parser.add_argument("--max_tokens", type=int, default=2048)
    parser.add_argument("--temperature", type=float, default=0.7)
    args = parser.parse_args()

    gemini = GeminiAPI()
    template_path = Path(__file__).parent / "prompts" / f"{args.task}.txt"
    prompt = template_path.read_text(encoding="utf-8").format(
        person=args.person, section=args.section, length=args.length
    )

    output = gemini.generate_text(prompt, max_tokens=args.max_tokens, temperature=args.temperature)
    print(output)

if __name__ == "__main__":
    main()