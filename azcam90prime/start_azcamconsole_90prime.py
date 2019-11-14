# script to start azcamconsole

import os

import system_config as config

# virtual enviroment
if config.use_venv:
    ipython = f"call {config.venv_script} && ipython"
else:
    ipython = "ipython"

# set profile and window title
profile = config.console_profile
profiledir = f"{config.datafolder_root}/azcam/profiles/{profile}"

# run ipython in current process window
xmode = f"InteractiveShell.xmode={config.xmode}"
cl = f'{ipython} --profile {profile} --profile-dir={profiledir} --{xmode} --TerminalInteractiveShell.term_title_format={profile} -i -c "{config.console_cmd}"'
os.system(cl)
