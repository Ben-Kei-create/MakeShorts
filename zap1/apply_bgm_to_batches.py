import os
import json
import glob

BGM_DIR = "zap1/bgm"
SCRIPT_DIR = "zap1/outputs/scripts"

def get_bgm_files():
    """BGMフォルダ内のmp3/wav/m4aをソートして取得"""
    bgm_files = sorted(
        [f for f in os.listdir(BGM_DIR) if f.lower().endswith((".mp3", ".wav", ".m4a"))]
    )
    if not bgm_files:
        raise FileNotFoundError("⚠️ BGMフォルダが空です。zap1/bgm/ に曲を配置してください。")
    return bgm_files

def assign_bgm_to_chapters():
    """各章JSONに順番でBGMファイルを追加"""
    bgm_files = get_bgm_files()
    batch_files = sorted(glob.glob(os.path.join(SCRIPT_DIR, "chapter_*.json")))

    print(f"🎬 {len(bgm_files)}曲のBGMを {len(batch_files)}章に割り当てます。\n")

    for i, batch_path in enumerate(batch_files):
        with open(batch_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        bgm_file = bgm_files[i % len(bgm_files)]
        bgm_path = os.path.join(BGM_DIR, bgm_file)

        if "output_paths" not in data:
            data["output_paths"] = {}
        data["output_paths"]["bgm_path"] = bgm_path.replace("\\\\", "/") # Ensure forward slashes for paths

        with open(batch_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"✅ {os.path.basename(batch_path)} → 🎵 {bgm_file}")

    print(f"\n🎶 全 {len(batch_files)}章へのBGM割り当て完了！")


if __name__ == "__main__":
    assign_bgm_to_chapters()