param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("chrome","edge")]
    [string]$Target
)

$ClaudeJson = "C:\Users\沈璞\.claude.json"
$McpCmd = "C:\Users\沈璞\AppData\Roaming\npm\chrome-devtools-mcp.cmd"

$ChromeArgs = @("/c", $McpCmd)

$EdgeArgs = @(
    "/c", $McpCmd,
    "--executablePath", "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    "--proxyServer", "direct://",
    "--userDataDir", "C:\Users\沈璞\.cache\chrome-devtools-mcp\edge-profile"
)

$args = if ($Target -eq "edge") { $EdgeArgs } else { $ChromeArgs }

$json = Get-Content $ClaudeJson -Raw -Encoding UTF8 | ConvertFrom-Json
if (-not $json.mcpServers) {
    $json | Add-Member -NotePropertyName mcpServers -NotePropertyValue (New-Object PSObject)
}

$entry = [PSCustomObject]@{
    type = "stdio"
    command = "cmd"
    args = $args
    env = (New-Object PSObject)
}
$json.mcpServers | Add-Member -NotePropertyName "chrome-devtools" -NotePropertyValue $entry -Force

($json | ConvertTo-Json -Depth 30) | Set-Content $ClaudeJson -Encoding UTF8

Write-Output "chrome-devtools MCP -> $Target"
Write-Output "Restart Claude Code session for changes to take effect."
