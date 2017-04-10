''' Provide a pivot chart maker example app. Similar to Excel pivot charts,
but with additonal ability to explode into multiple charts.
See README.md for more information.

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

class BokehPivot:

    """A base class for producing bokeh pivot charts"""
    def __init__(self):
        self.COLORS = ['#5e4fa2', '#3288bd', '#66c2a5', '#abdda4', '#e6f598', '#fee08b', '#fdae61', '#f46d43', '#d53e4f', '#9e0142']*1000
        self.C_NORM = "#31AADE"
        self.ADV_BASES = ['Consecutive', 'Total']
        #initialize globals dict
        self.gl = {'df_source':None, 'df_plots':None, 'columns':None, 'widgets':None, 'controls': None, 'plots':None}

        #List of widgets that use columns as their selectors
        self.wdg_col_all = ['x', 'y'] #all columns available for these widgets
        self.wdg_col_ser = ['x_group', 'series', 'explode', 'explode_group'] #seriesable columns available for these widgets
        self.wdg_col = self.wdg_col_all + self.wdg_col_ser

        #List of widgets that don't use columns as selector and share general widget update function
        self.wdg_non_col = ['chart_type', 'y_agg', 'y_weight', 'adv_op', 'adv_col_base', 'plot_title', 'plot_title_size',
            'plot_width', 'plot_height', 'opacity', 'x_min', 'x_max', 'x_scale', 'x_title',
            'x_title_size', 'x_major_label_size', 'x_major_label_orientation',
            'y_min', 'y_max', 'y_scale', 'y_title', 'y_title_size', 'y_major_label_size',
            'circle_size', 'bar_width', 'line_width']

        #Specify default widget values
        self.defaults = {}
        self.defaults['data_source'] = os.path.dirname(os.path.realpath(__file__)) + '/csv/US_electric_power_generation.csv'
        for w in self.wdg_col:
            self.defaults[w] = 'None'
        self.defaults['x'] = 'Year'
        self.defaults['y'] = 'Electricity Generation (TWh)'
        self.defaults['series'] = 'Technology'
        self.defaults['explode'] = 'Case'
        self.defaults['chart_type'] = 'Area'

        #On initial load, read 'widgets' parameter from URL query string and use to set data source (data_source)
        #and widget configuration object (wdg_config)
        self.wdg_config = {}
        self.args = bio.curdoc().session_context.request.arguments
        self.wdg_arr = self.args.get('widgets')
        if self.wdg_arr is not None:
            self.wdg_config = json.loads(urlp.unquote(self.wdg_arr[0].decode('utf-8')))
            if 'data' in self.wdg_config:
                self.defaults['data_source'] = str(self.wdg_config['data'])
                for w in self.wdg_col:
                    self.defaults[w] = 'None'

        #build widgets and plots
        self.gl['df_source'], self.gl['columns'] = self.get_data(self.defaults['data_source'])
        self.gl['widgets'] = self.build_widgets(self.gl['df_source'], self.gl['columns'], self.defaults, init_load=True, init_config=self.wdg_config)
        self.set_wdg_col_options()
        self.gl['controls'] = bl.widgetbox(list(self.gl['widgets'].values()), id='widgets_section')
        self.gl['plots'] = bl.column([], id='plots_section')
        self.update_plots()
        self.layout = bl.row(self.gl['controls'], self.gl['plots'], id='layout')

        bio.curdoc().add_root(self.layout)
        bio.curdoc().title = "Exploding Pivot Chart Maker"

    def get_data(self, data_source):
        '''
        Read a csv into a pandas dataframe, and determine which columns of the dataframe
        are discrete (strings), continuous (numbers), able to be filtered (aka filterable),
        and able to be used as a series (aka seriesable). NA values are filled based on the type of column,
        and the dataframe and columns are returned.

        Args:
            data_source (string): Path to csv file.

        Returns:
            df_source (pandas dataframe): A dataframe of the csv source, with filled NA values.
            cols (dict): Keys are categories of columns of df_source, and values are a list of columns of that category.
        '''

        df_source = pd.read_csv(data_source)
        cols = {}
        cols['all'] = df_source.columns.values.tolist()
        cols['discrete'] = [x for x in cols['all'] if df_source[x].dtype == object]
        cols['continuous'] = [x for x in cols['all'] if x not in cols['discrete']]
        cols['filterable'] = cols['discrete']+[x for x in cols['continuous'] if len(df_source[x].unique()) < 100]
        cols['seriesable'] = cols['discrete']+[x for x in cols['continuous'] if len(df_source[x].unique()) < 60]
        df_source[cols['discrete']] = df_source[cols['discrete']].fillna('{BLANK}')
        df_source[cols['continuous']] = df_source[cols['continuous']].fillna(0)
        return (df_source, cols)

    def build_widgets(self, df_source, cols, defaults, init_load=False, init_config={}):
        '''
        Use a dataframe and its columns to set widget options. Widget values may
        be set by URL parameters via init_config.

        Args:
            df_source (pandas dataframe): Dataframe of the csv source.
            cols (dict): Keys are categories of columns of df_source, and values are a list of columns of that category.
            defaults (dict): Keys correspond to widgets, and values (str) are the default values of those widgets.
            init_load (boolean, optional): If this is the initial page load, then this will be True, else False.
            init_config (dict): Initial widget configuration passed via URL.

        Returns:
            wdg (ordered dict): Dictionary of bokeh.model.widgets.
        '''
        PLOT_WIDTH = 300
        PLOT_HEIGHT = 300
        PLOT_FONT_SIZE = 10
        PLOT_AXIS_LABEL_SIZE = 8
        PLOT_LABEL_ORIENTATION = 45
        OPACITY = 0.8
        X_SCALE = 1
        Y_SCALE = 1
        CIRCLE_SIZE = 9
        BAR_WIDTH = 0.5
        LINE_WIDTH = 2
        CHARTTYPES = ['Dot', 'Line', 'Bar', 'Area']
        AGGREGATIONS = ['None', 'Sum', 'Ave', 'Weighted Ave']

        #Add widgets
        wdg = collections.OrderedDict()
        wdg['data'] = bmw.TextInput(title='Data Source (required)', value=defaults['data_source'], css_classes=['wdgkey-data'])
        wdg['x_dropdown'] = bmw.Div(text='X-Axis (required)', css_classes=['x-dropdown'])
        wdg['x'] = bmw.Select(title='X-Axis (required)', value=defaults['x'], options=['None'] + cols['all'], css_classes=['wdgkey-x', 'x-drop'])
        wdg['x_group'] = bmw.Select(title='Group X-Axis By', value=defaults['x_group'], options=['None'] + cols['seriesable'], css_classes=['wdgkey-x_group', 'x-drop'])
        wdg['y_dropdown'] = bmw.Div(text='Y-Axis (required)', css_classes=['y-dropdown'])
        wdg['y'] = bmw.Select(title='Y-Axis (required)', value=defaults['y'], options=['None'] + cols['all'], css_classes=['wdgkey-y', 'y-drop'])
        wdg['y_agg'] = bmw.Select(title='Y-Axis Aggregation', value='Sum', options=AGGREGATIONS, css_classes=['wdgkey-y_agg', 'y-drop'])
        wdg['y_weight'] = bmw.Select(title='Weighting Factor', value='None', options=['None'] + cols['all'], css_classes=['wdgkey-y_weight', 'y-drop'])
        wdg['series_dropdown'] = bmw.Div(text='Series', css_classes=['series-dropdown'])
        wdg['series'] = bmw.Select(title='Separate Series By', value=defaults['series'], options=['None'] + cols['seriesable'],
            css_classes=['wdgkey-series', 'series-drop'])
        wdg['series_legend'] = bmw.Div(text='', css_classes=['series-drop'])
        wdg['explode_dropdown'] = bmw.Div(text='Explode', css_classes=['explode-dropdown'])
        wdg['explode'] = bmw.Select(title='Explode By', value=defaults['explode'], options=['None'] + cols['seriesable'], css_classes=['wdgkey-explode', 'explode-drop'])
        wdg['explode_group'] = bmw.Select(title='Group Exploded Charts By', value=defaults['explode_group'], options=['None'] + cols['seriesable'],
            css_classes=['wdgkey-explode_group', 'explode-drop'])
        wdg['adv_dropdown'] = bmw.Div(text='Comparisons', css_classes=['adv-dropdown'])
        wdg['adv_op'] = bmw.Select(title='Operation', value='None', options=['None', 'Difference', 'Ratio'], css_classes=['wdgkey-adv_op', 'adv-drop'])
        wdg['adv_col'] = bmw.Select(title='Operate Across', value='None', options=['None'] + cols['all'], css_classes=['wdgkey-adv_col', 'adv-drop'])
        wdg['adv_col_base'] = bmw.Select(title='Base', value='None', options=['None'], css_classes=['wdgkey-adv_col_base', 'adv-drop'])
        wdg['filters'] = bmw.Div(text='Filters', css_classes=['filters-dropdown'])
        for j, col in enumerate(cols['filterable']):
            val_list = [str(i) for i in sorted(df_source[col].unique().tolist())]
            wdg['heading_filter_'+str(j)] = bmw.Div(text=col, css_classes=['filter-head'])
            wdg['filter_'+str(j)] = bmw.CheckboxGroup(labels=val_list, active=list(range(len(val_list))), css_classes=['wdgkey-filter_'+str(j), 'filter'])
        wdg['update'] = bmw.Button(label='Update Filters', button_type='success', css_classes=['filters-update'])
        wdg['adjustments'] = bmw.Div(text='Plot Adjustments', css_classes=['adjust-dropdown'])
        wdg['chart_type'] = bmw.Select(title='Chart Type', value=defaults['chart_type'], options=CHARTTYPES, css_classes=['wdgkey-chart_type', 'adjust-drop'])
        wdg['plot_width'] = bmw.TextInput(title='Plot Width (px)', value=str(PLOT_WIDTH), css_classes=['wdgkey-plot_width', 'adjust-drop'])
        wdg['plot_height'] = bmw.TextInput(title='Plot Height (px)', value=str(PLOT_HEIGHT), css_classes=['wdgkey-plot_height', 'adjust-drop'])
        wdg['plot_title'] = bmw.TextInput(title='Plot Title', value='', css_classes=['wdgkey-plot_title', 'adjust-drop'])
        wdg['plot_title_size'] = bmw.TextInput(title='Plot Title Font Size', value=str(PLOT_FONT_SIZE), css_classes=['wdgkey-plot_title_size', 'adjust-drop'])
        wdg['opacity'] = bmw.TextInput(title='Opacity (0-1)', value=str(OPACITY), css_classes=['wdgkey-opacity', 'adjust-drop'])
        wdg['x_scale'] = bmw.TextInput(title='X Scale', value=str(X_SCALE), css_classes=['wdgkey-x_scale', 'adjust-drop'])
        wdg['x_min'] = bmw.TextInput(title='X Min', value='', css_classes=['wdgkey-x_min', 'adjust-drop'])
        wdg['x_max'] = bmw.TextInput(title='X Max', value='', css_classes=['wdgkey-x_max', 'adjust-drop'])
        wdg['x_title'] = bmw.TextInput(title='X Title', value='', css_classes=['wdgkey-x_title', 'adjust-drop'])
        wdg['x_title_size'] = bmw.TextInput(title='X Title Font Size', value=str(PLOT_FONT_SIZE), css_classes=['wdgkey-x_title_size', 'adjust-drop'])
        wdg['x_major_label_size'] = bmw.TextInput(title='X Labels Font Size', value=str(PLOT_AXIS_LABEL_SIZE), css_classes=['wdgkey-x_major_label_size', 'adjust-drop'])
        wdg['x_major_label_orientation'] = bmw.TextInput(title='X Labels Degrees', value=str(PLOT_LABEL_ORIENTATION),
            css_classes=['wdgkey-x_major_label_orientation', 'adjust-drop'])
        wdg['y_scale'] = bmw.TextInput(title='Y Scale', value=str(Y_SCALE), css_classes=['wdgkey-y_scale', 'adjust-drop'])
        wdg['y_min'] = bmw.TextInput(title='Y  Min', value='', css_classes=['wdgkey-y_min', 'adjust-drop'])
        wdg['y_max'] = bmw.TextInput(title='Y Max', value='', css_classes=['wdgkey-y_max', 'adjust-drop'])
        wdg['y_title'] = bmw.TextInput(title='Y Title', value='', css_classes=['wdgkey-y_title', 'adjust-drop'])
        wdg['y_title_size'] = bmw.TextInput(title='Y Title Font Size', value=str(PLOT_FONT_SIZE), css_classes=['wdgkey-y_title_size', 'adjust-drop'])
        wdg['y_major_label_size'] = bmw.TextInput(title='Y Labels Font Size', value=str(PLOT_AXIS_LABEL_SIZE), css_classes=['wdgkey-y_major_label_size', 'adjust-drop'])
        wdg['circle_size'] = bmw.TextInput(title='Circle Size (Dot Only)', value=str(CIRCLE_SIZE), css_classes=['wdgkey-circle_size', 'adjust-drop'])
        wdg['bar_width'] = bmw.TextInput(title='Bar Width (Bar Only)', value=str(BAR_WIDTH), css_classes=['wdgkey-bar_width', 'adjust-drop'])
        wdg['line_width'] = bmw.TextInput(title='Line Width (Line Only)', value=str(LINE_WIDTH), css_classes=['wdgkey-line_width', 'adjust-drop'])
        wdg['download'] = bmw.Button(label='Download csv', button_type='success')
        wdg['export_config'] = bmw.Div(text='Export Config to URL', css_classes=['export-config', 'bk-bs-btn', 'bk-bs-btn-success'])

        #use init_config (from 'widgets' parameter in URL query string) to configure widgets.
        if init_load:
            for key in init_config:
                if key in wdg:
                    if hasattr(wdg[key], 'value'):
                        wdg[key].value = str(init_config[key])
                    elif hasattr(wdg[key], 'active'):
                        wdg[key].active = init_config[key]

        #Add update functions for widgets
        wdg['data'].on_change('value', self.update_data)
        wdg['update'].on_click(self.update_plots)
        wdg['download'].on_click(self.download)
        wdg['adv_col'].on_change('value', self.update_adv_col)
        for name in self.wdg_col:
            wdg[name].on_change('value', self.update_wdg_col)
        for name in self.wdg_non_col:
            wdg[name].on_change('value', self.update_wdg)

        return wdg

    def set_df_plots(self, df_source, cols, wdg):
        '''
        Apply filters, scaling, aggregation, and sorting to source dataframe, and return the result.

        Args:
            df_source (pandas dataframe): Dataframe of the csv source.
            cols (dict): Keys are categories of columns of df_source, and values are a list of columns of that category.
            wdg (ordered dict): Dictionary of bokeh model widgets.

        Returns:
            df_plots (pandas dataframe): df_source after having been filtered, scaled, aggregated, and sorted.
        '''
        df_plots = df_source.copy()

        #Apply filters
        for j, col in enumerate(cols['filterable']):
            active = [wdg['filter_'+str(j)].labels[i] for i in wdg['filter_'+str(j)].active]
            if col in cols['continuous']:
                active = [float(i) for i in active]
            df_plots = df_plots[df_plots[col].isin(active)]

        #Scale Axes
        if wdg['x_scale'].value != '' and wdg['x'].value in cols['continuous']:
            df_plots[wdg['x'].value] = df_plots[wdg['x'].value] * float(wdg['x_scale'].value)
        if wdg['y_scale'].value != '' and wdg['y'].value in cols['continuous']:
            df_plots[wdg['y'].value] = df_plots[wdg['y'].value] * float(wdg['y_scale'].value)

        #Apply Aggregation
        if wdg['y'].value in cols['continuous'] and wdg['y_agg'].value != 'None':
            groupby_cols = [wdg['x'].value]
            if wdg['x_group'].value != 'None': groupby_cols = [wdg['x_group'].value] + groupby_cols
            if wdg['series'].value != 'None': groupby_cols = [wdg['series'].value] + groupby_cols
            if wdg['explode'].value != 'None': groupby_cols = [wdg['explode'].value] + groupby_cols
            if wdg['explode_group'].value != 'None': groupby_cols = [wdg['explode_group'].value] + groupby_cols
            df_grouped = df_plots.groupby(groupby_cols, sort=False)
            if wdg['y_agg'].value == 'Sum':
                df_plots = df_grouped[wdg['y'].value].sum().reset_index()
            elif wdg['y_agg'].value == 'Ave':
                df_plots = df_grouped[wdg['y'].value].mean().reset_index()
            elif wdg['y_agg'].value == 'Weighted Ave' and wdg['y_weight'].value in cols['continuous']:
                df_plots = df_grouped.apply(self.wavg, wdg['y'].value, wdg['y_weight'].value).reset_index()
                df_plots.rename(columns={0: wdg['y'].value}, inplace=True)

        #Do Advanced Operations
        op = wdg['adv_op'].value
        col = wdg['adv_col'].value
        col_base = wdg['adv_col_base'].value
        y_val = wdg['y'].value
        y_agg = wdg['y_agg'].value
        if op != 'None' and col != 'None' and col in df_plots and col_base != 'None' and y_agg != 'None' and y_val in cols['continuous']:
            #sort df_plots so that col_base is at the front, so that we can use transform('first') later
            if col in cols['continuous'] and col_base not in self.ADV_BASES:
                col_base = float(col_base)
            col_list = df_plots[col].unique().tolist()
            if col_base not in self.ADV_BASES:
                col_list.remove(col_base)
                col_list = [col_base] + col_list
            df_plots['tempsort'] = df_plots[col].map(lambda x: col_list.index(x))
            df_plots = df_plots.sort_values('tempsort').reset_index(drop=True)
            df_plots.drop(['tempsort'], axis='columns', inplace=True)
            #groupby all columns that are not the operating column and y axis column so we can do operations on y-axis across the operating column
            groupcols = [i for i in df_plots.columns.values.tolist() if i not in [col, y_val]]
            if groupcols != []:
                df_grouped = df_plots.groupby(groupcols, sort=False)[y_val]
            else:
                #if we don't have other columns to group, make one, to prevent error
                df_plots['tempgroup'] = 1
                df_grouped = df_plots.groupby('tempgroup', sort=False)[y_val]
            #Now do operations with the groups:
            if op == 'Difference':
                if col_base == 'Consecutive':
                    df_plots[y_val] = df_grouped.diff()
                elif col_base == 'Total':
                    df_plots[y_val] = df_plots[y_val] - df_grouped.transform('sum')
                else:
                    df_plots[y_val] = df_plots[y_val] - df_grouped.transform('first')
            elif op == 'Ratio':
                if col_base == 'Consecutive':
                    df_plots[y_val] = df_grouped.diff()
                elif col_base == 'Total':
                    df_plots[y_val] = df_plots[y_val] / df_grouped.transform('sum')
                else:
                    df_plots[y_val] = df_plots[y_val] / df_grouped.transform('first')
            #Finally, clean up df_plots, dropping unnecessary columns, rows with the base value, and any rows with NAs for y_vals
            if 'tempgroup' in df_plots:
                df_plots.drop(['tempgroup'], axis='columns', inplace=True)
            df_plots = df_plots[~df_plots[col].isin([col_base])]
            df_plots = df_plots[pd.notnull(df_plots[y_val])]

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

        return df_plots

    def create_figures(self, df_plots, wdg, cols):
        '''
        Create figures based on the data in a dataframe and widget configuration, and return figures in a list.
        The explode widget determines if there will be multiple figures.

        Args:
            df_plots (pandas dataframe): Dataframe of csv source after being filtered, scaled, aggregated, and sorted.
            wdg (ordered dict): Dictionary of bokeh model widgets.
            cols (dict): Keys are categories of columns of df_source, and values are a list of columns of that category.

        Returns:
            plot_list (list): List of bokeh.model.figures.
        '''
        plot_list = []
        df_plots_cp = df_plots.copy()
        if wdg['explode'].value == 'None':
            plot_list.append(self.create_figure(df_plots_cp, df_plots, wdg, cols))
        else:
            if wdg['explode_group'].value == 'None':
                for explode_val in df_plots_cp[wdg['explode'].value].unique().tolist():
                    df_exploded = df_plots_cp[df_plots_cp[wdg['explode'].value].isin([explode_val])]
                    plot_list.append(self.create_figure(df_exploded, df_plots, wdg, cols, explode_val))
            else:
                for explode_group in df_plots_cp[wdg['explode_group'].value].unique().tolist():
                    df_exploded_group = df_plots_cp[df_plots_cp[wdg['explode_group'].value].isin([explode_group])]
                    for explode_val in df_exploded_group[wdg['explode'].value].unique().tolist():
                        df_exploded = df_exploded_group[df_exploded_group[wdg['explode'].value].isin([explode_val])]
                        plot_list.append(self.create_figure(df_exploded, df_plots, wdg, cols, explode_val, explode_group))
        return plot_list

    def create_figure(self, df_exploded, df_plots, wdg, cols, explode_val=None, explode_group=None):
        '''
        Create and return a figure based on the data in a dataframe and widget configuration.

        Args:
            df_exploded (pandas dataframe): Dataframe of just the data that will be plotted in this figure.
            df_plots (pandas dataframe): Dataframe of all plots data, used only for maintaining consistent series colors.
            wdg (ordered dict): Dictionary of bokeh model widgets.
            cols (dict): Keys are categories of columns of df_source, and values are a list of columns of that category.
            explode_val (string, optional): The value in the column designated by wdg['explode'] that applies to this figure.
            explode_group (string, optional): The value in the wdg['explode_group'] column that applies to this figure.

        Returns:
            p (bokeh.model.figure): A figure, with all glyphs added by the add_glyph() function.
        '''
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
        elif wdg['x'].value in cols['discrete']:
            kw['x_range'] = sorted(set(xs))
        if wdg['y'].value in cols['discrete']:
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
        if wdg['x'].value in cols['continuous']:
            if wdg['x_min'].value != '': p.x_range.start = float(wdg['x_min'].value)
            if wdg['x_max'].value != '': p.x_range.end = float(wdg['x_max'].value)
        if wdg['y'].value in cols['continuous']:
            if wdg['y_min'].value != '': p.y_range.start = float(wdg['y_min'].value)
            if wdg['y_max'].value != '': p.y_range.end = float(wdg['y_max'].value)

        #Add glyphs to figure
        c = self.C_NORM
        STACKEDTYPES = ['Bar', 'Area']
        if wdg['series'].value == 'None':
            if wdg['y_agg'].value != 'None' and wdg['y'].value in cols['continuous']:
                xs = df_exploded[x_col].values.tolist()
                ys = df_exploded[wdg['y'].value].values.tolist()
            self.add_glyph(wdg, p, xs, ys, c)
        else:
            full_series = df_plots[wdg['series'].value].unique().tolist() #for colors only
            if wdg['chart_type'].value in STACKEDTYPES: #We are stacking the series
                xs_full = sorted(df_exploded[x_col].unique().tolist())
                y_bases_pos = [0]*len(xs_full)
                y_bases_neg = [0]*len(xs_full)
            for i, ser in enumerate(df_exploded[wdg['series'].value].unique().tolist()):
                c = self.COLORS[full_series.index(ser)]
                df_series = df_exploded[df_exploded[wdg['series'].value].isin([ser])]
                xs_ser = df_series[x_col].values.tolist()
                ys_ser = df_series[wdg['y'].value].values.tolist()
                if wdg['chart_type'].value not in STACKEDTYPES: #The series will not be stacked
                    self.add_glyph(wdg, p, xs_ser, ys_ser, c, series=ser)
                else: #We are stacking the series
                    ys_pos = [ys_ser[xs_ser.index(x)] if x in xs_ser and ys_ser[xs_ser.index(x)] > 0 else 0 for i, x in enumerate(xs_full)]
                    ys_neg = [ys_ser[xs_ser.index(x)] if x in xs_ser and ys_ser[xs_ser.index(x)] < 0 else 0 for i, x in enumerate(xs_full)]
                    ys_stacked_pos = [ys_pos[i] + y_bases_pos[i] for i in range(len(xs_full))]
                    ys_stacked_neg = [ys_neg[i] + y_bases_neg[i] for i in range(len(xs_full))]
                    self.add_glyph(wdg, p, xs_full, ys_stacked_pos, c, y_bases=y_bases_pos, series=ser)
                    self.add_glyph(wdg, p, xs_full, ys_stacked_neg, c, y_bases=y_bases_neg, series=ser)
                    y_bases_pos = ys_stacked_pos
                    y_bases_neg = ys_stacked_neg
        return p

    def add_glyph(self, wdg, p, xs, ys, c, y_bases=None, series=None):
        '''
        Add a glyph to a Bokeh figure, depending on the chosen chart type.

        Args:
            wdg (ordered dict): Dictionary of bokeh model widgets.
            p (bokeh.model.figure): Bokeh figure.
            xs (list): List of x-values. These could be numeric or strings.
            ys (list): List of y-values. These could be numeric or strings. If series data is stacked, these values include stacking.
            c (string): Color to use for this series.
            y_bases (list, optional): Only used when stacking series. This is the previous cumulative stacking level.
            series (string): Name of current series for this glyph.

        Returns:
            Nothing.
        '''
        alpha = float(wdg['opacity'].value)
        y_unstacked = list(ys) if y_bases is None else [ys[i] - y_bases[i] for i in range(len(ys))]
        ser = ['None']*len(xs) if series is None else [series]*len(xs)
        if wdg['chart_type'].value == 'Dot':
            source = bms.ColumnDataSource({'x': xs, 'y': ys, 'x_legend': xs, 'y_legend': y_unstacked, 'ser_legend': ser})
            p.circle('x', 'y', source=source, color=c, size=int(wdg['circle_size'].value), fill_alpha=alpha, line_color=None, line_width=None)
        elif wdg['chart_type'].value == 'Line':
            source = bms.ColumnDataSource({'x': xs, 'y': ys, 'x_legend': xs, 'y_legend': y_unstacked, 'ser_legend': ser})
            p.line('x', 'y', source=source, color=c, alpha=alpha, line_width=float(wdg['line_width'].value))
        elif wdg['chart_type'].value == 'Bar':
            if y_bases is None: y_bases = [0]*len(ys)
            centers = [(ys[i] + y_bases[i])/2 for i in range(len(ys))]
            heights = [abs(ys[i] - y_bases[i]) for i in range(len(ys))]
            source = bms.ColumnDataSource({'x': xs, 'y': centers, 'x_legend': xs, 'y_legend': y_unstacked, 'h': heights, 'ser_legend': ser})
            p.rect('x', 'y', source=source, height='h', color=c, fill_alpha=alpha, width=float(wdg['bar_width'].value), line_color=None, line_width=None)
        elif wdg['chart_type'].value == 'Area':
            if y_bases is None: y_bases = [0]*len(ys)
            xs_around = xs + xs[::-1]
            ys_around = y_bases + ys[::-1]
            source = bms.ColumnDataSource({'x': xs_around, 'y': ys_around})
            p.patch('x', 'y', source=source, alpha=alpha, fill_color=c, line_color=None, line_width=None)


    def build_series_legend(self, df_plots, series_val):
        '''
        Return html for series legend, based on values of column that was chosen for series, and global COLORS.

        Args:
            df_plots (pandas dataframe): Dataframe of all plots data.
            series_val (string): Header for column chosen as series.

        Returns:
            series_legend_string (string): html to be used as legend.
        '''
        series_legend_string = '<div class="legend-header">Series Legend</div><div class="legend-body">'
        if series_val != 'None':
            active_list = df_plots[series_val].unique().tolist()
            for i, txt in reversed(list(enumerate(active_list))):
                series_legend_string += '<div class="legend-entry"><span class="legend-color" style="background-color:' + str(self.COLORS[i]) + ';"></span>'
                series_legend_string += '<span class="legend-text">' + str(txt) +'</span></div>'
        series_legend_string += '</div>'
        return series_legend_string


    def wavg(self, group, avg_name, weight_name):
        """ http://pbpython.com/weighted-average.html
        """
        d = group[avg_name]
        w = group[weight_name]
        try:
            return (d * w).sum() / w.sum()
        except ZeroDivisionError:
            return 0


    def update_data(self, attr, old, new):
        '''
        When data source is updated, rebuild widgets and plots.
        '''
        self.defaults['data_source'] = self.gl['widgets']['data'].value
        for w in self.wdg_col:
            self.defaults[w] = 'None'
        self.defaults['chart_type'] = 'Dot'
        self.gl['df_source'], self.gl['columns'] = self.get_data(self.defaults['data_source'])
        self.gl['widgets'] = self.build_widgets(self.gl['df_source'], self.gl['columns'], self.defaults)
        self.gl['controls'].children = list(self.gl['widgets'].values())
        self.gl['plots'].children = []

    def update_wdg(self, attr, old, new):
        '''
        When general widgets are updated (not in wdg_col), update plots only.
        '''
        self.update_plots()

    def update_wdg_col(self, attr, old, new):
        '''
        When widgets in wdg_col are updated, set the options of all wdg_col widgets,
        and update plots.
        '''
        self.set_wdg_col_options()
        self.update_plots()

    def update_adv_col(self, attr, old, new):
        '''
        When adv_col is set, find unique values of adv_col in dataframe, and set adv_col_base with those values.
        '''
        wdg = self.gl['widgets']
        df = self.gl['df_source']
        if wdg['adv_col'].value != 'None':
            wdg['adv_col_base'].options = ['None'] + self.ADV_BASES + [str(i) for i in sorted(df[wdg['adv_col'].value].unique().tolist())]

    def set_wdg_col_options(self):
        '''
        Limit available options for wdg_col widgets based on their selected values, so that users
        cannot select the same value for two different wdg_col widgets.
        '''
        cols = self.gl['columns']
        wdg = self.gl['widgets']
        #get list of selected values and use to reduce selection options.
        sels = [str(wdg[w].value) for w in self.wdg_col if str(wdg[w].value) !='None']
        all_reduced = [x for x in cols['all'] if x not in sels]
        ser_reduced = [x for x in cols['seriesable'] if x not in sels]
        for w in self.wdg_col:
            val = str(wdg[w].value)
            none_append = [] if val == 'None' else ['None']
            opt_reduced = all_reduced if w in self.wdg_col_all else ser_reduced
            wdg[w].options = [val] + opt_reduced + none_append

    def update_plots(self):
        '''
        Make sure x axis and y axis are set. If so, set the dataframe for the plots and build them.
        '''
        if self.gl['widgets']['x'].value == 'None' or self.gl['widgets']['y'].value == 'None':
            self.gl['plots'].children = []
            return
        self.gl['df_plots'] = self.set_df_plots(self.gl['df_source'], self.gl['columns'], self.gl['widgets'])
        self.gl['widgets']['series_legend'].text = self.build_series_legend(self.gl['df_plots'], self.gl['widgets']['series'].value)
        self.gl['plots'].children = self.create_figures(self.gl['df_plots'], self.gl['widgets'], self.gl['columns'])

    def download(self):
        '''
        Download a csv file of the currently viewed data to the downloads/ directory,
        with the current timestamp.
        '''
        self.gl['df_plots'].to_csv(os.path.dirname(os.path.realpath(__file__)) + '/downloads/out '+
            datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S-%f")+'.csv', index=False)
