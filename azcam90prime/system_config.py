# azcamserver configuration parameters

use_venv = 1
venv_script = "c:/venvs/azcam/Scripts/activate.bat"

server_profile = "AzCamServer"
console_profile = "AzCamConsole"
server_cmd = "import azcamserver_90prime; from  cli_servercommands import *"
console_cmd = "import azcamconsole_90prime; from  cli_consolecommands import *"

azcamlogfolder = "c:/azcam/azcamlog/azcamlog"
commonfolder = "c:/azcam/systems/common"
datafolder_root = "c:/data/90prime"
systemname = "90prime"

verbosity = 1
xmode = "Context"  # Minimal, Context, Verbose
test_mode = 0
readparfile = 1
servermode = "interactive"  # prompt, interactive, server
start_azcamtool = 1
start_webapp = 0
