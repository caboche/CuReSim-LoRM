#!/usr/bin/env python3

import argparse
import os
import pysam
import numpy as np
import matplotlib.pyplot as plt
import sys
import subprocess
from scipy import stats
from scipy.stats import exponweib
from collections import defaultdict


simulated_reads=""
real_reads=""
sam_file=""
bbmap=""
path="RESULTS"

parser = argparse.ArgumentParser()

def file_choices(choices,fname):
    ext = os.path.splitext(fname)[1][1:]
    if ext not in choices:
       parser.error("file doesn't end with one of {}".format(choices))
    return fname

parser.add_argument('grinder',help="grinder simulated reads in FASTQ format",type=lambda s:file_choices(("fastq","fq"),s))
parser.add_argument('reads',help="real reads in FASTQ format",type=lambda s:file_choices(("fastq","fq"),s))
parser.add_argument('sam',help="sam file of real reads",type=lambda s:file_choices(("sam"),s))
parser.add_argument('bbmap',help="distribution of identity obtained with bbmap",type=lambda s:file_choices(("txt"),s))
parser.add_argument("-o", "--output", help="output directoty [RESULTS]")

args = parser.parse_args()


simulated_reads=args.grinder
real_reads=args.reads
sam_file=args.sam
bbmap=args.bbmap

if args.output != None :
	path=args.output




# define the name of the directory to be created

try:
    os.mkdir(path)
except OSError:
    print ("Creation of the directory %s failed" % path)
else:
    print ("Successfully created the directory %s " % path)


#log file
log=open(path+"/log_error_profile.txt","w")

nb_reads=sum(1 for line in open(simulated_reads))
nb_reads=int(nb_reads/4)
log.write("nb simualted reads"+str(nb_reads)+"\n")


def stats_from_aligned_read(read):
    """Create summary information for an aligned read

    :param read: :class:`pysam.AlignedSegment` object
    """

    tags = dict(read.tags)
    try:
        tags.get('NM')
    except:
        raise IOError("Read is missing required 'NM' tag. Try running 'samtools fillmd -S - ref.fa'.")

    name = read.qname
    if read.flag == 4:
        return None
    counts = defaultdict(int)
    for (i, j) in read.cigar:
        counts[i] += j
    match = counts[0]
    ins = counts[1]
    delt = counts[2]
    # NM is edit distance: NM = INS + DEL + SUB
    sub = tags['NM'] - ins - delt
    length = match + ins + delt
    iden = 100*float(match - sub)/match
    acc = 100 - 100*float(tags['NM'])/length

    read_length = read.infer_read_length()
    coverage = 100*float(read.query_alignment_length) / read_length
    direction = '-' if read.is_reverse else '+'

    results = {
        "name":name,
        "coverage":coverage,
        "direction":direction,
        "length":length,
        "read_length":read_length,
        "ins":ins,
        "del":delt,
        "sub":sub,
        "iden":iden,
        "acc":acc
    }
    return results 


#####################################
## Define percentage of insertions, deletions and substitutions from sam file
#####################################

ins=0
dele=0
sub=0

nb=0
error=0.
p_ins=0.
p_sub=0.
p_del=0.

e=0.


samfile = pysam.AlignmentFile(sam_file,"rb")


for read in samfile.fetch():
    
	if not read.is_unmapped and (read.flag == 0  or read.flag == 16 ) :
		nb=nb+1
		res=stats_from_aligned_read(read)
		if (res['ins']+res['del']+res['sub'] != 0) :
			p_ins=p_ins+(res['ins']/float(res['ins']+res['del']+res['sub']))
			p_del=p_del+(res['del']/float(res['ins']+res['del']+res['sub']))
			p_sub=p_sub+(res['sub']/float(res['ins']+res['del']+res['sub']))
			e=e+float(res['ins']+res['del']+res['sub'])/read.query_alignment_length			

samfile.close()

p_ins=round(p_ins/nb,2)
p_del=round(p_del/nb,2)
p_sub=round(p_sub/nb,2)

log.write("INS "+str(p_ins)+"\n")
log.write("DEL "+str(p_del)+"\n")
log.write("SUB "+str(p_sub)+"\n")



#####################################
#identity histogram#
#####################################
log_prog=open("HISTO.txt","w")

with open(bbmap,"r") as ff: 
	dat = ff.readlines()
					 
	for line in dat:
		if not(line.startswith('#')) :
			data=line.split()
			for i in range(0,int(data[1])) :
				log_prog.write(data[0]+"\n")

log_prog.close()

######################################



data = np.loadtxt("HISTO.txt")
data=(100.-data)


a_out, Kappa_out, loc_out, Lambda_out = stats.exponweib.fit(data)
log.write("Estimation: "+str(a_out)+","+str(Kappa_out)+","+str(loc_out)+","+str(Lambda_out)+"\n")
R=exponweib.rvs(a=a_out,c=Kappa_out,loc=loc_out,scale = Lambda_out, size=nb_reads)  



#check [0;100]
for i in range(len(R)):
	if R[i]<0:
		R[i]=0.
		print ("NEG: ",R[i])
	if R[i]>100:
		R[i]=100.
		print ("SUP: ",R[i])
		



#Plot
bins = range(101)
fig = plt.figure() 
ax = fig.add_subplot(1, 1, 1)
ax.plot(bins, stats.exponweib.pdf(bins, a=a_out,c=Kappa_out,loc=loc_out,scale = Lambda_out))
ax.hist(data, bins = bins , density=True)
ax.annotate("Shape: $k = %.2f$ \n Scale: $\lambda = %.2f$"%(Kappa_out,Lambda_out), xy=(0.7, 0.85), xycoords=ax.transAxes)
plt.savefig(path+'/error_model.pdf')
plt.close(fig)


log_prog=open(path+"/OUTPUT_ERRORS.txt","w")
log_prog.write("read;ins;del;sub\n")

with open(simulated_reads,"r") as in_file:
	data=in_file.readlines()
	j=0
	while (j>=0) & (j<len(data)):
		if(j%4==0):
			out_f=open("tmp.fastq","w")
	
			readId=data[j]
			readId=readId[1:str.find(readId," ")]
			log_prog.write(readId+";")

			for i in range(0,4):
				out_f.write(data[j])
				j+=1
			out_f.close()

			
			sim=R[int(readId)-1]
			error=sim/100.

			if(error == 1.):
				print("WARNING ",sim)

			deletion=error*p_del
			insertion=error*p_ins
			substitution=error*p_sub

			log_prog.write(str(round(insertion,4))+";"+str(round(deletion,4))+";"+str(round(substitution,4))+"\n")


log_prog.close()


###########################
# Get size parameters
###########################





log_prog=open("tmp_size.txt","w")

n=0

with open(real_reads,"r") as ff: 
	dat = ff.readlines()
					 
	for line in dat:
		n+=1
		if (n==2) :
			log_prog.write(str(len(line)-1)+"\n")
			
		else :
			if(n==4) :
				n=0
			
log_prog.close()


data = np.loadtxt("tmp_size.txt",dtype="int")

os.remove("tmp_size.txt") 

gauss=0
longRead=0
longDel=0
short=0
veryShort=0


b=np.bincount(data)

condition= (data > 1450) & (data < 1600)
interval=np.extract(condition,data)
log.write("GAUSS: "+str(np.size(interval))+","+str(np.size(interval)/np.size(data)*100.)+"%: "+str(round(np.size(interval)/np.size(data)*100.))+"\n")

gauss=round(np.size(interval)/np.size(data)*100.)

c2= (data > 1600) 
i2=np.extract(c2,data)
log.write("LONG: "+str(np.size(i2))+","+str(np.size(i2)/np.size(data)*100.)+"%: "+str(round(np.size(i2)/np.size(data)*100.))+"\n")

longRead= round(np.size(i2)/np.size(data)*100.)

c3= (data < 200) 
i3=np.extract(c3,data)
log.write("VERY SHORT: "+str(np.size(i3))+","+str(np.size(i3)/np.size(data)*100.)+"%: "+str(round(np.size(i3)/np.size(data)*100.))+"\n")

veryShort=round(np.size(i3)/np.size(data)*100.)

c4= (data > 200) & (data < 1000)
i4=np.extract(c4,data)
log.write("SHORT: "+str(np.size(i4))+","+str(np.size(i4)/np.size(data)*100.)+"%: "+str(round(np.size(i4)/np.size(data)*100.))+"\n")

short=round(np.size(i4)/np.size(data)*100.)

c5= (data > 1000) & (data < 1450)
i5=np.extract(c5,data)
log.write("1000-1450: "+str(np.size(i5))+","+str(np.size(i5)/np.size(data)*100.)+"%: "+str(round(np.size(i5)/np.size(data)*100.))+"\n")

longDel=round(np.size(i5)/np.size(data)*100.)


if (longRead==0) :
	longRead=1

som=longRead+short+veryShort+longDel
gauss=100-som
print("############")
print(gauss,",",longDel,",",longRead,",",short,",",veryShort,",0")
#
log.write("############")
log.write(str(gauss)+","+str(longDel)+","+str(longRead)+","+str(short)+","+str(veryShort)+",0")
log.close();


#################
#Run CuReSim-LoRM
#################


para=str(gauss)+","+str(longDel)+","+str(longRead)+","+str(short)+","+str(veryShort)+",0"

profile=path+"/OUTPUT_ERRORS.txt"

print(simulated_reads)


command="java -jar CuReSim-LoRM.jar -f "+simulated_reads+" -o "+path+"/curesim_reads.fastq -p "+profile+" -para "+para

print("RUNNING "+command)


p = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)


(outputt, err) = p.communicate()  

p_status = p.wait()



