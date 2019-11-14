"""
Contains the PrimeFocus instrument class for the UAO 90" 90prime instrument.
"""

# SHOW FILTISIN
# returns 0 (0.0000?) none, 1 in beam, 3 jammed

import socket
import sys
import time

import azcam
from azcam.azcamserver.instruments.instrument import Instrument
from bokdata import BokData


class PrimeFocusInstrument(Instrument):
    """
    The interface to the 90prime instrument.
    The InstrumentServer is the galil, later Jeff Fookson's Ruby Galil server.
    """

    def __init__(self):
        """
        Create 90PrimeInstrument instrument object
        """

        # create Header object and set defaults
        super().__init__()

        self.Name = "90prime"
        self.Port = 9874  # port for galil server on bok
        self.host = "10.30.1.2"  # bok
        self.ActiveComps = [""]
        self.InstalledFilters = {}
        self.enabled = 1
        self.ActiveFilter = "unknown"  # current filter

        self.Locked = False  # communications lock for galilserver

        self.use_bokpop = 1

        self.focus_device = "instrument"

        # instrument server interface
        self.Iserver = InstrumentServerInterface(self.host, self.Port, self.Name)
        self.Iserver.Timeout = 20

        # bokpop
        self.bokpop = BokData("10.30.1.3", 5554, 1.0)  # 1 sec timeout

        # add keywords
        reply = self.define_keywords()
        if azcam.utils.check_reply(reply):
            return reply

    def initialize(self):

        if not self.enabled:
            azcam.AzCamWarning("Instrument is not enabled")
            return

        # execute a command to make sure communication is OK
        self.initialized = 1
        reply = self.get_focus()
        if reply[0] != "OK":
            self.initialized = 0
            return reply
        else:
            self.initialized = 1

        return

    def test(self, number_cycles=1):
        """       
        Test 90prime instrument.
        number_cycles is the number of cycles to repeat during testing.
        """

        for loop in range(number_cycles):

            if number_cycles > 1:
                azcam.utils.log(("   *** Test cycle: %d" % loop))

            # test Galil interface
            azcam.utils.log("Testing 90prime Galil instrument interface...")

            reply = self.initialize()
            if reply[0] != "OK":
                azcam.utils.log("*** Could not initialize Galil")
            else:
                azcam.utils.log((repr(reply)))

            # read current value of keywords
            for key in self.header.get_all_keywords():
                azcam.utils.log(("Keyword: %s has value: %s" % (key, self.read_keyword(key)[1])))

            reply = self.get_filter()
            if reply[0] == "OK":
                azcam.utils.log(("Filter is %s" % reply[1]))

            reply = self.get_focus()
            if reply[0] == "OK":
                azcam.utils.log(("Focus is %s" % reply[1]))

            azcam.utils.log("Finished testing 90prime Galil interface. OK")
            azcam.utils.log()
            azcam.utils.prompt("Press Enter to continue...")
            azcam.utils.log()

            """
            # test weather station server
            azcam.utils.log('Testing weather station...')
            reply=self.GetWeatherInfo()
            if reply[0]!='OK':
                azcam.utils.log('*** Could not get infrastructure weather data')
            else:
                azcam.utils.log(repr(reply))
            azcam.utils.log('Finished testing weather station. OK')
            print
            azcam.utils.prompt('Press Enter to continue...')
            print

            # test temperature server
            azcam.utils.log('Testing dome temperature server...')
            reply=self.GetTemperatureInfo()
            if reply[0]!='OK':
                azcam.utils.log('*** Could not get infrastructure temperature data')
            else:
                azcam.utils.log(repr(reply))
            azcam.utils.log('Finshed testing dome temperature server. OK')
            print
            azcam.utils.prompt('Press Enter to continue...')
            print

            # test PULIZZI power server
            azcam.utils.log('Testing PULIZZI power server...')
            reply=self.GetPowerInfo()
            if reply[0]!='OK':
                azcam.utils.log('*** Could not get infrastructure power data')
            else:
                azcam.utils.log(repr(reply))
            azcam.utils.log('Finished testing PULIZZI power server.')
	    print
	    azcam.utils.prompt('Press Enter to continue...')
	    print
	    """

        return

    def command(self, Command):
        """
        Command interface for instrument.
        """

        while self.Locked:
            time.sleep(0.01)

        self.Locked = True

        reply = self.Iserver.open()
        if reply[0] == "OK":
            reply = self.Iserver.recv(-2)  # read 'connected..' string and ignore
            reply = reply[1]

            reply = self.Iserver.send(Command, "")  # no terminator

            reply = self.Iserver.recv(-2)
            reply = reply[1]

            self.Iserver.send("CLIENTDONE", "")
            reply1 = self.Iserver.recv(-2)  # read 'shutting down...' string and ignore

            self.Iserver.close()
        else:
            self.Locked = False
            return reply

        # check for error, valid replies starts with 'OK: ' and errors with '?: '
        if reply.startswith("OK: "):
            reply = reply[4:]
            self.Locked = False
            self.Iserver.close()  # new
            return ["OK", reply]
        else:
            self.Locked = False
            self.Iserver.close()  # new
            return ["ERROR", reply]

    # *** FILTERS ***

    def get_all_filters(self, filter_id=0):
        """
        Return a list of all filters in wheel.
        """

        reply = self.command("SHOWFILTERS")  # returns space deliminated names
        if reply[0] != "OK":
            return reply

        self.InstalledFilters = reply[1].split(" ")  # make a list

        return self.InstalledFilters

    def check_filter(self, filter_id=0):
        """
        Returns TRUE if a filter is laoded in the beam.
        """

        # SHOW FILTISIN
        # returns 0 (0.0000?) none, 1 in beam, 3 jammed

        reply = self.command("SHOW FILTISIN")
        if reply[0] != "OK":
            return reply

        if reply[1].startswith(" 1"):
            return True
        else:
            return False

    def read_filter(self, filter_id=0):
        """
        Reads the filter name in the beam.
        The returned filter name string is in the form "FilterName in beam", e.g. "U in beam"
        """

        if not self.check_filter(filter_id):
            return ["OK", "none"]

        for i in range(5):
            reply = self.command("SHOWLOADEDFILTER")
            if reply[0] == "OK":
                break
            else:
                time.sleep(0.2)

        CurrentFilterName = reply[1]

        self.ActiveFilter = CurrentFilterName

        return ["OK", CurrentFilterName]

    def get_filter(self, filter_id=0):
        """
        Return the current filter position.
        filter_id is 0 for 90prime.
        """

        return self.read_filter()

    def set_filter(self, Filter, filter_id=0):
        """
        Set the current/loaded filter, typically the filter in the beam.
        Filter: a string containing the filter name to set.
        filter_id: the filter mechanism ID.
        """

        reply = self.get_filter(filter_id)
        currentfilter = reply

        if currentfilter == Filter:
            azcam.utils.log("Already at filter", currentfilter)
            return

        azcam.utils.log("Unloading filter", currentfilter)
        cmd = "SUNLOADFILT"
        reply = self.command(cmd)

        time.sleep(10)

        azcam.utils.log("Loading filter", Filter)
        cmd = "SLOADFILT %s" % Filter
        reply = self.command(cmd)

        time.sleep(10)
        reply = self.get_filter(filter_id)
        azcam.utils.log("Current filter is", reply)

        return

    # *** FOCUS ***

    def get_mean_focus(self):
        focus = self.get_focus_all()
        focus = focus[1:-1].split("*")
        a, b, c = map(float, focus)
        mean = int(1000 * (a + b + c) / 3.0)
        return mean

    def step_focus(self, FocusPosition, focus_id=0):
        """
        Moves all 3 actuators for instrument focus by the specified amount, in relative stepper motor steps.
        One focus actuator step is 2.645 microns, which corresponds to -0.0005 LVDT units. So the conversion is (-1322.5 um/LVDT unit).
        """

        cmd = "ALLFOCUS %d" % int(FocusPosition)

        reply = self.command(cmd)
        if reply[0] != "OK":
            return reply

        mean0 = self.get_mean_focus()
        for i in range(5):
            mean = self.get_mean_focus()
            delta = abs(mean - mean0)
            if delta < 2:
                break
            else:
                pass
                # azcam.utils.log(f'mean focus change: {delta}')

        return

    def set_focus(self, FocusPosition, focus_id=0):
        """
        Moves an individual actuators for instrument focus by the specified amount, in relative stepper motor steps.
        One focus actuator step is 2.645 microns, which corresponds to -0.0005 LVDT units. So the conversion is (-1322.5 um/LVDT unit).
        """

        cmd = "ALLFOCUS %d" % (FocusPosition)  # wrong, change this

        reply = self.command(cmd)
        if reply[0] != "OK":
            return reply

        return

    def set_focus_all(self, FocusPositionA, FocusPositionB, FocusPositionC):
        """
        Moves each of the 3 actuators for instrument focus by the amount specified, in relative stpper motor steps.
        One focus actuator step is 2.645 microns, which corresponds to -0.0005 LVDT units. So the conversion is (-1322.5 um/LVDT unit).
        """

        cmd = "FOCUS %d %d %d" % (FocusPositionA, FocusPositionB, FocusPositionC)

        reply = self.command(cmd)
        if reply[0] != "OK":
            return reply

        return

    def set_actuators(self, LvdtA, LvdtB, LvdtC):
        """
        Moves each of the 3 instrument focus actuators to the absolute value of the specified LVDT.
        One focus actuator step is 2.645 microns, which corresponds to -0.0005 LVDT units. So the conversion is (-1322.5 um/LVDT unit).
        """

        loops = 10  # number of iterations performed
        tolerance = 0.005  # allowed LVDT error
        scale = [-0.0005, -0.0005, -0.0005]  # LVDT to steps scale for A,B,C

        for i in range(loops):

            # get current values
            reply = self.get_focus_all()
            if reply[0] != "OK":
                return reply
            time.sleep(0.1)

            focus = reply[1].split("*")[1:]  # list of values
            for i, f in enumerate(focus):  # make floats
                focus[i] = float(f)

            # convert to stepper motor steps
            steps = [0, 0, 0]
            a = LvdtA - focus[0]
            if abs(a) > tolerance:
                steps[0] = int(a / scale[0])
            else:
                steps[0] = 0

            b = LvdtB - focus[1]
            if abs(b) > tolerance:
                steps[1] = int(b / scale[1])
            else:
                steps[1] = 0

            c = LvdtC - focus[2]
            if abs(c) > tolerance:
                steps[2] = int(c / scale[2])
            else:
                steps[2] = 0

            cmd = "FOCUS %d %d %d" % (steps[0], steps[1], steps[2])

            # stop when no correction required
            if max(steps) == 0 and min(steps) == 0:
                break

            reply = self.command(cmd)
            if reply[0] != "OK":
                return reply

            # get new values
            reply = self.get_focus_all()
            azcam.utils.log(("LVDT read: %s" % reply))
            if reply[0] != "OK":
                return reply

            focus = reply[1].split("*")[1:]  # list of values
            for i, f in enumerate(focus):  # make floats
                focus[i] = float(f)
            error = [LvdtA - focus[0], LvdtB - focus[1], LvdtC - focus[2]]

        return

    def get_focus(self, focus_id=0):
        """
        Return a single current LVDT focus position as a float.
        """

        for i in range(5):
            reply = self.get_focus_all()
            if reply[0] == "OK":
                break
            else:
                time.sleep(0.2)
        reply = reply[1].strip()
        FocusPosition = reply.split("*")[1:]

        return ["OK", FocusPosition[focus_id]]

    def get_focus_all(self):
        """
        Return the 3 current LVDT instrument focus position as a string.
        Return string is formated as "*LVDT_A*LVDT_B*LVDT_C*, e.g. "*01.123*01.321*01.765*"
        """

        cmd = "SHOWALLLVDTVALS"  # current LVDT values

        for i in range(5):
            reply = self.command(cmd)
            if reply[0] == "OK":
                break
            else:
                time.sleep(0.2)

        focuspositionstring = reply[1].replace(" ", "*")

        return [focuspositionstring]

    # *** KEYWORDS ***

    def define_keywords(self):
        """
        Defines instrument keywords, if they are not already defined.
        """

        if len(self.header.keywords) != 0:
            return

        # add keywords to header
        keywords = ["FILTER", "FOCUSVAL"]
        comments = {"FILTER": "Filter name", "FOCUSVAL": "Focus"}
        types = {"FILTER": str, "FOCUSVAL": str}

        for key in keywords:
            self.header.set_keyword(key, "", comments[key], types[key])

        return

    def read_keyword(self, Keyword):
        """
        Read an instrument keyword value.
        This command will read hardware to obtain the keyword value.
        """

        if Keyword == "FOCUSVAL":
            reply = self.get_focus_all()
        elif Keyword == "FILTER":
            reply = self.get_filter(1)
        elif Keyword == "FOCUS0":
            reply = self.get_focus(0)
        elif Keyword == "FOCUS1":
            reply = self.get_focus(1)
        elif Keyword == "FOCUS2":
            reply = self.get_focus(2)
        else:
            try:
                reply = self.header.Values[Keyword]
            except:
                raise azcam.AzCamError("keyword not defined")

        # store value in Header
        self.header.set_keyword(Keyword, reply)

        # convert type
        if self.header.typestrings[Keyword] == "int":
            reply = int(reply)
        elif self.header.typestrings[Keyword] == "float":
            reply = float(reply)

        t = self.header.get_type_string(self.header.typestrings[Keyword])

        return ["OK", reply, self.header.comments[Keyword], t]

    def read_header(self):
        """
        Reads, records, and returns the current header.
        This method looks up all keywords and queries hardware for the current value of each keyword.
        Returns [Header[]]: Each element Header[i] contains the sublist (keyword, value, comment, and type).
        Example: Header[2][1] is the value of keyword 2 and Header[2][3] is its type.
        Type is one of 'str', 'int', 'float', or 'complex'.
        """

        header = []
        reply = self.header.get_all_keywords()

        for key in reply:
            reply = self.read_keyword(key)
            list1 = [key, reply[0], reply[1], reply[2]]
            header.append(list1)

        # get infrastructure header info
        reply = self.get_info()

        return header

    # *** GUIDER ***

    def guider_init(self):
        """
        Initialize guider camera.
        """

        cmd = "INITGCAM"
        reply = self.command(cmd)
        time.sleep(10)

        return reply

    def set_guider_focus(self, Steps):
        """
        Move guider focus the specified number of steps.
        """

        cmd = "GFOCUS " + str(Steps)
        reply = self.command(cmd)
        time.sleep(10)

        return reply

    def set_guider_filter(self, FilterNumber):
        """
        Move guider filter wheel to position number.
        """

        cmd = "SETGFILTER " + str(FilterNumber)
        reply = self.command(cmd)
        time.sleep(10)

        return reply

    def get_guider_filter(self, filter_id=0):
        """
        Returns the current guider filter number.
        """

        cmd = "GETGFILTER"
        reply = self.command(cmd)

        if reply[0] != "OK":
            return reply

        CurrentFilterName = reply[1]

        return ["OK", CurrentFilterName]

    # *** INFRASTRUCTURE ***

    def get_info(self):
        """
        Get infrastructure info from servers running on bokpct.
        These are temperatures, humidity, dewpoints, and weather.
        """

        if self.use_bokpop:
            self.get_bokpop_info()

        return

    def get_bokpop_info(self):
        """
        Get info from bokpop server.
        """

        bokpopdata = self.bokpop.makeHeader()

        for item in bokpopdata:
            keyword = item[0]
            value = item[1]
            comment = item[2]
            self.header.set_keyword(keyword, value, comment, str)

        return

    # *** raw command to Galil, usually for testing only ***

    def send_raw(self, Command):
        """
        Send a raw galil command to the server.
        """

        cmd = "SENDRAW " + str(Command)
        reply = self.command(cmd)

        return reply


# *** instrument server interface ***


class InstrumentServerInterface(object):
    """
    Communicates with J. Fookson's 90prime insturment server using a socket.
    Responses from the server are in the form "OK:", "OK: message",  or "?: error message".
    Compound command may respond as "OK: OK:"
    """

    def __init__(self, Host, Port, Name):

        self.host = Host
        self.Port = Port
        self.Name = Name
        self.Timeout = 60.0  # socket timeout in seconds

    def open(self):
        """
        Open a socket connection to an instrument.
        Creates the socket and makes a connection.
        @return AzCamStatus
        """

        self.Socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.Socket.settimeout(float(self.Timeout))
        try:
            reply = self.Socket.connect((self.host, self.Port))
            return
        except:
            self.close()
            return ["ERROR", '"instrument %s not opened"' % self.Name]

    def close(self):
        """
        Close an open socket connection to an instrument.
        """

        try:
            self.Socket.close()
        except Exception as messasge:
            azcam.utils.log(message)
            pass

        return

    def command(self, Command, Terminator="\r\n"):
        """
        Communicte with the remote instrument server.
        Opens and closes the socket each time.
        Returns the exact reply from the server.
        """

        reply = self.open()
        if reply[0] == "OK":
            reply = self.send(str.encode(Command, Terminator))
            if reply[0] == "OK":
                reply = self.recv(-1, "\n").decode()

            self.close()

        return reply

    def command1(self, Command, Terminator="\r\n"):
        """
        Communicte with the remote instrument server.
        Opens and closes the socket each time.
        Returns the exact reply from the server.
        """

        reply = self.open()
        if reply[0] == "OK":
            reply = self.send(str.encode(Command, Terminator))
            if reply[0] == "OK":
                reply = self.recv(256, "\n").decode()

            self.close()

        return reply

    def send(self, Command, Terminator="\r\n"):
        """
        Send a command string to a socket instrument.
        Appends the terminator.
        """

        try:
            self.Socket.send(str.encode(Command + Terminator))  # send command with terminator
            return
        except:
            return ["ERROR", '"could not send command to instrument"']

    def recv(self, Length=-1, Terminator="\n"):
        """
        Receives a reply from a socket instrument.
        Terminates the socket read when Length bytes are received or when the Terminator is received.
        @param Length is the number of bytes to receive.  -1 means receive through Terminator character.
        @param Terminator is the terminator character.
        """

        if Length == -2:
            try:
                msg = self.Socket.recv(1024).decode()
                return ["OK", msg]
            except:
                return ["OK", ""]

        # receive Length bytes
        if Length != -1:
            msg = self.Socket.recv(Length).decode()
            return ["OK", msg]

        # receive with terminator
        msg = chunk = ""
        loop = 0
        while chunk != Terminator:  # CR LF is usually '\n' when translated
            try:
                chunk = self.Socket.recv(1).decode()
            except Exception as errorcode:
                return ["ERROR", '"error in instrument server communication"']
            if chunk != "":
                msg = msg + chunk
                loop = 0
            else:
                loop += 1
                if loop > 10:
                    return ["ERROR", '"error in instrument server communication loop"']

        Reply = msg[:-2]  # remove CR/LF
        if Reply == None:
            Reply = ""

        return ["OK", Reply]


# instance
instrument = PrimeFocusInstrument()
azcam.utils.set_object("instrument", instrument)
