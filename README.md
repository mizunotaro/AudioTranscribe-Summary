# Audio/Video Transcription + Summarization Tool  
# 音声／動画文字起こし＋要約ツール

This repository contains a Python script that uses OpenAI Whisper to transcribe video and audio files, then summarizes the results with an LLM (such as o3-mini). It also includes batch files (`.bat`) and PowerShell scripts (`.ps1`) for easy drag-and-drop execution on Windows, as well as a `requirements.txt` listing the necessary Python libraries. This document guides beginners step by step from setup to execution.  
このリポジトリには、OpenAI Whisper を使って動画・音声ファイルを文字起こしし、その結果を LLM（o3-mini など）で要約する Python スクリプトと、Windows 上でドラッグ＆ドロップで簡単に動かせるバッチファイル（.bat）および PowerShell スクリプト（.ps1）、必要な Python ライブラリをまとめた `requirements.txt` が含まれています。本ドキュメントでは、初心者の方にもわかりやすいように、セットアップから実行方法までを順に解説します。

---

---

## Table of Contents  
## 目次

1. [Overview / 概要](#overview-概要)  
2. [Prerequisites / 前提条件](#prerequisites-前提条件)  
3. [File Structure / ファイル構成](#file-structure-ファイル構成)  
4. [Installation Steps / インストール手順](#installation-steps-インストール手順)  
   - 4.1 [Setting Up Python Environment / Python 環境構築]  
   - 4.2 [Installing ffmpeg / ffmpeg インストール]  
   - 4.3 [Repository Placement / リポジトリ配置]  
   - 4.4 [Installing Required Libraries / 必要ライブラリのインストール]  
5. [Environment Variable Configuration (`.env`) / 環境変数設定（`.env`）](#environment-variable-configuration-env-環境変数設定env)  
6. [Preparing Configuration File (`prompt.json`) / 設定ファイル (`prompt.json`) の準備](#preparing-configuration-file-promptjson-設定ファイル-promptjson-の準備)  
7. [How to Run / 実行方法](#how-to-run-実行方法)  
   - 7.1 [Using the Batch File (`.bat`) / バッチファイル（`.bat`）を使う方法]  
   - 7.2 [Using the PowerShell Script (`.ps1`) / PowerShell スクリプト（`.ps1`）を使う方法]  
8. [File Descriptions / ファイルの説明](#file-descriptions-ファイルの説明)  
9. [Troubleshooting / トラブルシューティング](#troubleshooting-トラブルシューティング)  
10. [License & Notes / ライセンス・注意事項](#license--notes-ライセンス・注意事項)  

---

---

## 1. Overview / 概要

- **Purpose / 目的**  
  - Transcribe video/audio files using the Whisper API (OpenAI), then summarize the transcript with an LLM (e.g., o3-mini).  
    動画／音声ファイルを Whisper API（OpenAI）で文字起こしし、そのテキストをさらに LLM（o3-mini など）で要約します。  
  - Save results in the same folder as `<original_filename>.txt` (transcription) and `<original_filename>_summary.txt` (summary).  
    結果を同じフォルダに「`<元ファイル名>.txt`（文字起こし）」「`<元ファイル名>_summary.txt`（要約）」として保存します。  

- **Features / 特徴**  
  1. **Drag & Drop Support / ドラッグ＆ドロップ対応**  
     - On Windows, simply drag and drop your file(s) onto the `.bat` or `.ps1` to run the process.  
       Windows 上で `.bat` や `.ps1` ファイルにファイルをドラッグ＆ドロップするだけで処理が実行できます。  
  2. **Standalone Python Script Execution / Python スクリプト単体でも実行可能**  
     - By passing file paths as command-line arguments, you can process individual files instead of entire folders.  
       コマンドライン引数でファイルパスを渡せば、フォルダ全体でなく「指定したファイルのみ」を処理できます。  
  3. **Environment Variables via `.env` or CLI / 環境変数設定は `.env` またはターミナルから設定可能**  
     - You can consolidate Whisper model name, summary model name, prompt file path, etc., in `.env`, or specify them directly in the batch/PowerShell script.  
       Whisper モデル名、要約モデル名、プロンプトファイルパスなどを `.env` にまとめるか、直接バッチ／PowerShell で指定できます。  

---

## 2. Prerequisites / 前提条件

Please prepare and verify the following in advance:  
以下をあらかじめ準備・確認してください：

1. **Windows PC / Windows PC**  
   - Windows 10 or later is recommended. Administrator rights (to modify PowerShell execution policies) are recommended.  
     Windows 10 以降を想定。PowerShell 実行ポリシーを変更できる管理者権限があると安心です。  
2. **Python 3.9 or higher / Python 3.9 以上**  
   - Download and install the Windows installer from the [official site](https://www.python.org/downloads/windows/).  
     [公式サイト](https://www.python.org/downloads/windows/) から Windows 用インストーラを入手し、インストールしてください。  
   - Check “Add Python to PATH” during installation for convenience.  
     インストール時に「Add Python to PATH」にチェックを入れると簡単です。  
3. **ffmpeg (Audio/Video Conversion Tool) / ffmpeg（音声・動画変換ツール）**  
   - Required for converting files into Whisper-compatible format (mono 16kHz MP3).  
     Whisper で扱いやすい形式（モノラル 16kHz MP3）に自動で変換するために必要です。  
   - Download a Windows build from the [ffmpeg download page](https://ffmpeg.org/download.html), place the `ffmpeg.exe` in a folder of your choice, and add that folder to your `PATH`.  
     [ffmpeg のダウンロードページ](https://ffmpeg.org/download.html) から Windows 用ビルドを入手し、実行ファイル (`ffmpeg.exe`) を任意のフォルダに置いて、環境変数 `PATH` に追加してください。  
4. **OpenAI API Key / OpenAI API キー**  
   - Required for calling Whisper and the LLM (e.g., o3-mini).  
     Whisper および LLM（o3-mini など）を呼び出す際に必要です。  
   - Set it in the `OPENAI_API_KEY` environment variable. For example, in PowerShell:  
     環境変数 `OPENAI_API_KEY` にキーをセットしておいてください。例えば PowerShell なら：  
     ```powershell
     setx OPENAI_API_KEY "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
     ```  
   - Optionally verify with:  
     正しく読み込まれるか確認するには：  
     ```powershell
     python -c "import openai; print(openai.OpenAI().api_key)"
     ```  

---

## 3. File Structure / ファイル構成

At the root of the repository, the following files/folders exist:  
リポジトリのルートに以下のファイル／フォルダが存在します：

```
/
├── transcribe_files.py        # Main Python script / メインの Python スクリプト
├── prompt.json                # Prompt definition file for summarization / 要約用プロンプト定義ファイル
├── requirements.txt           # List of required Python libraries / 必要な Python ライブラリ一覧
├── run_transcribe.bat         # Windows batch file (supports drag & drop) / Windows バッチファイル（ドラッグ＆ドロップ対応）
├── run_transcribe.ps1         # PowerShell script (supports drag & drop) / PowerShell スクリプト（ドラッグ＆ドロップ対応）
├── .env                       # Environment variables configuration file / 環境変数をまとめたファイル
└── README.md                  # This document / 本ドキュメント
```

---

## 4. Installation Steps / インストール手順

### 4.1. Setting Up Python Environment / Python 環境構築

1. Download the Windows installer from the [official Python site](https://www.python.org/downloads/windows/).  
   [Python 公式サイト](https://www.python.org/downloads/windows/) から Windows 用インストーラをダウンロードしてください。  
2. Check “Add Python to PATH” during installation.  
   「Add Python to PATH」にチェックを入れてインストールしてください。  
3. Open Command Prompt or PowerShell and verify the version:  
   コマンドプロンプト／PowerShell を開き、以下を実行してバージョンを確認してください：  
   ```powershell
   python --version
   ```  
   If it shows Python 3.x.x, the installation succeeded.  
   `Python 3.x.x` と表示されれば成功です。

---

### 4.2. Installing ffmpeg / ffmpeg インストール

1. Go to the [ffmpeg official download page](https://ffmpeg.org/download.html) and download the Windows build.  
   [ffmpeg 公式ダウンロードページ](https://ffmpeg.org/download.html) に移動し、Windows 用ビルドをダウンロードしてください。  
2. Unzip the downloaded archive, copy the `bin/ffmpeg.exe` into a folder such as `C:\tools\ffmpeg\bin\`.  
   ダウンロードした ZIP を解凍し、中にある `bin/ffmpeg.exe` を任意のフォルダ（例：`C:\tools\ffmpeg\bin\`）にコピーします。  
3. Add `C:\tools\ffmpeg\bin` to your system `PATH`:  
   システム環境変数に `C:\tools\ffmpeg\bin` を追加します：  
   - Open Start Menu → “Edit the system environment variables” → “Environment Variables…”  
     「スタートメニュー」→「システム環境変数を編集」→「環境変数…」  
   - Under “System variables,” select `Path` → “Edit” → “New” → Add `C:\tools\ffmpeg\bin`.  
     「システム環境変数」欄で `Path` を選択 → 「編集」 → 新規で先ほどのパスを追加してください。  
4. Restart Command Prompt/PowerShell and verify the installation:  
   コマンドプロンプト／PowerShell を再起動し、以下を実行して起動確認してください：  
   ```powershell
   ffmpeg -version
   ```  
   If version information appears, the installation was successful.  
   バージョン情報が表示されれば成功です。

---

### 4.3. Repository Placement / リポジトリ配置

1. Create a folder of your choice (e.g., `C:\src\audio_transcribe+summary_dd\`).  
   任意のフォルダ（例：`C:\src\audio_transcribe+summary_dd\`）を作成します。  
2. Copy the following files into that folder:  
   以下のファイルをすべて同じフォルダにコピーしてください：  
   - `transcribe_files.py`  
   - `prompt.json`  
   - `run_transcribe.bat`  
   - `run_transcribe.ps1`  
   - `requirements.txt`  
   - `.env`  
3. Example folder structure:  
   フォルダ構成例：  
   ```bash
   C:\src\audio_transcribe+summary_dd\
   │
   ├── transcribe_files.py
   ├── prompt.json
   ├── requirements.txt
   ├── run_transcribe.bat
   ├── run_transcribe.ps1
   └── .env
   ```

---

### 4.4. Installing Required Libraries / 必要ライブラリのインストール

1. Open Command Prompt or PowerShell and navigate to the project directory:  
   コマンドプロンプト／PowerShell を開き、作業ディレクトリを移動します：  
   ```powershell
   cd C:\src\audio_transcribe+summary_dd
   ```  
2. Install the required libraries using `requirements.txt`:  
   `requirements.txt` を使って必要ライブラリをインストールします：  
   ```powershell
   pip install -r requirements.txt
   ```  
3. Example content of `requirements.txt`:  
   `requirements.txt` の内容例：  
   ```shell
   openai>=1.0.0
   python-dotenv>=0.20.0
   ```  
4. After installation, you may verify by running:  
   インストール後、以下を実行してライブラリが入っているか確認してもよいです：  
   ```powershell
   python -c "import openai, dotenv; print('OK')"
   ```

---

## 5. Environment Variable Configuration (`.env`) / 環境変数設定（`.env`）

By preparing a `.env` file, the Python script will automatically load the environment variables at runtime. Below is a sample. Modify the contents as needed and save it at the root of the repository as `.env`.  
`.env` ファイルを用意すると、Python スクリプト実行時に次の環境変数を自動で読み込みます。以下はサンプルです。実行前に適宜中身を修正し、リポジトリ直下の `.env` として保存してください。

```ini
# =============================
# 1. Input Media Files
# =============================
INPUT_DIR="./input"

# =============================
# 2. Transcription Output Directory
# =============================
OUTPUT_DIR="./output"

# =============================
# 3. Summary Output Directory
# =============================
SUMMARY_DIR="./output"

# =============================
# 4. Prompt File for Summarization
# =============================
PROMPT_PATH="./config/prompt_default.json"

# =============================
# 5. OpenAI API Key (Required)
# =============================
OPENAI_API_KEY="sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

# =============================
# 6. Whisper Model Name (Optional)
#    Default: "gpt-4o-mini-transcribe"
#    Other examples: "whisper-1", "gpt-4o-transcribe"
# =============================
WHISPER_MODEL_NAME="gpt-4o-transcribe"

# =============================
# 7. Summary Model Name (Optional)
#    Default: o3-mini
# =============================
SUMMARY_MODEL_NAME="o4-mini"

# =============================
# 8. Default Transcription Language (Optional)
#    ISO 639-1 language code (e.g., "ja" for Japanese, "en" for English)
#    If not specified, the API will auto-detect the language.
# =============================
# DEFAULT_LANGUAGE="ja"

# =============================
# 9. Default Prompt (Optional)
#    You can specify meeting context or domain-specific instructions.
# =============================
# DEFAULT_PROMPT="This recording is an online discussion about deep tech. It may contain domain-specific terminology such as clinical trials or intellectual property. If the language is Japanese, please convert Kanji appropriately and choose correct particles contextually. For other languages, choose appropriate terms based on context."
```

### Key Settings Explanation / 主要な設定説明

- `INPUT_DIR`: Folder containing media files to transcribe. If no CLI argument is given, all supported extensions in this folder will be processed by the Python script.  
  `INPUT_DIR`: 文字起こし対象のメディアファイルを置くフォルダ。Python スクリプトで引数が指定されなかった場合、このフォルダ内のすべての対応拡張子ファイルを処理します。  
- `OUTPUT_DIR`: Folder for saving transcription text (`.txt`).  
  `OUTPUT_DIR`: 文字起こしテキスト（.txt）を保存するフォルダ。  
- `SUMMARY_DIR`: Folder for saving summary text (`_summary.txt`).  
  `SUMMARY_DIR`: 要約テキスト（_summary.txt）を保存するフォルダ。  
- `PROMPT_PATH`: Path to the prompt file used for summarization (e.g., `./config/prompt_default.json`). If you want to refer to `prompt.json` at the repository root, set `PROMPT_PATH="./prompt.json"`.  
  `PROMPT_PATH`: 要約時に使用するプロンプトファイルのパス（例：`./config/prompt_default.json`）。実際にはリポジトリ直下にある `prompt.json` を参照する場合、`PROMPT_PATH="./prompt.json"` とすれば OK。  
- `OPENAI_API_KEY`: OpenAI API key. Required.  
  `OPENAI_API_KEY`: OpenAI API キー。必須です。  
- `WHISPER_MODEL_NAME`: Specify the Whisper model name. If not set, the default `"gpt-4o-mini-transcribe"` inside the script is used.  
  `WHISPER_MODEL_NAME`: Whisper モデル名を指定。未指定の場合はスクリプト内部のデフォルト `"gpt-4o-mini-transcribe"` が使われます。  
- `SUMMARY_MODEL_NAME`: Specify the summary LLM model name. If not set, `"o3-mini"` is used.  
  `SUMMARY_MODEL_NAME`: 要約用 LLM モデル名を指定。未指定の場合は `"o3-mini"` が使われます。  
- `DEFAULT_LANGUAGE`: Use if you want to explicitly set the transcription language (e.g., `"ja"`). If not specified, the language is auto-detected.  
  `DEFAULT_LANGUAGE`: 文字起こし言語を指定する場合に使います（例: `"ja"`）。指定がないと自動検出されます。  
- `DEFAULT_PROMPT`: You can directly specify transcription/summarization prompts. If set in `.env`, you don’t need to pass it in batch/PowerShell.  
  `DEFAULT_PROMPT`: 文字起こし・要約プロンプトを直接指定できます。あらかじめ `.env` にセットしておくと、「バッチ・PowerShell で渡さなくてもよい」ようになります。

---

## 6. Preparing Configuration File (`prompt.json`) / 設定ファイル (`prompt.json`) の準備

The `prompt.json` file, which defines the prompt for summarization, is mandatory. Ensure it contains content as shown below (with proper indentation):  
要約用の `prompt.json` は必須です。以下のような内容になっていることを確認してください（インデント入り）:

```json
{
  "version": "1.2.0",
  "updated_at": "2025-05-14T12:00:00+09:00",
  "changelog": [
    {
      "version": "1.2.0",
      "date": "2025-05-14",
      "notes": "Added alternatives in the Analysis section and bulleted the system prompt"
    },
    {
      "version": "1.1.0",
      "date": "2025-03-01",
      "notes": "Enhanced multilingual output settings"
    }
  ],
  "title": "General Discussion Summarization Prompt",
  "description": "A template for accurately summarizing and recording discussions from meetings, workshops, online discussions, etc., across all fields, with optional multilingual output, risk analysis, and decision support.",
  "system_prompt": "You are serving as an executive assistant with the following roles:\n1. Expert in management and business operations of deep-tech startups\n2. Possess broad specialized knowledge from finance, accounting, HR, labor, legal, IP, general affairs, to IT systems\n3. Deeply understand speakers' intentions and contexts from transcripts to extract essential information\n4. Strictly adhere to the output schema below and produce minutes as a JSON object\n\nFollow the order and format exactly as specified and output a JSON object.",
  "settings": {
    "model": "${SUMMARY_MODEL_NAME}",
    "temperature": 0.0,
    "max_tokens": 1024,
    "top_p": 1.0
  },
  "i18n": {
    "default_language": "${DEFAULT_LANGUAGE:-ja}",
    "auto_detect_language": true,
    "translate_to": [],
    "translate_behavior": "If the original language differs from default_language, translate to default_language before summarizing"
  },
  "logging": {
    "level": "INFO",
    "include_request_id": true,
    "format": "[{timestamp}] {level} [{request_id}]: {message}"
  },
  "output_schema": [
    {
      "section": "Metadata",
      "fields": [
        {
          "name": "request_id",
          "type": "string",
          "required": true,
          "description": "Unique request ID"
        },
        {
          "name": "session_id",
          "type": "string",
          "required": true,
          "description": "Session ID"
        },
        {
          "name": "generated_at",
          "type": "datetime",
          "required": true,
          "description": "Generation timestamp (ISO 8601)"
        },
        {
          "name": "model_used",
          "type": "string",
          "required": true,
          "description": "Model name used"
        },
        {
          "name": "language",
          "type": "string",
          "required": true,
          "description": "Output language code"
        },
        {
          "name": "discussion_title",
          "type": "string",
          "required": false,
          "description": "Discussion title (optional)"
        }
      ]
    },
    {
      "section": "Summary",
      "fields": [
        {
          "name": "overview",
          "type": "string",
          "required": true,
          "description": "Overview of the discussion"
        },
        {
          "name": "key_findings",
          "type": "list<string>",
          "required": true,
          "description": "Key findings/conclusions"
        },
        {
          "name": "action_items",
          "type": "list<string>",
          "required": false,
          "description": "Action items (if any)"
        }
      ]
    },
    {
      "section": "Domain-Specific Summary",
      "fields": [
        {
          "name": "specialized_topics",
          "type": "list<string>",
          "required": false,
          "description": "Key points by specialized domain"
        },
        {
          "name": "agenda_and_discussions",
          "type": "list<string>",
          "required": false,
          "description": "Summary of agenda items and discussions"
        },
        {
          "name": "topic_decisions",
          "type": "list<string>",
          "required": false,
          "description": "Decisions made for each topic/domain"
        }
      ]
    },
    {
      "section": "Analysis",
      "fields": [
        {
          "name": "risks",
          "type": "list<string>",
          "required": false,
          "description": "Risk factors"
        },
        {
          "name": "alternatives",
          "type": "list<string>",
          "required": false,
          "description": "Alternatives/considerations"
        },
        {
          "name": "final_decisions",
          "type": "list<string>",
          "required": false,
          "description": "Final decisions"
        }
      ]
    }
  ],
  "style_guidelines": [
    "Write factually and avoid subjective speculation such as ‘it seems that…’",
    "Define specialized terms in parentheses upon first use (e.g., 'SMB (Server Message Broker)').",
    "Use bullet points where appropriate to clarify key points (e.g., • Main conclusions • Next steps).",
    "Keep a business report style and avoid honorific expressions; use standard form."
  ],
  "context_instructions": "Insert the full transcript into the `<<TRANSCRIPT>>` placeholder below. Read the entire transcript and produce output fully compliant with the above schema.",
  "transcript_placeholder": "<<TRANSCRIPT>>"
}
```

---

## 7. How to Run / 実行方法

You can run the tool in either of the following ways. Drag-and-drop operations make it easy.  
以下のいずれかの方法で実行できます。ドラッグ＆ドロップ操作で簡単に動かせます。

---

### 7.1. Using the Batch File (`.bat`) / バッチファイル（`.bat`）を使う方法

#### Creating a Shortcut / ショートカットを作成

1. Right-click `run_transcribe.bat` in Explorer → “Create shortcut.”  
   エクスプローラで `run_transcribe.bat` を右クリック → 「ショートカットの作成」  
2. Place the created shortcut on your desktop or another convenient location.  
   作成されたショートカットをデスクトップなどに置いておくと便利です。

#### Running by Drag & Drop / ドラッグ＆ドロップで実行

1. Drag the target audio/video file (e.g., `meeting.mp4`) onto `run_transcribe.bat` (or its shortcut).  
   対象の音声／動画ファイル（例：`meeting.mp4`）を `run_transcribe.bat`（またはそのショートカット）にドラッグ＆ドロップします。  
2. A Command Prompt window will open and perform the following steps:  
   コマンドプロンプトが開き、次のように処理が行われます：  
   1. Set the `PROMPT_PATH` environment variable to the path of `prompt.json`.  
      環境変数 `PROMPT_PATH` に `prompt.json` のパスをセット  
   2. Launch the Python script `transcribe_files.py`, processing only the dropped file.  
      Python スクリプト `transcribe_files.py` が起動し、引数で渡されたファイルだけを処理  
   3. Transcribe → Summarize → Save output.  
      文字起こし → 要約 → 生成結果の保存  
   4. Display a completion message.  
      処理完了メッセージ表示  

3. When finished, the following files will be generated in the same folder:  
   終了後、以下のファイルが同フォルダ内に生成されます：  
   - `meeting.txt` (Transcription result) / 文字起こし結果  
   - `meeting_summary.txt` (Summary result) / 要約結果  

4. Temporary files are automatically deleted:  
   一時ファイルの自動削除  
   - The `temp_processing_<filename>` folder created during processing is automatically removed after completion.  
     処理中に生成された `temp_processing_<ファイル名>` フォルダは、処理終了後に自動で削除されます。

---

### 7.2. Using the PowerShell Script (`.ps1`) / PowerShell スクリプト（`.ps1`）を使う方法

#### Changing Execution Policy (First Time Only) / 実行ポリシーの変更（初回のみ）

1. Open PowerShell as Administrator and run:  
   管理者権限で PowerShell を開き、以下を実行してローカルスクリプトの実行を許可します：  
   ```powershell
   Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```  
2. When prompted, type “Y” to confirm.  
   確認メッセージが出たら「Y」を入力して確定します。

#### Creating a Shortcut (Optional) / ショートカットを作成（任意）

1. Right-click `run_transcribe.ps1` → “Create shortcut.”  
   `run_transcribe.ps1` を右クリック → 「ショートカットの作成」  
2. In the shortcut’s target field, set:  
   ショートカットのリンク先に以下を設定するとダブルクリックだけで実行可能になります：  
   ```powershell
   powershell.exe -File "C:\src\audio_transcribe+summary_dd\run_transcribe.ps1"
   ```  
3. Place the shortcut on your desktop or another convenient location.  
   ショートカットをデスクトップなどに置いておくと便利です。

#### Running by Drag & Drop / ドラッグ＆ドロップで実行

1. Drag the target audio/video file onto `run_transcribe.ps1` (or its shortcut).  
   対象の音声／動画ファイルを `run_transcribe.ps1`（またはそのショートカット）にドラッグ＆ドロップします。  
2. PowerShell will launch and perform the following steps:  
   PowerShell が起動し、以下の流れで処理が行われます：  
   1. Set the `PROMPT_PATH` environment variable to the path of `prompt.json`.  
      環境変数 `PROMPT_PATH` に `prompt.json` のパスをセット  
   2. Launch the Python script `transcribe_files.py` in single-file mode (processing only the dropped file).  
      Python スクリプト `transcribe_files.py` が引数で渡されたファイルを単一モードで処理  
   3. Transcribe → Summarize → Output to the same folder.  
      文字起こし → 要約 → 同フォルダに出力  
   4. Display a completion message.  
      完了メッセージ表示  

3. Example output:  
   出力例：  
   ```makefile
   【単一ファイルモード】 使用言語: 自動検出  
   --- meeting.mp4 処理開始（単一ファイルモード）---  
   再エンコード: meeting.mp4 → モノラル16kHz MP3(128kbps)  
   文字起こし: meeting_for_api.mp3 (モデル: gpt-4o-mini-transcribe, 言語: 自動検出)...  
   完了: meeting_for_api.mp3  
   出力完了: meeting.txt  
   要約出力完了: meeting_summary.txt  
   一時ディレクトリ 'C:\Users\…\temp_processing_meeting' を削除しました。  
   ======= 完了 =======  
   成功: 1  スキップ: 0  失敗: 0  
   ===================  
   ===== 文字起こし・要約 完了 =====  
   ```

---

## 8. File Descriptions / ファイルの説明

### transcribe_files.py  
**Description (English):**  
This script calls OpenAI Whisper to convert audio to text, then passes the text to an LLM (summary model) to generate a concise summary.  

- When you pass a file path as a command-line argument, it runs in “single-file mode.”  
- Uses environment variables (`INPUT_DIR`, `OUTPUT_DIR`, `TEMP_DIR`, `SUMMARY_DIR`) to control folder structure.  
- Logs and skips if Whisper or summarization fails.  
- Automatically deletes temporary folders once finished.  

**説明（日本語）：**  
OpenAI Whisper を呼び出して音声→テキスト化し、得られた文字列を LLM（要約モデル）に投げて短くまとめるスクリプトです。  

- コマンドライン引数にファイルパスを渡すと「単一ファイルモード」で動作します。  
- 環境変数 `INPUT_DIR`, `OUTPUT_DIR`, `TEMP_DIR`, `SUMMARY_DIR` を使用してフォルダを制御します。  
- Whisper や要約が失敗した場合はログを出力してスキップします。  
- 処理後は一時フォルダを自動的に削除します。

---

### prompt.json  
**Description (English):**  
Prompt definition file presented to the LLM during summarization.  

- Designed to return output in JSON format that conforms to the defined schema.  
- Ensure you have a valid JSON file before running the script (if you change the file name or path, update `.env` or the batch/PowerShell accordingly).  

**説明（日本語）：**  
要約時に LLM に提示するプロンプト定義ファイルです。  

- 出力を JSON 形式でスキーマに沿って返すように設計されています。  
- スクリプト実行前に有効な JSON ファイルを用意してください（ファイル名やパスを変更した場合は、`.env` やバッチ／PowerShell でも同じパスを指定する必要があります）。

---

### requirements.txt  
**Description (English):**  
Lists the Python libraries required to run the script.  

- At minimum, include the following for transcription and summarization:  
  ```shell
  openai>=1.0.0
  python-dotenv>=0.20.0
  ```  
- Add other packages as needed in the future.  

**説明（日本語）：**  
Python スクリプトの実行に必要なライブラリをまとめたファイルです。  

- 検索・要約機能には最低限以下が必要です：  
  ```shell
  openai>=1.0.0
  python-dotenv>=0.20.0
  ```  
- 追加で他のパッケージが必要になったら適宜追記してください。

---

### run_transcribe.bat  
**Description (English):**  
Windows batch file.  

- When you drag and drop a file onto it, it automatically calls `transcribe_files.py`.  
- The `PROMPT_PATH` environment variable is fixed inside the batch file; edit it if necessary.  

**説明（日本語）：**  
Windows のバッチファイルです。  

- ファイルをドラッグ＆ドロップすると、`transcribe_files.py` が自動で呼び出されます。  
- 環境変数 `PROMPT_PATH` はバッチ内で固定しています。変更が必要な場合はバッチを編集してください。

---

### run_transcribe.ps1  
**Description (English):**  
PowerShell wrapper script.  

- When you drag and drop a file onto it, it launches the Python script with the first file path as an argument.  
- You must adjust the execution policy (`Set-ExecutionPolicy RemoteSigned`) to run local scripts.  

**説明（日本語）：**  
PowerShell 用のラッパースクリプトです。  

- ファイルをドラッグ＆ドロップすると、最初のファイルパスを引数として Python スクリプトを起動します。  
- 実行ポリシーの調整（`Set-ExecutionPolicy RemoteSigned`）が必要です。

---

### .env  
**Description (English):**  
Environment variable configuration file.  

- Centralizes Whisper model name, summary model name, prompt path, output directories, etc.  
- Be sure to replace with correct paths and keys before using.  

**説明（日本語）：**  
環境変数をまとめたファイルです。  

- Whisperモデル名や要約モデル名、プロンプトパス、出力先などを一元管理できます。  
- 必ず正しいパス・キーに書き換えてから使用してください。

---

## 9. Troubleshooting / トラブルシューティング

### Python Module Errors at Runtime / Python 実行時にモジュールエラーが出る

```
ModuleNotFoundError: No module named 'openai'
```

- If you see this error, run `pip install -r requirements.txt` again.  
  上記のようなエラーが出た場合は、再度 `pip install -r requirements.txt` を実行してください。  
- If it still doesn’t resolve, you might have multiple Python versions installed. Try:  
  それでも解決しない場合は、Python が複数バージョンインストールされている可能性があります。以下のように明示的に実行してみてください：  
  ```powershell
  python -m pip install -r requirements.txt
  ```

---

### ffmpeg Not Found / ffmpeg が見つからない・コマンドが見つからないエラー

- Run `ffmpeg -version` to check if version information appears.  
  `ffmpeg -version` を実行してバージョン情報が表示されるか確認してください。  
- If you see “’ffmpeg’ is not recognized as an internal or external command…”, add the folder containing `ffmpeg.exe` to your `PATH` and restart PowerShell/Command Prompt.  
  `’ffmpeg’ は内部コマンドまたは外部コマンド...` と出る場合は、`ffmpeg.exe` のあるフォルダを環境変数 `PATH` に登録し、PowerShell／コマンドプロンプトを再起動してください。

---

### OpenAI API Key Errors / OpenAI API キーエラー

- If you see “API key not set,” verify that `OPENAI_API_KEY` is correctly set in your environment variables.  
  `API キーが設定されていません` と出る場合は、環境変数 `OPENAI_API_KEY` が正しくセットされているか確認してください。  
- To temporarily set it in PowerShell:  
  PowerShell で一時的にセットするなら：  
  ```powershell
  $env:OPENAI_API_KEY = "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
  ```  
  Then run `python transcribe_files.py` to check if the key is loaded.  
  その後 `python transcribe_files.py` を実行してキーが読み込まれるか試してください。

---

### prompt.json Loading Errors / prompt.json の読み込みエラー

- Usually caused by JSON syntax errors or incorrect file paths.  
  JSON 構文エラーやファイルパス間違いが原因です。  
- Save the file in UTF-8 encoding and verify the path specified in `.env`, batch, or PowerShell.  
  ファイルを UTF-8 で保存し、`.env` やバッチ／PowerShell で指定したパスが正しいか確認してください。

---

### Unexpected Summary Results / 要約の結果が想定と異なる

- Check that the `system_prompt` and schema in `prompt.json` are appropriate.  
  `prompt.json` 内の `system_prompt` やスキーマが適切であるかチェックしてください。  
- Adjust the LLM generation parameters (`temperature`, `max_tokens`) to stabilize output.  
  LLM の生成パラメータ（`temperature`, `max_tokens`）を調整することで出力を安定させることができます。

---

## 10. License & Notes / ライセンス・注意事項

This tool is a sample implementation. For commercial use, comply with the terms of service of each library and model.  
本ツールはサンプル実装です。商用利用の際は各ライブラリ・モデルの利用規約を遵守してください。

Using the OpenAI API may incur costs. Please review the OpenAI pricing page before use.  
OpenAI API の利用には料金がかかる場合があります。利用前に OpenAI の料金ページをご確認ください。

Whisper transcription and summarization require an internet connection. It will not work in an offline environment.  
Whisper 文字起こしおよび要約はインターネット接続が必要です。オフライン環境では動作しません。
