# azcamserver config file for 90prime

import os
import datetime

import azcam
import azcam.azcamserver
from azcam.ds9display import Ds9Display
from azcam.azcamserver.systemheader import SystemHeader
from azcam.azcamserver.controllers.controller_arc import ControllerArc
from azcam.azcamserver.tempcons.tempcon_cryoconm24 import TempConCryoCon
from azcam.azcamserver.exposures.exposure_arc import ExposureArc
from azcam.azcamserver.cmdserver import CommandServer
import system_config as config

azcam.db.verbosity = config.verbosity

# ****************************************************************
# files and folders
# ****************************************************************
systemname = config.systemname
azcam.db.systemname = systemname

systemfolder = azcam.utils.fix_path(os.path.dirname(__file__))
azcam.db.systemfolder = systemfolder
azcam.utils.add_searchfolder(systemfolder, 0)

datafolder = config.datafolder_root
azcam.db.datafolder = datafolder

# ****************************************************************
# configuration menu
# ****************************************************************
print("90prime Startup Menu\n")
options = {
    "90prime (standard mode)": "90prime normal",
    "90primeOne": "90primeone",
    "90prime with overscan rows": "90prime overscan",
    "90prime FAST mode (with overscan rows)": "90prime fast",
    "CSS mode": "90prime css azcamserver",
}
options = azcam.utils.show_menu(options)

CSS = 0
if "90primeone" in options:
    parfile = "/data/90prime/azcam/parameters_90prime_one.ini"
    template = "/data/90prime/templates/FitsTemplate_90PrimeOne_master.txt"
    timingfile = "/azcam/systems/bok/90prime/dspcode/dsptiming_90primeone/90PrimeOne_config0.lod"
elif "normal" in options:
    parfile = "/data/90prime/azcam/parameters_90prime_normal.ini"
    template = "/data/90prime/templates/FitsTemplate_90Prime_master.txt"
    timingfile = "/azcam/systems/bok/90prime/dspcode/dsptiming_90prime/90Prime_config0.lod"
elif "fast" in options:
    parfile = "/data/90prime/azcam/parameters_90prime_fast.ini"
    template = "/data/90prime/templates/FitsTemplate_90Prime_master.txt"
    timingfile = "/azcam/systems/bok/90prime/dspcode/dsptiming_fast/90Prime_config1.lod"
elif "overscan" in options:
    parfile = "/data/90prime/azcam/parameters_90prime_overscan.ini"
    template = "/data/90prime/templates/FitsTemplate_90Prime_master.txt"
    timingfile = "/azcam/systems/bok/90prime/dspcode/dsptiming_90prime/90Prime_config0.lod"
elif "css" in options:
    print("90Prime for CSS")
    CSS = 1
    parfile = "/data/90prime/azcam/parameters_90prime_css.ini"
    template = "/data/90prime/templates/FitsTemplate_90Prime_css.txt"
    timingfile = "/azcam/systems/bok/90prime/dspcode/dsptiming_90prime/90Prime_config0.lod"
else:
    raise azcam.AzCamError("bad server configuration")
azcam.db.parfile = parfile

# ****************************************************************
# start logging
# ****************************************************************
logfile = os.path.join(datafolder, "azcam/logs", "azcamserver.log")
logfile = azcam.utils.fix_path(logfile)
azcam.utils.start_logging(logfile)
azcam.utils.log(f"Configuring azcamserver for {options}")

# ****************************************************************
# common assets
# ****************************************************************
azcam.utils.add_searchfolder("../common")
azcam.utils.add_searchfolder(config.commonfolder)

# ****************************************************************
# controller
# ****************************************************************
controller = ControllerArc()
azcam.utils.set_object("controller", controller)
controller.timing_board = "arc22"
controller.clock_boards = ["arc32"]
controller.video_boards = ["arc47", "arc47", "arc47", "arc47"]
controller.set_boards()
controller.video_gain = 1
controller.video_speed = 1
controller.camserver.set_server("localhost", 2405)
controller.pci_file = f"{azcam.db.systemfolder}/dspcode/dsppci/pci3.lod"
controller.timing_file = timingfile

# ****************************************************************
# temperature controller
# ****************************************************************
tempcon = TempConCryoCon()
azcam.utils.set_object("tempcon", tempcon)
tempcon.control_temperature = -135.0
#tempcon.host = "10.0.0.45"
tempcon.host='10.30.3.32'
tempcon.init_commands = [
    "input A:units C",
    "input B:units C",
    "input C:units C",
    "input A:isenix 2",
    "input B:isenix 2",
    "loop 1:type pid",
    "loop 1:range mid",
    "loop 1:maxpwr 100",
]

# ****************************************************************
# dewar
# ****************************************************************
controller.header.set_keyword("DEWAR", "90prime", "Dewar name")

# ****************************************************************
# exposure
# ****************************************************************
exposure = ExposureArc()
azcam.utils.set_object("exposure", exposure)
exposure.filetype = azcam.db.filetypes["MEF"]
exposure.image.filetype = azcam.db.filetypes["MEF"]
exposure.aztime.sntp.servers = ["140.252.86.114"]
exposure.update_headers_in_background = 1
exposure.display_image = 0
exposure.remote_imageserver_filename = "azcamimage.fits"
exposure.image.server_type = "dataserver"
remote_imageserver_host = "10.30.1.2"
remote_imageserver_port = 6543
exposure.set_remote_server(remote_imageserver_host, remote_imageserver_port)
#exposure.set_remote_server()

# ****************************************************************
# focus script - server-side
# ****************************************************************
from focus import Focus

focus = Focus()
focus.focus_component = "instrument"
focus.focus_type = "step"
azcam.utils.set_object('focus', focus)

if CSS:
    exposure.image.server_type = "azcam"
    exposure.set_remote_server("10.30.6.2", 6543)
    exposure.filename.folder = "/home/css"

# ****************************************************************
# instrument
# ****************************************************************
from instrument_pf import PrimeFocusInstrument
instrument = PrimeFocusInstrument()
azcam.utils.set_object("instrument", instrument)

# ****************************************************************
# telescope
# ****************************************************************
from telescope_bok import BokTCS
telescope = BokTCS()
azcam.utils.set_object("telescope", telescope)


# ****************************************************************
# system header template
# ****************************************************************
system = SystemHeader("90prime", template)
azcam.utils.set_header("system", system)

# ****************************************************************
# detector
# ****************************************************************
if "90primeone" in options:
    from detector_bok90prime import detector_bok90prime_one

    exposure.set_detpars(detector_bok90prime_one)
else:
    from detector_bok90prime import detector_bok90prime

    if "overscan" in options:
        detector_bok90prime["format"] = [4032 * 2, 6, 0, 20, 4096 * 2, 0, 0, 20, 0]
    exposure.set_detpars(detector_bok90prime)

# ****************************************************************
# display
# ****************************************************************
display = Ds9Display()
azcam.db.objects["display"] = display
setattr(azcam, "display", display)
display.initialize()
del azcam.ds9display

# ****************************************************************
# ipython config
# ****************************************************************
azcam.utils.config_ipython()

# ****************************************************************
# command server
# ****************************************************************
cmdserver = CommandServer()
cmdserver.port = 2402
azcam.db.cmdserver = cmdserver
azcam.utils.log(f"Starting command server listening on port {cmdserver.port}")
cmdserver.start()

if CSS:
    from css import CSS

    css = CSS()
    azcam.utils.set_object("css", css)

# ****************************************************************
# read par file
# ****************************************************************
if config.readparfile:
    azcam.api.parfile_read(parfile)

# ****************************************************************
# apps
# ****************************************************************
if config.start_azcamtool:
    import start_azcamtool
if config.start_webapp:
    azcam.utils.add_searchfolder(f"{systemfolder}/webapp")
    import webapp

# ****************************************************************
# finish
# ****************************************************************
azcam.utils.log("Configuration complete")


def test():
    """
    For debug and testing.
    """

    azcam.utils.log("Running debug mode commands")

    return


# test mode
if config.test_mode:
    test()

# for debugger only
if 0:
    test()
