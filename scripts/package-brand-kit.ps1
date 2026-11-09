$ErrorActionPreference = 'Stop'
$root = Split-Path $PSScriptRoot -Parent
$kit = Join-Path $root 'brand-kit'
$assets = Join-Path $kit 'assets'
New-Item -ItemType Directory -Force -Path $assets | Out-Null
Copy-Item -LiteralPath (Join-Path $root 'img/sotolab-logo-white.png') -Destination (Join-Path $assets 'logo-light.png')
Copy-Item -LiteralPath (Join-Path $root 'img/sotolab-logo-black-v3.png') -Destination (Join-Path $assets 'logo-dark.png')
$files = @('index.html', 'redirect.js', 'guide.html', 'guide.css', 'guide.js', 'tokens.css', 'tokens.json', 'templates.html', 'assets') | ForEach-Object { Join-Path $kit $_ }
Compress-Archive -Path $files -DestinationPath (Join-Path $kit 'sotolab-brand-kit.zip') -Force
Write-Output 'Packaged brand-kit/sotolab-brand-kit.zip'
