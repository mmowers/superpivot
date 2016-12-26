## Intro
This bokeh app creates pivot charts from data, similar to Excel's pivot
chart functionality, but with the additional ability to explode into
multiple filterable charts.

The code was developed starting from Bokeh/examples/app/crossfilter.

The code is data-agnostic, so any other data 

## Setting Up From Scratch
Get Anaconda for python 2.7 at:
https://www.continuum.io/downloads

Then, here are the Bokeh installation instructions:
http://bokeh.pydata.org/en/latest/docs/installation.html
Easiest way, with Anaconda, from the command line:
```
conda install bokeh
```
Then, git clone this repo onto your computer.

## Running
From command line, cd into this git repo and type:
```
bokeh serve --show .
```
This will launch a browser window with the viewer. To see
a plot, you'll have to select the columns to use for x-axis and y-axis.
In addition you have these widgets:
* Chart Type: Select Scatter, Line, Bar, or Area
* Group X by: Select a column to group the x-axis (if both x-axis and grouping columns are discrete).
* Y-axis aggregation: You may aggregate y-axis data if it is numeric. "Sum" is currently the only option.
* Series: Pick a column to split the data into separate, color-coded series
* Series Legend: Click on this to see the color and name of each series
* Unstacked/Stacked: You may stack/unstack series vertically with this switch
* Size: Select a numeric column to represent sizes (only used for Scatter charts)
* Explode: Select a discrete column to split into multiple charts. The charts' titles will correspond to the
exploded column values.
* Filters: Each column can be used to filter data with checkboxes. After selecting Filters, you must press
the Update button to apply the filters
* Update: This is only used for updating the charts once filters have been changed
* Plot adjustments: Make additional modifications to the chart size and x-axis/y-axis limits and scale.


## Viewing data from other csvs
Simply put your data into csv/data.csv. Make sure that there are column headers (without spaces) and no row labels.

## Bokeh
This tool uses bokeh, built on python:
http://bokeh.pydata.org/en/latest/.
The site has good documentation in the User Guide and Reference.

There is also an active google group for issues:
https://groups.google.com/a/continuum.io/forum/#!forum/bokeh

And of course, python has pretty good documentation too:
https://docs.python.org/2.7/tutorial/