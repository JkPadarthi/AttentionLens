"Started: $(Get-Date) | cwd: $(Get-Location)" | Out-File "C:\Users\padar\opencode-task.log" -Append

$env:OPENCODE_SERVER_USERNAME = "hermes"
$env:OPENCODE_SERVER_PASSWORD = "PASTE_YOUR_REAL_PASSWORD_HERE"

# ---- FIX: opencode uses the process cwd as its project root ----
# Without this, Task Scheduler defaults to C:\Windows\System32,
# and the file API 500s on every path outside it.
Set-Location -Path "D:\GIT"

& "C:\Users\padar\.bun\bin\opencode.exe" serve --hostname 0.0.0.0 --port 4096
