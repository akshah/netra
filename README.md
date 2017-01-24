Netra: Tool to detect international routing detours
--------------------------------------------

Netra detects routing detours (routes that start and end in the same country but visit another country in between) as 
seen in control (BGP) plane; but can validate the detour using ICMP Paris traceroute locally and using RIPE Atlas 
platform. Input to Netra are raw RIB dumps in MRT format.  

A report on methodology and results analysis can be found here:  http://arxiv.org/pdf/1606.05047v1.pdf


Requirements
------------------

This is a python3 implementation. A connection to MySQL 5+ is needed to store results of analysis.
A list of required python modules is available in 'requirements.txt'.  
Other custom modules:  
BGP Data Engine: https://github.com/akshah/bgpDataEngine.git  
GeoInfo Interface: https://github.com/akshah/geoInfo.git  
Custom Utils: https://github.com/akshah/customUtilities.git  
RIPE API interface: https://github.com/RIPE-NCC/ripe-atlas-cousteau.git  

Instructions to launch analysis
--------------------------

1. Install Python3 and modules stated in requirements.txt
2. Install BGP Data Engine, GeoInfo and Custom Utils
3. Setup a MySQL DB with read/write access and update necessary information in conf/detourDetection.conf
4. Download RIB from the BGP speaking router in your network or use BGP Data Engine to download from RouteViews/RIPE RIS/BGPmon
5. If you wish to view paths only from certain BGP-peer or detect detours for only selected prefixes, update the 
filters/peers/fine_peers and filters/prefixes/fine_prefixes files respectively and update conf/detourDetection.conf.
6. Launch analysis using detectRIPELiveDetours.py

Note: If you want to launch traceroutes using RIPEAtlas you will need RIPE credits. Set up keys in conf/ripe.conf.
If you want to launch local traceroutes then scamper utility needs to be installed: https://www.caida.org/tools/measurement/scamper/
Scamper needs root access. Add your auth here: .sudo.auth

Contact
---------

For questions/comments feel free to contact akshah AT rams.colostate.edu