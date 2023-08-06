# python-nuttcp-parser
Parsing the output of NUTTCP in Python

##Usage
parser = nuttcp_parser.Parser(nuttcp_output) nuttcp_output must be string not bytes\
result = parser.parse()

##Returns
* duration in seconds
* transmitted_MB
* speed_Mbs
* RX
* TX
* and for TCP Additionally:  
    * retrans
    * RTT in ms
* and for UDP Additionally:  
    * dropped
    * packets
    * loss in %
