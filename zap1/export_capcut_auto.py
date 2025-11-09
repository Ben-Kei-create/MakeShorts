import pyautogui
import subprocess
import time
import os
import argparse
from pathlib import Path

def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--project", required=True, help="Path to the CapCut project file (.ccproj)")
    p.add_argument("--out",     required=True, help="Output path for the exported MP4 file")
    return p.parse_args()

# ========= 設定 =========
CAPCUT_PATH = "/Applications/CapCut.app/Contents/MacOS/CapCut"
EXPORT_WAIT_SEC = 60  # 書き出し時間（動画長に応じて調整）
# ========================

def open_capcut(project_path):
    print("🚀 CapCut起動中...")
    if not os.path.exists(CAPCUT_PATH):
        print(f"❌ エラー: CapCutアプリケーションが見つかりません: {CAPCUT_PATH}")
        print("     CAPCUT_PATHを正しいパスに設定してください。")
        return False
    if not os.path.exists(project_path):
        print(f"❌ エラー: CapCutプロジェクトファイルが見つかりません: {project_path}")
        return False
        
    subprocess.Popen([CAPCUT_PATH, os.path.abspath(project_path)])
    print("⏳ CapCutがプロジェクトを開くまで15秒待機します...")
    time.sleep(15)  # CapCutがプロジェクトを開くまで待つ
    return True

def export_project(output_mp4_path):
    print("🎬 エクスポート開始準備中...")
    
    # ===== 以下、座標を環境に合わせて一度だけ調整 =====
    # 注意: これらの座標はディスプレイ解像度やUIのレイアウトに依存します。
    # pyautogui.position() を使ってご自身の環境で座標を取得してください。
    EXPORT_BTN = (1800, 60)      # 右上の「エクスポート」ボタン (例)
    FILENAME_FIELD = (1000, 400) # 保存名入力欄 (例)
    CONFIRM_BTN = (1000, 750)    # 保存確定ボタン (例)
    # ===============================================

    print(f"🖱️ 「エクスポート」ボタンをクリックします: {EXPORT_BTN}")
    pyautogui.click(EXPORT_BTN)
    time.sleep(3) # ダイアログ表示待機

    print(f"🖱️ ファイル名入力欄をクリックします: {FILENAME_FIELD}")
    pyautogui.click(FILENAME_FIELD)
    time.sleep(1)

    # Clear existing text (Ctrl/Cmd+A, then Backspace)
    pyautogui.hotkey('command', 'a')
    time.sleep(0.5)
    pyautogui.press('backspace')
    
    export_filename = Path(output_mp4_path).stem
    print(f"⌨️ ファイル名を入力します: {export_filename}")
    pyautogui.typewrite(export_filename, interval=0.1)
    time.sleep(1)

    print(f"🖱️ 「エクスポート」確定ボタンをクリックします: {CONFIRM_BTN}")
    pyautogui.click(CONFIRM_BTN)
    
    print(f"💾 書き出し中... ({EXPORT_WAIT_SEC}秒待機します)")
    time.sleep(EXPORT_WAIT_SEC)
    
    print(f"✅ エクスポート完了！保存先: {output_mp4_path}")

if __name__ == "__main__":
    args = parse_args()
    if open_capcut(args.project):
        export_project(args.out)
