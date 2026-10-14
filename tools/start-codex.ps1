param([ValidateSet('cli','vscode')][string]$Mode = 'cli')
$ErrorActionPreference = 'Stop'
$taskRoot = Split-Path -Parent $PSScriptRoot
$taskClaudePath = Join-Path $env:USERPROFILE '.claude.json'
$taskOriginalEnv = @{}
$taskNames = @('ZOTERO_API_KEY','ZOTERO_LIBRARY_ID','ZOTERO_LIBRARY_TYPE')
foreach ($taskName in $taskNames) { $taskOriginalEnv[$taskName] = [Environment]::GetEnvironmentVariable($taskName, 'Process') }
try {
    if (Test-Path -LiteralPath $taskClaudePath) {
        $taskConfig = Get-Content -LiteralPath $taskClaudePath -Raw -Encoding UTF8 | ConvertFrom-Json
        $taskZotero = $taskConfig.mcpServers.zotero.env
        foreach ($taskName in $taskNames) {
            if (-not [Environment]::GetEnvironmentVariable($taskName, 'Process') -and $taskZotero.$taskName) {
                [Environment]::SetEnvironmentVariable($taskName, [string]$taskZotero.$taskName, 'Process')
            }
        }
    }
    foreach ($taskRequired in @('ZOTERO_API_KEY','ZOTERO_LIBRARY_ID')) {
        if (-not [Environment]::GetEnvironmentVariable($taskRequired, 'Process')) {
            throw "Missing $taskRequired. Configure it in the current process or existing local Claude settings; no secret is saved by this launcher."
        }
    }
    Push-Location -LiteralPath $taskRoot
    try {
        if ($Mode -eq 'vscode') {
            Write-Host 'Close all VS Code windows first so the new process inherits the Zotero environment. Install the official Codex extension if needed.'
            & code --new-window $taskRoot
        } else {
            & codex --cd $taskRoot
        }
        if ($LASTEXITCODE -ne 0) { throw "Launcher exited with code $LASTEXITCODE" }
    } finally { Pop-Location }
} finally {
    foreach ($taskName in $taskNames) { [Environment]::SetEnvironmentVariable($taskName, $taskOriginalEnv[$taskName], 'Process') }
}
