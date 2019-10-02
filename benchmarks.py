import os,subprocess
class hpl:
    """ A class to run single node HPL benchmark on node which are new procured and
    there is no scheduler to run jobs on them. Treating all the nodes as bare metal."""

    def __init__(self,nodename,rundir=os.getenv('PWD'),
                    sourcedir='/home/shaima0d/hpl_trials/input',ntasks=1,executable='xhpl_O3'):
        self.nodename= nodename
        self.rundir= os.path.join(rundir,nodename,'rundir')
        self.sourcedir = sourcedir
        self.script = os.path.join(self.rundir,'launch.sh')
        self.ntasks = ntasks
        self.executable = executable
    
    def setup_rundir(self):
        """ Sets up a run directory and copy the HPL.dat and 
            launch script written in bash to run the job.
            """
        os.makedirs(self.rundir, exist_ok=True)
        # Creating a bash script for lauching commands remotely
        fh = open(self.script,'w+')
        fh.write("#!/bin/bash --login \n \
        module load intelstack-default \n \
        module load intel/2019 \n \
        export PATH=~/Acceptance_testing/software/centos_7.0/build/l_mklb_p_2019.5.004/benchmarks_2019/linux/mkl/benchmarks/mp_linpack:$PATH \n  \
        mpirun -n %d %s &> log.txt & \n \
        exit \n \
        " % (self.ntasks,self.executable) )
        os.chmod(self.script,0o754)
        os.system('cp ' + self.sourcedir + "/HPL.dat " + self.rundir)
        

    def launch_hpl(self):
        """Launches an HPL job on the node with nodename parsed when the class was constructed"""

        out=subprocess.run(['ssh','-o ConnectTimeout=5','-o BatchMode=yes',self.nodename,'cd',self.rundir,';','./launch.sh'],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        # Check if the processes have started successfully
        out = subprocess.run(['ssh','-o ConnectTimeout=5','-o BatchMode=yes',self.nodename,'top -n 1 -b','| grep',self.executable],
                             stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        if self.executable in str(out.stdout.decode("utf-8")):
            print(" has started on ",self.nodename)
        else:
            print("HPL was not launched successfully on node ",self.nodename)
            print("error:" ,str(out.stderr.decode("utf-8")))   
            
            
    def kill_app_proc(self):
        out=subprocess.run(['ssh','-o ConnectTimeout=5','-o BatchMode=yes',self.nodename,'/usr/sbin/pidof',self.executable,'|','xargs kill'],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
         # Check if the processes still exists
        out = subprocess.run(['ssh','-o ConnectTimeout=5','-o BatchMode=yes',self.nodename,'top -n 1 -b','| grep', self.executable],
                             stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        if self.executable in str(out.stdout.decode("utf-8")):
            print("%s not killed on %s. Try killing it mannually." %(self.executable,self.nodename))
        else:
            print(self.executable,"not found on",self.nodename)
            
    def app_proc_status(self):
        out = subprocess.run(['ssh','-o ConnectTimeout=5','-o BatchMode=yes',self.nodename,'top -n 1 -b','| grep', self.executable],
                             stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        
        if self.executable in str(out.stdout.decode("utf-8")):
            print (self.executable, " is still running on",self.nodename)
        elif str(out.stdout.decode("utf-8")) == '':
            if str(out.stderr.decode("utf-8")) != '':
                print(str(out.stderr.decode("utf-8")))
            else:
                print(self.executable,"does not exist on", self.nodename)
             
     
    def get_metrics(self):
        """A function to parse the HPL.out and read the results collected by HPL run. 
           These results are then returned as a dictionary along with a message."""
        fname = os.path.join(self.rundir,'HPL.out')
        msg=str()
        metrics = {
                'N' : 0,
                'NB': 0,
                'P' : 0,
                'Q' : 0,
                'Time' : 0.0,
                'Gflops' : 0.0
            }
        f = open(fname,'r+')
        buf = f.readlines()
        f.close()
        line_number=0
        tmp_buf=list()
        for line1 in buf:
            if 'PASSED' in line1.split():
                for line2 in buf:
                    if ('T/V' in line2.split()) and ('Gflops' in line2.split()):
                        tmp_buf = buf[line_number + 2].split()
                        tmp_count = 1
                        for key in metrics:
                            metrics[key] = tmp_buf[tmp_count]
                            tmp_count += 1 
                    line_number +=1
                msg = 'Run ended successfully'
                break
            else:
                msg = "Run failed"
        return msg,metrics
    
        
        
        