import subprocess
import benchmarks,report


def create_nodelist(raw_list):
	"""Create a nodlist from a string which is a comma separeated list of hostname ranges.
	e.g. cn509-[02-10]-l,cn501-[10-20]-knl,.... """
	nodelist=list()
	tmp = raw_list.split(',')

	for i in range(len(tmp)):
		prefix = (tmp[i].split('-'))[0]
		if ('[' or ']')  in tmp[i]:
			suffix = (tmp[i].split('-'))[3]	
			start_indx = int (((tmp[i].split('-'))[1:3])[0].strip('['))
			end_indx   = int (((tmp[i].split('-'))[1:3])[1].strip(']'))
		else:
			suffix = (tmp[i].split('-'))[2]
			start_indx = int (((tmp[i].split('-'))[1:2])[0])
			end_indx = int (((tmp[i].split('-'))[1:2])[0])

		for j in range(start_indx,end_indx+1):
			nodelist.append(prefix + '-' + str(j).zfill(2) + '-' + suffix)
	return nodelist
 
 
def app_proc_status(nodename,app_name):
	out = subprocess.run(['ssh','-o ConnectTimeout=5','-o BatchMode=yes',nodename,'top -n 1 -b','| grep', app_name],
						stdout=subprocess.PIPE,stderr=subprocess.PIPE)
	if app_name in str(out.stdout.decode("utf-8")):
		print (app_name, " is still running on",nodename)
	elif str(out.stdout.decode("utf-8")) == '':
		if str(out.stderr.decode("utf-8")) != '':
			print(str(out.stderr.decode("utf-8")))
		else:
			print(app_name,"does not exist on", nodename)
	return 0

def execute_procs(nodelist,app_name):
	if app_name == 'hpl':
	    tests=list()
	    for i in range(len(nodelist)):
	        tests.append(benchmarks.hpl(nodelist[i]))
	        tests[i].setup_rundir() 
	        tests[i].launch_hpl()
	return 0


def status_procs(nodelist,app_name):
    if app_name == 'hpl':
    	tests=list()
    	for i in range(len(nodelist)):
    		tests.append(benchmarks.hpl(nodelist[i]))
    		tests[i].app_proc_status()
    return 0
   
def kill_procs(nodelist,app_name):	
	if app_name == 'hpl': 
		procs = list()	
		for i in range(len(nodelist)):
		    procs.append(benchmarks.hpl(nodelist[i]))
		    procs[i].kill_app_proc()
	return 0	    

def utilization(nodelist,app_name):
	report.resource_utilization(nodelist)


def report_procs(nodelist,app_name):
	if app_name == 'hpl':
		report.report_hpl(nodelist)
	return 0