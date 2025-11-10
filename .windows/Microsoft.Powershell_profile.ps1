# PowerShell Profile - Minimal & Optimized

# Import Modules
Import-Module Terminal-Icons -ErrorAction SilentlyContinue

# Starship Prompt
$env:STARSHIP_CONFIG = "$HOME\.config\starship\starship.toml"
Invoke-Expression (&starship init powershell)

# Set Nerd Font in Terminal (Ensure your Terminal is using one)
$Host.UI.RawUI.WindowTitle = "PowerShell - Customized"

# Aliases
# List files like Linux `ls` with icons
function ll { Get-ChildItem -Force | Format-Table -AutoSize }
function la { Get-ChildItem -Force -Hidden | Format-Table -AutoSize }

# Git Shortcuts
function gs { git status }
function ga { git add . }
function gc { git commit -m "$args" }
function gp { git push }

# Quick File Creation
function nf { param($name) New-Item -ItemType "File" -Path . -Name $name }

# Directory Management
function mkcd { param($dir) New-Item -ItemType Directory -Path $dir -Force; Set-Location $dir }

# Clear with 'c'
Set-Alias -Name c -Value Clear-Host


# Navigation
function docs { Set-Location -Path ([Environment]::GetFolderPath("MyDocuments")) }
function dtop { Set-Location -Path ([Environment]::GetFolderPath("Desktop")) }

# Clipboard (Mac/Linux-like pbcopy & pbpaste)
Set-Alias pbcopy "Set-Clipboard"
Set-Alias pbpaste "Get-Clipboard"

# Quality of Life Functions
function mkcd { param($dir) mkdir $dir -Force; Set-Location $dir }
function reload-profile { & $PROFILE }

# Uptime
function uptime {
    $uptime = (Get-Date) - (Get-CimInstance Win32_OperatingSystem).LastBootUpTime
    Write-Host ("Uptime: {0} days, {1} hours, {2} minutes" -f $uptime.Days, $uptime.Hours, $uptime.Minutes) -ForegroundColor Cyan
}

# System Info
function sysinfo { Get-ComputerInfo }

# Quick File Search
function ff { param($name) Get-ChildItem -Recurse -Filter "*${name}*" -ErrorAction SilentlyContinue }

# Quick Git Commit & Push
function gcom { git add .; git commit -m $args; git push }

# Network Utilities
function Get-PubIP { (Invoke-WebRequest http://ifconfig.me/ip).Content }

# Terminal Cleanup
function Clear-Cache {
    Write-Host "Clearing Temp & Cache Files..." -ForegroundColor Yellow
    Remove-Item -Path "$env:TEMP\*" -Recurse -Force -ErrorAction SilentlyContinue
    Write-Host "Done!" -ForegroundColor Green
}

# Show Available Commands
function Show-Help {
    Write-Host @"
PowerShell Custom Shortcuts:
----------------------------
ls      - Show files with icons
ll      - List all files (detailed)
la      - List hidden files
docs    - Open Documents folder
dtop    - Open Desktop folder
pbcopy  - Copy to clipboard (Mac-style)
pbpaste - Paste from clipboard (Mac-style)
mkcd    - Create & enter directory
reload-profile - Reload this profile
uptime  - Show system uptime
sysinfo - Show system info
ff <name> - Find file by name
gcom "message" - Quick Git commit & push
Get-PubIP - Show public IP address
Clear-Cache - Clean temp files

Use 'Show-Help' to see this message again.
"@
}
Write-Host "Type 'Show-Help' for available commands."
