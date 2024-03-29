import sys
import rrdtool
import math
import time

class RRDManager(object):
    #COSTANTI RRD------
	XFF1="0.5"
	XFF2="0.5"
	XFF3="0.5"
	XFF4="0.5"
	XFF5="0.5"
	STEP1="1"
	STEP2="6"
	STEP3="12"
	STEP4="288"
	STEP5="2016"
	ROWS1="24"
	ROWS2="10"
	ROWS3="24"
	ROWS4="7"
	ROWS5="4"
	#--------------
	def getActualTime(self):
		return int(math.floor(time.time()))

	#se eth_type non corrisponde a nulla (IP, MPLS, ...) inserire 0000
	def constructDataSource(self, dev_id, port_n, eth_type):
		return str(str(port_n)+'_'+str(eth_type))

	def __init__(self, filename, device, eth_types):
		# define rrd filename
		self.filename = filename
		self.eth_types = eth_types
		#self.eth_types.append(eth_types)
		# import port numbers for each device id
		self.device = device

		# build ALL data sources DS:deviceID_portN_ETH_TYPE:COUNTER:600:U:U
		self.data_sources = []
		self.raw_data_sources = []

		for dev_id in sorted(self.device):
			for port_n in self.device[dev_id]:
				for eth_type in self.eth_types:
					temp = str(self.constructDataSource(dev_id, port_n, eth_type))
					self.raw_data_sources.append(temp)
					self.data_sources.append('DS:' + temp + ':GAUGE:600:U:U')
		# create rrd w/ default step = 300 sec
		rrdtool.create(self.filename,
			       '--step',
			       '300',
		               '--start',
		               str(self.getActualTime()),
		               self.data_sources,
		               'RRA:AVERAGE:'+XFF1+':'+STEP1+':'+ROWS1,	 #i dati raccolti ogni 5 minuti per 2 ore
		               'RRA:AVERAGE:'+XFF2+':'+STEP2+':'+ROWS2,	 #i dati raccolti ogni 30 minuti per 5 ore
		               'RRA:AVERAGE:'+XFF3+':'+STEP3+':'+ROWS3,	 #i dati raccolti ogni ora per un giorno
			       'RRA:AVERAGE:'+XFF4+':'+STEP4+':'+ROWS4,  #i dati raccolti ogni giorno per una settimana
			       'RRA:AVERAGE:'+XFF5+':'+STEP5+':'+ROWS5) #i dati raccolti ogni settimana per 4 settimane
		print self.raw_data_sources
	
	# insert values w/ timestamp NOW for a set of given DS
	def update(self, data_sources, values):
		if (len(data_sources) != len(values)) or len(data_sources) <= 0 or (len(data_sources) >= self.data_sources):
			raise Exception('Wrong number of data_sources or values')
		for DS in data_sources:
			if DS not in self.raw_data_sources:
				raise Exception('Data source not available in RRD')
		template = ':'.join(data_sources)
		values = ':'.join(str(value) for value in values)
		rrdtool.update(self.filename, '-t', template, str(self.getActualTime()) + ':' + values)


################
#   T E S T    #
################
'''
device = {}
device['PEO1'] = [1,2,3,4]
device['PEO2'] = [1,2]
device['PEO3'] = [1,4,5,6]
device['PEO4'] = [2,3,5]

rrdman = RRDManager('test.rrd', device, ["0800", "0806", "0000"])
time.sleep(10)
rrdman.update([rrdman.constructDataSource('PEO1', 1, "0800"), rrdman.constructDataSource('PEO2', 1, "0806"), rrdman.constructDataSource('PEO3', 1, "0000")],[13000,15005,13501])
'''
