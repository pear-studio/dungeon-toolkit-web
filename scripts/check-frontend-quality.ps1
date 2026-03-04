# Frontend Code Quality Checker
# Checks for emoji, low contrast text, focus styles, and ARIA attributes
#
# Usage:
#   powershell -ExecutionPolicy Bypass -File scripts/check-frontend-quality.ps1

Write-Host "================================" -ForegroundColor Cyan
Write-Host "  Frontend Code Quality Check" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

$ErrorCount = 0
$WarningCount = 0
$StartTime = Get-Date

# Check 1: emoji detection
Write-Host "Check 1/4: Detecting emoji characters..." -ForegroundColor Yellow

$EmojiFound = $false
Get-ChildItem -Path ".\frontend\src" -Recurse -Include *.tsx,*.ts -ErrorAction SilentlyContinue | 
    ForEach-Object {
        $Content = Get-Content $_.FullName -Raw -Encoding UTF8
        # Match common emoji ranges (UTF-8)
        if ($Content -match '[\xF0-\xF7][\x80-\xBF][\x80-\xBF][\x80-\xBF]') {
            $EmojiFound = $true
            Write-Host "  Found emoji in: $($_.Name)" -ForegroundColor Red
        }
    }

if ($EmojiFound) {
    Write-Host "FAIL: emoji found in code" -ForegroundColor Red
    $ErrorCount++
} else {
    Write-Host "PASS: No emoji found" -ForegroundColor Green
}

Write-Host ""

# Check 2: Low contrast text
Write-Host "Check 2/4: Detecting low contrast text..." -ForegroundColor Yellow

$LowContrast = Get-ChildItem -Path ".\frontend\src" -Recurse -Include *.tsx,*.ts -ErrorAction SilentlyContinue | 
    Select-String -Pattern 'text-slate-(500|600|700)'

if ($LowContrast) {
    Write-Host "WARN: Found low contrast text (first 20):" -ForegroundColor Yellow
    $LowContrast | Select-Object -First 20 | ForEach-Object {
        Write-Host "  $($_.Filename):$($_.LineNumber)" -ForegroundColor Yellow
    }
    $Count = ($LowContrast | Measure-Object).Count
    if ($Count -gt 20) {
        Write-Host "... and $($Count - 20) more" -ForegroundColor Yellow
    }
    $WarningCount++
} else {
    Write-Host "PASS: No low contrast issues" -ForegroundColor Green
}

Write-Host ""

# Check 3: Missing focus styles on buttons
Write-Host "Check 3/4: Detecting buttons without focus styles..." -ForegroundColor Yellow

$ButtonFiles = Get-ChildItem -Path ".\frontend\src" -Recurse -Include *.tsx -ErrorAction SilentlyContinue | 
    Select-String -Pattern '<button'

$NoFocus = $ButtonFiles | Where-Object {
    $_.Line -notmatch 'focus:'
} | Select-Object -First 20

if ($NoFocus) {
    Write-Host "WARN: Found buttons without focus styles (first 20):" -ForegroundColor Yellow
    $NoFocus | ForEach-Object {
        Write-Host "  $($_.Filename):$($_.LineNumber)" -ForegroundColor Yellow
    }
    $WarningCount++
} else {
    Write-Host "PASS: All buttons have focus styles" -ForegroundColor Green
}

Write-Host ""

# Check 4: Missing aria attributes on icons
Write-Host "Check 4/4: Detecting icons without aria attributes..." -ForegroundColor Yellow

$IconFiles = Get-ChildItem -Path ".\frontend\src" -Recurse -Include *.tsx -ErrorAction SilentlyContinue | 
    Select-String -Pattern 'className=.*w-\d.*h-\d'

$NoAria = $IconFiles | Where-Object {
    $_.Line -notmatch 'aria-hidden' -and $_.Line -notmatch 'aria-label'
} | Select-Object -First 20

if ($NoAria) {
    Write-Host "WARN: Found icons without aria attributes (first 20):" -ForegroundColor Yellow
    $NoAria | ForEach-Object {
        Write-Host "  $($_.Filename):$($_.LineNumber)" -ForegroundColor Yellow
    }
    $WarningCount++
} else {
    Write-Host "PASS: All icons have aria attributes" -ForegroundColor Green
}

Write-Host ""

# Calculate duration
$EndTime = Get-Date
$Duration = $EndTime - $StartTime

# Summary
Write-Host "================================" -ForegroundColor Cyan
Write-Host "  Check Complete!" -ForegroundColor Cyan
Write-Host "  Duration: $($Duration.Milliseconds)ms" -ForegroundColor Cyan
Write-Host "  Errors: $ErrorCount" -ForegroundColor $(if ($ErrorCount -gt 0) {"Red"} else {"Green"})
Write-Host "  Warnings: $WarningCount" -ForegroundColor $(if ($WarningCount -gt 0) {"Yellow"} else {"Green"})
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Exit codes
if ($ErrorCount -gt 0) {
    Write-Host "FAILED: Please fix the errors above" -ForegroundColor Red
    exit 1
} elseif ($WarningCount -gt 0) {
    Write-Host "PASSED with warnings (optimization recommended)" -ForegroundColor Yellow
    exit 0
} else {
    Write-Host "PASSED: All checks successful!" -ForegroundColor Green
    exit 0
}
