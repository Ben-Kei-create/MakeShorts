#!/usr/bin/env python3
import os, json, glob, argparse, re, subprocess
from pathlib import Path
from collections import defaultdict

# ---------- ユーティリティ ----------
def slugify(s:str)->str:
    s = s.strip()
    s = re.sub(r"[^\w\s-]", "", s, flags=re.UNICODE)
    s = re.sub(r"[\s]+", "-", s)
    return s.lower()

def load_master(package_path:str)->dict:
    with open(package_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if "package" not in data or "script" not in data["package"] or "chapters" not in data["package"]["script"]:
        raise ValueError("master JSON の形式が不十分です（package.script.chapters が必要）")
    return data

def ensure_dir(p:Path):
    p.mkdir(parents=True, exist_ok=True)

# ---------- 章バッチ生成（emotion_level付き） ----------
def create_chapter_batches(master:dict, scripts_out_dir:Path):
    pkg = master.get("package", {})
    chapters = pkg.get("script", {}).get("chapters", [])
    thumbnails = pkg.get("thumbnails", [])
    curve = pkg.get("emotion_curve", [])

    prompt_lookup = defaultdict(lambda: {"still": [], "motion": []})
    for t in thumbnails:
        slot = t.get("slot")
        if slot:
            prompt_lookup[slot]["still"].append(t.get("still_prompt",""))
            prompt_lookup[slot]["motion"].append(t.get("motion_prompt",""))

    emotion_lookup = {item.get("chapter_index"): item.get("level") for item in curve}

    ensure_dir(scripts_out_dir)
    for idx, ch in enumerate(chapters):
        chap_id = ch.get("id")
        if not chap_id:
            continue
        batch = {
            "chapter_index": idx,
            "id": chap_id,
            "title": ch.get("title",""),
            "duration_sec": ch.get("time",{}).get("duration_sec",0),
            "narration_text": ch.get("narration",""),
            "still_prompts": prompt_lookup[chap_id]["still"][:3],
            "motion_prompts": prompt_lookup[chap_id]["motion"][:3],
            "bgm_tag": ch.get("audio",{}).get("bgm_tag",""),
            "sfx": ch.get("audio",{}).get("sfx",[]),
            "lesson": ch.get("lesson",""),
            "emotion_level": emotion_lookup.get(idx, 5),
            "voice_speaker": "ずんだもん",
            "output_paths": {
                "image_dir": f"zap1/images/{chap_id}/",
                "voice_path": f"zap1/voice/{chap_id}.wav"
            }
        }
        out = scripts_out_dir / f"chapter_{idx:02d}_{chap_id}.json"
        with open(out, "w", encoding="utf-8") as f:
            json.dump(batch, f, ensure_ascii=False, indent=2)
    print(f"🧩 章バッチ生成完了: {scripts_out_dir}")

# ---------- 字幕（SRT）生成 + CapCut統合 ----------
def to_srt_lines(narration:str, start_sec:float, duration:float, max_chars:int=24):
    # 超単純ブレイク：句点・改行・長さで分割
    text = narration.replace("\r","").strip()
    parts = []
    buf = ""
    for ch in text:
        buf += ch
        if ch in ".。!?\n" or len(buf) >= max_chars:
            parts.append(buf.strip())
            buf = ""
    if buf.strip():
        parts.append(buf.strip())
    if not parts:
        return []

    seg_dur = duration / len(parts)
    lines = []
    cur = start_sec
    for i, seg in enumerate(parts, 1):
        st = cur
        en = start_sec + duration if i==len(parts) else (cur + seg_dur)
        lines.append((i, st, en, seg))
        cur = en
    return lines

def fmt_ts(sec:float):
    if sec < 0: sec = 0
    ms = int(round((sec - int(sec)) * 1000))
    s = int(sec) % 60
    m = (int(sec) // 60) % 60
    h = int(sec) // 3600
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

def gen_subtitles_and_integrate(master:dict, srt_out_dir:Path, ccproj_path:Path):
    pkg = master["package"]
    chapters = pkg["script"]["chapters"]
    ensure_dir(srt_out_dir)

    # グローバルタイムを章のdurationで進める
    g = 0.0
    cc_sub_clips = []
    for idx, ch in enumerate(chapters):
        dur = float(ch.get("time",{}).get("duration_sec",0) or 0)
        if dur <= 0:
            continue
        nid = ch.get("id", f"chapter{idx}")
        narration = ch.get("narration","")
        lines = to_srt_lines(narration, g, dur)

        # SRT出力
        srt_path = srt_out_dir / f"chapter_{idx:02d}_{nid}.srt"
        with open(srt_path, "w", encoding="utf-8") as sf:
            for no, st, en, seg in lines:
                sf.write(f"{no}\n{fmt_ts(st)} --> {fmt_ts(en)}\n{seg}\n\n")
        print(f"📝 {srt_path} を生成")

        # CapCut字幕トラック用
        cc_sub_style = {
            "font_family":"Hiragino Sans",
            "font_size": 42,
            "fill": "#FFFFFF",
            "stroke": {"color":"#000000","width":4},
            "align":"center",
            "position":"bottom_center",
            "margin_bottom": 80
        }
        # visual_styleがあれば上書き
        if "visual_style" in ch:
            if "subtitle_fade_in" in ch["visual_style"]:
                cc_sub_style["fade_in"] = ch["visual_style"]["subtitle_fade_in"]
            if "subtitle_fade_out" in ch["visual_style"]:
                cc_sub_style["fade_out"] = ch["visual_style"]["subtitle_fade_out"]

        for no, st, en, seg in lines:
            cc_sub_clips.append({
                "start": round(st,3),
                "duration": round(en - st,3),
                "text": seg,
                "style": cc_sub_style
            })
        g += dur

    # CapCutプロジェクトへ統合
    if ccproj_path.exists():
        with open(ccproj_path, "r", encoding="utf-8") as f:
            proj = json.load(f)
        track = None
        for t in proj.get("tracks", []):
            if t.get("type") == "subtitles":
                track = t
                break
        if track is None:
            proj.setdefault("tracks", []).append({"type":"subtitles","clips":[]})
            track = proj["tracks"][-1]
        track["clips"] = cc_sub_clips
        with open(ccproj_path, "w", encoding="utf-8") as f:
            json.dump(proj, f, ensure_ascii=False, indent=2)
        print(f"✅ CapCut字幕トラック統合: {ccproj_path}")
    else:
        print("⚠ CapCutプロジェクトが未生成のため字幕統合をスキップしました。")

# ---------- メイン ----------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--package", required=True, help="人物ごとの master.json (packages/<slug>/master.json)")
    ap.add_argument("--images-root", default="zap1/images")
    ap.add_argument("--voice-root",  default="zap1/voice")
    ap.add_argument("--bgm-root",    default="zap1/bgm")
    ap.add_argument("--outdir",      default="zap1/output")
    ap.add_argument("--scripts-dir", default="zap1/outputs/scripts", help="章バッチJSONの出力先ディレクトリ")
    ap.add_argument("--export",      action="store_true", help="CapCutをGUI自動操作で書き出し")
    args = ap.parse_args()

    master = load_master(args.package)
    person = master["package"].get("person") or "project"
    slug = slugify(person)

    # 出力系パス
    outputs_root = Path("zap1/outputs")
    ensure_dir(outputs_root)
    master_out = outputs_root / f"{slug}_master.json"
    with open(master_out, "w", encoding="utf-8") as f:
        json.dump(master, f, ensure_ascii=False, indent=2)
    print(f"📦 master を保存: {master_out}")

    scripts_dir = Path(args.scripts_dir)
    create_chapter_batches(master, scripts_dir)

    # CapCutプロジェクト生成
    outdir = Path(args.outdir)
    ensure_dir(outdir)
    ccproj = outdir / f"{slug}_capcut.ccproj"
    shotcsv = outdir / f"{slug}_shotlist.csv"

    cmd = [
        "python3", "build_capcut_project.py",
        "--scripts-dir", str(scripts_dir),
        "--images-root", args.images_root,
        "--voice-root",  args.voice_root,
        "--bgm-root",    args.bgm_root,
        "--out-ccproj",  str(ccproj),
        "--out-csv",     str(shotcsv),
    ]
    print("🛠  CapCutプロジェクト生成:", " ".join(cmd))
    subprocess.run(cmd, check=True)
    print(f"✅ CapCutプロジェクト: {ccproj}")
    print(f"✅ ショットリスト:      {shotcsv}")

    # 字幕生成 + 統合
    srt_out = outputs_root / "subtitles"
    gen_subtitles_and_integrate(master, srt_out, ccproj)

    # 任意：自動エクスポート（GUI）
    if args.export:
        # ここはあなたが以前使った GUI 自動化スクリプトを再利用想定
        # 例: python3 zap1/export_capcut_auto.py --project <ccproj> --out <mp4>
        exported = outdir / "exported" / f"{slug}_final.mp4"
        ensure_dir(exported.parent)
        print("🚀 CapCut自動エクスポート開始（GUI操作）")
        try:
            subprocess.run([
                "python3","zap1/export_capcut_auto.py",
                "--project", str(ccproj),
                "--out",     str(exported)
            ], check=True)
        except Exception as e:
            print("⚠ 自動エクスポートに失敗しました:", e)
        else:
            print(f"🎬 エクスポート完了: {exported}")

if __name__ == "__main__":
    main()
