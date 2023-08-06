#!/usr/bin/env python

import subprocess
import sys
import math
from lifelines import CoxPHFitter
cph = CoxPHFitter()
#import scipy.stats as stats
#class DevNull:
#	def write(self, msg):
#		pass
#sys.stderr = DevNull()
import csv
import numpy as np
import pandas as pd
pd.options.mode.chained_assignment = None
import gzip
import time
start=time.time()
#import StringIO
import argparse
import warnings



import threading
from multiprocessing import Process, Manager
import itertools
import time
import warnings
#import progressbar
#from multiprocessing.dummy import Pool as ThreadPool

def HWE_test_chi(obs_AA, obs_Aa, obs_aa, miss):
	obs_t = (obs_Aa + obs_AA + obs_aa - miss)
	f_A = (2*obs_AA + obs_Aa) / (2 * obs_t)
	f_a = (2*obs_aa + obs_Aa) / (2 * obs_t)

	chi = ((obs_Aa - (2 * f_A * f_a * obs_t))**2)/(2 * f_A * f_a * obs_t) + ((obs_AA - ((f_A **2) * obs_t))**2)/((f_A **2) * obs_t) + ((obs_aa - ((f_a **2) * obs_t))**2)/((f_a **2) * obs_t)
	p_value = 1 - stats.chi2.cdf(x=chi, df=1)
	#p_hwe = 1.0 if p_hwe > 1.0 else p_hwe

	return p_value

def maf_calc(gp0n,gp1n,gp2n,a_l,miss):
	if (gp0n>gp2n):
		maf=((2*gp2n+gp1n)/(2*(a_l-miss)))
	else:
		maf=((2*gp0n+gp1n)/(2*(a_l-miss)))
	return maf

def info_calc(gp0,gp1,gp2,a_l,miss):
	N = a_l - miss
	e = []
	for i in range(a_l):
		e.append((2.0*gp2[i]) + gp1[i])

	p = np.sum(e) / (N*2.0)

	if (p<1 and p>0):
		nom=[]
		for i in range(a_l):
			nom.append(((4.0*gp2[i]) + gp1[i]) - ((2.0*gp2[i]) + gp1[i])**2)
		info= 1 - (np.sum(nom)/(2*(N)*p*(1-p)))
	else:
		info = 1
	return info


def HWE_test(obs_hom2, obs_het, obs_hom1):
	if obs_hom1 < 0 or obs_hom2 < 0 or obs_het < 0:
		raise Exception("FATAL ERROR - SNP-HWE: Current genotype configuration (%s  %s %s) includes negative count" % (obs_hets, obs_hom1, obs_hom2))

	obs_homc = int(obs_hom2) if obs_hom1 < obs_hom2 else int(obs_hom1)
	obs_homr = int(obs_hom1) if obs_hom1 < obs_hom2 else int(obs_hom2)
	obs_hets = int(obs_het)

	rare_copies = 2 * obs_homr + obs_hets
	genotypes   = obs_hets + obs_homc + obs_homr

	het_probs = [0.0] * (rare_copies + 1)

	#start at midpoint
	mid = int(rare_copies * (2 * genotypes - rare_copies) / (2 * genotypes))

	#check to ensure that midpoint and rare alleles have same parity
	if (rare_copies & 1) ^ (mid & 1):
		mid +=1

	curr_hets = int(mid)
	curr_homr = int((rare_copies - mid) / 2)
	curr_homc = int(genotypes - curr_hets - curr_homr)

	het_probs[mid] = 1.0
	sum = float(het_probs[mid])

	for curr_hets in range(mid, 0, -2):

		het_probs[curr_hets - 2] = het_probs[curr_hets] * curr_hets * (curr_hets - 1.0) / (4.0 * (curr_homr + 1.0) * (curr_homc + 1.0))

		sum += het_probs[curr_hets - 2]
		# 2 fewer heterozygotes for next iteration -> add one rare, one common homozygote
		curr_homr += 1
		curr_homc += 1

	curr_hets = mid
	curr_homr = (rare_copies - mid) / 2
	curr_homc = genotypes - curr_hets - curr_homr 

	for curr_hets in range(mid, rare_copies - 1, 2):

		het_probs[curr_hets + 2] = het_probs[curr_hets] * 4.0 * curr_homr * curr_homc / ((curr_hets + 2.0) * (curr_hets + 1.0))

		sum += het_probs[curr_hets + 2]
		# 2 more heterozygotes for next iteration -> add one rare, one common homozygote
		curr_homr -= 1
		curr_homc -= 1

	for i in range(0, rare_copies + 1):
		het_probs[i] /= sum

	#alternate p-value calculation for p_hi/p_lo
	p_hi = float(het_probs[obs_hets])
	for i in range(obs_hets, rare_copies+1):
		p_hi += het_probs[i]

	p_lo = float(het_probs[obs_hets])
	for i in range(obs_hets-1, -1, -1):
		p_lo += het_probs[i]

	p_hi_lo = 2.0 * p_hi if p_hi < p_lo else 2.0 * p_lo

	p_hwe = 0.0
	#  p-value calculation for p_hwe
	for i in range(0, rare_copies + 1):
		if het_probs[i] > het_probs[obs_hets]:
			continue;
		p_hwe += het_probs[i]

	p_hwe = 1.0 if p_hwe > 1.0 else p_hwe

	return p_hwe



def do_work(in_queue, out_list, sub):
	while True:
		item = in_queue.get()
		line_no, line = item
	# exit signal
		if line == None:
			return

		if args.r == 1:
			# Using R work
			result = crgwas(line, line_no )
		if args.r == 0:
			# Using lifelines work for cause-specific
			gp, info, maf, hwe, gl = QC(line, line_no)
			df3_1 = pycrgwas(gp, sub)
			result = output(df3_1, info, maf, hwe, gl)
		# output
		out_list.append(result)

def gwasprogress( ):
	sys.stdout.write('\r')
	progress = "#" + str(i-args.thread) + " SNPS ANALYSED @ {0:0.01f} SECS PER SNP #".format((time.time()-start)/i)
	#sys.stdout.write(progress.center(os.get_terminal_size().columns))
	sys.stdout.write(progress)
	sys.stdout.flush()
	work.put(num_and_line)

def crgwas(line, line_no ):
	gl=line.split(' ')
	gp0j=gl[5::3]
	gp1j=gl[6::3]
	gp2j=gl[7::3]
	gp0=[float(i) for i in gp0j]
	gp1=[float(i) for i in gp1j]
	gp2=[float(i) for i in gp2j]

	gp = [];a_l=len(gp1)
	miss=0
	for i in range(a_l):
		if (gp0[i]+gp1[i]+gp2[i])>0:
			gp.append(gp1[i]+(2*gp2[i]))
		else:
			gp.append(np.nan)
			miss+=1
	gp0n=np.nansum(gp0)
	gp1n=np.nansum(gp1)
	gp2n=np.nansum(gp2)

	#QC measures
	info=info_calc(gp0,gp1,gp2,a_l,miss)
	maf=maf_calc(gp0n,gp1n,gp2n,a_l,miss)
	hwe=HWE_test(gp0n,gp1n,gp2n)

	#Analysis
	sub['gz']=gp
	sub[[args.t_pheno, args.et_pheno]] = sub[[args.t_pheno, args.et_pheno]].astype(int)
	robjects.globalenv['sub'] = sub

	while True:
		try:
			test=cmprsk.crr(ftime=sub[args.t_pheno],fstatus=sub[args.et_pheno],cov1=sub.iloc[:,2:],failcode=args.obs,cencode=0)
			res=base.summary(test).rx2('coef')
			#resconv=base.summary(test).rx2('conv') STILL NEED TO CODE CONV
			df3 = pd.DataFrame({'beta':[res.rx('gz',1)],'se':[res.rx('gz',3)],'p':[res.rx('gz',5)],'conv':[1]})
			df3['beta'] = df3['beta'].str[0]
			df3['se'] = df3['se'].str[0]
			df3['p'] = df3['p'].str[0]
			break

		except RRuntimeError:
			print("R had an issue with this one:", gl[1])
			df3 = pd.DataFrame({'beta':[-9],'se':[-9],'p':[-9],'conv':[0]})
			break

	df1 = pd.DataFrame({'chr':[args.chr],'snp':[gl[1]],'bp':[gl[2]],'info':[info],'maf':[maf],'hwe':[hwe],'ea':[gl[3]],'nea':[gl[4]]})
	result=df1.join(df3)
	return result;

def QC(line, line_no ):
	gl=line.split(' ')
	gp0j=gl[5::3]
	gp1j=gl[6::3]
	gp2j=gl[7::3]
	if args.chr:
		gl[0]=args.chr
	gl=gl[0:5]
	gp0=[float(i) for i in gp0j]
	gp1=[float(i) for i in gp1j]
	gp2=[float(i) for i in gp2j]

	gp = [];a_l=len(gp1)
	miss=0
	for i in range(a_l):
		if (gp0[i]+gp1[i]+gp2[i])>0:
			gp.append(gp1[i]+(2*gp2[i]))
		else:
			gp.append(np.nan)
			miss+=1
	gp0n=np.nansum(gp0)
	gp1n=np.nansum(gp1)
	gp2n=np.nansum(gp2)

	#QC measures

	info=info_calc(gp0,gp1,gp2,a_l,miss)
	maf=maf_calc(gp0n,gp1n,gp2n,a_l,miss)
	hwe=HWE_test(gp0n,gp1n,gp2n)
	return(gp, info, maf, hwe, gl)

def pycrgwas(gp, sub ):
	#Analysis
	subsnp=sub
	subsnp['gz']=gp

	if args.int:
		subsnp['int'] = gp*sub[args.int]

	subn = subsnp.dropna()
	cph.fit(subn,duration_col=args.t_pheno,event_col='bin')
	df3_1=cph.summary
	return(df3_1)

def output(df3_1, info, maf, hwe, gl ):
	if args.verbose == 0:
		df3_2 = df3_1.loc['gz',:]
		df3 = pd.DataFrame({'beta':[df3_2.loc['coef']],'se':[df3_2.loc['se(coef)']],'p':[df3_2.loc['p']],'conv':[1]},dtype='float64') # potential to make this similar to verbose == 1 block in future... 
		df1 = pd.DataFrame({'chr':[gl[0]],'test':[gl[1]],'snp':[gl[1]],'bp':[gl[2]],'info':[info],'maf':[maf],'hwe':[hwe],'ea':[gl[3]],'nea':[gl[4]]})
		result=df1.join(df3)

	if args.verbose == 1:
		df3_1.rename(index=str, columns={"coef":"beta","se(coef)":"se"}, inplace=True)
		df3 = df3_1.loc[:,['beta','se','p']]
		df1n = pd.DataFrame({'chr':[gl[0]],'snp':[gl[1]],'bp':[gl[2]],'info':[info],'maf':[maf],'hwe':[hwe],'ea':[gl[3]],'nea':[gl[4]],'conv':[1]})
		df1 = pd.concat([df1n]*df3.shape[0])
		df1.reset_index(drop=True, inplace=True)
		df3.reset_index(drop=True, inplace=True)
		result = pd.concat([df1,df3], axis=1)
		result['test'] = df3_1.index
		result['test'].replace(to_replace="gz",value=gl[1],inplace=True)

	result['p'] = result['p'].apply(lambda x: round(x,5))
	result[['info','maf','hwe']] = result[['info','maf','hwe']].apply(lambda x: round(x,2))
	result[['beta','se']] = result[['beta','se']].apply(lambda x: round(x,4))
	return result;




parser = argparse.ArgumentParser()

# set argparse
parser.add_argument('--gfile', type=str, default="",
		    help='gen file needed')
parser.add_argument('--sfile', type=str, default="",
		    help='sample file needed')
parser.add_argument('--ofile', type=str, default="",
		    help='output file stem, e.g. <ofile>.out')
parser.add_argument('--chr', type=str,
		    help='chromosome number to use in output file')
parser.add_argument('--obs', type=int, default=1,
		    help='which obs indicator is the competing risk (1 is default, do not specify 0 as it is reserved for censored observations)')
parser.add_argument('--t_pheno', type=str, default="",
		    help='time to event in SAMPLE file')
parser.add_argument('--et_pheno', type=str, default="",
		    help='event type indicator in SAMPLE file')
parser.add_argument('--covs', type=str, default="",
		    help='comma delimited list of covariates in SAMPLE file')
parser.add_argument('--int', type=str, default="",
		    help='covariate to adjust for SNP covariate interaction, must be from SAMPLE file')
parser.add_argument('--crtype', type=int, default=0,
		    help='use 0 for subdistribution competing risks (default), 1 for cause-specific competing risks and 2 for conventional Cox PH survival model')
parser.add_argument('--r', type=int, default=0,
		    help='use 1 to perform analysis with R package cmprsk or 0 to perform analysis in Python package lifelines')
parser.add_argument('--verbose', type=int, default=0,
		    help='use 1 to print results of covariates tested at each SNP, includes interaction terms of specified')
parser.add_argument('--thread', type=int, default=1,
		    help='specify number of threads to use (please consider the hardware limitations of your computer/cluster)')
args=parser.parse_args()

if args.r == 1:
	import rpy2.robjects as robjects
	r = robjects.r
	from rpy2.robjects.packages import importr
	from rpy2.robjects import r, pandas2ri
	pandas2ri.activate()
	#import R's "base" package
	base = importr('base')
	#import R's "utils" package
	utils = importr('utils')
	cmprsk = importr('cmprsk')
	robjects.r['options'](warn=-1)
	from rpy2.rinterface import RRuntimeError
	#warnings.filterwarnings("ignore", category=RRuntimeError) # Sort out why this generates error!
	robjects.r('sink("/dev/null")')

if __name__ == "__main__":
	print("##############################")
	print("#      WELCOME TO CRAG       #")
	print("##############################\n")

	# Reduce sample to needed covs

	sample = pd.read_csv(args.sfile,sep=" ") 
	list=[args.t_pheno,args.et_pheno]
	if args.covs!="":
		list.extend(args.covs.split(','))
	if args.int!="":
		list.extend(args.int.split(','))
	sub=sample[list]
	sub=sub.drop([0])
	sub[list] = sub[list].apply(pd.to_numeric)
	sub['bin'] = np.where(sub[args.et_pheno] == args.obs, 1, 0)

	if args.crtype==0:

		tmax=sub.loc[sub['bin']==1][args.t_pheno].max()
		sub[args.t_pheno] = np.where((sub[args.et_pheno] != args.obs) & (sub[args.et_pheno] != 0), tmax, sub[args.t_pheno])

	if args.crtype==2:

		sub['bin'] = np.where(sub[args.et_pheno] > 0, 1, 0)

	sub=sub.drop(columns=[args.et_pheno])



	# Check for low variance
	if args.covs:

		print("##############################")
		print("#    CLINICAL ANALYSIS...    #")
		print("##############################\n")
		low_var = pd.DataFrame(sub.var(0) < 10e-5)
		print("\nResults of the low variance (<10e-5) test... (if True these are removed to avoid convergence issues)")
		if args.int:

			print(low_var.loc[args.covs.split(',') + args.int.split(',')])

		if not args.int:

			print(low_var.loc[args.covs.split(',')])

		lvf=low_var[low_var.iloc[:,0] == True]

		if not lvf.empty:

			sub = sub.drop(lvf.index,axis = 1)

		print("\nResults of pre-GWAS multivariable analysis...")

		cph.fit(sub,duration_col=args.t_pheno,event_col='bin')
		cph.print_summary()

	# Open gen file and perform calculation every line
	colNames = ('chr','snp','test','bp','ea','nea','p','info','maf','hwe','beta','se')
	#CHR SNP BP P INFO MAF HWE BETA SE CONV
	print("##############################")
	print("#   BEGIN GWAS ANALYSIS...   #")
	print("##############################\n")
	num_workers = args.thread

	manager = Manager()
	results = manager.list()
	work = manager.Queue(num_workers)

	#start for workers
	pool = []
	for i in range(num_workers):
		p = Process(target=do_work, args=(work, results,sub))
		p.start()
		pool.append(p)
	i=1
	if args.gfile.endswith('gz'):

		with gzip.open(args.gfile,'rt') as f:
			iters = itertools.chain(f, (None,)*num_workers)
			for num_and_line in enumerate(iters):
				gwasprogress()
				i+=1

	else:
		with open(args.gfile,'rt') as f:
			iters = itertools.chain(f, (None,)*num_workers)
			for num_and_line in enumerate(iters):
				gwasprogress()
				i+=1
	for p in pool:
		p.join()

	f_results=pd.concat(results)
	final=f_results.ix[:,colNames]
	final.to_csv(args.ofile + ".out",sep=" ",index=False)

	print("\n\n##############################")
	print("#      END OF ANALYSIS       #")
	print("##############################\n")
