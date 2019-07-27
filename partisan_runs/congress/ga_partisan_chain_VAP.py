
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 11 15:06:44 2019

@author: Katherine
"""

# Imports

import os

from gerrychain import Graph, GeographicPartition, Partition, Election, accept
from gerrychain.updaters import Tally, cut_edges
import geopandas as gpd
import numpy as np
from gerrychain.random import random
import copy

from gerrychain import MarkovChain
from gerrychain.constraints import single_flip_contiguous
from gerrychain.proposals import propose_random_flip, recom
from gerrychain.accept import always_accept
from gerrychain.metrics import polsby_popper
from gerrychain import constraints
from gerrychain.constraints import no_vanishing_districts

from collections import defaultdict, Counter
from itertools import combinations_with_replacement


import matplotlib.pyplot as plt

import networkx as nx

import pandas

import math

#from IPython.display import clear_output

from functools import partial

from gerrychain.tree import recursive_tree_part
# setup -- SLOW

#shapefile = "https://github.com/mggg-states/NC-shapefiles/raw/master/NC_VTD.zip"
shapefile = "./maupped_ga_2016_precincts/maupped_ga_2016_precincts.shp"
df = gpd.read_file(shapefile)

#county_col = "County"
#pop_col = "PL10AA_TOT"
#uid = "VTD"
variables = ["ID","FIPS2", "PRES16D", "PRES16R", "PRES16L", "SEN16D", "SEN16R", "SEN16L",]
for x in df.columns:
   if x in variables:
       df[x] = df[x].astype(int)
#county_col = "COUNTYFP10"
pop_col = "TOTPOP"

df["CPOP"] = df["TOTPOP"]-df["NCPOP"]
ccol = "CPOP"
uid = "ID"
VAP = "VAP"
num_districts = 14



graph = Graph.from_geodataframe(df,ignore_errors=True)
graph.add_data(df,list(df))
graph = nx.relabel_nodes(graph, df[uid])

elections = [
        Election("PRES16",{"Democratic": "PRES16D","Republican":"PRES16R" }),
        Election("SEN16",{"Democratic": "SEN16D","Republican":"SEN16R" })]

#my_updaters = {"population" : updaters.Tally("TOTPOP", alias="population")}
my_updaters = {"population" : Tally(pop_col, alias="population"), "VAP": Tally(VAP, alias="VAP"), "cpop": Tally(ccol, alias="cpop"),
            "cut_edges": cut_edges}
election_updaters = {election.name: election for election in elections}
my_updaters.update(election_updaters)

tot_pop_col = 0
tot_ccol = 0
tot_VAP = 0
#for tallying over VAP:
for n in graph.nodes():
    graph.node[n][VAP] = int(graph.node[n][VAP])
    tot_VAP += graph.node[n][VAP]

cddict = recursive_tree_part(graph,range(num_districts),tot_VAP/num_districts,VAP,0.01,1)

starting_partition = Partition(graph,assignment=cddict,updaters=my_updaters)

#-------------------------------------------------------------------------------------------

#CHAIN FOR TOTPOP
proposal = partial(
        recom, pop_col=VAP, pop_target=tot_VAP/num_districts, epsilon=0.02, node_repeats=1
   )

compactness_bound = constraints.UpperBound(
        lambda p: len(p["cut_edges"]), 2 * len(starting_partition["cut_edges"])
    )

chain = MarkovChain(
        proposal,
         constraints=[
            constraints.within_percent_of_ideal_population(starting_partition, 0.12),compactness_bound
          #constraints.single_flip_contiguous#no_more_discontiguous
        ],
        accept=accept.always_accept,
        initial_state=starting_partition,
        total_steps=10000
    )


t = 0
SENwins_list = []
PRESwins_list = []
cutedges_list = []
for part in chain:
    SENwins_list.append(part["SEN16"].wins("Republican"))
    PRESwins_list.append(part["PRES16"].wins("Republican"))
    cutedges_list.append(len(part["cut_edges"]))
    t += 1
    if t % 100 == 0:
        print("finished chain " + str(t))
        

#CHANGE
plt.figure()
plt.hist(SENwins_list)
plt.title("Histogram of Republican Seats (based on Senate 2016)")
plt.xlabel("Seats")
#plt.savefig("PA_hist_symmetric_entropy_5000.png")
plt.show()

plt.figure()
plt.hist(PRESwins_list)
plt.title("Histogram of Republican Seats (based on Pres 2016)")
plt.xlabel("Seats")
#plt.savefig("PA_hist_symmetric_entropy_5000.png")
plt.show()

plt.figure()
plt.hist(cutedges_list)
plt.title("Histogram of Cut Edges")
plt.xlabel("Cut Edges")
#plt.savefig("PA_hist_symmetric_entropy_5000.png")
plt.show()

