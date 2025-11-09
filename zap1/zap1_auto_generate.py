import sys
import os
import argparse
import json
from tqdm import tqdm

# Add project root to Python path to allow importing from gemini_cli
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from gemini_cli.api import GeminiAPI

def main():
    """
    Generates scripts for each chapter of a person's story and creates a meta.json file.
    """
    parser = argparse.ArgumentParser(description="Generate scripts and meta.json for a person's story.")
    parser.add_argument("--person", required=True, help="The name of the person to generate a story about.")
    args = parser.parse_args()
    person = args.person

    gemini = GeminiAPI()
    output_dir = "zap1/outputs"
    scripts_dir = os.path.join(output_dir, "scripts")
    os.makedirs(scripts_dir, exist_ok=True)

    # 1. Define chapter information
    chapters_config = [
        {"id": "opening", "title": "プロローグ", "bgm": "dramatic.mp3"},
        {"id": "chapter1", "title": "少年時代", "bgm": "calm.mp3"},
        {"id": "chapter2", "title": "挑戦と失敗", "bgm": "tense.mp3"},
        {"id": "chapter3", "title": "新たなる希望", "bgm": "inspiring.mp3"},
        {"id": "chapter4", "title": "栄光と代償", "bgm": "tense.mp3"},
        {"id": "ending", "title": "エピローグ", "bgm": "inspiring.mp3"}
    ]

    prompt_template = open("gemini_cli/prompts/script.txt", "r", encoding="utf-8").read()

    print(f"🎬 {person}の物語の生成を開始します...")

    # 2. & 3. Loop through chapters with a progress bar
    for ch in tqdm(chapters_config, desc="各章の台本を生成中"):
        chapter_id = ch["id"]
        chapter_title = ch["title"]
        
        chapter_path = os.path.join(scripts_dir, f"{chapter_id}.txt")

        if os.path.exists(chapter_path):
            tqdm.write(f"⏩ スキップ: {chapter_title} ({chapter_id}.txt は既に存在します)")
            continue

        tqdm.write(f"⏳ 生成中: {chapter_title}")
        
        # Generate script text
        prompt = prompt_template.format(person=person, section=chapter_title, length=1100)
        text = gemini.generate_text(prompt)
        
        with open(chapter_path, "w", encoding="utf-8") as f:
            f.write(text)
        
        tqdm.write(f"✅ 保存完了: {chapter_path}")

    # 4. Create meta.json after all chapters are processed
    meta_chapters = []
    for ch in chapters_config:
        meta_chapters.append({
            "id": ch["id"],
            "title": ch["title"],
            "bgm": ch["bgm"],
            "script_path": os.path.join(output_dir, "scripts", f"{ch['id']}.txt").replace("\\\\", "/")
        })

    meta_content = {
        "title": f"{person}の物語",
        "chapters": meta_chapters
    }

    meta_path = os.path.join(output_dir, "meta.json")
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta_content, f, ensure_ascii=False, indent=2)

    # 6. Display final message
    print(f"\n✨ すべての章が生成され、{meta_path}を出力しました。")

if __name__ == '__main__':
    # 5. How to run: python3 zap1/zap1_auto_generate.py --person "Walt Disney"
    main()
