#!/usr/bin/env python3
import json, argparse, os, subprocess
from pathlib import Path

# ========= ユーティリティ =========
def ensure_dir(p: Path):
    p.mkdir(parents=True, exist_ok=True)

def load_master(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

# ========= 単章テスト用処理 =========
def extract_single_chapter(master: dict, chapter_index: int = 0) -> dict:
    pkg = master["package"]
    script = pkg.get("script", {})
    chapters = script.get("chapters", [])
    if not chapters:
        raise ValueError("❌ master.json に chapters がありません。")

    if chapter_index >= len(chapters):
        raise IndexError(f"❌ chapter_index {chapter_index} は範囲外です。")

    single = chapters[chapter_index]
    print(f"🎬 テスト対象: 第{chapter_index+1}章「{single.get('title','無題')}」")

    # 一章だけのmaster構成を生成
    # emotion_levelは元の章のものを引き継ぐ
    emotion_level = 5
    for item in pkg.get("emotion_curve", []):
        if item.get("chapter_index") == chapter_index:
            emotion_level = item.get("level", 5)
            break

    pkg["script"]["chapters"] = [single]
    pkg["emotion_curve"] = [{"chapter_index": 0, "level": emotion_level}] # テスト用なので0章として扱う
    return {"package": pkg}

def inject_visual_meta(chapter_json: Path, grade: str, fade: float):
    with open(chapter_json, "r", encoding="utf-8") as f:
        ch = json.load(f)
    ch["visual_style"] = {
        "grade": grade,            # "warm" / "cool" / "desaturated"
        "subtitle_fade_in": fade,  # 秒数
        "subtitle_fade_out": fade
    }
    with open(chapter_json, "w", encoding="utf-8") as f:
        json.dump(ch, f, ensure_ascii=False, indent=2)
    print(f"✨ グレーディング({grade})＋字幕フェード({fade}s)を付与 → {chapter_json}")

# ========= メイン処理 =========
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--package", required=True, help="テスト対象 master.json")
    ap.add_argument("--chapter", type=int, default=0, help="テストする章番号 (0開始)")
    ap.add_argument("--grade", default="warm", help="グレーディングタイプ (warm/cool/desaturated)")
    ap.add_argument("--fade", type=float, default=0.5, help="字幕フェード秒数")
    args = ap.parse_args()

    master = load_master(args.package)
    single_master = extract_single_chapter(master, args.chapter)

    # 出力先
    out_dir = Path("zap1/test_output")
    ensure_dir(out_dir)
    test_json = out_dir / "test_master.json"
    with open(test_json, "w", encoding="utf-8") as f:
        json.dump(single_master, f, ensure_ascii=False, indent=2)
    print(f"🧩 テスト用 master.json 作成: {test_json}")

    # 一章だけバッチ生成
    # make_all.py は scripts-dir を引数で受け取るので、テスト用のscriptsディレクトリを指定
    scripts_out_dir = out_dir / "scripts"
    ensure_dir(scripts_out_dir)
    
    # make_all.py を呼び出す際に、scripts-dir と outdir をテスト用に指定
    cmd = [
        "python3", "make_all.py",
        "--package", str(test_json),
        "--outdir", str(out_dir.parent), # zap1/output を指すように調整
        "--scripts-dir", str(scripts_out_dir) # zap1/test_output/scripts を指すように調整
    ]
    print("🚀 make_all.py 実行:", " ".join(cmd))
    subprocess.run(cmd, check=True)

    # グレーディング・フェード追加
    # make_all.py が生成したバッチJSONは scripts_out_dir にある
    chapter_files = sorted(scripts_out_dir.glob("chapter_*.json"))
    if chapter_files:
        inject_visual_meta(chapter_files[0], args.grade, args.fade)
    else:
        print("⚠ バッチJSONが見つかりませんでした。")

    print("\n✅ テスト完了。CapCutで zap1/output/test_capcut.ccproj を確認してください。")

if __name__ == "__main__":
    main()