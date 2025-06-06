<# 
    run_transcribe.ps1

    ドラッグ＆ドロップされたファイルを処理するラッパー
#>

Param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]] $files
)

# 1) 改修後の Python スクリプトの場所
$scriptPath = "C:\src\audio_transcribe+summary_dd\transcribe_files.py"

# 2) 要約用プロンプト JSON のフルパスを環境変数に設定
$env:PROMPT_PATH = "C:\src\audio_transcribe+summary_dd\prompt.json"

# 3) Python 実行コマンド（環境変数 PATH に python.exe が通っていれば "python"）
$pythonExe = "python"

# 4) ドラッグされたファイルが１つ以上あるかチェック
if ($files.Count -eq 0) {
    Write-Host "ファイルをドラッグ＆ドロップしてください。"
    exit
}

# 5) 最初に渡されたファイルパスを Python にそのまま渡す
#    （Python 側で“単一ファイルモード”として処理される）
Push-Location (Split-Path $scriptPath -Parent)
& $pythonExe $scriptPath $files[0]
Pop-Location

Write-Host "===== 文字起こし・要約 完了 ====="
