# clean_migrations.ps1
# Remove Django migration files that start with numbers
# Preserves __init__.py

$ErrorActionPreference = "Stop"

Get-ChildItem -Recurse -Path . `
    -Filter "*.py" |
Where-Object {
    $_.FullName -match "\\migrations\\[0-9].*\.py$"
} |
ForEach-Object {
    Write-Host "Deleting $($_.FullName)"
    Remove-Item $_.FullName -Force
}
