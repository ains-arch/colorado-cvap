"""
Data Preparation for CO blockgroup and precinct data
"""

import geopandas as gpd
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pickle
import maup

# Import shapefiles with decennial data

co_bgs_decennial = gpd.read_file("data/CO_block_groups/CO_block_groups.shp")

co_blocks = gpd.read_file("data/CO_blocks_10/CO_blocks_2010.shp")

# Clean ACS data from NHGIS
# * TOTPOP broken down by race and Hispanic origin
# * aggregate VAP counts

co_bgs_acs = pd.read_csv("data/nhgis0028_csv/nhgis0028_ds239_20185_2018_blck_grp.csv")

ga_bgs_acs["GEOID"] = ga_bgs_acs["GISJOIN"].apply(lambda geoid: geoid[1:3] + geoid[4:7] + geoid[8:])

pop_cols_to_rename = {"AJWVE001": "TOTPOP18",
                     "AJWVE003": "NH_WHITE18",
                     "AJWVE004": "NH_BLACK18",
                     "AJWVE005": "NH_AMIN18",
                     "AJWVE006": "NH_ASIAN18",
                     "AJWVE007": "NH_NHPI18",
                     "AJWVE008": "NH_OTHER18",
                     "AJWVE009": "NH_2MORE18",
                     "AJWVE012": "HISP18",
                     "AJWVE013": "H_WHITE18",
                     "AJWVE014": "H_BLACK18",
                     "AJWVE015": "H_AMIN18",
                     "AJWVE016": "H_ASIAN18",
                     "AJWVE017": "H_NHPI18",
                     "AJWVE018": "H_OTHER18",
                     "AJWVE019": "H_2MORE18"}

ga_bgs_acs.rename(columns=pop_cols_to_rename,inplace=True)



u18_cols = (["AJWBE{:03}".format(i) for i in range(3,7)] 
          + ["AJWBE{:03}".format(i) for i in range(27,31)])
vap_cols = (["AJWBE{:03}".format(i) for i in range(7,26)] 
          + ["AJWBE{:03}".format(i) for i in range(31,50)])

## Sanity check that U18 + VAP is equal to TOTPOP for all blocks
(ga_bgs_acs[u18_cols].sum(axis=1) + ga_bgs_acs[vap_cols].sum(axis=1) == ga_bgs_acs.TOTPOP18).all()

ga_bgs_acs["U18_18"] = ga_bgs_acs[u18_cols].sum(axis=1)
ga_bgs_acs["VAP18"] = ga_bgs_acs[vap_cols].sum(axis=1)

ga_bgs_acs.head()

cols_to_drop = ['COUSUBA','PLACEA','CONCITA', 'RES_ONLYA','TRUSTA','AIANHHA','AITSCEA',
                'ANRCA','CBSAA','METDIVA','CSAA','NECTAA','NECTADIVA','CNECTAA', 'UAA',
                'SLDUA','SLDLA','ZCTA5A','SUBMCDA','SDELMA','SDSECA','SDUNIA',]

cols_to_drop.extend(list(ga_bgs_acs.filter(regex='AJW')))

ga_bgs_acs_clean = ga_bgs_acs.drop(columns=cols_to_drop)

ga_bgs_acs_clean.to_csv("data/GA_ACS_VAP_POP_bgs_2014-18.csv")

ga_bgs_acs_clean.columns



# ## Merge ACS with decennial shapefile

ga_bgs_decennial.columns

cols = ['TOTPOP', 'NH_WHITE', 'NH_BLACK', 'NH_AMIN','NH_ASIAN', 'NH_NHPI', 
        'NH_OTHER', 'NH_2MORE', 'HISP', 'H_WHITE', 'H_BLACK', 'H_AMIN', 
        'H_ASIAN', 'H_NHPI', 'H_OTHER', 'H_2MORE', 'VAP', 'HVAP', 'WVAP', 
        'BVAP', 'AMINVAP', 'ASIANVAP', 'NHPIVAP', 'OTHERVAP','2MOREVAP']

ga_bgs_decennial.rename(columns={k: "{}10".format(k) for k in cols}, inplace=True)



ga_bgs = pd.merge(ga_bgs_decennial, ga_bgs_acs_clean, on="GEOID")

ga_bgs.to_file("data/GA_blockgroups_2018/GA_blockgroups_2018.shp")



# ## Merge ACS POP/VAP with CPOP/CVAP data

ga_bgs = gpd.read_file("data/GA_blockgroups_2018/GA_blockgroups_2018.shp")

ga_citz_bgs = gpd.read_file("../shapes/Georgia/GA_block_groups/GA_block_groups_cvap_2018.shp")

citz_cols_to_rename = {'HCVAP': 'HCVAP18',
                     'NHCVAP': 'NHCVAP18',
                     '2MORECVAP': '2MORCVAP18',
                     'AMINCVAP': 'AMINCVAP18',
                     'ASIANCVAP': 'ACVAP18',
                     'BCVAP': 'BCVAP18',
                     'NHPICVAP': 'NHPICVAP18',
                     'WCVAP': 'WCVAP18',
                     'CVAP': 'CVAP18',
                     'HCPOP': 'HCPOP18',
                     'NHCPOP': 'NHCPOP18',
                     '2MORECPOP': '2MORCPOP18',
                     'AMINCPOP': 'AMINCPOP18',
                     'ASIANCPOP': 'ACPOP18',
                     'BCPOP': 'BCPOP18',
                     'NHPICPOP': 'NHPICPOP18',
                     'WCPOP': 'WCPOP18',
                     'CPOP': 'CPOP18'}

ga_citz_bgs.rename(columns=citz_cols_to_rename, inplace=True)

ga_citz_bgs.head()





ga_block_groups = pd.merge(ga_bgs,
         ga_citz_bgs[['GEOID', 'HCVAP18', 'NHCVAP18', '2MORCVAP18', 'AMINCVAP18', 
                      'ACVAP18', 'BCVAP18', 'NHPICVAP18', 'WCVAP18', 'CVAP18', 
                      'HCPOP18', 'NHCPOP18', '2MORCPOP18', 'AMINCPOP18', 'ACPOP18',
                      'BCPOP18','NHPICPOP18', 'WCPOP18','CPOP18']], on="GEOID")

ga_block_groups.to_file("data/GA_blockgroups_2018/GA_blockgroups_all_pops.shp")



ga_block_groups.columns



# ## Maup 2014-18 ACS data to block and then up to (2016/2018) precincts
#
# - Compare weighting by decenial VAP v. weighting by decenial TOTPOP

# ### 2014-18 ACS data on blocks

assignment = maup.assign(ga_blocks, ga_block_groups)

weights_TOTPOP = ga_blocks.TOTPOP / assignment.map(ga_block_groups.TOTPOP10)
weights_VAP = ga_blocks.VAP / assignment.map(ga_block_groups.VAP10)

cols = ['TOTPOP18', 'NH_WHITE18', 'NH_BLACK18', 'NH_AMIN18', 'NH_ASIAN18', 'NH_NHPI18', 
        'NH_OTHER18', 'NH_2MORE18', 'HISP18', 'H_WHITE18', 'H_BLACK18', 'H_AMIN18', 
        'H_ASIAN18', 'H_NHPI18', 'H_OTHER18', 'H_2MORE18', 'U18_18', 'VAP18', 
        'HCVAP18', 'NHCVAP18', '2MORCVAP18', 'AMINCVAP18', 'ACVAP18', 'BCVAP18',
        'NHPICVAP18', 'WCVAP18', 'CVAP18', 'HCPOP18', 'NHCPOP18', '2MORCPOP18',
        'AMINCPOP18', 'ACPOP18', 'BCPOP18', 'NHPICPOP18', 'WCPOP18', 'CPOP18']

prorated_TOTPOP = maup.prorate(assignment, ga_block_groups[cols], weights_TOTPOP)
prorated_VAP = maup.prorate(assignment, ga_block_groups[cols], weights_VAP)

prorated_TOTPOP.head()

prorated_VAP.head()



# ### Aggregate from blocks to precincts

ga_pcts_2016 = gpd.read_file("data/GA_precincts_16/GA_precincts16.shp")

ga_pcts_2018 = gpd.read_file("data/GA_2018_precincts/GA_2018_precincts.shp")

ga_pcts_2016.shape, ga_pcts_2018.shape, 

ga_pcts_2018 = ga_pcts_2018.to_crs(ga_pcts_2016.crs)

ga_blocks = ga_blocks.to_crs(ga_pcts_2016.crs)

assign_pct_2016 = maup.assign(ga_blocks, ga_pcts_2016)
assign_pct_2018 = maup.assign(ga_blocks, ga_pcts_2018)



# +
pct_2016_TOTPOP = prorated_TOTPOP.groupby(assign_pct_2016).sum()
pct_2016_VAP = prorated_VAP.groupby(assign_pct_2016).sum()

pct_2018_TOTPOP = prorated_TOTPOP.groupby(assign_pct_2018).sum()
pct_2018_VAP = prorated_VAP.groupby(assign_pct_2018).sum()
# -

ga_pcts_2016[cols] = pct_2016_VAP

ga_pcts_2018[cols] = pct_2018_VAP

ga_pcts_2016.to_file("data/GA_precincts_all_pops/GA_precincts_2016.shp")

ga_pcts_2018.to_file("data/GA_precincts_all_pops/GA_precincts_2018.shp")

# ## Investigate Error between dissagregation methods

acs_tot_m = pct_2016_TOTPOP[['TOTPOP18', 'NH_WHITE18', 'NH_BLACK18', 'NH_AMIN18', 'NH_ASIAN18', 
                         'NH_NHPI18', 'NH_OTHER18', 'NH_2MORE18', 'HISP18','VAP18']].values
acs_vap_m = pct_2016_VAP[['TOTPOP18', 'NH_WHITE18', 'NH_BLACK18', 'NH_AMIN18', 'NH_ASIAN18', 
                         'NH_NHPI18', 'NH_OTHER18', 'NH_2MORE18', 'HISP18','VAP18']].values
dec_m = ga_pcts_2016[["TOTPOP", "NH_WHITE", "NH_BLACK", "NH_AMIN", "NH_ASIAN", "NH_NHPI", 
                      "NH_OTHER", "NH_2MORE", "HISP", "VAP"]].values

plt.hist(np.abs(pct_2016_TOTPOP.values - pct_2016_VAP.values).sum(axis=1), bins=100,
         alpha=0.5, histtype="stepfilled", label="2016 Precincts")
plt.hist(np.abs(pct_2018_TOTPOP.values - pct_2018_VAP.values).sum(axis=1), bins=100,
         alpha=0.5, histtype="stepfilled", label="2018 Precincts")
plt.title("Total L1 error by precinct over all 36 ACS columns")
plt.legend()
plt.show()

plt.hist(np.abs(acs_tot_m - dec_m).sum(axis=1), bins=100, alpha=0.5, histtype="stepfilled", label="TOTPOP dissaggreation")
plt.hist(np.abs(acs_vap_m - dec_m).sum(axis=1), bins=100, alpha=0.5, histtype="stepfilled", label="VAP dissaggreation")
plt.show()

plt.hist(pct_2016_TOTPOP.TOTPOP18 - ga_pcts_2016["TOTPOP"],bins=100,
         alpha=0.5, histtype="stepfilled", label="TOTPOP dissaggreation")
plt.hist(pct_2016_VAP.TOTPOP18 - ga_pcts_2016["TOTPOP"],bins=100,
        alpha=0.5, histtype="stepfilled", label="VAP dissaggreation")
plt.legend()
plt.title("Change in TOTPOP since 2010 by precinct")
plt.show()



plt.hist((acs_tot_m - dec_m)[:,9],bins=100,
         alpha=0.5, histtype="stepfilled", label="TOTPOP dissaggreation")
plt.hist((acs_vap_m - dec_m)[:,9],bins=100,
        alpha=0.5, histtype="stepfilled", label="VAP dissaggreation")
plt.title("Change in VAP since 2010 by precinct")
plt.legend()
plt.show()



plt.hist((acs_tot_m - dec_m)[:,8], bins=100,
         alpha=0.5, histtype="stepfilled", label="TOTPOP dissaggreation")
plt.hist((acs_vap_m - dec_m)[:,8], bins=100,
        alpha=0.5, histtype="stepfilled", label="VAP dissaggreation")
plt.title("Change in HISP since 2010 by precinct")
plt.legend()
plt.show()

plt.hist((acs_tot_m - dec_m)[:,2], bins=100,
         alpha=0.5, histtype="stepfilled", label="TOTPOP dissaggreation")
plt.hist((acs_vap_m - dec_m)[:,2], bins=100,
        alpha=0.5, histtype="stepfilled", label="VAP dissaggreation")
plt.title("Change in NH_BLACK since 2010 by precinct")
plt.legend()
plt.show()

plt.hist((acs_tot_m - dec_m)[:,1], bins=100,
         alpha=0.5, histtype="stepfilled", label="TOTPOP dissaggreation")
plt.hist((acs_vap_m - dec_m)[:,1], bins=100,
        alpha=0.5, histtype="stepfilled", label="VAP dissaggreation")
plt.title("Change in NH_WHITE since 2010 by precinct")
plt.legend()
plt.show()

df_2016 = (pct_2016_TOTPOP - pct_2016_VAP).stack().reset_index().set_index("level_0").rename(columns={"level_1": "var", 0: "error"})
df_2018 = (pct_2018_TOTPOP - pct_2018_VAP).stack().reset_index().set_index("level_0").rename(columns={"level_1": "var", 0: "error"})
df = df_2016.assign(year=2016).append(df_2018.assign(year=2018))

plt.figure(figsize=(20,10))
sns.boxplot(data=df, y="error", x="var", hue="year", whis=(1,99), fliersize=2,
            order=['TOTPOP18', 'VAP18', 'CPOP18' ,'CVAP18', 'NH_BLACK18', 'HISP18', 'NH_WHITE18',
                   'BCPOP18', "HCPOP18", "WCPOP18",'BCVAP18', 'HCVAP18', 'WCVAP18'])
plt.show()

plt.figure(figsize=(20,10))
sns.violinplot(data=df, y="error", x="var", hue="year", split=True, scale="count",palette="Set2",
            order=['TOTPOP18', 'VAP18', 'CPOP18' ,'CVAP18', 'NH_BLACK18', 'HISP18', 'NH_WHITE18',
                   'BCPOP18', "HCPOP18", "WCPOP18",'BCVAP18', 'HCVAP18', 'WCVAP18'], inner="quartile")
plt.show()

(pct_2016_TOTPOP - pct_2016_VAP).query("TOTPOP18 > 100 or TOTPOP18 < -100")

(pct_2018_TOTPOP - pct_2018_VAP).query("TOTPOP18 > 100 or TOTPOP18 < -100")

df.query("error > 450")

df.query("error < -600")




