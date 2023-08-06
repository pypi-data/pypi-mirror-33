

class Parser():
    def __init__(self, nuttcp_string):
        self.nuttcp_string = nuttcp_string

    def parse(self):
        lines = self.nuttcp_string.splitlines()
        last_line = lines[len(lines) - 1]
        if last_line.endswith('loss'):
            protocol = 'udp'
        else:
            protocol = 'tcp'
        summary_split = last_line.split('=')
        transmit = summary_split[0].split('/')
        transmitted_MB = float(transmit[0].split()[0]) # output of NUTTCP is always in MB
        duration = transmit[1].split()
        rest = summary_split[1].split()
        speed = float(rest[0])
        tx = int(rest[2])
        rx = int(rest[4])
        if protocol == 'tcp':
            retrans = int(rest[6])
            rtt = float(rest[8])
        else:
            dropped = int(rest[6])
            packets = int(rest[8])
            loss = float(rest[10])
        result = NUTTCPResult(protocol)
        result.summary['transmitted_MB'] = transmitted_MB
        result.summary['duration'] = float(duration[0])
        result.summary['speed_Mbs'] = speed
        result.summary['RX'] = rx
        result.summary['TX'] = tx

        #TCP only
        if protocol == 'tcp':
            result.summary['retrans'] = retrans
            result.summary['RTT'] = rtt
        else:
            result.summary['dropped'] = dropped
            result.summary['packets'] = packets
            result.summary['loss'] = loss
        return result




class NUTTCPResult():
    def __init__(self, protocol):
        self.protocol = protocol
        if self.protocol == 'tcp':
            self.summary = dict.fromkeys(['duration', 'transmitted_MB', 'speed_Mbs', 'RX', 'TX', 'retrans', 'RTT'])
        else:
            self.summary = dict.fromkeys(['duration', 'transmitted_MB', 'speed_Mbs', 'RX', 'TX', 'dropped', 'packets', 'loss'])
