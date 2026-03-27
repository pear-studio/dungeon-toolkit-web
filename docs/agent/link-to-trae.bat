@echo off
:: 创建符号链接：docs/agent/ -> .trae/
:: 需要管理员权限运行

cd /d %~dp0\..\..

echo 正在创建符号链接...

:: 删除旧目录
if exist ".trae\rules" (
    rmdir /s /q ".trae\rules"
    echo 已删除 .trae\rules
)
if exist ".trae\skills" (
    rmdir /s /q ".trae\skills"
    echo 已删除 .trae\skills
)

:: 创建符号链接
mklink /D ".trae\rules" "docs\agent\rules"
mklink /D ".trae\skills" "docs\agent\skills"

echo.
echo 符号链接创建完成:
echo   .trae\rules  -^> docs\agent\rules
echo   .trae\skills -^> docs\agent\skills
pause