import json, os, glob
from pathlib import Path
from natsort import natsorted
import argparse

def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--scripts-dir", default="zap1/outputs/scripts")
    p.add_argument("--images-root", default="zap1/images")
    p.add_argument("--voice-root",  default="zap1/voice")
    p.add_argument("--bgm-root",    default="zap1/bgm")
    p.add_argument("--out-ccproj",  default="zap1/output/walt_capcut.ccproj")
    p.add_argument("--out-csv",     default="zap1/output/shotlist.csv")
    return p.parse_args()

# 既存の定数を引数で上書き
args = parse_args()
SCRIPTS_DIR = args.scripts_dir
IMAGES_ROOT = args.images_root
VOICE_ROOT  = args.voice_root
BGM_ROOT    = args.bgm_root
OUT_CCPROJ  = args.out_ccproj
OUT_CSV     = args.out_csv

FPS = 30
IMG_FIT = "cover"      # "cover" or "contain"（レターボックス回避推奨は"cover"）
IMG_XFADE_SEC = 0.5     # 画像クリップ間の微フェード
AUDIO_FADE_SEC = 1.5    # BGMの曲間クロスフェード
DUCKING_DB = -12        # ボイス下でBGMを-12dB
PADDING_LEAD = 0.0      # 先頭余白(秒)
# ============================================================

def read_chapter_batches():
    files = natsorted(glob.glob(os.path.join(SCRIPTS_DIR, "chapter_*.json")))
    chapters = []
    for f in files:
        with open(f, "r", encoding="utf-8") as rf:
            data = json.load(rf)
            chapters.append(data)
    # chapter_indexでソート（安全策）
    chapters = sorted(chapters, key=lambda x: x.get("chapter_index", 0))
    return chapters

def sec2frame(s): return int(round(s * FPS))

def ensure_dirs():
    Path(os.path.dirname(OUT_CCPROJ)).mkdir(parents=True, exist_ok=True)

def motion_by_emotion(level:int, index:int):
    """emotion_levelに応じたKen Burnsプリセットを返す"""
    if level <= 2:
        base = "kenburns-zoom-out"
    elif level <= 4:
        base = "kenburns-pan-right"
    elif level <= 6:
        base = "kenburns-zoom-in"
    elif level <= 8:
        base = "kenburns-pan-left"
    else:
        base = "kenburns-zoom-in"
    # 軽いバリエーション付け
    if index % 2 == 0 and "zoom" in base:
        base += "-slow"
    return base

def make_timeline(chapters):
    """
    内部的な『汎用CapCut風プロジェクトJSON』を構築。
    ※CapCutはバージョンでスキーマが変わる可能性があるため、
      「パス・開始秒・長さ・トラック構造」を素直に持つ最小構成を出力。
      読み込み時にズレたら、このJSONを基にCapCutで手修正しやすい。
    """
    t = {
        "meta": {"name": "Walt Documentary Auto Timeline", "fps": FPS, "resolution": "1920x1080"},
        "tracks": [
            {"type": "video", "clips": []},   # 画像並べ
            {"type": "audio", "role": "voice", "clips": []},   # 章ボイス
            {"type": "audio", "role": "bgm", "clips": []},     # BGM
            {"type": "subtitles", "clips": []}                 # 予備（今回は未使用）
        ],
        "mix": {
            "ducking": {"enable": True, "under_role": "voice", "target_role": "bgm", "gain_db": DUCKING_DB}
        }
    }

    # === 映像・ボイス ===
    global_time = PADDING_LEAD
    shotlist_rows = []

    video_track = t["tracks"][0]["clips"]
    voice_track = t["tracks"][1]["clips"]

    for chap in chapters:
        chap_id = chap["id"]
        dur = float(chap.get("duration_sec", 0) or 0)
        if dur <= 0: 
            continue

        # 画像3枚が基本（不足は章内で繰り返し）
        stills = chap.get("still_prompts", [])  # 中身はプロンプトだが、実ファイルは images/<id> 内の実体を使う
        # 実ファイルを拾う（*.png, *.jpg）
        img_files = natsorted(
            glob.glob(os.path.join(IMAGES_ROOT, chap_id, "*.png")) +
            glob.glob(os.path.join(IMAGES_ROOT, chap_id, "*.jpg")) +
            glob.glob(os.path.join(IMAGES_ROOT, chap_id, "*.jpeg"))
        )
        if not img_files:
            # 画像が未生成でも、空白フレームにならないようにプレースホルダ扱い
            img_files = []

        # 3分割
        per = dur / max(1, max(3, len(img_files)))  # 画像が多ければ均等分割
        frames = []
        # 並べる対象
        targets = img_files if img_files else []
        if img_files and len(img_files) < 3:
            # 2以下なら重複使用
            while len(targets) < 3:
                targets += img_files
            targets = targets[:3]
        elif not img_files:
            # 本当に何も無い場合はダミーエントリ（CapCut上で後差し替え）
            targets = [f"[MISSING:{chap_id}:img{i+1}]" for i in range(3)]

        start = global_time
        for i, path in enumerate(targets):
            length = per
            if i == len(targets)-1:
                # 端数は最後に吸収
                length = (PADDING_LEAD + sum([c.get('duration_sec',0) for c in chapters[:chapters.index(chap)]]) 
                          + dur) - (start)

            # 感情レベルに応じたモーションを適用
            emotion_level = chap.get("emotion_level", 5)  # デフォルト5
            motion = motion_by_emotion(emotion_level, i)
            video_track.append({
                "path": path.replace("\\\\", "/"),
                "start": round(start, 3),
                "duration": round(length, 3),
                "fit": IMG_FIT,
                "transition_in": {"type": "fade", "duration": IMG_XFADE_SEC} if i>0 else None,
                "transition_out": {"type": "fade", "duration": IMG_XFADE_SEC} if i < len(targets)-1 else None,
                "motion": {"preset": motion, "emotion_level": emotion_level}
            })
            shotlist_rows.append([chap["chapter_index"], chap_id, path, round(start,3), round(length,3)])
            start += length

        # ボイス
        voice_path = os.path.join(VOICE_ROOT, f"{chap_id}.wav")
        if os.path.exists(voice_path):
            voice_track.append({
                "path": voice_path.replace("\\\\", "/"),
                "start": round(global_time, 3),
                "duration": round(dur, 3),
                "fade_in": AUDIO_FADE_SEC/2,
                "fade_out": AUDIO_FADE_SEC/2
            })

        global_time += dur

    # === BGM（フォルダ内を順に敷き詰め・曲間クロスフェード） ===
    bgm_files = natsorted(
        glob.glob(os.path.join(BGM_ROOT, "*.mp3")) +
        glob.glob(os.path.join(BGM_ROOT, "*.wav")) +
        glob.glob(os.path.join(BGM_ROOT, "*.m4a")) +
        glob.glob(os.path.join(BGM_ROOT, "*.flac"))
    )
    total_len = PADDING_LEAD + sum(float(c.get("duration_sec",0) or 0) for c in chapters)
    bgm_track = t["tracks"][2]["clips"]

    tpos = 0.0
    idx = 0
    while tpos < total_len and bgm_files:
        fpath = bgm_files[idx % len(bgm_files)]
        # 仮：曲長は未知→CapCut側で曲末まで自動延長してくれるケース多し。
        # ここでは「チャプターの境目に合わせず、全体を順送り」で置く。
        # （必要ならffprobe等で実長取得→明示長にしてもOK）
        clip_len = min(190.0, total_len - tpos)  # だいたい3分弱相当・末尾で打ち切り
        bgm_track.append({
            "path": fpath.replace("\\\\", "/"),
            "start": round(max(0, tpos - (idx>0)*AUDIO_FADE_SEC), 3),
            "duration": round(clip_len + (idx>0)*AUDIO_FADE_SEC, 3),
            "fade_in": AUDIO_FADE_SEC if idx>0 else 0.5,
            "fade_out": AUDIO_FADE_SEC
        })
        tpos += clip_len
        idx += 1

    return t, shotlist_rows

def write_outputs(project_json, shotlist_rows):
    ensure_dirs()
    with open(OUT_CCPROJ, "w", encoding="utf-8") as wf:
        json.dump(project_json, wf, ensure_ascii=False, indent=2)

    # 参照用ショットリスト
    import csv
    with open(OUT_CSV, "w", encoding="utf-8", newline="") as cf:
        w = csv.writer(cf)
        w.writerow(["chapter_index","chapter_id","image_path","start_sec","duration_sec"])
        w.writerows(shotlist_rows)

from shutil import copyfile

def copy_to_capcut_projects(out_ccproj_path: str, person_name: str):
    """生成された.ccprojをCapCutのローカルプロジェクトフォルダにコピーする"""
    try:
        # CapCutのローカルプロジェクトフォルダ
        base_dir = "/Users/fumiaki/Movies/CapCut/User Data/projects"
        project_dir = os.path.join(base_dir, person_name.replace(" ", "_"))
        os.makedirs(project_dir, exist_ok=True)

        dest_path = os.path.join(project_dir, f"{person_name.replace(' ', '_')}.ccproj")
        copyfile(out_ccproj_path, dest_path)

        print(f"📦 CapCutプロジェクトフォルダにコピー完了: {dest_path}")
        print("   → CapCutを開けばホーム画面に自動で表示されます。")
    except Exception as e:
        print(f"⚠️ CapCutプロジェクトフォルダへのコピーに失敗: {e}")

def main():
    chapters = read_chapter_batches()
    project_json, shotlist_rows = make_timeline(chapters)
    write_outputs(project_json, shotlist_rows)
    print(f"✅ CapCutプロジェクトJSONを書き出し: {OUT_CCPROJ}")
    print(f"✅ ショットリストCSVを書き出し:      {OUT_CSV}")
    print("   → CapCutで .ccproj を開けばタイムラインが展開されます。")

    # CapCutローカルプロジェクトへの自動コピー
    try:
        # 人名を抽出（ファイル名などから判定）
        person_name = Path(OUT_CCPROJ).stem.split("_capcut")[0] # _capcutまで含めてsplit
        copy_to_capcut_projects(OUT_CCPROJ, person_name)
    except Exception as e:
        print(f"⚠️ 自動コピー中にエラー: {e}")

if __name__ == "__main__":
    main()
