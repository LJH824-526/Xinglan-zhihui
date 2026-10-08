# Auto-enable blender_mcp addon and start its MCP server on Blender launch
import addon_utils
import bpy

# 1. Enable the addon (and persist it in preferences)
try:
    addon_utils.enable("blender_mcp", default_set=True)
    print("[blmcp-autostart] addon enabled")
except Exception as e:
    print("[blmcp-autostart] enable failed:", e)

# 2. Start the MCP socket server (port 9876)
try:
    bpy.ops.blendermcp.start_server()
    print("[blmcp-autostart] MCP server started")
except Exception as e:
    print("[blmcp-autostart] start_server failed:", e)

# 3. Save preferences so the addon stays enabled for future launches
try:
    bpy.ops.wm.save_userpref()
    print("[blmcp-autostart] userpref saved")
except Exception as e:
    print("[blmcp-autostart] save_userpref failed:", e)
