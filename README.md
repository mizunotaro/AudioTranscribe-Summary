# 音声／動画文字起こし＋要約ツール

このリポジトリには、OpenAI Whisper を使って動画・音声ファイルを文字起こしし、その結果を LLM（o3-mini など）で要約する Python スクリプトと、Windows 上でドラッグ＆ドロップで簡単に動かせるバッチファイル（.bat）および PowerShell スクリプト（.ps1）、必要な Python ライブラリをまとめた `requirements.txt` が含まれています。本ドキュメントでは、初心者の方にもわかりやすいように、セットアップから実行方法までを順に解説します。

---

## 目次

1. [概要](#概要)  
2. [前提条件](#前提条件)  
3. [ファイル構成](#ファイル構成)  
4. [インストール手順](#インストール手順)  
   - 4.1 Python 環境構築  
   - 4.2 ffmpeg インストール  
   - 4.3 リポジトリ配置  
   - 4.4 必要ライブラリのインストール  
5. [環境変数設定（`.env`）](#環境変数設定env)  
6. [設定ファイル (`prompt.json`) の準備](#設定ファイル-promptjson-の準備)  
7. [実行方法](#実行方法)  
   - 7.1 バッチファイル（`.bat`）を使う方法  
   - 7.2 PowerShell スクリプト（`.ps1`）を使う方法  
8. [ファイルの説明](#ファイルの説明)  
9. [トラブルシューティング](#トラブルシューティング)  
10. [ライセンス・注意事項](#ライセンス・注意事項)  

---

## 概要

- **目的**  
  - 動画／音声ファイルを Whisper API（OpenAI）で文字起こしし、そのテキストをさらに LLM（o3-mini など）で要約。  
  - 結果を同じフォルダに「`<元ファイル名>.txt`（文字起こし）」「`<元ファイル名>_summary.txt`（要約）」として保存します。  
- **特徴**  
  1. **ドラッグ＆ドロップ対応**  
     - Windows 上で `.bat` や `.ps1` ファイルにファイルをドラッグ＆ドロップするだけで処理が実行できます。  
  2. **Python スクリプト単体でも実行可能**  
     - コマンドライン引数でファイルパスを渡せば、フォルダ全体でなく「指定したファイルのみ」を処理します。  
  3. **環境変数設定は `.env` またはターミナルから設定可能**  
     - Whisper モデル名、要約モデル名、プロンプトファイルパスなどを `.env` にまとめるか、直接バッチ／PowerShell で指定できます。  

---

## 前提条件

以下をあらかじめ準備・確認してください：

1. **Windows PC**  
   - Windows 10 以降を想定。PowerShell 実行ポリシーを変更できる管理者権限があると安心です。  
2. **Python 3.9 以上**  
   - [公式サイト](https://www.python.org/downloads/windows/) から Windows 用インストーラを入手し、インストールしてください。  
   - インストール時に「Add Python to PATH」にチェックを入れると簡単です。  
3. **ffmpeg（音声・動画変換ツール）**  
   - Whisper で扱いやすい形式（モノラル 16kHz MP3）に自動で変換するために必要です。  
   - [ffmpeg のダウンロードページ](https://ffmpeg.org/download.html) から Windows 用ビルドを入手し、実行ファイル (`ffmpeg.exe`) を任意のフォルダに置いて、環境変数 `PATH` に追加してください。  
4. **OpenAI API キー**  
   - Whisper および LLM（o3-mini など）を呼び出す際に必要です。  
   - 環境変数 `OPENAI_API_KEY` にキーをセットしておいてください。例えば PowerShell なら：  
     ```powershell
     setx OPENAI_API_KEY "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
     ```  
   - コマンドラインで一度 `python -c "import openai; print(openai.OpenAI().api_key)"` を実行してキーが正しく読み込まれるかチェックしておくと安心です。  

---

## ファイル構成

リポジトリのルートに以下のファイル／フォルダ が存在します：

```
/
├── transcribe_files.py        # メインの Python スクリプト
├── prompt.json                # 要約用プロンプト定義ファイル
├── requirements.txt           # 必要な Python ライブラリ一覧
├── run_transcribe.bat         # Windows バッチファイル（ドラッグ＆ドロップ対応）
├── run_transcribe.ps1         # PowerShell スクリプト（ドラッグ＆ドロップ対応）
├── .env                       # 環境変数をまとめたファイル
└── README.md                  # 本ドキュメント
```

---

## インストール手順

### 4.1. Python 環境構築

1. [Python 公式サイト](https://www.python.org/downloads/windows/) から Windows 用インストーラをダウンロード。  
2. 「Add Python to PATH」にチェックを入れてインストール。  
3. コマンドプロンプト／PowerShell を開き、以下を実行してバージョンを確認：  
   ```powershell
   python --version
   ```  
   Python 3.x.x と表示されれば成功です。

### 4.2. ffmpeg インストール

1. [ffmpeg 公式ダウンロードページ](https://ffmpeg.org/download.html) に移動し、Windows 用ビルドをダウンロード。  
2. zip を解凍し、中にある `bin/ffmpeg.exe` を任意のフォルダ（例：`C:\tools\ffmpeg\bin\`）にコピー。  
3. システム環境変数に `C:\tools\ffmpeg\bin` を追加：  
   - 「スタートメニュー」→「環境変数」→「システム環境変数を編集」→「環境変数…」  
   - 「システム環境変数」欄で `Path` を選択 → 「編集」 → 新規で先ほどのパスを追加。  
4. コマンドプロンプト／PowerShell を再起動し、以下を実行して起動確認：  
   ```powershell
   ffmpeg -version
   ```  
   バージョン情報が表示されれば成功です。

### 4.3. リポジトリ配置

1. 任意のフォルダ（例：`C:\src\audio_transcribe+summary_dd\`）を作成。  
2. 以下のファイルをすべて同じフォルダにコピー：  
   - `transcribe_files.py`  
   - `prompt.json`  
   - `run_transcribe.bat`  
   - `run_transcribe.ps1`  
   - `requirements.txt`  
   - `.env`  
3. フォルダ構成例：  
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

### 4.4. 必要ライブラリのインストール

1. コマンドプロンプト／PowerShell を開き、作業ディレクトリを移動：  
   ```powershell
   cd C:\src\audio_transcribe+summary_dd
   ```  
2. `requirements.txt` を使って必要ライブラリをインストール：  
   ```powershell
   pip install -r requirements.txt
   ```  
3. ファイルの内容（例）：  
   ```shell
   openai>=1.0.0
   python-dotenv>=0.20.0
   ```  
4. インストール後、以下を実行してライブラリが入っているか確認してもよいです：  
   ```powershell
   python -c "import openai, dotenv; print('OK')"
   ```

---

## 環境変数設定（.env）

`.env` ファイルを用意すると、Python スクリプト実行時に次の環境変数を自動で読み込みます。以下はサンプルです。実行前に適宜中身を修正し、リポジトリ直下の `.env` として保存してください。

```ini
# =============================
# 1. 入力メディアファイル
# =============================
INPUT_DIR="./input"

# =============================
# 2. 文字起こし出力先
# =============================
OUTPUT_DIR="./output"

# =============================
# 3. 要約結果出力先
# =============================
SUMMARY_DIR="./output"

# =============================
# 4. 要約時に使用するプロンプトファイル
# =============================
PROMPT_PATH="./config/prompt_default.json"

# =============================
# 5. OpenAI APIキー (必須)
# =============================
OPENAI_API_KEY="sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

# =============================
# 6. 使用する Whisper モデル名 (オプション)
#    指定がない場合のデフォルトは "gpt-4o-mini-transcribe"
#    他の選択肢例: "whisper-1", "gpt-4o-transcribe"
# =============================
WHISPER_MODEL_NAME="gpt-4o-transcribe"

# =============================
# 7. 要約用モデル名 (オプション)
#    デフォルトは o3-mini
# =============================
SUMMARY_MODEL_NAME="o4-mini"

# =============================
# 8. デフォルトの文字起こし言語 (オプション)
#    ISO 639-1 形式の言語コード
#    例: "ja" (日本語), "en" (英語)
#    指定がない場合は API が自動検出
# =============================
# DEFAULT_LANGUAGE="ja"

# =============================
# 9. デフォルトのプロンプト (オプション)
#    会議の背景や専門用語などを指示できます
# =============================
# DEFAULT_PROMPT="この録音は、ディープテック技術に関するオンライン会議のものです。専門用語として臨床試験や知財等に関する専門用語が含まれます。日本語の場合は適切に漢字の変換や「てにをは」を文脈から読み取り、日本語以外の言語の場合も適切に文脈から適切な単語を選択するようにして下さい。"
```

### 主要な設定説明

- `INPUT_DIR`: 文字起こし対象のメディアファイルを置くフォルダ。Python スクリプトで引数が指定されなかった場合、このフォルダ内のすべての対応拡張子ファイルを処理します。  
- `OUTPUT_DIR`: 文字起こしテキスト（.txt）を保存するフォルダ。  
- `SUMMARY_DIR`: 要約テキスト（_summary.txt）を保存するフォルダ。  
- `PROMPT_PATH`: 要約時に使用するプロンプトファイルのパス（例：`./config/prompt_default.json`）。実際にはリポジトリ直下にある `prompt.json` を参照する場合、`PROMPT_PATH="./prompt.json"` とすれば OK。  
- `OPENAI_API_KEY`: OpenAI API キー。必須です。  
- `WHISPER_MODEL_NAME`: Whisper モデル名を指定。未指定の場合はスクリプト内部のデフォルト `"gpt-4o-mini-transcribe"` が使われます。  
- `SUMMARY_MODEL_NAME`: 要約用 LLM モデル名を指定。未指定の場合は `"o3-mini"` が使われます。  
- `DEFAULT_LANGUAGE`: 文字起こし言語を指定する場合に使います（例: `"ja"`）。指定がないと自動検出。  
- `DEFAULT_PROMPT`: 文字起こし・要約プロンプトを直接指定できます。あらかじめ `.env` にセットしておくと、「バッチ・PowerShell で渡さなくてもよい」ようになります。

---

## 設定ファイル (prompt.json) の準備

要約用のプロンプトを定義した `prompt.json` は必須です。以下のような内容になっていることを確認してください（インデント入り）:

```json
{
  "version": "1.2.0",
  "updated_at": "2025-05-14T12:00:00+09:00",
  "changelog": [
    {
      "version": "1.2.0",
      "date": "2025-05-14",
      "notes": "分析セクションに alternatives を追加、システムプロンプトを箇条書き化"
    },
    {
      "version": "1.1.0",
      "date": "2025-03-01",
      "notes": "多言語出力設定の強化"
    }
  ],
  "title": "汎用ディスカッション要約プロンプト",
  "description": "会議やワークショップ、オンライン討論など、あらゆる分野の議論を高精度に要約・記録し、必要に応じて多言語出力、リスク分析、意思決定支援まで行うテンプレート。",
  "system_prompt": "あなたは次の役割を担うエグゼクティブアシスタントです:\n1. ディープテックスタートアップ企業の経営・事業運営全般に精通する\n2. 財務・経理・人事・労務・法務・知財・総務・ITシステムまで幅広い専門知識を有する\n3. 議論の文字起こしから話者の意図と文脈を深く理解し、本質的な情報を抽出する\n4. 以下の出力スキーマに完全に準拠して議事録を作成する\n\n以下の順序と形式を厳守し、JSON オブジェクトとして出力してください。",
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
    "translate_behavior": "もし元言語が default_language と異なる場合、default_language に翻訳してから要約する"
  },
  "logging": {
    "level": "INFO",
    "include_request_id": true,
    "format": "[{timestamp}] {level} [{request_id}]: {message}"
  },
  "output_schema": [
    {
      "section": "メタ情報",
      "fields": [
        {
          "name": "request_id",
          "type": "string",
          "required": true,
          "description": "一意なリクエストID"
        },
        {
          "name": "session_id",
          "type": "string",
          "required": true,
          "description": "セッションID"
        },
        {
          "name": "generated_at",
          "type": "datetime",
          "required": true,
          "description": "生成日時 (ISO 8601)"
        },
        {
          "name": "model_used",
          "type": "string",
          "required": true,
          "description": "使用したモデル名"
        },
        {
          "name": "language",
          "type": "string",
          "required": true,
          "description": "出力言語コード"
        },
        {
          "name": "discussion_title",
          "type": "string",
          "required": false,
          "description": "議論のタイトル（任意）"
        }
      ]
    },
    {
      "section": "要約",
      "fields": [
        {
          "name": "overview",
          "type": "string",
          "required": true,
          "description": "議論の概要"
        },
        {
          "name": "key_findings",
          "type": "list<string>",
          "required": true,
          "description": "重要な発見・結論"
        },
        {
          "name": "action_items",
          "type": "list<string>",
          "required": false,
          "description": "アクションアイテム（必要時）"
        }
      ]
    },
    {
      "section": "分野ごとのまとめ",
      "fields": [
        {
          "name": "specialized_topics",
          "type": "list<string>",
          "required": false,
          "description": "専門分野別の要点"
        },
        {
          "name": "agenda_and_discussions",
          "type": "list<string>",
          "required": false,
          "description": "議題と議論内容の要約"
        },
        {
          "name": "topic_decisions",
          "type": "list<string>",
          "required": false,
          "description": "各分野・議題での決定事項"
        }
      ]
    },
    {
      "section": "分析",
      "fields": [
        {
          "name": "risks",
          "type": "list<string>",
          "required": false,
          "description": "リスク要因"
        },
        {
          "name": "alternatives",
          "type": "list<string>",
          "required": false,
          "description": "代替案・検討事項"
        },
        {
          "name": "final_decisions",
          "type": "list<string>",
          "required": false,
          "description": "最終的な意思決定事項"
        }
      ]
    }
  ],
  "style_guidelines": [
    "事実ベースで記述し、'～のように思われる' などの主観的推測を含めない",
    "専門用語は初出時に括弧内で定義を示す（例: 『SMB（サーバーメッセージブローカー）』）",
    "必要に応じて箇条書きを使用し、要点を明確にする（例: ・主要結論 ・次のステップ）",
    "文体はビジネスレポート形式とし、敬語を避け標準形で記述する"
  ],
  "context_instructions": "以下の `<<TRANSCRIPT>>` プレースホルダに文字起こし全文が挿入されます。全文を読み込み、上記スキーマに完全準拠して出力してください。",
  "transcript_placeholder": "<<TRANSCRIPT>>"
}
```

## 実行方法

以下のいずれかの方法で実行できます。ドラッグ＆ドロップ操作で簡単に動かせます。

### 7.1. バッチファイル（`.bat`）を使う方法

#### ショートカットを作成

エクスプローラで `run_transcribe.bat` を右クリック → 「ショートカットの作成」  
作成されたショートカットをデスクトップなどに置いておくと便利です。

#### ドラッグ＆ドロップで実行

対象の音声／動画ファイル（例：`meeting.mp4`）を `run_transcribe.bat`（またはそのショートカット）にドラッグ＆ドロップします。  
コマンドプロンプトが開き、次のように処理が行われます：

1. 環境変数 `PROMPT_PATH` に `prompt.json` のパスをセット  
2. Python スクリプト `transcribe_files.py` が起動し、引数で渡されたファイルだけを処理  
3. 文字起こし → 要約 → 生成結果の保存  
4. 処理完了メッセージ表示  

終了後、以下のファイルが同フォルダ内に生成されます：

- `meeting.txt` （文字起こし結果）  
- `meeting_summary.txt` （要約結果）  

一時ファイルの自動削除  
処理中に生成された `temp_processing_<ファイル名>` フォルダは、処理終了後に自動で削除されます。

---

### 7.2. PowerShell スクリプト（`.ps1`）を使う方法

#### 実行ポリシーの変更（初回のみ）

管理者権限で PowerShell を開き、以下を実行してローカルスクリプトの実行を許可します：

```powershell
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
```

確認メッセージが出たら「Y」を入力して確定。

#### ショートカットを作成（任意）

`run_transcribe.ps1` を右クリック → 「ショートカットの作成」  
ショートカットのリンク先に以下を設定するとダブルクリックだけで実行可能になります：

```powershell
powershell.exe -File "C:\src\audio_transcribe+summary_dd\run_transcribe.ps1"
```

ショートカットをデスクトップなどに置いておくと便利です。

#### ドラッグ＆ドロップで実行

対象の音声／動画ファイルを `run_transcribe.ps1`（またはそのショートカット）にドラッグ＆ドロップします。  
PowerShell が起動し、以下の流れで処理が行われます：

1. 環境変数 `PROMPT_PATH` に `prompt.json` のパスをセット  
2. Python スクリプト `transcribe_files.py` が引数で渡されたファイルを単一モードで処理  
3. 文字起こし → 要約 → 同フォルダに出力  
4. 完了メッセージ表示  

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

## ファイルの説明

### transcribe_files.py

実際に OpenAI Whisper を呼び出して音声→テキスト化し、得られた文字列を LLM（要約モデル）に投げて短くまとめるスクリプト。

- コマンドライン引数にファイルパスを渡すと「単一ファイルモード」で動きます。  
- 環境変数 `INPUT_DIR`, `OUTPUT_DIR`, `TEMP_DIR`, `SUMMARY_DIR` を使ってフォルダを制御します。  
- Whisper／要約失敗時はログ出力しつつスキップ。  
- 処理後は一時フォルダを自動で削除します。

### prompt.json

要約時に LLM に提示するプロンプト定義ファイル。

- 出力を JSON 形式でスキーマに沿って返すように設計されています。  
- 必ずスクリプト実行前に有効な JSON ファイルを用意してください（ファイル名やパスを変更した場合は、`.env` やバッチ／PowerShell でも同じパスを指定する必要があります）。

### requirements.txt

Python スクリプトの実行に必要なライブラリをまとめたファイル。

- 検索・要約機能には最低限以下が必要です：  
  ```shell
  openai>=1.0.0
  python-dotenv>=0.20.0
  ```  
- 追加で他のパッケージが必要になったら適宜追記してください。

### run_transcribe.bat

Windows のバッチファイル。

- ファイルをドラッグ＆ドロップすると、`transcribe_files.py` が自動で呼び出されます。  
- 環境変数 `PROMPT_PATH` はバッチ内で固定しています。変更が必要な場合はバッチを編集してください。

### run_transcribe.ps1

PowerShell 用のラッパースクリプト。

- ファイルをドラッグ＆ドロップすると、最初のファイルパスを引数として Python スクリプトを起動します。  
- 実行ポリシーの調整（`Set-ExecutionPolicy RemoteSigned`）が必要です。

### .env

環境変数をまとめたファイル。

- Whisperモデル名や要約モデル名、プロンプトパス、出力先などを一元管理できます。  
- 必ず正しいパス・キーに書き換えてから使用してください。

---

## トラブルシューティング

### Python 実行時にモジュールエラーが出る

```
ModuleNotFoundError: No module named 'openai'
```

- 上記のようなエラーが出た場合は、再度 `pip install -r requirements.txt` を実行してください。  
- それでも解決しない場合は、Python が複数バージョンインストールされている可能性があります。  
  ```powershell
  python -m pip install -r requirements.txt
  ```  
  のように明示的に実行してみてください。

### ffmpeg が見つからない・コマンドが見つからないエラー

- `ffmpeg -version` を実行してバージョン情報が表示されるか確認。  
- `’ffmpeg’ は内部コマンドまたは外部コマンド...` と出る場合は、`ffmpeg.exe` のあるフォルダを環境変数 `PATH` に登録し、PowerShell／コマンドプロンプトを再起動してください。

### OpenAI API キーエラー

- `API キーが設定されていません` と出る場合は、環境変数 `OPENAI_API_KEY` が正しくセットされているか確認。  
- PowerShell で一時的にセットするなら：  
  ```powershell
  $env:OPENAI_API_KEY = "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
  ```  
  その後 `python transcribe_files.py` を実行してキーが読み込まれるか試してください。

### prompt.json の読み込みエラー

- JSON 構文エラーやファイルパス間違いが原因です。  
- ファイルを UTF-8 で保存し、`.env` やバッチ／PowerShell で指定したパスが正しいか確認してください。

### 要約の結果が想定と異なる

- `prompt.json` 内の `system_prompt` やスキーマが適切であるかチェック。  
- LLM の生成パラメータ（`temperature`, `max_tokens`）を調整することで出力を安定させることができます。

---

## ライセンス・注意事項

本ツールはサンプル実装です。商用利用の際は各ライブラリ・モデルの利用規約を遵守してください。

OpenAI API の利用には料金がかかる場合があります。利用前に OpenAI の料金ページ をご確認ください。

Whisper等を用いた文字起こしおよび要約はインターネット接続が必要です。オフライン環境では動作しません。
