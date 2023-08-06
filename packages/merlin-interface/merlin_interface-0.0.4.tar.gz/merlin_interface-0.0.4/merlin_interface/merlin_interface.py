import socket
import time


class MerlinInterface(object):
    def __init__(
            self, tcp_ip="127.0.0.1", tcp_port=6341, test_mode=False):
        """
        Class for interfacing with a Medipix3 detector via the Merlin software,
        via the TCP/IP API.

        Parameter
        ---------
        tcp_ip : string, default "127.0.0.1"
            IP address for the Merlin software. For connecting on the same
            computer, use "127.0.0.1".
        tcp_port : int, default 6341
        test_mode : bool, default False
        """
        self._tcp_ip = tcp_ip
        self._tcp_port = tcp_port
        self._receive_string_buffer = 1000
        self._message_preamble = b"MPX"
        self.test_mode = test_mode

    def __repr__(self):
        if self.test_mode:
            test_mode_string = " (test mode)"
        else:
            test_mode_string = ""
        return '<%s, %s:%s%s>' % (
            self.__class__.__name__,
            self._tcp_ip, self._tcp_port,
            test_mode_string,
            )

    def _make_message_string(
            self,
            command_name,
            command_type,
            command_argument_list=None):
        """
        Parameters
        ----------
        command_name : bytes
        command_type : bytes
        command_argument_list : list
        """
        if command_argument_list is None:
            command_argument_list = []
        command_string_list = [
                command_type,
                command_name]
        for command_argument in command_argument_list:
            command_string_list.append(str(command_argument).encode())
        command_len_string = str(
                len(b",".join(
                    command_string_list))+1).zfill(10)

        command_string_list.insert(0, command_len_string.encode())
        command_string_list.insert(0, self._message_preamble)
        command_string = b",".join(command_string_list)
        return(command_string)

    def _send_packet(self, command_string):
        if self.test_mode:
            return_data = command_string + b",0"
        else:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((self._tcp_ip, self._tcp_port))
            s.send(command_string)
            return_data = s.recv(self._receive_string_buffer)
            time.sleep(0.01)
            s.close()
        self._check_packet_response(
                command_string, return_data)
        if self.test_mode:
            print(return_data)
        return(return_data)

    def _check_packet_response(self, command_string, return_data):
        # Todo: use more specific exceptions
        if (len(command_string) + 1) > len(return_data):
            raise Exception(
                "Return data too short: " +
                str(return_data))
        elif int(return_data[-1]) == 3:
            raise ValueError(
                "Medipix: Input parameter is out of range" +
                str(return_data))
        elif int(return_data[-1]) == 2:
            raise Exception(
                "Medipix: Command not recognised, probably caused "
                "by bug in this Python wrapper: " +
                str(return_data))
        elif int(return_data[-1]) == 1:
            raise Exception(
                "Medipix: system is busy: ",
                str(return_data))

    # DRIVER VARIABLES

    @property
    def softwareversion(self):
        command_name = b"SOFTWAREVERSION"
        command_type = b"GET"
        command_string = self._make_message_string(
                command_name, command_type)
        return_data = self._send_packet(command_string)
        return(return_data)

    # EXECUTE COMMANDS

    def startacquisition(self):
        command_name = b"STARTACQUISITION"
        command_type = b"CMD"
        command_string = self._make_message_string(
                command_name,
                command_type)
        self._send_packet(command_string)

    def stopacquisition(self):
        command_name = b"STOPACQUISITION"
        command_type = b"CMD"
        command_string = self._make_message_string(
                command_name,
                command_type)
        self._send_packet(command_string)

    def softtrigger(self):
        command_name = b"SOFTTRIGGER"
        command_type = b"CMD"
        command_string = self._make_message_string(
                command_name,
                command_type)
        self._send_packet(command_string)

    def reset(self):
        command_name = b"RESET"
        command_type = b"CMD"
        command_string = self._make_message_string(
                command_name,
                command_type)
        self._send_packet(command_string)

    # MEDIPIX3 modes

    @property
    def colourmode(self):
        command_name = b"COLOURMODE"
        command_type = b"GET"
        command_string = self._make_message_string(
                command_name, command_type)
        return_data = self._send_packet(command_string)
        return(return_data)

    @colourmode.setter
    def colourmode(self, value):
        command_name = b"COLOURMODE"
        command_type = b"SET"
        command_argument_list = [str(value)]
        command_string = self._make_message_string(
                command_name,
                command_type,
                command_argument_list)
        self._send_packet(command_string)

    @property
    def chargesumming(self):
        command_name = b"CHARGESUMMING"
        command_type = b"GET"
        command_string = self._make_message_string(
                command_name, command_type)
        return_data = self._send_packet(command_string)
        return(return_data)

    @chargesumming.setter
    def chargesumming(self, value):
        command_name = b"CHARGESUMMING"
        command_type = b"SET"
        command_argument_list = [str(value)]
        command_string = self._make_message_string(
                command_name,
                command_type,
                command_argument_list)
        self._send_packet(command_string)

    @property
    def gain(self):
        command_name = b"GAIN"
        command_type = b"GET"
        command_string = self._make_message_string(
                command_name, command_type)
        return_data = self._send_packet(command_string)
        return(return_data)

    @gain.setter
    def gain(self, value):
        command_name = b"GAIN"
        command_type = b"SET"
        command_argument_list = [str(value)]
        command_string = self._make_message_string(
                command_name,
                command_type,
                command_argument_list)
        self._send_packet(command_string)

    @property
    def continousrw(self):
        command_name = b"CONTINOUSRW"
        command_type = b"GET"
        command_string = self._make_message_string(
                command_name, command_type)
        return_data = self._send_packet(command_string)
        return(return_data)

    @continousrw.setter
    def continousrw(self, value):
        command_name = b"CONTINOUSRW"
        command_type = b"SET"
        command_argument_list = [str(value)]
        command_string = self._make_message_string(
                command_name,
                command_type,
                command_argument_list)
        self._send_packet(command_string)

    @property
    def enablecounter1(self):
        command_name = b"ENABLECOUNTER1"
        command_type = b"GET"
        command_string = self._make_message_string(
                command_name, command_type)
        return_data = self._send_packet(command_string)
        return(return_data)

    @enablecounter1.setter
    def enablecounter1(self, value):
        command_name = b"ENABLECOUNTER1"
        command_type = b"SET"
        command_argument_list = [str(value)]
        command_string = self._make_message_string(
                command_name,
                command_type,
                command_argument_list)
        self._send_packet(command_string)

    @property
    def threshold0(self):
        command_name = b"THRESHOLD0"
        command_type = b"GET"
        command_string = self._make_message_string(
                command_name, command_type)
        return_data = self._send_packet(command_string)
        return(return_data)

    @threshold0.setter
    def threshold0(self, value):
        command_name = b"THRESHOLD0"
        command_type = b"SET"
        command_argument_list = [str(value)]
        command_string = self._make_message_string(
                command_name,
                command_type,
                command_argument_list)
        self._send_packet(command_string)

    @property
    def threshold1(self):
        command_name = b"THRESHOLD1"
        command_type = b"GET"
        command_string = self._make_message_string(
                command_name, command_type)
        return_data = self._send_packet(command_string)
        return(return_data)

    @threshold1.setter
    def threshold1(self, value):
        command_name = b"THRESHOLD1"
        command_type = b"SET"
        command_argument_list = [str(value)]
        command_string = self._make_message_string(
                command_name,
                command_type,
                command_argument_list)
        self._send_packet(command_string)

    @property
    def threshold2(self):
        command_name = b"THRESHOLD2"
        command_type = b"GET"
        command_string = self._make_message_string(
                command_name, command_type)
        return_data = self._send_packet(command_string)
        return(return_data)

    @threshold2.setter
    def threshold2(self, value):
        command_name = b"THRESHOLD2"
        command_type = b"SET"
        command_argument_list = [str(value)]
        command_string = self._make_message_string(
                command_name,
                command_type,
                command_argument_list)
        self._send_packet(command_string)

    @property
    def threshold3(self):
        command_name = b"THRESHOLD3"
        command_type = b"GET"
        command_string = self._make_message_string(
                command_name, command_type)
        return_data = self._send_packet(command_string)
        return(return_data)

    @threshold3.setter
    def threshold3(self, value):
        command_name = b"THRESHOLD3"
        command_type = b"SET"
        command_argument_list = [str(value)]
        command_string = self._make_message_string(
                command_name,
                command_type,
                command_argument_list)
        self._send_packet(command_string)

    @property
    def threshold4(self):
        command_name = b"THRESHOLD4"
        command_type = b"GET"
        command_string = self._make_message_string(
                command_name, command_type)
        return_data = self._send_packet(command_string)
        return(return_data)

    @threshold4.setter
    def threshold4(self, value):
        command_name = b"THRESHOLD4"
        command_type = b"SET"
        command_argument_list = [str(value)]
        command_string = self._make_message_string(
                command_name,
                command_type,
                command_argument_list)
        self._send_packet(command_string)

    @property
    def threshold5(self):
        command_name = b"THRESHOLD5"
        command_type = b"GET"
        command_string = self._make_message_string(
                command_name, command_type)
        return_data = self._send_packet(command_string)
        return(return_data)

    @threshold5.setter
    def threshold5(self, value):
        command_name = b"THRESHOLD5"
        command_type = b"SET"
        command_argument_list = [str(value)]
        command_string = self._make_message_string(
                command_name,
                command_type,
                command_argument_list)
        self._send_packet(command_string)

    @property
    def threshold6(self):
        command_name = b"THRESHOLD6"
        command_type = b"GET"
        command_string = self._make_message_string(
                command_name, command_type)
        self._send_packet(command_string)

    @threshold6.setter
    def threshold6(self, value):
        command_name = b"THRESHOLD6"
        command_type = b"SET"
        command_argument_list = [str(value)]
        command_string = self._make_message_string(
                command_name,
                command_type,
                command_argument_list)
        self._send_packet(command_string)

    @property
    def threshold7(self):
        command_name = b"THRESHOLD7"
        command_type = b"GET"
        command_string = self._make_message_string(
                command_name, command_type)
        return_data = self._send_packet(command_string)
        return(return_data)

    @threshold7.setter
    def threshold7(self, value):
        command_name = b"THRESHOLD7"
        command_type = b"SET"
        command_argument_list = [str(value)]
        command_string = self._make_message_string(
                command_name,
                command_type,
                command_argument_list)
        self._send_packet(command_string)

    @property
    def counterdepth(self):
        command_name = b"COUNTERDEPTH"
        command_type = b"GET"
        command_string = self._make_message_string(
                command_name, command_type)
        return_data = self._send_packet(command_string)
        return(return_data)

    @counterdepth.setter
    def counterdepth(self, value):
        command_name = b"COUNTERDEPTH"
        command_type = b"SET"
        command_argument_list = [str(value)]
        command_string = self._make_message_string(
                command_name,
                command_type,
                command_argument_list)
        self._send_packet(command_string)

    @property
    def temperature(self):
        command_name = b"TEMPERATURE"
        command_type = b"GET"
        command_string = self._make_message_string(
                command_name, command_type)
        return_data = self._send_packet(command_string)
        return(return_data)

    @temperature.setter
    def temperature(self, value):
        command_name = b"TEMPERATURE"
        command_type = b"SET"
        command_argument_list = [str(value)]
        command_string = self._make_message_string(
                command_name,
                command_type,
                command_argument_list)
        self._send_packet(command_string)

    @property
    def hvbias(self):
        command_name = b"HVBIAS"
        command_type = b"GET"
        command_string = self._make_message_string(
                command_name, command_type)
        return_data = self._send_packet(command_string)
        return(return_data)

    @hvbias.setter
    def hvbias(self, value):
        command_name = b"HVBIAS"
        command_type = b"SET"
        command_argument_list = [str(value)]
        command_string = self._make_message_string(
                command_name,
                command_type,
                command_argument_list)
        self._send_packet(command_string)

    # ACQUISITION AND TRIGGER CONTROL

    @property
    def numframestoacquire(self):
        command_name = b"NUMFRAMESTOACQUIRE"
        command_type = b"GET"
        command_string = self._make_message_string(
                command_name, command_type)
        return_data = self._send_packet(command_string)
        return(return_data)

    @numframestoacquire.setter
    def numframestoacquire(self, value):
        command_name = b"NUMFRAMESTOACQUIRE"
        command_type = b"SET"
        command_argument_list = [str(value)]
        command_string = self._make_message_string(
                command_name,
                command_type,
                command_argument_list)
        self._send_packet(command_string)

    @property
    def acquisitiontime(self):
        command_name = b"ACQUSITIONTIME"
        command_type = b"GET"
        command_string = self._make_message_string(
                command_name, command_type)
        return_data = self._send_packet(command_string)
        return(return_data)

    @acquisitiontime.setter
    def acquisitiontime(self, value):
        command_name = b"ACQUSITIONTIME"
        command_type = b"SET"
        command_argument_list = [str(value)]
        command_string = self._make_message_string(
                command_name,
                command_type,
                command_argument_list)
        self._send_packet(command_string)

    @property
    def acquisitionperiod(self):
        command_name = b"ACQUSITIONPERIOD"
        command_type = b"GET"
        command_string = self._make_message_string(
                command_name, command_type)
        return_data = self._send_packet(command_string)
        return(return_data)

    @acquisitionperiod.setter
    def acquisitionperiod(self, value):
        command_name = b"ACQUSITIONPERIOD"
        command_type = b"SET"
        command_argument_list = [str(value)]
        command_string = self._make_message_string(
                command_name,
                command_type,
                command_argument_list)
        self._send_packet(command_string)

    @property
    def triggerstart(self):
        command_name = b"TRIGGERSTART"
        command_type = b"GET"
        command_string = self._make_message_string(
                command_name, command_type)
        return_data = self._send_packet(command_string)
        return(return_data)

    @triggerstart.setter
    def triggerstart(self, value):
        command_name = b"TRIGGERSTART"
        command_type = b"SET"
        command_argument_list = [str(value)]
        command_string = self._make_message_string(
                command_name,
                command_type,
                command_argument_list)
        self._send_packet(command_string)

    @property
    def triggerstop(self):
        command_name = b"TRIGGERSTOP"
        command_type = b"GET"
        command_string = self._make_message_string(
                command_name, command_type)
        return_data = self._send_packet(command_string)
        return(return_data)

    @triggerstop.setter
    def triggerstop(self, value):
        command_name = b"TRIGGERSTOP"
        command_type = b"SET"
        command_argument_list = [str(value)]
        command_string = self._make_message_string(
                command_name,
                command_type,
                command_argument_list)
        self._send_packet(command_string)

    @property
    def numframespertrigger(self):
        command_name = b"NUMFRAMESPERTRIGGER"
        command_type = b"GET"
        command_string = self._make_message_string(
                command_name, command_type)
        return_data = self._send_packet(command_string)
        return(return_data)

    @numframespertrigger.setter
    def numframespertrigger(self, value):
        command_name = b"NUMFRAMESPERTRIGGER"
        command_type = b"SET"
        command_argument_list = [str(value)]
        command_string = self._make_message_string(
                command_name,
                command_type,
                command_argument_list)
        self._send_packet(command_string)

    @property
    def triggeroutttl(self):
        command_name = b"TriggerOutTTL"
        command_type = b"GET"
        command_string = self._make_message_string(
                command_name, command_type)
        return_data = self._send_packet(command_string)
        return(return_data)

    @triggeroutttl.setter
    def triggeroutttl(self, value):
        command_name = b"TriggerOutTTL"
        command_type = b"SET"
        command_argument_list = [str(value)]
        command_string = self._make_message_string(
                command_name,
                command_type,
                command_argument_list)
        self._send_packet(command_string)

    @property
    def triggeroutlvds(self):
        command_name = b"TriggerOutLVDS"
        command_type = b"GET"
        command_string = self._make_message_string(
                command_name, command_type)
        return_data = self._send_packet(command_string)
        return(return_data)

    @triggeroutlvds.setter
    def triggeroutlvds(self, value):
        command_name = b"TriggerOutLVDS"
        command_type = b"SET"
        command_argument_list = [str(value)]
        command_string = self._make_message_string(
                command_name,
                command_type,
                command_argument_list)
        self._send_packet(command_string)

    @property
    def triggeroutttlinvert(self):
        command_name = b"TriggerOutTTLInvert"
        command_type = b"GET"
        command_string = self._make_message_string(
                command_name, command_type)
        return_data = self._send_packet(command_string)
        return(return_data)

    @triggeroutttlinvert.setter
    def triggeroutttlinvert(self, value):
        command_name = b"TriggerOutTTLInvert"
        command_type = b"SET"
        command_argument_list = [str(value)]
        command_string = self._make_message_string(
                command_name,
                command_type,
                command_argument_list)
        self._send_packet(command_string)

    @property
    def triggeroutlvdsinvert(self):
        command_name = b"TriggerOutLVDSInvert"
        command_type = b"GET"
        command_string = self._make_message_string(
                command_name, command_type)
        return_data = self._send_packet(command_string)
        return(return_data)

    @triggeroutlvdsinvert.setter
    def triggeroutlvdsinvert(self, value):
        command_name = b"TriggerOutLVDSInvert"
        command_type = b"SET"
        command_argument_list = [str(value)]
        command_string = self._make_message_string(
                command_name,
                command_type,
                command_argument_list)
        self._send_packet(command_string)

    @property
    def triggeroutttldelay(self):
        command_name = b"TriggerOutTTLDelay"
        command_type = b"GET"
        command_string = self._make_message_string(
                command_name, command_type)
        return_data = self._send_packet(command_string)
        return(return_data)

    @triggeroutttldelay.setter
    def triggeroutttldelay(self, value):
        command_name = b"TriggerOutTTLDelay"
        command_type = b"SET"
        command_argument_list = [str(value)]
        command_string = self._make_message_string(
                command_name,
                command_type,
                command_argument_list)
        self._send_packet(command_string)

    @property
    def triggeroutlvdsdelay(self):
        command_name = b"TriggerOutLVDSDelay"
        command_type = b"GET"
        command_string = self._make_message_string(
                command_name, command_type)
        return_data = self._send_packet(command_string)
        return(return_data)

    @triggeroutlvdsdelay.setter
    def triggeroutlvdsdelay(self, value):
        command_name = b"TriggerOutLVDSDelay"
        command_type = b"SET"
        command_argument_list = [str(value)]
        command_string = self._make_message_string(
                command_name,
                command_type,
                command_argument_list)
        self._send_packet(command_string)

    @property
    def triggerusedelay(self):
        command_name = b"TriggerUseDelay"
        command_type = b"GET"
        command_string = self._make_message_string(
                command_name, command_type)
        return_data = self._send_packet(command_string)
        return(return_data)

    @triggerusedelay.setter
    def triggerusedelay(self, value):
        command_name = b"TriggerUseDelay"
        command_type = b"SET"
        command_argument_list = [str(value)]
        command_string = self._make_message_string(
                command_name,
                command_type,
                command_argument_list)
        self._send_packet(command_string)

    # Threshold scan control

    @property
    def thscan(self):
        command_name = b"THSCAN"
        command_type = b"GET"
        command_string = self._make_message_string(
                command_name, command_type)
        return_data = self._send_packet(command_string)
        return(return_data)

    @thscan.setter
    def thscan(self, value):
        command_name = b"THSCAN"
        command_type = b"SET"
        command_argument_list = [str(value)]
        command_string = self._make_message_string(
                command_name,
                command_type,
                command_argument_list)
        self._send_packet(command_string)

    @property
    def thstart(self):
        command_name = b"THSTART"
        command_type = b"GET"
        command_string = self._make_message_string(
                command_name, command_type)
        return_data = self._send_packet(command_string)
        return(return_data)

    @thstart.setter
    def thstart(self, value):
        command_name = b"THSTART"
        command_type = b"SET"
        command_argument_list = [str(value)]
        command_string = self._make_message_string(
                command_name,
                command_type,
                command_argument_list)
        self._send_packet(command_string)

    @property
    def thstop(self):
        command_name = b"THSTOP"
        command_type = b"GET"
        command_string = self._make_message_string(
                command_name, command_type)
        return_data = self._send_packet(command_string)
        return(return_data)

    @thstop.setter
    def thstop(self, value):
        command_name = b"THSTOP"
        command_type = b"SET"
        command_argument_list = [str(value)]
        command_string = self._make_message_string(
                command_name,
                command_type,
                command_argument_list)
        self._send_packet(command_string)

    @property
    def thstep(self):
        command_name = b"THSTEP"
        command_type = b"GET"
        command_string = self._make_message_string(
                command_name, command_type)
        return_data = self._send_packet(command_string)
        return(return_data)

    @thstep.setter
    def thstep(self, value):
        command_name = b"THSTEP"
        command_type = b"SET"
        command_argument_list = [str(value)]
        command_string = self._make_message_string(
                command_name,
                command_type,
                command_argument_list)
        self._send_packet(command_string)

    @property
    def thnumsteps(self):
        command_name = b"THNUMSTEPS"
        command_type = b"GET"
        command_string = self._make_message_string(
                command_name, command_type)
        return_data = self._send_packet(command_string)
        return(return_data)

    @thnumsteps.setter
    def thnumsteps(self, value):
        command_name = b"THNUMSTEPS"
        command_type = b"SET"
        command_argument_list = [str(value)]
        command_string = self._make_message_string(
                command_name,
                command_type,
                command_argument_list)
        self._send_packet(command_string)

    # Local File Saving Control

    @property
    def filedirectory(self):
        command_name = b"FILEDIRECTORY"
        command_type = b"GET"
        command_string = self._make_message_string(
                command_name, command_type)
        return_data = self._send_packet(command_string)
        return(return_data)

    @filedirectory.setter
    def filedirectory(self, value):
        command_name = b"FILEDIRECTORY"
        command_type = b"SET"
        command_argument_list = [str(value)]
        command_string = self._make_message_string(
                command_name,
                command_type,
                command_argument_list)
        self._send_packet(command_string)

    @property
    def filename(self):
        command_name = b"FILENAME"
        command_type = b"GET"
        command_string = self._make_message_string(
                command_name, command_type)
        return_data = self._send_packet(command_string)
        return(return_data)

    @filename.setter
    def filename(self, value):
        command_name = b"FILENAME"
        command_type = b"SET"
        command_argument_list = [str(value)]
        command_string = self._make_message_string(
                command_name,
                command_type,
                command_argument_list)
        self._send_packet(command_string)

    @property
    def fileenable(self):
        command_name = b"FILEENABLE"
        command_type = b"GET"
        command_string = self._make_message_string(
                command_name, command_type)
        return_data = self._send_packet(command_string)
        return(return_data)

    @fileenable.setter
    def fileenable(self, value):
        command_name = b"FILEENABLE"
        command_type = b"SET"
        command_argument_list = [str(value)]
        command_string = self._make_message_string(
                command_name,
                command_type,
                command_argument_list)
        self._send_packet(command_string)

    # Commands related to getting the status of the detector

    @property
    def detectorstatus(self):
        command_name = b"DETECTORSTATUS"
        command_type = b"GET"
        command_string = self._make_message_string(
                command_name, command_type)
        return_data = self._send_packet(command_string)
        return(return_data)
