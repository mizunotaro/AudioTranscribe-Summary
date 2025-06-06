#!/usr/bin/env python3
"""
transcribe_files.py

動画・音声ファイルを OpenAI Whisper で文字起こしし、
さらに文字起こしテキストを LLM で要約して保存するスクリプト。
各種パスやモデルは .env で設定可能（デフォルト値あり）。
"""

import openai
import os
from pathlib import Path
import subprocess
import shutil
from dotenv import load_dotenv
import sys
from math import floor
import json

# .env ファイルから環境変数を読み込む
load_dotenv()

# --- 定数設定 ---
DEFAULT_MODEL_NAME = "gpt-4o-mini-transcribe"
MODEL_NAME_FROM_ENV = os.getenv("WHISPER_MODEL_NAME", DEFAULT_MODEL_NAME)

SUMMARY_MODEL_NAME = os.getenv("SUMMARY_MODEL_NAME", "o3-mini")

# PROMPT_PATH は必須
PROMPT_PATH_ENV = os.getenv("PROMPT_PATH")
if not PROMPT_PATH_ENV:
    print("エラー: 要約用プロンプトファイルが .env の PROMPT_PATH に指定されていません", file=sys.stderr)
    sys.exit(1)
PROMPT_PATH = Path(PROMPT_PATH_ENV)
try:
    with open(PROMPT_PATH, encoding="utf-8") as f:
        hr_config = json.load(f)
except Exception as e:
    print(f"プロンプト読み込みエラー: {e}", file=sys.stderr)
    hr_config = {}

TARGET_AUDIO_FORMAT = "mp3"
MAX_FILE_SIZE_BYTES = 25 * 1024 * 1024
MAX_MODEL_SECONDS = 25
SIZE_MARGIN_SEC = 5
MODEL_MARGIN_SEC = 5

# OpenAI クライアント初期化
try:
    client = openai.OpenAI()
    if not client.api_key:
        raise openai.AuthenticationError("APIキーが設定されていません。")
except Exception as e:
    print(f"OpenAI クライアント初期化エラー: {e}", file=sys.stderr)
    client = None

def ensure_dir(directory: Path):
    directory.mkdir(parents=True, exist_ok=True)

def get_output_filename(input_file: Path, output_dir: Path) -> Path:
    return output_dir / (input_file.stem + ".txt")

def convert_audio_for_api(input_file: Path, temp_dir: Path) -> list[Path] | None:
    stem = input_file.stem
    tmp_mp3 = temp_dir / f"{stem}_for_api.{TARGET_AUDIO_FORMAT}"
    try:
        print(f"再エンコード: {input_file.name} → モノラル16kHz MP3(128kbps)")
        cmd = [
            "ffmpeg", "-y", "-i", str(input_file),
            "-vn",
            "-acodec", "libmp3lame",
            "-b:a", "128k",
            "-ac", "1",
            "-ar", "16000",
            str(tmp_mp3)
        ]
        subprocess.run(cmd, capture_output=True, encoding="utf-8", errors="ignore", text=True, check=True)

        size = tmp_mp3.stat().st_size
        if size < MAX_FILE_SIZE_BYTES:
            print(f"変換後サイズ: {size/(1024*1024):.2f}MB (25MB 以下)")
            return [tmp_mp3]

        bytes_per_sec = 128_000 // 8
        file_sec_limit = floor(MAX_FILE_SIZE_BYTES / bytes_per_sec) - SIZE_MARGIN_SEC
        model_sec_limit = MAX_MODEL_SECONDS - MODEL_MARGIN_SEC
        chunk_sec = min(file_sec_limit, model_sec_limit, 600)
        print(f"警告: {size/(1024*1024):.2f}MB → {chunk_sec}s ごとに分割します")

        pattern = temp_dir / f"{stem}_%03d_for_api.{TARGET_AUDIO_FORMAT}"
        cmd_split = [
            "ffmpeg", "-y", "-i", str(tmp_mp3),
            "-f", "segment",
            "-segment_time", str(chunk_sec),
            "-c", "copy",
            str(pattern)
        ]
        subprocess.run(cmd_split, capture_output=True, text=True, encoding="utf-8", errors="ignore", check=True)

        tmp_mp3.unlink()
        chunks = sorted(temp_dir.glob(f"{stem}_*_for_api.{TARGET_AUDIO_FORMAT}"))
        print(f"分割完了: {len(chunks)} チャンク生成")
        return chunks

    except Exception as e:
        print(f"音声変換エラー ({input_file.name}): {e}")
        if tmp_mp3.exists():
            tmp_mp3.unlink(missing_ok=True)
        return None

def transcribe_audio_with_openai(
    audio_path: Path,
    model: str,
    language: str | None = None,
    prompt: str | None = None
) -> str | None:
    if client is None:
        print("OpenAI クライアント未初期化 → スキップ")
        return None

    params = {"model": model, "response_format": "text"}
    log = [f"文字起こし: {audio_path.name} (モデル: {model}"
           + (f", 言語: {language}" if language else ", 言語: 自動検出")]
    if prompt:
        params["prompt"] = prompt
        log.append("プロンプト使用")
    print(", ".join(log) + ")...")

    try:
        with open(audio_path, "rb") as f:
            resp = client.audio.transcriptions.create(file=f, **params)
        print(f"完了: {audio_path.name}")
        return getattr(resp, "text", str(resp)).strip()
    except openai.BadRequestError as e:
        msg = getattr(e, "error", {}).get("message", "")
        if any(k in msg for k in ("corrupted", "unsupported", "Invalid file format")) \
           and audio_path.suffix.lower() != ".wav":
            wav_path = audio_path.with_suffix(".wav")
            print(f"警告: {audio_path.name} → WAV に再エンコードし再試行")
            try:
                subprocess.run([
                    "ffmpeg", "-y", "-i", str(audio_path),
                    "-vn", "-ac", "1", "-ar", "16000",
                    "-c:a", "pcm_s16le", str(wav_path)
                ], capture_output=True, text=True, encoding="utf-8", errors="ignore", check=True)
                return transcribe_audio_with_openai(wav_path, model, language, prompt)
            finally:
                wav_path.unlink(missing_ok=True)
        print(f"文字起こしエラー ({audio_path.name}): {e}")
    except Exception as e:
        print(f"文字起こし例外 ({audio_path.name}): {e}")

    return None

def summarize_transcript(text: str) -> str:
    system_prompt = hr_config.get("system_prompt", "")
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user",   "content": text}
    ]
    resp = client.chat.completions.create(
        model=SUMMARY_MODEL_NAME,
        messages=messages
    )
    return resp.choices[0].message.content.strip()

def main():
    global client

    if client is None:
        print("API キー設定エラー → 終了")
        return

    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
    except:
        print("エラー: ffmpeg が見つかりません")
        return

    args = sys.argv[1:]
    single_file_to_process = None
    supported_suffixes = [
        '.mp3','.mp4','.mpeg','.mpga','.m4a','.wav','.webm',
        '.aac','.flac','.ogg','.opus','.mov','.avi','.mkv','.flv','.wmv'
    ]
    for candidate in args:
        lower = candidate.lower()
        for sfx in supported_suffixes:
            if lower.endswith(sfx):
                single_file_to_process = Path(candidate)
                break
        if single_file_to_process:
            break

    if single_file_to_process:
        if not single_file_to_process.exists() or not single_file_to_process.is_file():
            print(f"エラー: 指定されたファイルが見つからない、またはファイルではありません: {single_file_to_process}")
            return

        parent_dir = single_file_to_process.parent
        os.environ["INPUT_DIR"] = str(parent_dir)
        os.environ["OUTPUT_DIR"] = str(parent_dir)
        os.environ["SUMMARY_DIR"] = str(parent_dir)
        temp_subdir = parent_dir / f"temp_processing_{single_file_to_process.stem}"
        os.environ["TEMP_DIR"] = str(temp_subdir)

        process_only_this = True

        default_lang = os.getenv("DEFAULT_LANGUAGE")
        cli_lang = None
        prompt_cli = None
        arg_list = args[:]
        first = arg_list[0]
        lang_candidate = first.lstrip('-').lower()
        if first.startswith('-') and lang_candidate.isalpha() and len(lang_candidate) <= 3:
            cli_lang = lang_candidate
            if len(arg_list) >= 2:
                prompt_cli = " ".join(arg_list[1:])
        else:
            prompt_cli = " ".join(arg_list)

        target_lang = cli_lang or default_lang
        final_prompt = prompt_cli or os.getenv("DEFAULT_PROMPT")

        print(f"【単一ファイルモード】 使用言語: {target_lang or '自動検出'}")
        if final_prompt:
            print(f"プロンプト: \"{final_prompt}\"")
        print(f"書き起こしモデル: {MODEL_NAME_FROM_ENV} | 要約モデル: {SUMMARY_MODEL_NAME}")

    else:
        process_only_this = False
        default_lang = os.getenv("DEFAULT_LANGUAGE")
        cli_lang = None
        prompt_cli = None
        args_lp = sys.argv[1:]
        if args_lp:
            lang_candidate = args_lp[0].lstrip('-')
            if len(args_lp) == 1 and lang_candidate.isalpha() and len(lang_candidate) <= 3:
                cli_lang = lang_candidate.lower()
            elif len(args_lp) >= 2 and lang_candidate.isalpha() and len(lang_candidate) <= 3:
                cli_lang = lang_candidate.lower()
                prompt_cli = " ".join(args_lp[1:])
            else:
                prompt_cli = " ".join(args_lp)

        target_lang = cli_lang or default_lang
        final_prompt = prompt_cli or os.getenv("DEFAULT_PROMPT")

        print(f"使用言語: {target_lang or '自動検出'}")
        if final_prompt:
            print(f"プロンプト: \"{final_prompt}\"")
        print(f"書き起こしモデル: {MODEL_NAME_FROM_ENV} | 要約モデル: {SUMMARY_MODEL_NAME}")

    INPUT_DIR = Path(os.getenv("INPUT_DIR", "./input"))
    OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", "./output"))
    TEMP_DIR = Path(os.getenv("TEMP_DIR", "./temp_processing"))
    SUMMARY_DIR = Path(os.getenv("SUMMARY_DIR", "./output/summaries"))

    ensure_dir(INPUT_DIR)
    ensure_dir(OUTPUT_DIR)
    ensure_dir(TEMP_DIR)
    ensure_dir(SUMMARY_DIR)

    processed = skipped = failed = 0

    if process_only_this:
        item = single_file_to_process
        print(f"\n--- {item.name} 処理開始（単一ファイルモード）---")
        if item.suffix.lower() not in supported_suffixes:
            print(f"非対応拡張子: {item.suffix} → 終了")
            return

        out_txt = OUTPUT_DIR / (item.stem + ".txt")
        if out_txt.exists():
            print(f"{out_txt.name} 既に存在 → スキップ")
            skipped += 1
        else:
            chunks = convert_audio_for_api(item, TEMP_DIR)
            if not chunks:
                print(f"{item.name} 変換失敗 → 終了")
                failed += 1
            else:
                full_text = ""
                for ch in chunks:
                    txt = transcribe_audio_with_openai(ch, MODEL_NAME_FROM_ENV, target_lang, final_prompt)
                    if txt is None:
                        full_text = None
                        break
                    full_text += txt + "\n"
                    ch.unlink(missing_ok=True)

                if full_text is None:
                    print(f"{item.name} 文字起こし失敗")
                    failed += 1
                else:
                    with open(out_txt, "w", encoding="utf-8") as f:
                        f.write(full_text.strip())
                    print(f"出力完了: {out_txt.name}")

                    try:
                        summary = summarize_transcript(full_text)
                        summary_path = SUMMARY_DIR / f"{item.stem}_summary.txt"
                        with open(summary_path, "w", encoding="utf-8") as sf:
                            sf.write(summary)
                        print(f"要約出力完了: {summary_path.name}")
                    except Exception as e:
                        print(f"要約失敗: {e}")
                    processed += 1
    else:
        files = list(INPUT_DIR.iterdir())
        if not files:
            print(f"入力フォルダ {INPUT_DIR} が空です")

        for item in files:
            print(f"\n--- {item.name} 処理開始 ---")
            if item.suffix.lower() not in supported_suffixes:
                print(f"非対応拡張子: {item.suffix} → スキップ")
                skipped += 1
                continue

            out_txt = OUTPUT_DIR / (item.stem + ".txt")
            if out_txt.exists():
                print(f"{out_txt.name} 既に存在 → スキップ")
                skipped += 1
                continue

            chunks = convert_audio_for_api(item, TEMP_DIR)
            if not chunks:
                print(f"{item.name} 変換失敗 → スキップ")
                failed += 1
                continue

            full_text = ""
            for ch in chunks:
                txt = transcribe_audio_with_openai(ch, MODEL_NAME_FROM_ENV, target_lang, final_prompt)
                if txt is None:
                    full_text = None
                    break
                full_text += txt + "\n"
                ch.unlink(missing_ok=True)

            if full_text is None:
                print(f"{item.name} 文字起こし失敗")
                failed += 1
                continue

            with open(out_txt, "w", encoding="utf-8") as f:
                f.write(full_text.strip())
            print(f"出力完了: {out_txt.name}")

            try:
                summary = summarize_transcript(full_text)
                summary_path = SUMMARY_DIR / f"{item.stem}_summary.txt"
                with open(summary_path, "w", encoding="utf-8") as sf:
                    sf.write(summary)
                print(f"要約出力完了: {summary_path.name}")
            except Exception as e:
                print(f"要約失敗: {e}")

            processed += 1

    if TEMP_DIR.exists():
        for tmp in TEMP_DIR.iterdir():
            try:
                if tmp.is_dir():
                    shutil.rmtree(tmp)
                else:
                    tmp.unlink()
            except Exception as e:
                print(f"警告: 一時ファイル削除失敗 ({tmp}): {e}")
        try:
            TEMP_DIR.rmdir()
            print(f"一時ディレクトリ '{TEMP_DIR}' を削除しました。")
        except Exception as e:
            print(f"警告: 一時ディレクトリ削除失敗: {e}")

    print("======= 完了 =======")
    print(f"成功: {processed}  スキップ: {skipped}  失敗: {failed}")
    print("===================")

if __name__ == "__main__":
    main()
