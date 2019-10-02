import benchmarks
import os

def report_hpl(nodelist,csv='results.csv'):
    HPL_reference = 2165.0
    tolerance = -2.50 # Value above -2.5% is acceptable
    
    gflops=list()
    deviation=list()
    msgs=list()
    report=list()
    for i in range(len(nodelist)):
        report.append(benchmarks.hpl(nodelist[i]))
        msg,metric=report[i].get_metrics()
        msgs.append(msg)
        gflops.append(float(metric['Gflops']))
        deviation.append((-1 + gflops[i]/HPL_reference)*100)
    
    
    fh = open(csv,'w+')
    fh.write("HPL Reference value,%f\n" %HPL_reference)
    fh.write("Acceptabale tolreance,>= %2.2f percent\n" %tolerance)
    fh.write("Maximum GFLOPs,%f\n" %max(gflops))
    fh.write("Minimum GFLOPs,%f\n" %min(gflops))
    fh.write("Average GFLOPs,%f\n" %(sum(gflops)/len(gflops)))
    
    fh.write("Hostname,GFLOPs,% (GFLOPs - Ref),Acceptance status\n")
    
    
    for i in range(len(nodelist)):
        status = "PASS" if deviation[i] >= tolerance else "FAIL"
        fh.write("%s,%4.2f,%2.2f,%s\n" %(nodelist[i],gflops[i],deviation[i],status))
        
    fh.close()
    
    return 0


def resource_utilization(nodelist,csv='utilization.csv'):
    
    fh = open(csv,'w+')
    fh.write("Hostname,App,%%CPU,%%MEM\n")
    for i in range(len(nodelist)):
        out = subprocess.run(['ssh','-o ConnectTimeout=5','-o BatchMode=yes',nodelist[i],'top -n 1 -b','| grep', self.app_name],
                          stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        tmp = str(out.stdout.decode("utf-8")).split()
        fh.write(nodelist[i],tmp[11],tmp[8],tmp[9])
    fh.close()
    