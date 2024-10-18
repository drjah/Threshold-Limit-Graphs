# Threshold-Limit-Graphs
Python code to create threshold limit graphs 
This code can produce graphs similar to those described in a free paper on Cureus:
https://www.cureus.com/articles/7823-threshold-limit-graphical-approach-to-understanding-outcome-predictive-metrics-data-from-the-osteoarthritis-initiative#!/

Instructions for Generating Threshold Limit Graphs

These are instructions for generating Threshold Limit graphs (TLgraphs), using the python code: genoutcomepredict.py, with graph specifications obtained from an excel file “input_parameters.xlsx”. The threshold limit graphical approach is described in a paper by Hipp et al. \[1\] Use of a specifications file requires careful, a priori thought about the important outcomes and the variables that might help predict the outcomes, along with the inclusion and exclusion criteria that need to be used when processing the excel file with the raw data.

Note: The program can be run either directly from python code or from an executable that can be created from the python code - e.g. using pyinstaller.

If running from python, the dependencies must first be installed.

1. Prerequisites - In addition to the program, two files are needed:
    1. An Excel format file that has the data to be analyzed. The column labels in this file must match the parameters specified in the file “input_parameters.xlsx”
    2. An Excel format file named “input_parameters.xlsx”
    3. This file must have this exact name
    4. This file specifies all of the TLgraphs that you want created from the data – one row per TLgraph you want created
    5. In the first worksheet, this file must have the following 23 columns (A to W):

| Column name | Description |
| --- | --- |
| excel_file | The name of the excel file with the data to be analyzed. The complete pathname must be specified |
| output_dir | The directory where the TL graphs are to be placed. Using this parameter, you can group TLgraphs into separate folders, for example preop variables that predict preop symptoms, preop variables that predict postop outcomes, etc |
| outcome | The outcome variable that might be predicted by a predictive variable. This must match exactly one of the column headings in the excel file with the data |
| oname | The text used to describe the outcome variable in the TLgraph |
| oLL | The lower limit to be used with the Y-axis in the TLgraph – running descriptive statistics can help here |
| oUL | The upper limit to be used with the Y-axis in the TLgraph |
| variable | The potential predictive variable. This must match exactly one of the column headings in the excel file with the data |
| vname | The text used to describe the predictor variable in the TLgraph |
| filter1 | The first variable in the Excel file to be used to filter the data. This must match exactly one of the column headings in the excel file with the data. Use NA if no filters are needed. |
| f1op | The filter 1 operator. This can be ==, >, &lt; , &gt;=, <=, != or leave blank if unused |
| f1criteria | The numeric criteria to be applied in filter1 |
| filter2 | The second variable in the Excel file to be used to filter the data. |
| f2op | The filter 2 operator. This can be ==, >, &lt; , &gt;=, <=, != |
| f2criteria | The numeric criteria to be applied in filter 2 |
| filter3 | The third variable in the Excel file to be used to filter the data. |
| f3op | The filter 3 operator. This can be ==, >, &lt; , &gt;=, <=, != |
| f3criteria | The numeric criteria to be applied in filter 3 |
| filter4 | The fourth variable in the Excel file to be used to filter the data. |
| f4op | The filter 4 operator. This can be ==, >, &lt; , &gt;=, <=, != |
| f4criteria | The numeric criteria to be applied in filter 4 |
| plot_type | 1 if you only want a graph showing results for values greater than the threshold<br><br>2 if you only want a graph showing results for values less than the threshold<br><br>3 if you only want a graph showing both lines |
| min_n | The minimum number of data points that must exist in order to plot a point in the TLgraph |
| Graphtype | c if mean values of the outcome variable are to be plotted on the y-axis, m if median values of the outcome variable are to be plotted on the y-axis, or p if percentages are to be plotted on the Y-axis (requires a binary outcome variable) |

1. Once both the Excel files have been created, then run the program. The only input required by the program is the directory that contains the Excel file with the input parameters. The full path to the directory should be provided. An example command:

Python genoutcomepredict c:\\rootfolder\\subfolder\\workingdirectory

1. Once the program is running, it will produce the requested plots one by one. Clicking on the X at the upper right of the window will close that plot and create the next plot. Descriptive error messages will be generated when needed. The plots will be saved in the folder specified.
2. To quickly identify potentially predictive metrics, you can view the plots as thumbnails using Windows Explorer. Look for metrics where either the blue line or the red line shows a clear upward or downward trend. If either line (blue or red) displays a consistent trend that passes outside the shaded confidence interval, this indicates that the metric may effectively predict the variable plotted on the Y-axis. Recall:

- Blue Line: Represents data points calculated only when values are above the threshold.
- Red Line: Represents data points calculated only when values are below the threshold.

1. Once the trend is identified using the TL-Graph, you can identify a threshold level that might be used to group data points (e.g. the predictive metric is above the threshold = 1, or 0 if <= the threshold. Then, analysis of variance, tests of proportions, sensitivity, specificity, and many other standard statistical tests can be applied to the data.

1\. Hipp JA, Chan EF. Threshold Limit Graphical Approach to Understanding Outcome Predictive Metrics: Data from the Osteoarthritis Initiative. Cureus. 2017;9(7):e1447.
