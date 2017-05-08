'''
ReEDS-specific functions and variables.
'''
from __future__ import division
import os
import math
import json
import pandas as pd
import collections
import bokeh.io as bio
import bokeh.layouts as bl
import bokeh.models.widgets as bmw
import bokeh.models.sources as bms
import bokeh.models.tools as bmt
import bokeh.plotting as bp
import datetime
import six.moves.urllib.parse as urlp
import gdxl

this_dir_path = os.path.dirname(os.path.realpath(__file__))
inflation_mult = 1.2547221 #2004$ to 2015$

#Preprocess functions
def scale_column(df, **kw):
    df[kw['column']] = df[kw['column']] * kw['scale_factor']
    return df

def scale_column_filtered(df, **kw):
    cond = df[kw['by_column']].isin(kw['by_vals'])
    df.loc[cond, kw['change_column']] = df.loc[cond, kw['change_column']] * kw['scale_factor']
    return df

def discount_costs(df, **kw):
    #inner join the cost_cat_type.csv table to get types of costs (Capital, Operation)
    cost_cat_type = pd.read_csv(this_dir_path + '/csv/cost_cat_type.csv')
    df = pd.merge(left=df, right=cost_cat_type, on='cost_cat', sort=False)
    #make new column that is the pv multiplier
    df['pv_mult'] = df.apply(lambda x: get_pv_mult(int(x['year']), x['type']), axis=1)
    df['Discounted Cost (2015$)'] = df['Cost (2015$)'] * df['pv_mult']
    return df

#Return present value multiplier
def get_pv_mult(year, type, dinvest=0.054439024, dsocial=0.03, lifetime=20, refyear=2017, lastyear=2050):
    if type == "Operation":
        pv_mult = 1 / (1 + dsocial)**(year - refyear)
    elif type == "Capital":
        pv_mult = CRF(dinvest, lifetime) / CRF(dinvest, min(lifetime, lastyear + 1 - year)) * 1 / (1 + dsocial)**(year - refyear)
    return pv_mult

#Capital recovery factor
def CRF(i,n):
    return i/(1-(1/(1+i)**n))

def pre_elec_price(df, **kw):
    df = df.pivot_table(index=['n','year'], columns='elem', values='value').reset_index()
    df.drop(['t2','t4','t5','t6','t7','t8','t9','t10','t11','t12','t13','t14','t15','t16'], axis='columns', inplace=True)
    df.columns.name = None
    df['t3'] = df['t3'] * inflation_mult
    df['t17'] = df['t17'] * inflation_mult
    df.rename(columns={'t1': 'load', 't3': 'Reg Price (2015$/MWh)', 't17': 'Comp Price (2015$/MWh)'}, inplace=True)
    return df

def pre_elec_price_components(dfs, **kw):
    df_load = dfs['load'][dfs['load']['type'] == 'reqt']
    df_load = df_load.drop('type', 1)
    df_main = dfs['main']
    df_main['value'] = df_main['value'] * inflation_mult
    df = pd.merge(left=df_main, right=df_load, how='inner', on=['n','year'], sort=False)
    return df

def add_huc_reg(df, **kw):
    huc_map = pd.read_csv(this_dir_path + '/csv/huc_2_ratios.csv')
    df = pd.merge(left=df, right=huc_map, how='outer', on='n', sort=False)
    df['value'] = df['value'] * df['pca_huc_ratio']
    df = df.drop('pca_huc_ratio', 1)
    df = df.drop('huc_pca_ratio', 1)
    return df

#Results metadata
results_meta = collections.OrderedDict((
    ('Capacity (GW)',
        {'file': 'CONVqn.gdx',
        'param': 'CONVqnallyears',
        'columns': ['tech', 'n', 'year', 'Capacity (GW)'],
        'preprocess': [
            {'func': scale_column, 'args': {'scale_factor': .001, 'column': 'Capacity (GW)'}},
            {'func': scale_column_filtered, 'args': {'by_column': 'tech', 'by_vals': ['UPV', 'DUPV', 'distPV'], 'change_column': 'Capacity (GW)', 'scale_factor': 1/1.1}},
        ],
        'presets': collections.OrderedDict((
            ('Stacked Capacity',{'x':'year','y':'Capacity (GW)', 'y_agg':'Sum','series':'tech', 'explode': 'scenario','chart_type':'Area'}),
            ('Tech Compare',{'x':'year','y':'Capacity (GW)', 'y_agg':'Sum','series':'scenario', 'explode': 'tech','chart_type':'Line'}),
        )),
        }
    ),
    ('New Capacity (GW)',
        {'file': 'CONVqn.gdx',
        'param': 'CONVqn_newallyears',
        'columns': ['tech', 'n', 'year', 'Capacity (GW)'],
        'preprocess': [
            {'func': scale_column, 'args': {'scale_factor': .001, 'column': 'Capacity (GW)'}},
            {'func': scale_column_filtered, 'args': {'by_column': 'tech', 'by_vals': ['UPV', 'DUPV', 'distPV'], 'change_column': 'Capacity (GW)', 'scale_factor': 1/1.1}},
        ],
        'presets': collections.OrderedDict((
            ('Stacked Capacity',{'x':'year','y':'Capacity (GW)', 'y_agg':'Sum','series':'tech', 'explode': 'scenario','chart_type':'Bar', 'bar_width':'1.5'}),
            ('Tech Compare',{'x':'year','y':'Capacity (GW)', 'y_agg':'Sum','series':'scenario', 'explode': 'tech','chart_type':'Line'}),
        )),
        }
    ),
    ('Generation (TWh)',
        {'file': 'CONVqn.gdx',
        'param': 'CONVqmnallyears',
        'columns': ['tech', 'n', 'year', 'Generation (TWh)'],
        'preprocess': [
            {'func': scale_column, 'args': {'scale_factor': 0.000001, 'column': 'Generation (TWh)'}},
        ],
        'presets': collections.OrderedDict((
            ('Stacked Gen',{'x':'year','y':'Generation (TWh)', 'y_agg':'Sum','series':'tech', 'explode': 'scenario','chart_type':'Area'}),
            ('Tech Compare',{'x':'year','y':'Generation (TWh)', 'y_agg':'Sum','series':'scenario', 'explode': 'tech','chart_type':'Line'}),
        )),
        }
    ),
    ('Emissions, Fuel, Prices',
        {'file': 'Reporting.gdx',
        'param': 'AnnualReport',
        'columns': ['n', 'year', 'type', 'value'],
        'presets': collections.OrderedDict((
            ('Scenario Compare',{'x':'year','y':'value', 'y_agg':'Sum','series':'scenario', 'explode': 'type','chart_type':'Line'}),
        )),
        }
    ),
    ('System Cost',
        {'file': 'systemcost.gdx',
        'param': 'aSystemCost_ba',
        'columns': ['cost_cat', 'n', 'year', 'Cost (2015$)'],
        'preprocess': [
            {'func': scale_column, 'args': {'scale_factor': inflation_mult, 'column': 'Cost (2015$)'}},
            {'func': discount_costs, 'args': {}},
        ],
        'presets': collections.OrderedDict((
            ('Stacked (filter years!)',{'x':'scenario','y':'Discounted Cost (2015$)', 'y_agg':'Sum','series':'cost_cat', 'explode': 'None','chart_type':'Bar'}),
        )),
        }
    ),
    ('Gen by m',
        {'file': 'CONVqn.gdx',
        'param': 'CONVqmnallm',
        'columns': ['tech', 'n', 'year', 'm', 'Gen'],
        'presets': collections.OrderedDict((
            ('Stacked Gen by m',{'x':'m','y':'Gen', 'y_agg':'Sum','series':'tech', 'explode': 'scenario','chart_type':'Bar'}),
        )),
        }
    ),
    ('Electricity Price',
        {'file': 'Reporting.gdx',
        'param': 'ElecPriceOut',
        'columns': ['n', 'year', 'elem', 'value'],
        'preprocess': [
            {'func': pre_elec_price, 'args': {}},
        ],
        'presets': collections.OrderedDict((
            ('National Competitive',{'x':'year','y':'Comp Price (2015$/MWh)', 'y_agg':'Weighted Ave', 'y_weight':'load', 'series':'scenario', 'explode': 'None', 'chart_type':'Line'}),
            ('Census Competitive',{'x':'year','y':'Comp Price (2015$/MWh)', 'y_agg':'Weighted Ave', 'y_weight':'load', 'series':'scenario', 'explode': 'censusregions', 'chart_type':'Line'}),
            ('National Regulated',{'x':'year','y':'Reg Price (2015$/MWh)', 'y_agg':'Weighted Ave', 'y_weight':'load', 'series':'scenario', 'explode': 'None', 'chart_type':'Line'}),
            ('Census Regulated',{'x':'year','y':'Reg Price (2015$/MWh)', 'y_agg':'Weighted Ave', 'y_weight':'load', 'series':'scenario', 'explode': 'censusregions', 'chart_type':'Line'}),
        )),
        }
    ),
    ('Elec Price Components',
        {'sources': [
            {'name': 'load', 'file': 'CONVqn.gdx', 'param': 'CONVqmnallyears', 'columns': ['type', 'n', 'year', 'load']},
            {'name': 'main', 'file': 'MarginalPrices.gdx', 'param': 'wpmarg_BA_ann_allyrs', 'columns': ['n', 'elec_comp_type','year', 'value']},
        ],
        'preprocess': [
            {'func': pre_elec_price_components, 'args': {}},
        ],
        'presets': collections.OrderedDict((
            ('Stacked Components',{'x':'year','y':'value', 'y_agg':'Weighted Ave', 'y_weight':'load', 'series':'elec_comp_type', 'explode': 'scenario', 'chart_type':'Bar'}),
            ('Scenario Compare',{'x':'year','y':'value', 'y_agg':'Weighted Ave', 'y_weight':'load', 'series':'scenario', 'explode': 'elec_comp_type', 'chart_type':'Line'}),
        )),
        }
    ),
    ('Water Withdrawals (Bil Gals)',
        {'file': "water_output.gdx",
        'param': 'WaterWqctnallyears',
        'columns': ["tech", "cool_tech", "n", "year", "value"],
        'preprocess': [
            {'func': scale_column, 'args': {'scale_factor': 0.001, 'column': 'value'}},
            {'func': add_huc_reg, 'args': {}},
        ],
        'presets': collections.OrderedDict((
            ('National',{'x':'year','y':'value', 'y_agg':'Sum', 'series':'scenario', 'chart_type':'Line'}),
        )),
        }
    ),
    ('Water Consumption (Bil Gals)',
        {'file': "water_output.gdx",
        'param': 'WaterCqctnallyears',
        'columns': ["tech", "cool_tech", "n", "year", "value"],
        'preprocess': [
            {'func': scale_column, 'args': {'scale_factor': 0.001, 'column': 'value'}},
            {'func': add_huc_reg, 'args': {}},
        ],
        'presets': collections.OrderedDict((
            ('National',{'x':'year','y':'value', 'y_agg':'Sum', 'series':'scenario', 'chart_type':'Line'}),
        )),
        }
    ),
    ('JEDI Wind Cost',
        {'file': "JediWind.gdx",
        'param': 'JediWindCost',
        'columns': ["category", "TRG", "windtype", "n", "year","Cost (2015$)"],
        'preprocess': [
            {'func': scale_column, 'args': {'scale_factor': inflation_mult, 'column': 'Cost (2015$)'}},
        ],
        'presets': collections.OrderedDict((
            ('Scenario Compare',{'x':'year','y':'Cost (2015$)', 'y_agg':'Sum', 'series':'scenario', 'explode':'category', 'chart_type':'Line'}),
        )),
        }
    ),
    ('JEDI Wind Capacity',
        {'file': "JediWind.gdx",
        'param': 'JediWindBuilds',
        'columns': ["category", "TRG", "windtype", "n", "year","Capacity (MW)"],
        'presets': collections.OrderedDict((
            ('Scenario Compare',{'x':'year','y':'Capacity (MW)', 'y_agg':'Sum', 'series':'scenario', 'explode':'category', 'chart_type':'Line'}),
        )),
        }
    ),
    ('wat_access',
        {'file': "water_output.gdx",
        'param': 'WatAccessallyears',
        'columns': ["n", "class", "year", "value"],
        }
    ),
    ('<Old> System Cost',
        {'file': 'Reporting.gdx',
        'param': 'aSystemCost',
        'columns': ['cost_cat', 'year', 'Cost (2015$)'],
        'preprocess': [
            {'func': scale_column, 'args': {'scale_factor': inflation_mult, 'column': 'Cost (2015$)'}},
            {'func': discount_costs, 'args': {}},
        ],
        }
    ),
    ('cap_wind',
        {'file': 'CONVqn.gdx',
        'param': 'Windiallc',
        'columns': ["windtype", "i", "year", "class", "value"],
        }
    ),
    ('cap_wind_nrr',
        {'file': 'CONVqn.gdx',
        'param': 'WR2GOallyears',
        'columns': ["i",  "class",  "windtype", "bin","year", "value"],
        }
    ),
    ('cap_csp_nrr',
        {'file': 'CONVqn.gdx',
        'param': 'CSP2GOallyears',
        'columns': ["i",  "cspclass", "bin","year", "value"],
        }
    ),
    ('cap_upv_nrr',
        {'file': "CONVqn.gdx",
        'param': 'UPVR2GOallyears',
        'columns': ["n",  "upvclass", "bin","year", "value"],
        }
    ),
    ('cap_dupv_nrr',
        {'file': "CONVqn.gdx",
        'param': 'DUPVR2GOallyears',
        'columns': ["n",  "dupvclass", "bin","year", "value"],
        }
    ),
    ('op_cap',
        {'file': "CONVqn.gdx",
        'param': 'OperCONVqnallyears',
        'columns': ["tech", "n", "year", "value"],
        }
    ),
    ('retire',
        {'file': "CONVqn.gdx",
        'param': 'Retireqnallyears',
        'columns': ["tech", "n", "year", "value"],
        }
    ),
    ('rebuild',
        {'file': "CONVqn.gdx",
        'param': 'Rebuildqnallyears',
        'columns': ["tech", "n", "year", "value"],
        }
    ),
    ('upgrade',
        {'file': "CONVqn.gdx",
        'param': 'Upgradeqnallyears',
        'columns': ["techold", "technew", "n", "year", "value"],
        }
    ),
    ('hydb',
        {'file': "CONVqn.gdx",
        'param': 'HydBin_allyrs',
        'columns': ["cat", "class", "n", "year", "value"],
        }
    ),
    ('pshb',
        {'file': "CONVqn.gdx",
        'param': 'PHSBIN_allyrs',
        'columns': ["class", "n", "year", "value"],
        }
    ),
    ('plan_res',
        {'file': "Reporting.gdx",
        'param': 'PlanRes',
        'columns': ["tech", "n", "year", "m", "value"],
        }
    ),
    ('oper_res',
        {'file': "Reporting.gdx",
        'param': 'OperRes',
        'columns': ["tech", "n", "year", "m", "value"],
        }
    ),
    ('vrre',
        {'file': "Reporting.gdx",
        'param': 'VRREOut',
        'columns': ["n","m","year","tech","type","value"],
        }
    ),
    ('trans',
        {'file': "Reporting.gdx",
        'param': 'Transmission',
        'columns': ["n", "n2", "year", "type", "value"],
        }
    ),
    ('annual_rep',
        {'file': "Reporting.gdx",
        'param': 'AnnualReport',
        'columns': ["n", "year", "type", "value"],
        }
    ),
    ('annual_rep',
        {'file': "Reporting.gdx",
        'param': 'AnnualReport',
        'columns': ["n", "year", "type", "value"],
        }
    ),
    ('fuel_cost',
        {'file': "Reporting.gdx",
        'param': 'fuelcost',
        'columns': ["year", "country", "type", "value"],
        }
    ),
    ('reg_fuel_cost',
        {'file': "Reporting.gdx",
        'param': 'reg_fuelcost',
        'columns': ["nerc", "year", "type", "value"],
        }
    ),
    ('switches',
        {'file': "Reporting.gdx",
        'param': 'ReportSwitches',
        'columns': ["class", "switch", "value", "ignore"],
        }
    ),
    ('st_rps',
        {'file': "StRPSoutputs.gdx",
        'param': 'StRPSoutput',
        'columns': ["tech", "st", "year", "value"],
        }
    ),
    ('st_rps_mar',
        {'file': "StRPSoutputs.gdx",
        'param': 'StRPSmarginalout',
        'columns': ["st", "year", "const", "value"],
        }
    ),
    ('st_rps_rec',
        {'file': "StRPSoutputs.gdx",
        'param': 'RECallyears',
        'columns': ["n", "st2", "tech", "year", "value"],
        }
    ),
    ('ac_flow',
        {'file': "Transmission.gdx",
        'param': 'TransFlowAC',
        'columns': ["n", "n2", "year", "m", "value"],
        }
    ),
    ('dc_flow',
        {'file': "Transmission.gdx",
        'param': 'TransFlowDC',
        'columns': ["n", "n2", "year", "m", "value"],
        }
    ),
    ('cont_flow',
        {'file': "Transmission.gdx",
        'param': 'ContractFlow',
        'columns': ["n", "n2", "year", "m", "value"],
        }
    ),
    ('obj_fnc',
        {'file': "z.gdx",
        'param': 'z_allyrs',
        'columns': ["year", "value"],
        }
    ),
))

#Columns metadata.
columns_meta = {
    'tech':{
        'type': 'string',
        'map': this_dir_path + '/csv/tech_map.csv',
        'style': this_dir_path + '/csv/tech_style.csv',
    },
    'n':{
        'type': 'string',
        'join': this_dir_path + '/csv/hierarchy.csv',
    },
    'huc_2':{
        'type': 'string',
        'join': this_dir_path + '/csv/huc_join.csv',
    },
    'huc_4':{
        'type': 'string',
        'join': this_dir_path + '/csv/huc_join.csv',
    },
    'huc_6':{
        'type': 'string',
        'join': this_dir_path + '/csv/huc_join.csv',
    },
    'huc_8':{
        'type': 'string',
        'join': this_dir_path + '/csv/huc_join.csv',
    },
    'year':{
        'type': 'number',
        'filterable': True,
        'seriesable': True,
    },
    'm':{
        'type': 'string',
        'style': this_dir_path + '/csv/m_style.csv',
    },
    'cost_cat':{
        'type': 'string',
        'map': this_dir_path + '/csv/cost_cat_map.csv',
        'style': this_dir_path + '/csv/cost_cat_style.csv',
    },
}