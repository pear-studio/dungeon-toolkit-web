@echo off

chcp 65001 >nul

:: Rules: docs/agent/rules/*.md 硬链接到 .cursor/rules/*.mdc

:: https://cursor.com/docs/context/rules

:: Skills: 目录符号链接 .cursor/skills -> docs/agent/skills

:: https://cursor.com/docs/context/skills

::

:: 注意: Windows 下 mklink /D 的目标若为相对路径, 会相对"链接所在目录"

:: (即 .cursor\)解析, 从而指向错误路径. skills 必须使用仓库根的绝对路径.

::

:: mklink /H 同卷硬链接; mklink /D 目录符号链接(有时需管理员或开发者模式)

:: 可重复运行



cd /d %~dp0\..\..

set "REPO_ROOT=%CD%"



if not exist "docs\agent\rules" (

    echo 错误: 源目录 docs\agent\rules 不存在

    pause

    exit /b 1

)

if not exist "docs\agent\skills" (

    echo 错误: 源目录 docs\agent\skills 不存在

    pause

    exit /b 1

)



if not exist ".cursor" mkdir ".cursor"



echo 正在链接 Cursor 规则目录 .cursor\rules ...

if not exist ".cursor\rules" mkdir ".cursor\rules"

del /q ".cursor\rules\*.mdc" 2>nul

for %%f in (docs\agent\rules\*.md) do (

    echo 硬链接: %%~nf.md -^> .cursor\rules\%%~nf.mdc

    mklink /H ".cursor\rules\%%~nf.mdc" "%REPO_ROOT%\docs\agent\rules\%%~nf.md"

)



echo.

echo 正在链接 Cursor skills 目录...

if exist ".cursor\skills" (

    rmdir /s /q ".cursor\skills" 2>nul

    del ".cursor\skills" 2>nul

    echo 已删除旧的 .cursor\skills

)

mklink /D ".cursor\skills" "%REPO_ROOT%\docs\agent\skills"



echo.

echo 完成. Cursor 将加载:

echo   .cursor\rules\*.mdc  -^> docs\agent\rules\*.md

echo   .cursor\skills       -^> %REPO_ROOT%\docs\agent\skills

echo.

echo 规则文件:

dir /b ".cursor\rules\*.mdc"

pause

