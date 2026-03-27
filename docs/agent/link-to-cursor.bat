@echo off
chcp 65001 >nul
:: 创建符号链接：docs/agent/rules/*.md -> .codemaker/rules/*.mdc
:: 需要管理员权限运行

cd /d %~dp0\..\..

:: 检查源目录是否存在
if not exist "docs\agent\rules" (
    echo 错误: 源目录 docs\agent\rules 不存在
    pause
    exit /b 1
)

echo 正在创建 Cursor 规则链接...

:: 确保 .codemaker/rules 目录存在
if not exist ".codemaker\rules" mkdir ".codemaker\rules"

:: 删除旧的 .mdc 文件
del /q ".codemaker\rules\*.mdc" 2>nul

:: 遍历 docs/agent/rules/*.md 并创建对应的 .mdc 硬链接
for %%f in (docs\agent\rules\*.md) do (
    echo 链接: %%~nf.md -^> %%~nf.mdc
    mklink /H ".codemaker\rules\%%~nf.mdc" "%%f"
)

echo.
echo 链接创建完成:
echo   .codemaker\rules\*.mdc -^> docs\agent\rules\*.md
echo.
echo 文件列表:
dir /b ".codemaker\rules\*.mdc"
pause