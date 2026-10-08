# blender-control.ps1 — start / stop / status for the xiaozhi-MCP Blender instance
# Usage:
#   powershell -ExecutionPolicy Bypass -File blender-control.ps1 -Action start
#   powershell -ExecutionPolicy Bypass -File blender-control.ps1 -Action stop [-Force]
#   powershell -ExecutionPolicy Bypass -File blender-control.ps1 -Action status
# NOTE: paths are relative to THIS file's folder ($PSScriptRoot) — move freely.
param(
  [Parameter(Mandatory = $true)][ValidateSet('start', 'stop', 'status')]$Action,
  [switch]$Force
)

$ErrorActionPreference = 'SilentlyContinue'
$Base       = $PSScriptRoot
$BlenderExe = "C:\Program Files\Blender Foundation\Blender 4.2\blender.exe"
$Autostart  = Join-Path $Base 'blender_autostart.py'
$Py         = "C:\Users\slk\venv\Scripts\python.exe"
$Client     = Join-Path $Base 'blender_cmd.py'
$TmpDir     = $Base

function Test-Port9876 {
  (Test-NetConnection 127.0.0.1 -Port 9876 -WarningAction SilentlyContinue).TcpTestSucceeded
}

function Send-Code([string]$Code) {
  $tmp = Join-Path $TmpDir ("_code_" + [guid]::NewGuid().ToString("N").Substring(0, 6) + ".py")
  Set-Content -Path $tmp -Value $Code -Encoding UTF8
  $out = & $Py $Client execute_code -f $tmp 2>$null
  Remove-Item $tmp -Force -ErrorAction SilentlyContinue
  return ($out -join "`n")
}

switch ($Action) {

  'start' {
    if (Test-Port9876) { Write-Output "Blender MCP already running (port 9876 UP). Nothing to do."; break }
    Start-Process -FilePath $BlenderExe -ArgumentList '--python', "`"$Autostart`""
    Write-Output "Blender launching, waiting for MCP port 9876 ..."
    for ($i = 0; $i -lt 30; $i++) {
      Start-Sleep -Seconds 1
      if (Test-Port9876) { Write-Output "OK: Blender MCP server is UP (port 9876)."; break }
      if ($i -eq 29) { Write-Output "TIMEOUT: port 9876 did not come up in 30s." }
    }
  }

  'stop' {
    if (Test-Port9876) {
      # 1. check unsaved changes
      $resp = Send-Code @'
import bpy
print("STATE_DIRTY" if bpy.data.is_dirty else "STATE_CLEAN")
'@
      if ($resp -match 'STATE_DIRTY') {
        # 2a. save unsaved work: in place if it has a file, otherwise to a backup
        $r2 = Send-Code @'
import bpy
if bpy.data.filepath:
    bpy.ops.wm.save_mainfile()
    print("SAVED_IN_PLACE:", bpy.data.filepath)
else:
    p = r"C:\Users\slk\BlenderMCP_autosave_backup.blend"
    bpy.ops.wm.save_as_mainfile(filepath=p)
    print("SAVED_BACKUP:", p)
'@
        Write-Output ($r2 -replace '\n', ' | ')
      }
      # 3. graceful quit
      Send-Code @'
import bpy
bpy.ops.wm.quit_blender()
'@ | Out-Null
      Start-Sleep -Seconds 4
    }
    $left = Get-Process blender -ErrorAction SilentlyContinue
    if ($left) {
      if ($Force) {
        $left | Stop-Process -Force
        Write-Output ("Force closed remaining Blender processes: " + ($left.Id -join ', '))
      } else {
        Write-Output ("MCP instance closed. Other Blender processes still running (no unsaved-data check possible): " + ($left.Id -join ', ') + "  -> use -Force to kill.")
      }
    } else {
      Write-Output "Blender fully closed."
    }
  }

  'status' {
    $procs = Get-Process blender -ErrorAction SilentlyContinue
    if ($procs) {
      Write-Output ("Blender processes: " + (($procs | ForEach-Object { "PID $($_.Id) (started $($_.StartTime.ToString('HH:mm:ss')))" }) -join '; '))
    } else {
      Write-Output "Blender processes: none"
    }
    Write-Output ("MCP port 9876: " + $(if (Test-Port9876) { "UP" } else { "down" }))
  }
}
