@echo off

cd /d %~dp0\..\..

set "REPO_ROOT=%CD%"


if not exist "docs\agent\rules\ai-usage.md" (
    echo Error: Source file docs\agent\rules\ai-usage.md does not exist
    pause
    exit /b 1
)

if not exist "docs\agent\skills" (
    echo Error: Source directory docs\agent\skills does not exist
    pause
    exit /b 1
)


if not exist ".claude" mkdir ".claude"


echo Linking Claude Code project config ...

if exist ".claude\CLAUDE.md" (
    del /q ".claude\CLAUDE.md" 2>nul
    echo Deleted old .claude\CLAUDE.md
)

echo Hardlink: docs\agent\rules\ai-usage.md -^> .claude\CLAUDE.md
mklink /H ".claude\CLAUDE.md" "%REPO_ROOT%\docs\agent\rules\ai-usage.md"

if %ERRORLEVEL% neq 0 (
    echo Failed to create hardlink, trying symlink...
    mklink ".claude\CLAUDE.md" "%REPO_ROOT%\docs\agent\rules\ai-usage.md"
)


echo.
echo Linking Claude Code skills directory...

if exist ".claude\skills" (
    rmdir /s /q ".claude\skills" 2>nul
    del ".claude\skills" 2>nul
    echo Deleted old .claude\skills
)

mklink /D ".claude\skills" "%REPO_ROOT%\docs\agent\skills"

if %ERRORLEVEL% neq 0 (
    echo.
    echo Error: Failed to create skills symlink. May require admin or developer mode.
)


echo.
echo Done! Claude Code will load:
echo   .claude\CLAUDE.md  -^> docs\agent\rules\ai-usage.md
echo   .claude\skills     -^> docs\agent\skills
echo.

echo Skills:
for /d %%d in (docs\agent\skills\*) do (
    echo   - %%~nd
)
echo.

pause
