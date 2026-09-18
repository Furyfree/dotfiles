# Minimal PowerShell profile: parity with the zsh/bash setup.

if (Get-Command starship -ErrorAction SilentlyContinue) { Invoke-Expression (& starship init powershell | Out-String) }
if (Get-Command mise -ErrorAction SilentlyContinue) { Invoke-Expression (& mise activate pwsh | Out-String) }
if (Get-Command zoxide -ErrorAction SilentlyContinue) { Invoke-Expression (& zoxide init powershell | Out-String) }

Set-PSReadLineOption -HistorySearchCursorMovesToEnd
Set-PSReadLineKeyHandler -Key UpArrow -Function HistorySearchBackward
Set-PSReadLineKeyHandler -Key DownArrow -Function HistorySearchForward

Set-Alias -Name ls -Value eza -ErrorAction SilentlyContinue
Set-Alias -Name cat -Value bat -ErrorAction SilentlyContinue
Set-Alias -Name lg -Value lazygit -ErrorAction SilentlyContinue
