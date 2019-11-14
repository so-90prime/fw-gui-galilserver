# azcamconsole config file for 90prime

import os

import azcam
import azcam.azcamconsole
import system_config as config

azcam.db.verbosity = config.verbosity

# ****************************************************************
# files and folders
# ****************************************************************
systemname = config.systemname
azcam.db.systemname = systemname

systemfolder = f"{os.path.dirname(__file__)}"
azcam.db.systemfolder = systemfolder
azcam.utils.add_searchfolder(systemfolder, 0)  # top level only

datafolder = config.datafolder_root
azcam.db.datafolder = datafolder

parfile = f"{datafolder}/azcam/parameters_90prime_azcamconsole.ini"
azcam.db.parfile = parfile

# ****************************************************************
# start logging
# ****************************************************************
logfile = os.path.join(datafolder, "azcam/logs", "azcamconsole.log")
azcam.utils.start_logging(logfile)
azcam.utils.log(f"Configuring azcamconsole for 90prime")

# ****************************************************************
# common assets
# ****************************************************************
azcam.utils.add_searchfolder("../common")
azcam.utils.add_searchfolder(config.commonfolder)

# ****************************************************************
# config ipython if in use
# ****************************************************************
azcam.utils.config_ipython()

# ****************************************************************
# display
# ****************************************************************
from azcam.ds9display import Ds9Display

display = Ds9Display()
azcam.db.objects["display"] = display
setattr(azcam, "display", display)
display.initialize()
del azcam.ds9display

# ****************************************************************
# focus script
# ****************************************************************
from focus import Focus

focus = Focus()
azcam.utils.set_object('focus', focus)
focus.focus_component = "instrument"
focus.focus_type = "step"

# ****************************************************************
# observe script
# ****************************************************************
from observe.observe import Observe

if azcam.db.get("qtapp") is None:
    import PyQt4.QtGui as QtGui

    qtapp = QtGui.QApplication([])
    azcam.db.qtapp = qtapp
observe = Observe()
azcam.utils.set_object('observe', observe)
observe.move_telescope_during_readout = 1

# ****************************************************************
# try to connect to azcamserver
# ****************************************************************
connected = azcam.api.connect()
if connected:
    azcam.utils.log("Connected to azcamserver")
else:
    azcam.utils.log("Not connected to azcamserver")

# ****************************************************************
# read par file
# ****************************************************************
if config.readparfile:
    azcam.api.parfile_read(parfile)
    
# now can init observe as parfile required
observe.initialize()

# ****************************************************************
# finish
# ****************************************************************

# ****************************************************************
# debug and testing
# ****************************************************************
def test(self):

    azcam.utils.log("Running debug mode commands")

    return


# test mode
if config.test_mode:
    test()

# for debugger only
if 0:
    test()
