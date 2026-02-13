# clean_migrations.ps1
# Clean migrations and SQLite database (Development only)

$ErrorActionPreference = "Stop"

Write-Host "Cleaning migrations and SQLite databases..."

# Delete migration files (except __init__.py)
Get-ChildItem -Recurse -Filter "*.py" |
Where-Object { $_.FullName -match "migrations\\[0-9].*\.py$" } |
Remove-Item -Force -Verbose

# Delete SQLite databases
Get-ChildItem -Recurse -Filter "*.sqlite3" |
Remove-Item -Force -Verbose

Write-Host "Cleanup complete. Run migrations again."
