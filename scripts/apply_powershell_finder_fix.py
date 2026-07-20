#!/usr/bin/env python3
from pathlib import Path

path = Path(__file__).resolve().parents[1] / "install.ps1"
text = path.read_text(encoding="utf-8")
old = '''    $Output = & $Python.Executable @($Python.Prefix + @("-B", "-E", "-s", "-S", "-c", $Finder, $HomeDirectory))
    $Code = $LASTEXITCODE
'''
new = '''    $FinderPath = Join-Path ([System.IO.Path]::GetTempPath()) ("ams-find-uninstaller-" + [Guid]::NewGuid().ToString("N") + ".py")
    $Utf8NoBom = New-Object System.Text.UTF8Encoding -ArgumentList $false
    [System.IO.File]::WriteAllText($FinderPath, $Finder, $Utf8NoBom)
    try {
        $Output = & $Python.Executable @($Python.Prefix + @("-B", "-E", "-s", "-S", $FinderPath, $HomeDirectory))
        $Code = $LASTEXITCODE
    }
    finally {
        Remove-Item -LiteralPath $FinderPath -Force -ErrorAction SilentlyContinue
    }
'''
if new not in text:
    if text.count(old) != 1:
        raise SystemExit(f"Expected one PowerShell finder invocation, found {text.count(old)}")
    text = text.replace(old, new, 1)
path.write_text(text, encoding="utf-8", newline="\n")
print("PowerShell canonical uninstaller finder quoting fixed.")
