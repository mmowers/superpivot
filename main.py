#Starting from Bokeh/examples/app/crossfilter
from __future__ import division
import pandas as pd
import collections as col
import bokeh.io as bio
import bokeh.layouts as bl
import bokeh.models.widgets as bmw
import bokeh.plotting as bp

df = pd.read_csv('csv/data.csv')
SZ_MIN = 6
SZ_MAX = 20
SZ_NORM = 9
COLORS = ['#5e4fa2', '#3288bd', '#66c2a5', '#abdda4', '#e6f598', '#ffffbf', '#fee08b', '#fdae61', '#f46d43', '#d53e4f', '#9e0142']
C_NORM = "#31AADE"
chartTypes = ['Scatter', 'Line']

columns = sorted(df.columns)
discrete = [x for x in columns if df[x].dtype == object]
continuous = [x for x in columns if x not in discrete]

def create_figures():
    plot_list = []
    if wdg['explode'].value == 'None':
        plot_list.append(create_figure())
    else:
        explode_vals = list(sorted(set(df[wdg['explode'].value].values)))
        for explode_val in explode_vals:
            plot_list.append(create_figure(explode_val))
    return plot_list

def create_figure(explode_val='None'):
    if explode_val == 'None':
        df_filtered = df
    else:
        df_filtered = df[df[wdg['explode'].value].isin([explode_val])]
    xs = df_filtered[wdg['x'].value].values
    ys = df_filtered[wdg['y'].value].values
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

    p = bp.figure(plot_height=300, plot_width=400, tools='pan,box_zoom,reset', **kw)
    p.xaxis.axis_label = x_title
    p.yaxis.axis_label = y_title

    if wdg['x'].value in discrete:
        p.xaxis.major_label_orientation = pd.np.pi / 4

    sz = SZ_NORM
    if wdg['size'].value != 'None':
        max_val = df_filtered[wdg['size'].value].max()
        min_val = df_filtered[wdg['size'].value].min()
        vals = df_filtered[wdg['size'].value]
        sz = SZ_MIN + (SZ_MAX - SZ_MIN)/(max_val - min_val)*(vals - min_val)
        sz = sz.tolist()

    c = C_NORM
    if wdg['color'].value != 'None':
        groups = pd.cut(df_filtered[wdg['color'].value].values, len(COLORS))
        c = [COLORS[xx] for xx in groups.codes]
    if wdg['chartType'].value == 'Scatter':
        p.circle(x=xs, y=ys, color=c, size=sz, alpha=0.6, hover_alpha=0.5)
    elif wdg['chartType'].value == 'Line':
        p.line(x=xs, y=ys, alpha=0.6, hover_alpha=0.5)
    return p


def update(attr, old, new):
    layout.children[1] = bl.column(create_figures())

wdg = col.OrderedDict((
    ('chartType', bmw.Select(title='Chart Type', value=chartTypes[0], options=chartTypes)),
    ('x', bmw.Select(title='X-Axis', value='mpg', options=columns)),
    ('y', bmw.Select(title='Y-Axis', value='hp', options=columns)),
    ('color', bmw.Select(title='Color', value='None', options=['None'] + continuous)),
    ('size', bmw.Select(title='Size', value='None', options=['None'] + continuous)),
    ('explode', bmw.Select(title='Explode', value='None', options=['None'] + columns)),
))

wdg['chartType'].on_change('value', update)
wdg['x'].on_change('value', update)
wdg['y'].on_change('value', update)
wdg['color'].on_change('value', update)
wdg['size'].on_change('value', update)
wdg['explode'].on_change('value', update)

controls = bl.widgetbox(wdg.values(), width=200)
plots = bl.column(create_figures())
layout = bl.row(controls, plots)

bio.curdoc().add_root(layout)
