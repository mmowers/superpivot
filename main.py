from __future__ import division
import math
import json
import re
import numpy as np
import pandas as pd
import collections
import bokeh.io as bio
import bokeh.layouts as bl
import bokeh.models as bm
import bokeh.models.widgets as bmw
import bokeh.models.sources as bms
import bokeh.models.tools as bmt
import bokeh.plotting as bp
import datetime
try:
    import urllib.parse as urlp
except ImportError:
    import urllib as urlp

PLOT_WIDTH = 300
PLOT_HEIGHT = 300
PLOT_FONT_SIZE = 10
PLOT_AXIS_LABEL_SIZE = 8
PLOT_LABEL_ORIENTATION = 45
OPACITY = 0.6
X_SCALE = 1
Y_SCALE = 1
CIRCLE_SIZE = 9
BAR_WIDTH = 0.5
LINE_WIDTH = 2
COLORS = ['#5e4fa2', '#3288bd', '#66c2a5', '#abdda4', '#e6f598', '#fee08b', '#fdae61', '#f46d43', '#d53e4f', '#9e0142']*10
C_NORM = "#31AADE"
CHARTTYPES = ['Dot', 'Line', 'Bar', 'Area']
AGGREGATIONS = ['None', 'Sum']

def get_data():
    global df, columns, discrete, continuous, filterable, seriesable
    data_source = wdg['data'].value
    df = pd.read_csv(data_source)
    columns = sorted(df.columns)
    discrete = [x for x in columns if df[x].dtype == object]
    continuous = [x for x in columns if x not in discrete]
    filterable = discrete+[x for x in continuous if len(df[x].unique()) < 500]
    seriesable = discrete+[x for x in continuous if len(df[x].unique()) < 60]
    df[discrete] = df[discrete].fillna('{BLANK}')
    df[continuous] = df[continuous].fillna(0)

def build_widgets():
    global uniq, wdg, init_load
    data_source = wdg['data'].value
    wdg.clear()
    uniq += 1

    wdg['data'] = bmw.TextInput(title='Data Source (required)', value=data_source, id='data_source-'+str(uniq))
    wdg['x_dropdown'] = bmw.Div(text='X-Axis (required)', id='x_dropdown-'+str(uniq))
    wdg['x'] = bmw.Select(title='X-Axis (required)', value='None', options=['None'] + columns, id='x_drop_x-'+str(uniq))
    wdg['x_group'] = bmw.Select(title='Group X-Axis By', value='None', options=['None'] + seriesable, id='x_drop_xgroup-'+str(uniq))
    wdg['y_dropdown'] = bmw.Div(text='Y-Axis (required)', id='y_dropdown-'+str(uniq))
    wdg['y'] = bmw.Select(title='Y-Axis (required)', value='None', options=['None'] + columns, id='y_drop_y-'+str(uniq))
    wdg['y_agg'] = bmw.Select(title='Y-Axis Aggregation', value='None', options=AGGREGATIONS, id='y_drop_y_agg-'+str(uniq))
    wdg['series_dropdown'] = bmw.Div(text='Series', id='series_dropdown-'+str(uniq))
    wdg['series_legend'] = bmw.Div(text='', id='series_drop_legend-'+str(uniq))
    wdg['series'] = bmw.Select(title='Separate Series By', value='None', options=['None'] + seriesable, id='series_drop_series-'+str(uniq))
    wdg['series_stack'] = bmw.Select(title='Series Stacking', value='Unstacked', options=['Unstacked', 'Stacked'], id='series_drop_stack-'+str(uniq))
    wdg['explode_dropdown'] = bmw.Div(text='Explode', id='explode_dropdown-'+str(uniq))
    wdg['explode'] = bmw.Select(title='Explode By', value='None', options=['None'] + seriesable, id='explode_drop_explode-'+str(uniq))
    wdg['explode_group'] = bmw.Select(title='Group Exploded Charts By', value='None', options=['None'] + seriesable, id='explode_drop_group-'+str(uniq))
    wdg['filters'] = bmw.Div(text='Filters', id='filters-'+str(uniq))
    for j, col in enumerate(filterable):
        val_list = [str(i) for i in sorted(df[col].unique().tolist())]
        wdg['heading_filter_'+str(j)] = bmw.Div(text=col, id='heading_filter_'+str(j)+'-'+str(uniq))
        wdg['filter_'+str(j)] = bmw.CheckboxGroup(labels=val_list, active=list(range(len(val_list))), id='filter_'+str(j)+'-'+str(uniq))
    wdg['update'] = bmw.Button(label='Update Filters', button_type='success', id='update_button-'+str(uniq))
    wdg['adjustments'] = bmw.Div(text='Plot Adjustments', id='adjust_plots-'+str(uniq))
    wdg['chartType'] = bmw.Select(title='Chart Type', value=CHARTTYPES[0], options=CHARTTYPES, id='adjust_plot_chart_type-'+str(uniq))
    wdg['plot_width'] = bmw.TextInput(title='Plot Width (px)', value=str(PLOT_WIDTH), id='adjust_plot_width-'+str(uniq))
    wdg['plot_height'] = bmw.TextInput(title='Plot Height (px)', value=str(PLOT_HEIGHT), id='adjust_plot_height-'+str(uniq))
    wdg['plot_title'] = bmw.TextInput(title='Plot Title', value='', id='adjust_plot_title-'+str(uniq))
    wdg['plot_title_size'] = bmw.TextInput(title='Plot Title Font Size', value=str(PLOT_FONT_SIZE), id='adjust_plot_title_size-'+str(uniq))
    wdg['opacity'] = bmw.TextInput(title='Opacity (0-1)', value=str(OPACITY), id='adjust_plot_opacity-'+str(uniq))
    wdg['x_scale'] = bmw.TextInput(title='X Scale', value=str(X_SCALE), id='adjust_plot_x_scale-'+str(uniq))
    wdg['x_min'] = bmw.TextInput(title='X Min', value='', id='adjust_plot_x_min-'+str(uniq))
    wdg['x_max'] = bmw.TextInput(title='X Max', value='', id='adjust_plot_x_max-'+str(uniq))
    wdg['x_title'] = bmw.TextInput(title='X Title', value='', id='adjust_plot_x_title-'+str(uniq))
    wdg['x_title_size'] = bmw.TextInput(title='X Title Font Size', value=str(PLOT_FONT_SIZE), id='adjust_plot_x_title_size-'+str(uniq))
    wdg['x_major_label_size'] = bmw.TextInput(title='X Labels Font Size', value=str(PLOT_AXIS_LABEL_SIZE), id='adjust_plot_x_labels_size-'+str(uniq))
    wdg['x_major_label_orientation'] = bmw.TextInput(title='X Labels Degrees', value=str(PLOT_LABEL_ORIENTATION), id='adjust_plot_x_labels_orientation-'+str(uniq))
    wdg['y_scale'] = bmw.TextInput(title='Y Scale', value=str(Y_SCALE), id='adjust_plot_y_scale-'+str(uniq))
    wdg['y_min'] = bmw.TextInput(title='Y  Min', value='', id='adjust_plot_y_min-'+str(uniq))
    wdg['y_max'] = bmw.TextInput(title='Y Max', value='', id='adjust_plot_y_max-'+str(uniq))
    wdg['y_title'] = bmw.TextInput(title='Y Title', value='', id='adjust_plot_y_title-'+str(uniq))
    wdg['y_title_size'] = bmw.TextInput(title='Y Title Font Size', value=str(PLOT_FONT_SIZE), id='adjust_plot_y_title_size-'+str(uniq))
    wdg['y_major_label_size'] = bmw.TextInput(title='Y Labels Font Size', value=str(PLOT_AXIS_LABEL_SIZE), id='adjust_plot_y_labels_size-'+str(uniq))
    wdg['circle_size'] = bmw.TextInput(title='Circle Size (Dot Only)', value=str(CIRCLE_SIZE), id='adjust_plot_circle_size-'+str(uniq))
    wdg['bar_width'] = bmw.TextInput(title='Bar Width (Bar Only)', value=str(BAR_WIDTH), id='adjust_plot_bar_width-'+str(uniq))
    wdg['line_width'] = bmw.TextInput(title='Line Width (Line Only)', value=str(LINE_WIDTH), id='adjust_plot_line_width-'+str(uniq))
    wdg['download'] = bmw.Button(label='Download csv', button_type='success')
    wdg['export_config'] = bmw.Div(text='Export Config to URL', id='export_config-'+str(uniq))

    wdg['series_legend'].text = build_series_legend()

    if init_load:
        for wc_key in wdg_config:
            for w_key in wdg:
                if str(re.sub(r'[0-9]+$', '', wdg[w_key]._id)) == str(wc_key):
                    if hasattr(wdg[w_key], 'value'):
                        wdg[w_key].value = str(wdg_config[wc_key])
                    elif hasattr(wdg[w_key], 'active'):
                        wdg[w_key].active = wdg_config[wc_key]
        init_load = False

    wdg['data'].on_change('value', update_data)
    wdg['chartType'].on_change('value', update_sel)
    wdg['x'].on_change('value', update_sel)
    wdg['x_group'].on_change('value', update_sel)
    wdg['y'].on_change('value', update_sel)
    wdg['y_agg'].on_change('value', update_sel)
    wdg['series'].on_change('value', update_sel)
    wdg['series_stack'].on_change('value', update_sel)
    wdg['explode'].on_change('value', update_sel)
    wdg['explode_group'].on_change('value', update_sel)
    wdg['plot_title'].on_change('value', update_sel)
    wdg['plot_title_size'].on_change('value', update_sel)
    wdg['plot_width'].on_change('value', update_sel)
    wdg['plot_height'].on_change('value', update_sel)
    wdg['opacity'].on_change('value', update_sel)
    wdg['x_min'].on_change('value', update_sel)
    wdg['x_max'].on_change('value', update_sel)
    wdg['x_scale'].on_change('value', update_sel)
    wdg['x_title'].on_change('value', update_sel)
    wdg['x_title_size'].on_change('value', update_sel)
    wdg['x_major_label_size'].on_change('value', update_sel)
    wdg['x_major_label_orientation'].on_change('value', update_sel)
    wdg['y_min'].on_change('value', update_sel)
    wdg['y_max'].on_change('value', update_sel)
    wdg['y_scale'].on_change('value', update_sel)
    wdg['y_title'].on_change('value', update_sel)
    wdg['y_title_size'].on_change('value', update_sel)
    wdg['y_major_label_size'].on_change('value', update_sel)
    wdg['circle_size'].on_change('value', update_sel)
    wdg['bar_width'].on_change('value', update_sel)
    wdg['line_width'].on_change('value', update_sel)
    wdg['update'].on_click(update_plots)
    wdg['download'].on_click(download)

def set_df_plots():
    global df_plots
    df_plots = df.copy()

    #Apply filters
    for j, col in enumerate(filterable):
        active = [wdg['filter_'+str(j)].labels[i] for i in wdg['filter_'+str(j)].active]
        if col in continuous:
            active = [float(i) for i in active]
        df_plots = df_plots[df_plots[col].isin(active)]

    #Scale Axes
    if wdg['x_scale'].value != '' and wdg['x'].value in continuous:
        df_plots[wdg['x'].value] = df_plots[wdg['x'].value] * float(wdg['x_scale'].value)
    if wdg['y_scale'].value != '' and wdg['y'].value in continuous:
        df_plots[wdg['y'].value] = df_plots[wdg['y'].value] * float(wdg['y_scale'].value)

    #Apply Aggregation
    if wdg['y_agg'].value == 'Sum' and wdg['y'].value in continuous:
        groupby_cols = [wdg['x'].value]
        if wdg['x_group'].value != 'None': groupby_cols = [wdg['x_group'].value] + groupby_cols
        if wdg['series'].value != 'None': groupby_cols = [wdg['series'].value] + groupby_cols
        if wdg['explode'].value != 'None': groupby_cols = [wdg['explode'].value] + groupby_cols
        if wdg['explode_group'].value != 'None': groupby_cols = [wdg['explode_group'].value] + groupby_cols
        df_plots = df_plots.groupby(groupby_cols, as_index=False, sort=False)[wdg['y'].value].sum()

    #Sort Dataframe
    sortby_cols = [wdg['x'].value]
    if wdg['x_group'].value != 'None': sortby_cols = [wdg['x_group'].value] + sortby_cols
    if wdg['series'].value != 'None': sortby_cols = [wdg['series'].value] + sortby_cols
    if wdg['explode'].value != 'None': sortby_cols = [wdg['explode'].value] + sortby_cols
    if wdg['explode_group'].value != 'None': sortby_cols = [wdg['explode_group'].value] + sortby_cols
    df_plots = df_plots.sort_values(sortby_cols).reset_index(drop=True)

    #Rearrange column order for csv download
    unsorted_columns = [col for col in df_plots.columns if col not in sortby_cols + [wdg['y'].value]]
    df_plots = df_plots[sortby_cols + unsorted_columns + [wdg['y'].value]]

def create_figures():
    plot_list = []
    df_plots_cp = df_plots.copy()
    if wdg['explode'].value == 'None':
        plot_list.append(create_figure(df_plots_cp))
    else:
        if wdg['explode_group'].value == 'None':
            for explode_val in df_plots_cp[wdg['explode'].value].unique().tolist():
                df_exploded = df_plots_cp[df_plots_cp[wdg['explode'].value].isin([explode_val])]
                plot_list.append(create_figure(df_exploded, explode_val))
        else:
            for explode_group in df_plots_cp[wdg['explode_group'].value].unique().tolist():
                df_exploded_group = df_plots_cp[df_plots_cp[wdg['explode_group'].value].isin([explode_group])]
                for explode_val in df_exploded_group[wdg['explode'].value].unique().tolist():
                    df_exploded = df_exploded_group[df_exploded_group[wdg['explode'].value].isin([explode_val])]
                    plot_list.append(create_figure(df_exploded, explode_val, explode_group))
    return plot_list

def create_figure(df_exploded, explode_val=None, explode_group=None):
    # If x_group has a value, create a combined column in the dataframe for x and x_group
    x_col = wdg['x'].value
    if wdg['x_group'].value != 'None':
        x_col = str(wdg['x_group'].value) + '_' + str(wdg['x'].value)
        df_exploded[x_col] = df_exploded[wdg['x_group'].value].map(str) + ' ' + df_exploded[wdg['x'].value].map(str)

    #Build x and y ranges and figure title
    kw = dict()

    #Set x and y ranges. When x is grouped, there is added complication of separating the groups
    xs = df_exploded[x_col].values.tolist()
    ys = df_exploded[wdg['y'].value].values.tolist()
    if wdg['x_group'].value != 'None':
        kw['x_range'] = []
        unique_groups = df_exploded[wdg['x_group'].value].unique().tolist()
        unique_xs = df_exploded[wdg['x'].value].unique().tolist()
        for i, ugr in enumerate(unique_groups):
            for uxs in unique_xs:
                kw['x_range'].append(str(ugr) + ' ' + str(uxs))
            #Between groups, add entries that consist of spaces. Increase number of spaces from
            #one break to the next so that each entry is unique
            kw['x_range'].append(' ' * (i + 1))
    elif wdg['x'].value in discrete:
        kw['x_range'] = sorted(set(xs))
    if wdg['y'].value in discrete:
        kw['y_range'] = sorted(set(ys))

    #Set figure title
    kw['title'] = wdg['plot_title'].value
    seperator = '' if kw['title'] == '' else ', '
    if explode_val is not None:
        if explode_group is not None:
            kw['title'] = kw['title'] + seperator + "%s = %s" % (wdg['explode_group'].value, str(explode_group))
        seperator = '' if kw['title'] == '' else ', '
        kw['title'] = kw['title'] + seperator + "%s = %s" % (wdg['explode'].value, str(explode_val))

    #Add figure tools
    hover = bmt.HoverTool(
            tooltips=[
                ("ser", "@ser_legend"),
                ("x", "@x_legend"),
                ("y", "@y_legend"),
            ]
    )
    TOOLS = [bmt.BoxZoomTool(), bmt.PanTool(), hover, bmt.ResetTool(), bmt.SaveTool()]

    #Create figure with the ranges, titles, and tools, and adjust formatting and labels
    p = bp.figure(plot_height=int(wdg['plot_height'].value), plot_width=int(wdg['plot_width'].value), tools=TOOLS, **kw)
    p.toolbar.active_drag = TOOLS[0]
    p.title.text_font_size = wdg['plot_title_size'].value + 'pt'
    p.xaxis.axis_label = wdg['x_title'].value
    p.yaxis.axis_label = wdg['y_title'].value
    p.xaxis.axis_label_text_font_size = wdg['x_title_size'].value + 'pt'
    p.yaxis.axis_label_text_font_size = wdg['y_title_size'].value + 'pt'
    p.xaxis.major_label_text_font_size = wdg['x_major_label_size'].value + 'pt'
    p.yaxis.major_label_text_font_size = wdg['y_major_label_size'].value + 'pt'
    p.xaxis.major_label_orientation = 'horizontal' if wdg['x_major_label_orientation'].value == '0' else math.radians(float(wdg['x_major_label_orientation'].value))
    if wdg['x'].value in continuous:
        if wdg['x_min'].value != '': p.x_range.start = float(wdg['x_min'].value)
        if wdg['x_max'].value != '': p.x_range.end = float(wdg['x_max'].value)
    if wdg['y'].value in continuous:
        if wdg['y_min'].value != '': p.y_range.start = float(wdg['y_min'].value)
        if wdg['y_max'].value != '': p.y_range.end = float(wdg['y_max'].value)

    #Add glyphs to figure
    c = C_NORM
    if wdg['series'].value == 'None':
        if wdg['y_agg'].value != 'None' and wdg['y'].value in continuous:
            xs = df_exploded[x_col].values.tolist()
            ys = df_exploded[wdg['y'].value].values.tolist()
        add_glyph(p, xs, ys, c)
    else:
        full_series = df_plots[wdg['series'].value].unique().tolist() #for colors only
        if wdg['series_stack'].value == 'Stacked':
            xs_full = sorted(df_exploded[x_col].unique().tolist())
            y_bases_pos = [0]*len(xs_full)
            y_bases_neg = [0]*len(xs_full)
        for i, ser in enumerate(df_exploded[wdg['series'].value].unique().tolist()):
            c = COLORS[full_series.index(ser)]
            df_series = df_exploded[df_exploded[wdg['series'].value].isin([ser])]
            xs_ser = df_series[x_col].values.tolist()
            ys_ser = df_series[wdg['y'].value].values.tolist()
            if wdg['series_stack'].value == 'Unstacked':
                add_glyph(p, xs_ser, ys_ser, c, series=ser)
            else:
                ys_pos = [ys_ser[xs_ser.index(x)] if x in xs_ser and ys_ser[xs_ser.index(x)] > 0 else 0 for i, x in enumerate(xs_full)]
                ys_neg = [ys_ser[xs_ser.index(x)] if x in xs_ser and ys_ser[xs_ser.index(x)] < 0 else 0 for i, x in enumerate(xs_full)]
                ys_stacked_pos = [ys_pos[i] + y_bases_pos[i] for i in range(len(xs_full))]
                ys_stacked_neg = [ys_neg[i] + y_bases_neg[i] for i in range(len(xs_full))]
                add_glyph(p, xs_full, ys_stacked_pos, c, y_bases=y_bases_pos, series=ser)
                add_glyph(p, xs_full, ys_stacked_neg, c, y_bases=y_bases_neg, series=ser)
                y_bases_pos = ys_stacked_pos
                y_bases_neg = ys_stacked_neg
    return p

def add_glyph(p, xs, ys, c, y_bases=None, series=None):
    alpha = float(wdg['opacity'].value)
    y_unstacked = list(ys) if y_bases is None else [ys[i] - y_bases[i] for i in range(len(ys))]
    ser = ['None']*len(xs) if series is None else [series]*len(xs)
    if wdg['chartType'].value == 'Dot':
        source = bms.ColumnDataSource({'x': xs, 'y': ys, 'x_legend': xs, 'y_legend': y_unstacked, 'ser_legend': ser})
        p.circle('x', 'y', source=source, color=c, size=int(wdg['circle_size'].value), fill_alpha=alpha, line_color=None, line_width=None)
    elif wdg['chartType'].value == 'Line':
        source = bms.ColumnDataSource({'x': xs, 'y': ys, 'x_legend': xs, 'y_legend': y_unstacked, 'ser_legend': ser})
        p.line('x', 'y', source=source, color=c, alpha=alpha, line_width=float(wdg['line_width'].value))
    elif wdg['chartType'].value == 'Bar':
        if y_bases is None: y_bases = [0]*len(ys)
        centers = [(ys[i] + y_bases[i])/2 for i in range(len(ys))]
        heights = [abs(ys[i] - y_bases[i]) for i in range(len(ys))]
        source = bms.ColumnDataSource({'x': xs, 'y': centers, 'x_legend': xs, 'y_legend': y_unstacked, 'h': heights, 'ser_legend': ser})
        p.rect('x', 'y', source=source, height='h', color=c, fill_alpha=alpha, width=float(wdg['bar_width'].value), line_color=None, line_width=None)
    elif wdg['chartType'].value == 'Area':
        if y_bases is None: y_bases = [0]*len(ys)
        xs_around = xs + xs[::-1]
        ys_around = y_bases + ys[::-1]
        source = bms.ColumnDataSource({'x': xs_around, 'y': ys_around})
        p.patch('x', 'y', source=source, alpha=alpha, fill_color=c, line_color=None, line_width=None)


def build_series_legend():
    series_legend_string = '<div class="legend-header">Series Legend</div><div class="legend-body">'
    if wdg['series'].value != 'None':
        active_list = df_plots[wdg['series'].value].unique().tolist()
        for i, txt in reversed(list(enumerate(active_list))):
            series_legend_string += '<div class="legend-entry"><span class="legend-color" style="background-color:' + str(COLORS[i]) + ';"></span>'
            series_legend_string += '<span class="legend-text">' + str(txt) +'</span></div>'
    series_legend_string += '</div>'
    return series_legend_string


def update_data(attr, old, new):
    get_data()
    build_widgets()
    controls.children = list(wdg.values())
    update_plots()

def update_sel(attr, old, new):
    update_plots()

def update_plots():
    if wdg['x'].value == 'None' or wdg['y'].value == 'None':
        plots.children = []
        return
    set_df_plots()
    wdg['series_legend'].text = build_series_legend()
    plots.children = create_figures()

def download():
    df_plots.to_csv('downloads/out '+datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S-%f")+'.csv', index=False)

init_load = True
wdg_config = {}
data_file = 'csv/power.csv'
args = bio.curdoc().session_context.request.arguments
wdg_arr = args.get('widgets')
if wdg_arr is not None:
    wdg_config = json.loads(urlp.unquote(wdg_arr[0].decode('utf-8')))
    if 'data_source-' in wdg_config:
        data_file = str(wdg_config['data_source-'])

wdg = collections.OrderedDict()
wdg['data'] = bmw.TextInput(title='Data Source', value=data_file)
get_data()
uniq = 0
build_widgets()
controls = bl.widgetbox(list(wdg.values()), id='widgets_section')
plots = bl.column([], id='plots_section')
update_plots()
layout = bl.row(controls, plots, id='layout')

bio.curdoc().add_root(layout)
bio.curdoc().title = "Exploding Pivot Chart Maker"