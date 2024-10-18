''' code to calculate Threshold Limit (TL) Graphs as described in 
    Hipp JA, Chan EF. Threshold Limit Graphical Approach to Understanding Outcome Predictive Metrics:
                    Data from the Osteoarthritis Initiative. Cureus 2017;9:e1447.

This code requires one command line parameter: the directory where the input file is located
There must be an Excel format input file in that directory named input_parameters.xlsx that has 24 columns of data:
    Column A "excel_file": the filename of the excel format file with all of the data that will be used to generate the TL graphs
                the data to be used must be in the first worksheet in that file. There can be other worksheets - they are ignored
    Column B "output_dir": The full path of the directory to store the TL graphs
                This can help to group TL graphs into folders
    Column C "outcome": The name of the variable with the outcome variable to be predicted
                This must exactly match one of the column names in the input excel file
    Column D "oname": The text that will be used to label the Y-axis in the TL graph
    Column E "oLL": The lower limit of the Y-Axis
    Column F "oUL": The upper limit of the Y-Axis
    Column G "variable": The name of the variable to be tested for it's ability to predict the outcome
                This must exactly match one of the column names in the input excel file
    Column H "vname": The text that will be used to label the X-axis in the TL graph
    Column I "filter1": The name of the variable that may be used to filter the data. Enter "NA" if you don't want to use filter 1
                This must exactly match one of the column names in the input excel file
    Column J "f1op": The filter 1 operation to be applied. this can be: ==, >, >=, <, <=, !=
    Column K "f1criteria": The criteria top be applied in the filter - eg variable == 2
    Column I "filter2": The name of the variable that may be used to filter the data. Enter "NA" if you don't want to use filter 2
                This must exactly match one of the column names in the input excel file
    Column J "f2op": The filter 2 operation to be applied. this can be: ==, >, >=, <, <=, !=
    Column K "f2criteria": The criteria top be applied in the filter - eg variable == 2
    Column I "filter3": The name of the variable that may be used to filter the data. Enter "NA" if you don't want to use filter 3
                This must exactly match one of the column names in the input excel file
    Column J "f3op": The filter 3 operation to be applied. this can be: ==, >, >=, <, <=, !=
    Column K "f3criteria": The criteria top be applied in the filter - eg variable == 2
    Column I "filter4": The name of the variable that may be used to filter the data. Enter "NA" if you don't want to use filter 4
                This must exactly match one of the column names in the input excel file
    Column J "f4op": The filter 4 operation to be applied. this can be: ==, >, >=, <, <=, !=
    Column K "f4criteria": The criteria top be applied in the filter - eg variable == 2
    Column L "plot type":   1 if you only want a graph showing results for values greater than the threshold
                            2 if you only want a graph showing results for values less than the threshold
                            3 if you only want a graph showing both lines
    Column M "min n": The minimum number of data points that must exist in order to plot a point in the TLgraph
    Column N "Graphtype":   c if mean values of the outcome variable are to be plotted on the y-axis,
                            m if median values of the outcome variable are to be plotted on the y-axis, or
                            p if percentages are to be plotted on the Y-axis (requires a binary outcome variable)



'''
    



import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import statsmodels.stats.proportion as smp

if len(sys.argv) != 2:
    raise ValueError('The working directory with the required file: input_parameters.xlsx must be specified in the command line.')
working_dir = sys.argv[1]
if not os.path.exists(working_dir):
    print("The working directory:", working_dir, "does not exist")
    sys.exit()
chk = os.path.join(working_dir, "input_parameters.xlsx")
if not os.path.exists(chk):
    print("The required file:", chk, "that contains all the specifications for the graphs, does not exist")
    sys.exit()

# Set random seed once for reproducibility
np.random.seed(0)

def bootstrap_mean_confidence_interval(data, num_boots=1000, ci=95):
    samples = np.random.choice(data, size=(num_boots, len(data)), replace=True)
    boot_means = np.mean(samples, axis=1)
    lower_bound = np.percentile(boot_means, (100 - ci) / 2)
    upper_bound = np.percentile(boot_means, 100 - (100 - ci) / 2)
    return lower_bound, upper_bound

def bootstrap_median_confidence_interval(data, num_boots=1000, ci=95):
    samples = np.random.choice(data, size=(num_boots, len(data)), replace=True)
    boot_medians = np.median(samples, axis=1)
    lower_bound = np.percentile(boot_medians, (100 - ci) / 2)
    upper_bound = np.percentile(boot_medians, 100 - (100 - ci) / 2)
    return lower_bound, upper_bound

def apply_filters(df, filters, excel_file):
    for filter_var, filter_op, filter_criteria in filters:
        if pd.notna(filter_var):
            if filter_var not in df.columns:
                print("\nThe filter variable:", filter_var, "is not in", excel_file)
                continue
            query_str = f"`{filter_var}` {filter_op} {filter_criteria}"
            df = df.query(query_str)
    return df

def plot_TL_graph(df, output_dir, outcome, oname, oll, oul, variable, vname, plot_type, minn, graphtype):
    # Set up statistic and confidence interval functions based on graph type
    if graphtype == 'c':
        stat_func = np.mean
        ci_func = bootstrap_mean_confidence_interval
        y_label = 'Average ' + oname
        ci_lower, ci_upper = ci_func(df[outcome].values)
        y_lim = (oll, oul)
    elif graphtype == 'm':
        stat_func = np.median
        ci_func = bootstrap_median_confidence_interval
        y_label = 'Median ' + oname
        ci_lower, ci_upper = ci_func(df[outcome].values)
        y_lim = (oll, oul)
    elif graphtype == 'p':
        # For proportions, outcome should be binary (0/1)
        stat_func = np.mean  # Mean of binary data gives proportion
        cnt = df[outcome].sum()
        nobs = df[outcome].size
        ci_lower, ci_upper = smp.proportion_confint(cnt, nobs, alpha=0.05, method='wilson')
        y_label = 'Proportion of patients ' + oname
        y_lim = (0, 1)
    else:
        print("Invalid graph type")
        return

    # Compute thresholds
    thresholds = np.linspace(df[variable].min(), df[variable].max(), 20)
    stats_above = []
    stats_below = []

    for threshold in thresholds:
        filtered_above = df[df[variable] >= threshold]
        filtered_below = df[df[variable] <= threshold]
        stat_above = stat_func(filtered_above[outcome]) if filtered_above[outcome].size >= minn else np.nan
        stat_below = stat_func(filtered_below[outcome]) if filtered_below[outcome].size >= minn else np.nan
        stats_above.append(stat_above)
        stats_below.append(stat_below)

    # Generate the plot
    fig, ax = plt.subplots(figsize=(10, 6))
    plot_title = f'{oname} by {vname} Threshold'
    ax.set_title(plot_title)
    ax.set_ylabel(y_label)
    ax.set_xlabel(f'Threshold level of {vname}')
    ax.set_ylim(y_lim)

    if plot_type == 1 or plot_type == 3:
        ax.plot(thresholds, stats_above, marker='>', ms=10, fillstyle='none', linestyle='-', color='blue', label='Includes only above threshold')
    if plot_type == 2 or plot_type == 3:
        ax.plot(thresholds, stats_below, marker='<', ms=10, fillstyle='none', linestyle='-', color='red', label='Includes only below threshold')

    if graphtype in ['c', 'm']:
        ax.fill_between(thresholds, ci_lower, ci_upper, color='purple', alpha=0.2, label='95% CI')
    elif graphtype == 'p':
        # For proportions, ci_lower and ci_upper are scalars
        ci_lower_arr = np.full_like(thresholds, ci_lower)
        ci_upper_arr = np.full_like(thresholds, ci_upper)
        ax.fill_between(thresholds, ci_lower_arr, ci_upper_arr, color='purple', alpha=0.2, label='95% CI')

    ax.legend()
    plt.grid(True)
    figname = f"{variable}_{graphtype}_{outcome}_plot{plot_type}.png"
    figpath = os.path.join(output_dir, figname)
    print("Writing to:", figpath)
    plt.savefig(figpath)
    # plt.show()  # optional
    plt.close(fig)  # Close the figure to free memory

def main():
    os.chdir(working_dir)
    # Read parameters from the input Excel file
    params_df = pd.read_excel('input_parameters.xlsx', engine='openpyxl')
    for index, row in params_df.iterrows():
        excel_file = row['excel_file']
        if not os.path.exists(excel_file):
            print("The Excel file:", excel_file, "specified in the first column of input_parameters.xlsx does not exist")
            continue
        output_dir = row['output_dir']
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        graphtype = row['graphtype']  # c for mean, m for median, p for proportion
        outcome = row['outcome']
        oname = row['oname']
        oll = row['oLL']
        oul = row['oUL']
        variable = row['variable']
        vname = row['vname']
        filter1 = row['filter1']
        f1op = row['f1op']
        f1criteria = row['f1criteria']
        filter2 = row['filter2']
        f2op = row['f2op']
        f2criteria = row['f2criteria']
        filter3 = row['filter3']
        f3op = row['f3op']
        f3criteria = row['f3criteria']
        filter4 = row['filter4']
        f4op = row['f4op']
        f4criteria = row['f4criteria']
        plot_type = int(row['plot_type'])
        minn = int(row['min_n'])

        filters = [
            (filter1, f1op, f1criteria),
            (filter2, f2op, f2criteria),
            (filter3, f3op, f3criteria),
            (filter4, f4op, f4criteria)
        ]

        # Read the data
        df = pd.read_excel(excel_file, engine='openpyxl')

        # Check that outcome and variable are in columns
        if outcome not in df.columns:
            print("\nThe outcome variable:", outcome, "is not in", excel_file)
            continue
        if variable not in df.columns:
            print("\nThe predictor variable:", variable, "is not in", excel_file)
            continue

        # Apply filters
        df = apply_filters(df, filters, excel_file)

        # Remove rows with missing data in variable or outcome
        df = df.dropna(subset=[variable, outcome])

        # Ensure that df is not empty after filtering
        if df.empty:
            print("Dataframe is empty after applying filters.")
            continue

        plot_TL_graph(df, output_dir, outcome, oname, oll, oul, variable, vname, plot_type, minn, graphtype)

if __name__ == "__main__":
    main()
