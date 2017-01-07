# Exploding Pivot Charts

## Intro
This bokeh app creates pivot charts from data, similar to Excel's pivot
chart functionality, but with the additional ability to explode into
multiple pivot charts.

The code was developed starting from Bokeh/examples/app/crossfilter.

The code is data-agnostic, so any other properly formatted data can
be used in place of csv/power.csv (see below) and be visualized.

## Setting Up From Scratch
Get Anaconda for python 2.7 or 3.5 at:
https://www.continuum.io/downloads

You can check if Anaconda automatically installed bokeh by going to
command line and simply entering:
```
bokeh
```
If you get a message that says
```
ERROR: Must specify subcommand...
```
you already have Bokeh. If not, here are the Bokeh installation instructions:
http://bokeh.pydata.org/en/latest/docs/installation.html. The easiest way,
from the command line:
```
conda install bokeh
```
Finally, git clone this repo onto your computer with:
```
git clone https://github.com/mmowers/superpivot.git
```

## Running
From command line, cd into the superpivot repo and type:
```
bokeh serve --show .
```
This will launch a browser window with the viewer. To see
a plot, you'll have to select the columns to use for x-axis and y-axis, which are two of the widgets
on the left-hand side of the screen. Here is the full list of widgets:
* Data Source (required): Enter a path to a properly formatted csv file (see below). The path is relative to the
root of this repo, but absolute paths may be entered as well, e.g. 'C:/somefolder/somefile.csv'. Make sure
that there are column headers for each column in the csv file and no row labels.
* X-axis (required): Select a column to use as x-axis
* Y-axis (required: Select a column to use as y-axis
* Series: Pick a column to split the data into separate, color-coded series
* Series Legend: Click on this to see the color and name of each series
* Separate Charts By: Select a discrete column to split into multiple charts. The charts' titles will correspond to the
exploded column values.
* Group X By: Select a column to group the x-axis (if both x-axis and grouping columns are discrete).
* Y-axis aggregation: You may aggregate y-axis data if it is numeric. "Sum" is currently the only option.
* Series Stacking: You may stack/unstack series vertically with this switch
* Chart Type: Select Scatter, Line, Bar, or Area
* Filters: Each column can be used to filter data with checkboxes. After selecting Filters, you must press
the Update button to apply the filters
* Update Filters: This is only used for updating the charts once filters have been changed
* Plot adjustments: Make additional modifications to the chart size, x-axis/y-axis limits and scale, etc.
* Download csv: This will download the data you are viewing (after applying filters, aggregation, etc.) into
a csv file in the downloads/ folder

## Resources
This tool uses bokeh, built on python:
http://bokeh.pydata.org/en/latest/.
The site has good documentation in the User Guide and Reference.

There is also an active google group for issues:
https://groups.google.com/a/continuum.io/forum/#!forum/bokeh

And of course, python has pretty good documentation too:
https://docs.python.org/2.7/tutorial/
https://docs.python.org/3.5/tutorial/