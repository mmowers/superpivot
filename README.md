# Exploding Pivot Charts

## Intro
This bokeh app creates multiple pivot charts from data, similar to Tableau.
Currently, ReEDS results and csvs are supported.

A more simplified version of this app has been contributed as an example to the main Bokeh repo:
https://github.com/bokeh/bokeh/tree/master/examples/app/pivot

There are two different ways to use this app: On Orion (easiest way), and locally. See the following sections for details on each:

## Running on Orion (easiest)
1. Simply double click the *Launch Super Pivot.bat* file on your desktop on Orion. This will launch the bokeh server in a terminal window and a browser window for the results
    * If you're curious, you can open the .bat file in a text editor. The contents will look like:
      ```
      start bokeh serve D:\CommonGitRepos\Bokeh\superpivot   --host 1wp11rdori01.nrel.gov:<port> --host localhost:<port> --port  <port> 
      explorer http://1wp11rdori01.nrel.gov:<port>/superpivot 
      ```
    * Here is a breakdown of the contents of *Launch Super Pivot.bat*:
        * `bokeh serve`: Launch bokeh server. See http://bokeh.pydata.org/en/latest/docs/user_guide/server.html for more info.
        * `D:\CommonGitRepos\Bokeh\superpivot`: Path to bokeh app that we are running. Note that this app will be updated frequently. If you want to manage your own copies on Orion, simply copy this app and enter the new path in the .bat file instead.
        * `--host 1wp11rdori01.nrel.gov:<port> --host localhost:<port>`: The first host allows requests that are external to Orion (but on the NREL network) to access this bokeh server. The Second allows internal requests to localhost.
        * `--port <port>`: Jonathan has assigned you a unique port on Orion to run your bokeh server. We can't all use the same port number because each port can only be used once.
        * `explorer ...`: Open browser window for superpivot.
1. Go to the *Loading ReEDS data* section below.
1. When done, simply close the terminal window that is running the server.

## Running Locally
1. If you don't already have Python/Bokeh, Easiest way is to get Anaconda for python 2.7 at:
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
1. This tool reads from the gdx outputs from ReEDS runs. The gams python bindings need to be installed so the necessary python modules are available for reading gdx data into Python. On command line, navigate to the Python API files for Python 2.7, e.g. C:\\GAMS\\win64\\24.7\\apifiles\\Python\\api and run this command:
    ```
    python setup.py install
    ```
1. Finally, git clone this repo to your computer, and on command line (or git bash) enter
    ```
    bokeh serve --show \path\to\this\repo
    ```
    This will launch the bokeh server and a browser window to view the app.
    * Note that we simply used the same command to start the bokeh server process on Orion:
      ```
      bokeh serve D:\CommonGitRepos\Bokeh\superpivot
      ```
1. Go to the *Loading ReEDS data* section below

## Loading data
After starting up the app in a browser window, you must enter a path in the *Data Source* field, either to a CSV file or to a ReEDS run or set of runs:
    * *CSV*: Enter a path to a csv file. This file must be properly formatted, with column headers but no row headers. You can *Shift+Right Click* on a csv file, then select *Copy as Path* to get the full path to a file. After that, see the *Core Pivot Functionality* section below.
    * *ReEDS Run(s)*: Here are the options:
        * Enter a path to a ReEDS run folder (inside which there is a *gdxfiles/* folder). This works using shared drives too. For example,  *\\\\nrelqnap01d\\ReEDS\\someProject\\runs\\someRun*.
        * Enter a path to a folder containing ReEDS run folders. For example,  *\\\\nrelqnap01d\\ReEDS\\someProject\\runs*.
        * Enter a path to a csv file that contains a list of runs (see *csv/scenario_template.csv* for an example.)
        After that, see the *ReEDS Widgets* and *Core Pivot Functionality* sections below.

## ReEDS Widgets
* *Meta*: Click the *Meta* section to expand, and see the files used for some default *maps* (to rename and aggregate ReEDS categories), *styles* (to reorder categories and style them), and *merges* (to join more columns, e.g. to add regional aggregations). If you'd like to update any of these files, simply edit the file (only if you're working locally), or point to a new file.
* *Filter Scenarios*: A list of scenarios will be fetched after entering a path in *Runs*. Use the *Filter Scenarios* section to reduce the scenarios from which the app will fetch data.
* *Result*: Select a result from the *Result* select box. It may take a few seconds to fetch the data, depending on the number of scenarios being analyzed. After the result data is fetched, the following widgets will appear
* *Presets*: You may select a preset result from the *Preset* select box. For example, for *Generation*, *Stacked Generation* is a preset result.
* See the *Core Pivot Functionality* section below for the rest of the available widgets.

## Core Pivot Functionality
* X-axis (required): Select a column to use as x-axis
* Group X By: Select a column to group the x-axis (if both x-axis and grouping columns are discrete).
* Y-axis (required): Select a column to use as y-axis
* *Y-Axis Aggregation*: Select *Sum*, *Average*, or *Weighted Average*. *Weighted Average* requires another field, the *Weighting Factor*. For electricity price, for example, select *load* as the *Weighting Factor*.
* Series: Pick a column to split the data into separate, color-coded series. If Chart Type (see Plot Adjustments
below) is Area or Bar, series will automatically be stacked. If Chart Type is Line or Dot, the series will not be stacked.
* Series Legend: Click on this to see the color and name of each series
* Explode By: Select a discrete column to split into multiple charts. The charts' titles will correspond to the
exploded column values.
* Group Exploded Charts By: Select a discrete column to group exploded charts. Play around with plot sizes (see below)
and/or resize your browser screen to make a nice 2d array of charts.
* *Comparisons*: This section allows comparisons across any dimension. You first select the *Operation*, then the column you'd like to *Operate Across*, then the *Base* that you'd like to compare to. Here are a couple examples for ReEDS results:
    * Generation differences: Select *Generation* as *Result*, and select *Stacked Gen* under *Presets*. Then, under *Comparisons*, select *Operation*=*Difference*, *Operate Across*=*scenario*, and *Base*=your-base-case.
    * Generation Fraction: Select *Generation* as *Result*, and select *Stacked Gen* under *Presets*. Then, under *Comparisons*, select *Operation*=*Ratio*, *Operate Across*=*tech*, and *Base*=*Total*.
    * Capacity Differences, solve-year-to-solve-year: Select *Capacity* as *Result*, and select *Stacked Capacity* under *Presets*. Then, under *Comparisons*, select *Operation*=*Difference*, *Operate Across*=*year*, and *Base*=*Consecutive*.
* Filters: Each column can be used to filter data with checkboxes. After selecting Filters, you must press
the Update Filters button to apply the filters
* Update Filters: This is used for updating the charts once filters have been changed
* Plot Adjustments: Make additional modifications to the chart type, size, x-axis/y-axis limits and scale, etc.
* *Download*: Download any data you're viewing with the *Download csv of View* button, or download all data for a given source/result with the *Download csv of Source* button. It will be downloaded into a timestamped file in the *downloads\\* folder. Note that if you're accessing a bokeh server on Orion, this folder is in *D:\\CommonGitRepos\\Bokeh\\superpivot*
* *Export Config to URL*: Save any widget configuration for later use with this button, and copy the resulting URL from the address bar. At a later time, you will be able to load the same view by simply visiting that URL (with your bokeh server running). If the URL is from Orion, you may access the URL from any computer connected to the NREL network (while the bokeh server on Orion is still running). Currently you cannot use the same URL on different machines that are running different bokeh servers because the paths to files in the *Meta* section are different (work in progress).


## Pro tips
1. Pressing *Alt* will collapse all expandable sections.
1. To suppress the automatic update of the plot while configuring the widgets, simply set *X-axis* to *None* to stop rendering of plots, then make your widget changes, then finally set *X-axis* to the value you'd like.
1. You may interact with the bokeh server with multiple browser windows/tabs, and these interactions will be independent, so you can leave one result open in one tab while you load another in a separate tab, for example.
1. The charts themselves have some useful features shown on the right-hand-side of each chart. For example, hovering over data on a chart will show you the series, x-value, and y-value of the data (not currently working for Area charts). You may also box-zoom or pan (and reset to go back to the initial view). Finally, the charts can be saved as pngs.

## Troubleshooting
1. If the window becomes unresponsive, simply refresh the page (you may want to export config first).
1. If a page refresh doesn't work, then restart the bokeh server. If you have time, you can send Matt a screenshot of the error in the terminal window, if there is one.

## Modifying App Code
* On local, modify the code at will. If the modifications would be useful for other team members, please push the changes back to origin.
* On Orion, please create a copy of D:\\CommonGitRepos\\Bokeh\\superpivot and make modifications to that copy so that you don't effect others who are working off the common repo.

## Additional Resources
This tool uses bokeh, built on python:
http://bokeh.pydata.org/en/latest/.
The site has good documentation in the User Guide and Reference.

There is also an active google group for issues:
https://groups.google.com/a/continuum.io/forum/#!forum/bokeh

And of course, python has good documentation too:
https://docs.python.org/2.7/tutorial/
