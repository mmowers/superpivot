#Starting from Bokeh/examples/app/crossfilter
from __future__ import division
import numpy as np
import pandas as pd
import collections
import bokeh.io as bio
import bokeh.layouts as bl
import bokeh.models.widgets as bmw
import bokeh.plotting as bp

df = pd.read_csv('csv/data.csv')
SZ_MIN = 6
SZ_MAX = 20
SZ_NORM = 9
COLORS = ['#5e4fa2', '#3288bd', '#66c2a5', '#abdda4', '#e6f598', '#ffffbf', '#fee08b', '#fdae61', '#f46d43', '#d53e4f', '#9e0142']*5
C_NORM = "#31AADE"
CHARTTYPES = ['Scatter', 'Line']

columns = sorted(df.columns)
discrete = [x for x in columns if df[x].dtype == object]
continuous = [x for x in columns if x not in discrete]
filterable = discrete+[x for x in continuous if df[x].dtype == np.int64 and len(df[x].unique()) < 500]

def create_figures():
    df_filtered = df
    for col in filterable:
        active = [wdg[col].labels[i] for i in wdg[col].active]
        if col in continuous:
            active = [int(i) for i in active]
        df_filtered = df_filtered[df_filtered[col].isin(active)]

    plot_list = []
    if wdg['explode'].value == 'None':
        plot_list.append(create_figure(df_filtered))
    else:
        explode_vals = list(sorted(set(df_filtered[wdg['explode'].value].values)))
        for explode_val in explode_vals:
            df_exploded = df_filtered[df_filtered[wdg['explode'].value].isin([explode_val])]
            plot_list.append(create_figure(df_exploded, explode_val))
    return plot_list

def create_figure(df_exploded, explode_val='None'):
    xs = df_exploded[wdg['x'].value].values
    ys = df_exploded[wdg['y'].value].values
    x_title = wdg['x'].value.title()
    y_title = wdg['y'].value.title()

    kw = dict()
    if wdg['x'].value in discrete:
        kw['x_range'] = sorted(set(xs))
    if wdg['y'].value in discrete:
        kw['y_range'] = sorted(set(ys))
    kw['title'] = "%s vs %s" % (x_title, y_title)
    if explode_val != 'None':
        kw['title'] = kw['title'] + ", " + wdg['explode'].value + "=" + str(explode_val)

    p = bp.figure(plot_height=int(wdg['plot_height'].value), plot_width=int(wdg['plot_width'].value), tools='pan,box_zoom,reset', **kw)
    p.xaxis.axis_label = x_title
    p.yaxis.axis_label = y_title

    if wdg['x'].value in discrete:
        p.xaxis.major_label_orientation = pd.np.pi / 4

    sz = SZ_NORM
    if wdg['size'].value != 'None':
        max_val = df_exploded[wdg['size'].value].max()
        min_val = df_exploded[wdg['size'].value].min()
        vals = df_exploded[wdg['size'].value]
        sz = SZ_MIN + (SZ_MAX - SZ_MIN)/(max_val - min_val)*(vals - min_val)
        sz = sz.tolist()

    c = C_NORM
    if wdg['series'].value == 'None':
        add_series(p, xs, ys, c, sz)
    else:
        for i, ser in enumerate(df_exploded[wdg['series'].value].unique()):
            df_series = df_exploded[df_exploded[wdg['series'].value].isin([ser])]
            xs_ser = df_series[wdg['x'].value].values
            ys_ser = df_series[wdg['y'].value].values
            c = COLORS[i]
            add_series(p, xs_ser, ys_ser, c, sz)
    return p

def add_series(p, xs, ys, c, sz):
    if wdg['chartType'].value == 'Scatter':
        p.circle(x=xs, y=ys, color=c, size=sz, alpha=0.6, hover_alpha=1)
    elif wdg['chartType'].value == 'Line':
        p.line(x=xs, y=ys, color=c, alpha=0.6, hover_alpha=1)

def update_sel(attr, old, new):
    update()

def update():
    plots.children = create_figures()

wdg = collections.OrderedDict((
    ('chartType', bmw.Select(title='Chart Type', value=CHARTTYPES[0], options=CHARTTYPES, name='hithere')),
    ('x', bmw.Select(title='X-Axis', value=columns[0], options=columns)),
    ('y', bmw.Select(title='Y-Axis', value=columns[1], options=columns)),
    ('series', bmw.Select(title='Series', value='None', options=['None'] + columns)),
    ('size', bmw.Select(title='Size', value='None', options=['None'] + continuous)),
    ('explode', bmw.Select(title='Explode', value='None', options=['None'] + columns)),
))
wdg['filters'] = bmw.Div(text='Filters', id='filters')
for col in filterable:
    val_list = [str(i) for i in df[col].unique().tolist()]
    wdg[col+'_heading'] = bmw.Div(text=col, id=col+'_filter_heading')
    wdg[col] = bmw.CheckboxGroup(labels=val_list, active=range(len(val_list)), id=col+'_dropboxes')

wdg['adjustments'] = bmw.Div(text='Plot Adjustments', id='adjust_plots')
wdg['plot_width'] = bmw.TextInput(title='Plot Width (px)', value='300', id='plot_width_adjust')
wdg['plot_height'] = bmw.TextInput(title='Plot Height (px)', value='300', id='plot_height_adjust')
wdg['update'] = bmw.Button(label='Update', button_type='success', id='update-button')

wdg['chartType'].on_change('value', update_sel)
wdg['x'].on_change('value', update_sel)
wdg['y'].on_change('value', update_sel)
wdg['series'].on_change('value', update_sel)
wdg['size'].on_change('value', update_sel)
wdg['explode'].on_change('value', update_sel)
wdg['plot_width'].on_change('value', update_sel)
wdg['plot_height'].on_change('value', update_sel)
wdg['update'].on_click(update)

controls = bl.widgetbox(wdg.values(), id='widgets_section')
plots = bl.column(create_figures(), id='plots_section')
layout = bl.row(controls, plots, id='layout')

bio.curdoc().add_root(layout)
bio.curdoc().title = "Exploding Pivot Chart Maker"