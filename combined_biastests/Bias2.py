# from __future__ import print_function 
import PyFunctions
from PyFunctions import *
import ROOT
import math
import glob
import sys
import csv
import pandas as pd

from array import array
import re
import json
import types
import os
import numpy as np
import matplotlib.pyplot as plt


def num_after_point(x):
    s = str(x)
    if not '.' in s:
        return 0
    return len(s) - s.index('.') - 1


def poisson_errors(obs, alpha=1 - 0.6827):
    """
    Return poisson low and high values for a series of data observations
    """
    from scipy.stats import gamma

    lows = np.nan_to_num(gamma.ppf(alpha / 2, np.array(obs)))
    highs = np.nan_to_num(gamma.ppf(1.0 - alpha / 2, np.array(obs) + 1))
    return lows, highs


def biasplot(channel = 1):
    bkg_envelope = []
    for irow,row in enumerate(T1):
        bgvals_env = [getattr(row, "n_exp_final_binch{}_proc_background_{}".format(channel,i)) for i in range(41,60)]                       
        nbg_env = getattr(row, "n_exp_final_binch{}_proc_background".format(channel))
        bkg_envelope.append(bw*sum(bgvals_env))

    bkg_bern = []
    for irow,row in enumerate(T2):
        bgvals_bern = [getattr(row, "n_exp_final_binch{}_proc_background_{}".format(channel,i)) for i in range(41,60)]                                                                      
        nbg_bern = getattr(row, "n_exp_final_binch{}_proc_background".format(channel))
        bkg_bern.append(bw*sum(bgvals_bern))

    bkg_envelope = np.array(bkg_envelope)
    bkg_bern = np.array(bkg_bern)

    lows, highs = poisson_errors(bkg_envelope, alpha=1 - 0.6827)
    biasvalues = []
    for e in range(len(bkg_envelope)):
        if bkg_envelope[e] > bkg_bern[e]: 
            biasvalues.append((bkg_envelope[e] - bkg_bern[e])/(highs[e]-bkg_envelope[e]))
        else: 
            biasvalues.append((bkg_envelope[e] - bkg_bern[e])/(bkg_envelope[e]-lows[e]))
    
    plt.hist(biasvalues, bins=50)
    plt.ylabel('#toys')
    plt.xlabel('Bias')
    plt.savefig('bias_signalinjection_pvalue/Bias_mass{}_ctau{}_channel{}.png'.format(mass,ctaus[j],channel))
    
    return

masseslist = [0.5,0.525,0.55,0.575,0.6,0.625,0.65,0.675,0.7,0.725,0.75,0.775,0.8,0.825,0.85,0.875,0.9,0.925,0.95,1.25,1.5,1.75,2,2.24,2.4,2.5,2.6,2.76,3,3.25,3.5,3.75,4,4.24,4.52,4.76,5,5.5,6,6.6,7,7.49,8,8.4,9,9.5,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25]

# masseslist = [5.8]

masses = []
for i in range(len(masseslist)):
    if (masseslist[i] > 0.41 and masseslist[i] < 0.515) or (masseslist[i] > 0.495 and masseslist[i] < 0.61) or (masseslist[i] > 0.695 and masseslist[i] < 0.88) or (masseslist[i] > 0.915 and masseslist[i] < 1.13) or (masseslist[i] > 2.81 and masseslist[i] < 4.09) or (masseslist[i] > 8.59 and masseslist[i] < 11.27):
        continue
    masses.append(masseslist[i])


print len(masses)
print masses                                                                                 
                                               
mass = masses[int(sys.argv[1])]

ctaus = [1,10,100]
# ctaus = [1]


mlow = mass*(1-5*0.011)
mhigh = mass*(1+5*0.011)
bw = (mhigh-mlow)/100.

print "Running on mass", mass

os.chdir("mass_{}".format(mass))

for j in range(len(ctaus)):

        print "Looking at ctau----------",ctaus[j], "----------------"

        # os.chdir("./mass_{}".format(mass))
        for file in glob.glob("datacard*allbinsbias.txt"):
                if "ctau{}_".format(ctaus[j]) in file:
                        print(file)
                        cardname = file
        outname = (cardname.split("datacard_")[1]).split(".txt")[0]
        print outname

        # Signal Injection
        ntoys = 50
        # name = "analysis"
        INJ = [0.]


        for i in INJ:

            rmin = 0
            rmax = 20

            
            nbatches = 5
            for batch in range(1,nbatches+1):

                print "running on batch", batch

                name = "0{}_{}_analysis".format(batch,ctaus[j])
                namenew = "0{}_{}_newanalysis".format(batch,ctaus[j])

                pdfindexbern = " --setParameters   pdf_index223=0,pdf_index312=0,pdf_index111=0,pdf_index112=0,pdf_index113=0,pdf_index121=0,pdf_index122=0,pdf_index123=0,pdf_index211=0,pdf_index212=0,pdf_index213=0,pdf_index221=0,pdf_index222=0,pdf_index311=0,pdf_index313=0,pdf_index321=0,pdf_index322=0,pdf_index323=0,pdf_index411=0,pdf_index412=0,pdf_index413=0,pdf_index421=0,pdf_index422=0,pdf_index423=0,pdf_index511=0,pdf_index512=0,pdf_index513=0,pdf_index521=0,pdf_index522=0,pdf_index523=0,pdf_index611=0,pdf_index612=0,pdf_index613=0,pdf_index621=0,pdf_index622=0,pdf_index623=0   --freezeParameters   pdf_index223,pdf_index312,pdf_index111,pdf_index112,pdf_index113,pdf_index121,pdf_index122,pdf_index123,pdf_index211,pdf_index212,pdf_index213,pdf_index221,pdf_index222,pdf_index311,pdf_index313,pdf_index321,pdf_index322,pdf_index323,pdf_index411,pdf_index412,pdf_index413,pdf_index421,pdf_index422,pdf_index423,pdf_index511,pdf_index512,pdf_index513,pdf_index521,pdf_index522,pdf_index523,pdf_index611,pdf_index612,pdf_index613,pdf_index621,pdf_index622,pdf_index623"

                fitcmd0 = "combine -M FitDiagnostics -d %s -m %f -t %d --toysFile higgsCombine%s%f.GenerateOnly.mH%i.%i.root --rMin %f --rMax %f --saveWorkspace -n %s%f --forceRecreateNLL --keepFailures --saveNormalizations   --savePredictionsPerToy  --saveWithUncertainties --cminDefaultMinimizerStrategy=0" %(cardname, mass, ntoys, name, i, mass, batch, rmin, rmax, namenew, i) + pdfindexbern

                fitcmd1 = "combine -M FitDiagnostics -d %s -m %f -t %d --toysFile higgsCombine%s%f.GenerateOnly.mH%.1f.%i.root --rMin %f --rMax %f --saveWorkspace -n %s%f --forceRecreateNLL --keepFailures --saveNormalizations   --savePredictionsPerToy  --saveWithUncertainties --cminDefaultMinimizerStrategy=0" %(cardname, mass, ntoys, name, i, mass, batch, rmin, rmax, namenew, i) + pdfindexbern

                fitcmd2 = "combine -M FitDiagnostics -d %s -m %f -t %d --toysFile higgsCombine%s%f.GenerateOnly.mH%.2f.%i.root --rMin %f --rMax %f --saveWorkspace -n %s%f --forceRecreateNLL --keepFailures --saveNormalizations   --savePredictionsPerToy  --saveWithUncertainties --cminDefaultMinimizerStrategy=0" %(cardname, mass, ntoys, name, i, mass, batch, rmin, rmax, namenew, i) + pdfindexbern

                fitcmd3 = "combine -M FitDiagnostics -d %s -m %f -t %d --toysFile higgsCombine%s%f.GenerateOnly.mH%.3f.%i.root --rMin %f --rMax %f --saveWorkspace -n %s%f --forceRecreateNLL --keepFailures --saveNormalizations   --savePredictionsPerToy  --saveWithUncertainties --cminDefaultMinimizerStrategy=0" %(cardname, mass, ntoys, name, i, mass, batch, rmin, rmax, namenew, i) + pdfindexbern


                if num_after_point(mass) == 0:
                    os.system(fitcmd0)

                elif num_after_point(mass) == 1:
                    os.system(fitcmd1)

                elif num_after_point(mass) == 2:
                    os.system(fitcmd2)

                elif num_after_point(mass) == 3:
                    os.system(fitcmd3)

            

            # T1 = ROOT.TChain("tree_fit_b")
            # T1.Add("fitDiagnostics0*_%i_analysis%f.root" %(ctaus[j],i))


            # T2 = ROOT.TChain("tree_fit_b")
            # T2.Add("fitDiagnostics0*_%i_newanalysis%f.root" %(ctaus[j],i))

            # if not os.path.exists("bias_signalinjection_pvalue"):
            #     os.makedirs("bias_signalinjection_pvalue")


            # for ch in range(2):
            #     biasplot(channel = ch+1)
                

            # channel = 1
            # rows = []
            # for irow,row in enumerate(T1):
            #     # if irow < 4: continue
            #     # r = row.r
            #     bgvals_env = [getattr(row, "n_exp_final_binch{}_proc_background_{}".format(channel,i)) for i in range(41,60)]                                                                   
            #     # bgvals_envsum = bw*sum(bgvals_env)
    
            #     nbg_env = getattr(row, "n_exp_final_binch{}_proc_background".format(channel))
            #     print nbg_env

            # for irow,row in enumerate(T2):
            #     # if irow < 4: continue
            #     # r = row.r
            #     bgvals_bern = [getattr(row, "n_exp_final_binch{}_proc_background_{}".format(channel,i)) for i in range(41,60)]                                                                       
            #     nbg_bern = getattr(row, "n_exp_final_binch{}_proc_background".format(channel))
              
            # print bgvals_env, bgvals_bern
            # print nbg_env, nbg_bern
            # print bw*sum(bgvals_env), bw*sum(bgvals_bern)


os.chdir("./..")


