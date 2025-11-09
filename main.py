import argparse
import subprocess
from config.model_registry import GEMINI_MODELS

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--person", required=True)
    args = parser.parse_args()
    person = args.person

    print(f"🎬 素材生成開始: {person}")
    subprocess.run(["python3", "-m", "zap1.zap1_auto_generate", "--person", person])

    print(f"🎞️ 動画生成開始: {person}")
    subprocess.run(["python3", "-m", "zap2.shorts_pipeline", person, "--model", GEMINI_MODELS["default"]])

if __name__ == "__main__":
    main()