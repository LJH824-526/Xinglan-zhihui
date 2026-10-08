@echo off
title XiaoZhi x Blender MCP - 停止
cd /d "%~dp0"

echo [..] 停止小智桥接...
powershell -NoProfile -Command "Get-CimInstance Win32_Process | Where-Object { $_.Name -like '*python*' -and $_.CommandLine -match 'mcp_pipe' } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force; Write-Output ('  killed PID ' + $_.ProcessId) }"

echo [..] 关闭 Blender（如有未保存的修改会自动保存/备份）...
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0blender-control.ps1" -Action stop

echo.
echo 已全部停止。下次使用请双击 一键启动.bat
pause
