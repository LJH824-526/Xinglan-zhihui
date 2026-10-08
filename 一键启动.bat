@echo off
title XiaoZhi x Blender MCP
cd /d "%~dp0"

echo ============================================
echo   XiaoZhi x Blender MCP - 一键启动
echo ============================================

rem ---------- 1) Blender MCP 服务 ----------
powershell -NoProfile -Command "exit [int](Test-NetConnection 127.0.0.1 -Port 9876 -WarningAction SilentlyContinue).TcpTestSucceeded"
if errorlevel 1 goto launch_blender
echo [OK] Blender MCP 服务已在运行，跳过启动 Blender
goto blender_ok

:launch_blender
echo [..] 正在启动 Blender（约需 10-20 秒）...
start "" "C:\Program Files\Blender Foundation\Blender 4.2\blender.exe" --python "%~dp0blender_autostart.py"
set /a tries=0
:waitloop
timeout /t 2 /nobreak >nul
set /a tries+=1
powershell -NoProfile -Command "exit [int](Test-NetConnection 127.0.0.1 -Port 9876 -WarningAction SilentlyContinue).TcpTestSucceeded"
if not errorlevel 1 goto waitloop
if %tries% geq 30 (
    echo [!] 超时：Blender MCP 服务 60 秒内未就绪，请检查 Blender 窗口是否正常打开
    goto bridge_step
)
goto waitloop

:blender_ok
echo [OK] Blender MCP 服务就绪 (端口 9876)

:bridge_step
rem ---------- 2) 小智桥接 ----------
powershell -NoProfile -Command "if (Get-CimInstance Win32_Process | Where-Object { $_.Name -like '*python*' -and $_.CommandLine -match 'mcp_pipe' }) { exit 1 } else { exit 0 }"
if errorlevel 1 (
    echo [OK] 小智桥接已在运行，跳过
    goto done
)
echo [..] 正在启动小智桥接（新窗口）...
start "Xiaozhi-Blender-MCP" /D "%~dp0" "C:\Users\slk\venv\Scripts\python.exe" mcp_pipe.py
timeout /t 3 /nobreak >nul
echo [OK] 桥接已启动

:done
echo.
echo ============================================
echo   全部就绪！现在可以对小智语音说：
echo   "帮我在Blender里创建一个立方体"
echo ============================================
echo 提示：桥接窗口保持开着；收工时运行 一键停止.bat
echo.
pause
