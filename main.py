from __future__ import division
import numpy as np
import pandas as pd
import collections
import bokeh.io as bio
import bokeh.layouts as bl
import bokeh.models.widgets as bmw
import bokeh.plotting as bp

SZ_MIN = 6
SZ_MAX = 20
SZ_NORM = 9
COLORS = ['#5e4fa2', '#3288bd', '#66c2a5', '#abdda4', '#e6f598', '#ffffbf', '#fee08b', '#fdae61', '#f46d43', '#d53e4f', '#9e0142']*10
C_NORM = "#31AADE"
CHARTTYPES = ['Scatter', 'Line', 'Bar', 'Area']
AGGREGATIONS = ['None', 'Sum']

def create_figures():
    plot_list = []
    if wdg['x'].value == 'None' or wdg['y'].value == 'None':
        return plot_list

    df_filtered = df
    for j, col in enumerate(filterable):
        active = [wdg['filter_'+str(j)].labels[i] for i in wdg['filter_'+str(j)].active]
        if col in continuous:
            active = [int(i) for i in active]
        df_filtered = df_filtered[df_filtered[col].isin(active)]

    if wdg['x_scale'].value != '' and wdg['x'].value in continuous:
        df_filtered[wdg['x'].value] = df_filtered[wdg['x'].value] * float(wdg['x_scale'].value)
    if wdg['y_scale'].value != '' and wdg['y'].value in continuous:
        df_filtered[wdg['y'].value] = df_filtered[wdg['y'].value] * float(wdg['y_scale'].value)

    if wdg['x_group'].value != 'None':
        df_filtered[str(wdg['x_group'].value) + '_' + str(wdg['x'].value)] = df_filtered[wdg['x_group'].value].map(str) + ' ' + df_filtered[wdg['x'].value].map(str)

    if wdg['explode'].value == 'None':
        plot_list.append(create_figure(df_filtered, df_filtered))
    else:
        explode_vals = list(sorted(set(df_filtered[wdg['explode'].value].values)))
        for explode_val in explode_vals:
            df_exploded = df_filtered[df_filtered[wdg['explode'].value].isin([explode_val])]
            plot_list.append(create_figure(df_exploded, df_filtered, explode_val))
    return plot_list

def create_figure(df_exploded, df_filtered, explode_val='None'):
    x_col = wdg['x'].value if wdg['x_group'].value == 'None' else str(wdg['x_group'].value) + '_' + str(wdg['x'].value)

    xs = df_exploded[x_col].values.tolist()
    ys = df_exploded[wdg['y'].value].values.tolist()

    kw = dict()
    if wdg['x_group'].value != 'None':
        kw['x_range'] = []
        unique_groups = sorted(df[wdg['x_group'].value].unique().tolist())
        unique_xs = sorted(df[wdg['x'].value].unique().tolist())
        for i, ugr in enumerate(unique_groups):
            for uxs in unique_xs:
                kw['x_range'].append(str(ugr) + ' ' + str(uxs))
            kw['x_range'].append(' ' * i) #increase number of spaces from one break to the next so that each blank entry is seen as unique

    elif wdg['x'].value in discrete:
        kw['x_range'] = sorted(set(xs))
    if wdg['y'].value in discrete:
        kw['y_range'] = sorted(set(ys))
    if explode_val != 'None':
        kw['title'] = "%s = %s" % (wdg['explode'].value, str(explode_val))

    p = bp.figure(plot_height=int(wdg['plot_height'].value), plot_width=int(wdg['plot_width'].value), tools='pan,box_zoom,reset', **kw)
    adjust_axes(p)

    if wdg['x'].value in discrete or wdg['x_group'].value != 'None':
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
        if wdg['y_agg'].value != 'None' and wdg['y'].value in continuous:
            df_exploded = df_exploded.groupby([x_col], as_index=False, sort=False)[wdg['y'].value].sum()
            xs = df_exploded[x_col].values
            ys = df_exploded[wdg['y'].value].values
            xs, ys = (list(t) for t in zip(*sorted(zip(xs, ys))))
        add_series(p, xs, ys, c, sz)
    else:
        full_series = df_filtered[wdg['series'].value].unique().tolist() #for colors only
        if wdg['y_agg'].value != 'None' and wdg['y'].value in continuous:
            df_exploded = df_exploded.groupby([wdg['series'].value, x_col], as_index=False, sort=False)[wdg['y'].value].sum()
        if wdg['series_stack'].active == 1:
            x_bases = df_exploded[x_col].unique().tolist()
            y_bases = [0]*len(x_bases)
        for i, ser in enumerate(df_exploded[wdg['series'].value].unique()):
            df_series = df_exploded[df_exploded[wdg['series'].value].isin([ser])]
            xs_ser = df_series[x_col].values
            ys_ser = df_series[wdg['y'].value].values
            xs_ser, ys_ser = (list(t) for t in zip(*sorted(zip(xs_ser, ys_ser))))
            c = COLORS[full_series.index(ser)]
            if wdg['series_stack'].active == 0:
                add_series(p, xs_ser, ys_ser, c, sz)
            else:
                y_ser_bases = []
                for j, x in enumerate(xs_ser):
                    base_index = x_bases.index(x)
                    y_ser_bases.append(y_bases[base_index])
                    y_bases[base_index] += ys_ser[j]
                    ys_ser[j] = y_bases[base_index]
                add_series(p, xs_ser, ys_ser, c, sz, y_bases=y_ser_bases)
    return p

def add_series(p, xs, ys, c, sz, y_bases=None):
    alpha = float(wdg['opacity'].value)
    if wdg['chartType'].value == 'Scatter':
        p.circle(x=xs, y=ys, color=c, size=sz, fill_alpha=alpha, line_color=None, line_width=None)
    elif wdg['chartType'].value == 'Line':
        p.line(x=xs, y=ys, color=c, alpha=alpha, line_width=2)
    elif wdg['chartType'].value == 'Bar':
        if y_bases is None: y_bases = [0]*len(ys)
        centers = [(ys[i] + y_bases[i])/2 for i in range(len(ys))]
        heights = [ys[i] - y_bases[i] for i in range(len(ys))]
        p.rect(x=xs, y=centers, height=heights, color=c, fill_alpha=alpha, width=0.5, line_color=None, line_width=None)
    elif wdg['chartType'].value == 'Area':
        if y_bases is None: y_bases = [0]*len(ys)
        xs_around = xs + xs[::-1]
        ys_around = y_bases + ys[::-1]
        p.patch(x=xs_around, y=ys_around, alpha=alpha, fill_color=c, line_color=None, line_width=None)


def build_series_legend():
    series_legend_string = '<div class="legend-header">Series Legend</div><div class="legend-body">'
    if wdg['series'].value != 'None':
        active_list = []
        filter_num = filterable.index(wdg['series'].value)
        for i, val in enumerate(df[wdg['series'].value].unique().tolist()):
            if(i in wdg['filter_'+str(filter_num)].active): active_list.append(val)
        for i, txt in reversed(list(enumerate(active_list))):
            series_legend_string += '<div class="legend-entry"><span class="legend-color" style="background-color:' + str(COLORS[i]) + ';"></span>'
            series_legend_string += '<span class="legend-text">' + str(txt) +'</span></div>'
    series_legend_string += '</div>'
    return series_legend_string

def adjust_axes(p):
    if wdg['x'].value in continuous:
        if wdg['x_min'].value != '': p.x_range.start = float(wdg['x_min'].value)
        if wdg['x_max'].value != '': p.x_range.end = float(wdg['x_max'].value)
    if wdg['y'].value in continuous:
        if wdg['y_min'].value != '': p.y_range.start = float(wdg['y_min'].value)
        if wdg['y_max'].value != '': p.y_range.end = float(wdg['y_max'].value)

def update_data(attr, old, new):
    build_widgets()
    controls.children = wdg.values()
    update()

def update_sel(attr, old, new):
    update()

def update():
    wdg['series_legend'].text = build_series_legend()
    plots.children = create_figures()

def build_widgets():
    global df, columns, discrete, continuous, filterable, seriesable, wdg, uniq

    data_source = wdg['data'].value

    df = pd.read_csv(data_source)
    columns = sorted(df.columns)
    discrete = [x for x in columns if df[x].dtype == object]
    continuous = [x for x in columns if x not in discrete]
    filterable = discrete+[x for x in continuous if df[x].dtype == np.int64 and len(df[x].unique()) < 500]
    seriesable = discrete+[x for x in continuous if df[x].dtype == np.int64 and len(df[x].unique()) < 60]

    wdg.clear()
    uniq += 1

    wdg['data'] = bmw.TextInput(title='Data Source', value=data_source)
    wdg['chartType'] = bmw.Select(title='Chart Type', value=CHARTTYPES[0], options=CHARTTYPES)
    wdg['x'] = bmw.Select(title='X-Axis', value='None', options=['None'] + columns)
    wdg['x_group'] = bmw.Select(title='Group X by', value='None', options=['None'] + seriesable)
    wdg['y'] = bmw.Select(title='Y-Axis', value='None', options=['None'] + columns)
    wdg['y_agg'] = bmw.Select(title='Y-Axis Aggregation', value='None', options=AGGREGATIONS)
    wdg['series'] = bmw.Select(title='Series', value='None', options=['None'] + seriesable)
    wdg['series_stack'] = bmw.RadioButtonGroup(labels=["Unstacked", "Stacked"], active=0)
    wdg['series_legend'] = bmw.Div(text=build_series_legend(), id='series_legend'+str(uniq))
    wdg['size'] = bmw.Select(title='Size', value='None', options=['None'] + continuous)
    wdg['explode'] = bmw.Select(title='Explode', value='None', options=['None'] + seriesable)
    wdg['filters'] = bmw.Div(text='Filters', id='filters'+str(uniq))
    for j, col in enumerate(filterable):
        val_list = [str(i) for i in df[col].unique().tolist()]
        wdg['heading_filter_'+str(j)] = bmw.Div(text=col, id='heading_filter_'+str(j)+'-'+str(uniq))
        wdg['filter_'+str(j)] = bmw.CheckboxGroup(labels=val_list, active=range(len(val_list)), id='filter_'+str(j)+'-'+str(uniq))
    wdg['update'] = bmw.Button(label='Update', button_type='success', id='update-button'+str(uniq))
    wdg['adjustments'] = bmw.Div(text='Plot Adjustments', id='adjust_plots'+str(uniq))
    wdg['plot_width'] = bmw.TextInput(title='Plot Width (px)', value='300', id='adjust_plot_width'+str(uniq))
    wdg['plot_height'] = bmw.TextInput(title='Plot Height (px)', value='300', id='adjust_plot_height'+str(uniq))
    wdg['opacity'] = bmw.TextInput(title='Opacity (0-1)', value='0.6', id='adjust_plot_opacity'+str(uniq))
    wdg['x_scale'] = bmw.TextInput(title='x scale', value='1', id='adjust_plot_x_scale'+str(uniq))
    wdg['x_min'] = bmw.TextInput(title='x min', value='', id='adjust_plot_x_min'+str(uniq))
    wdg['x_max'] = bmw.TextInput(title='x max', value='', id='adjust_plot_x_max'+str(uniq))
    wdg['y_scale'] = bmw.TextInput(title='y scale', value='1', id='adjust_plot_y_scale'+str(uniq))
    wdg['y_min'] = bmw.TextInput(title='y min', value='', id='adjust_plot_y_min'+str(uniq))
    wdg['y_max'] = bmw.TextInput(title='y max', value='', id='adjust_plot_y_max'+str(uniq))

    wdg['data'].on_change('value', update_data)
    wdg['chartType'].on_change('value', update_sel)
    wdg['x'].on_change('value', update_sel)
    wdg['x_group'].on_change('value', update_sel)
    wdg['y'].on_change('value', update_sel)
    wdg['y_agg'].on_change('value', update_sel)
    wdg['series'].on_change('value', update_sel)
    wdg['series_stack'].on_change('active', update_sel)
    wdg['size'].on_change('value', update_sel)
    wdg['explode'].on_change('value', update_sel)
    wdg['plot_width'].on_change('value', update_sel)
    wdg['plot_height'].on_change('value', update_sel)
    wdg['opacity'].on_change('value', update_sel)
    wdg['x_min'].on_change('value', update_sel)
    wdg['x_max'].on_change('value', update_sel)
    wdg['x_scale'].on_change('value', update_sel)
    wdg['y_min'].on_change('value', update_sel)
    wdg['y_max'].on_change('value', update_sel)
    wdg['y_scale'].on_change('value', update_sel)
    wdg['update'].on_click(update)

wdg = collections.OrderedDict()
wdg['data'] = bmw.TextInput(title='Data Source', value='csv/data.csv')
uniq = 0
build_widgets()

controls = bl.widgetbox(wdg.values(), id='widgets_section')
plots = bl.column(create_figures(), id='plots_section')
layout = bl.row(controls, plots, id='layout')

bio.curdoc().add_root(layout)
bio.curdoc().title = "Exploding Pivot Chart Maker"