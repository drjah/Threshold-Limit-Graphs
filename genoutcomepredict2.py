import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import statsmodels.stats.proportion as smp


class TLGraphGenerator:
    def __init__(self, working_dir):
        if not os.path.exists(working_dir):
            raise ValueError(f"The working directory '{working_dir}' does not exist.")
        self.working_dir = working_dir
        os.chdir(self.working_dir)

    def load_parameters(self, param_file='input_parameters.xlsx'):
        if not os.path.exists(param_file):
            raise ValueError(f"Parameter file '{param_file}' not found in working directory '{self.working_dir}'.")
        self.params_df = pd.read_excel(param_file, engine='openpyxl')

    def load_data(self, excel_file):
        if not os.path.exists(excel_file):
            raise ValueError(f"Data file '{excel_file}' not found.")
        return pd.read_excel(excel_file, engine='openpyxl')

    def apply_filters(self, df, filters):
        for filter_var, filter_op, filter_criteria in filters:
            if pd.notna(filter_var):
                if filter_var not in df.columns:
                    print(f"Warning: Filter variable '{filter_var}' not in data columns, skipping filter.")
                    continue
                query_str = f"`{filter_var}` {filter_op} {filter_criteria}"
                df = df.query(query_str)
        return df

    def generate_graphs(self):
        for _, row in self.params_df.iterrows():
            try:
                # Load data
                df = self.load_data(row['excel_file'])

                # Filter data
                filters = [
                    (row['filter1'], row['f1op'], row['f1criteria']),
                    (row['filter2'], row['f2op'], row['f2criteria']),
                    (row['filter3'], row['f3op'], row['f3criteria']),
                    (row['filter4'], row['f4op'], row['f4criteria'])
                ]
                df = self.apply_filters(df, filters)

                # Drop missing values for predictor and outcome
                df = df.dropna(subset=[row['variable'], row['outcome']])
                if df.empty:
                    print(f"Warning: Dataframe is empty after filtering for '{row['excel_file']}', skipping graph.")
                    continue

                # Plot TL graph
                self.plot_TL_graph(
                    df=df,
                    output_dir=row['output_dir'],
                    outcome=row['outcome'],
                    oname=row['oname'],
                    oll=row['oLL'],
                    oul=row['oUL'],
                    variable=row['variable'],
                    vname=row['vname'],
                    plot_type=int(row['plot_type']),
                    minn=int(row['min_n']),
                    graphtype=row['graphtype']
                )
            except Exception as e:
                print(f"Error processing row '{row}': {e}")

    def plot_TL_graph(self, df, output_dir, outcome, oname, oll, oul, variable, vname, plot_type, minn, graphtype):
        # Set up output directory
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Set up statistic and confidence interval functions
        stat_func, ci_func, y_label = self.get_statistic_functions(outcome, oname, graphtype)
        ci_lower, ci_upper = ci_func(df[outcome].values)
        y_lim = (oll, oul) if graphtype in ['c', 'm'] else (0, 1)

        # Compute thresholds
        thresholds = np.linspace(df[variable].min(), df[variable].max(), 20)
        stats_above, stats_below = self.calculate_statistics(df, variable, outcome, thresholds, minn, stat_func)

        # Plotting
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.set_title(f'{oname} by {vname} Threshold')
        ax.set_ylabel(y_label)
        ax.set_xlabel(f'Threshold level of {vname}')
        ax.set_ylim(y_lim)

        if plot_type in [1, 3]:
            ax.plot(thresholds, stats_above, marker='>', ms=10, fillstyle='none', linestyle='-', color='blue', label='Above threshold')
        if plot_type in [2, 3]:
            ax.plot(thresholds, stats_below, marker='<', ms=10, fillstyle='none', linestyle='-', color='red', label='Below threshold')

        if graphtype in ['c', 'm']:
            ax.fill_between(thresholds, ci_lower, ci_upper, color='purple', alpha=0.2, label='95% CI')
        elif graphtype == 'p':
            ci_lower_arr, ci_upper_arr = np.full_like(thresholds, ci_lower), np.full_like(thresholds, ci_upper)
            ax.fill_between(thresholds, ci_lower_arr, ci_upper_arr, color='purple', alpha=0.2, label='95% CI')

        ax.legend()
        plt.grid(True)
        figpath = os.path.join(output_dir, f"{variable}_{graphtype}_{outcome}_plot{plot_type}.png")
        plt.savefig(figpath)
        plt.close(fig)

    @staticmethod
    def calculate_statistics(df, variable, outcome, thresholds, minn, stat_func):
        stats_above, stats_below = [], []
        for threshold in thresholds:
            filtered_above = df[df[variable] >= threshold]
            filtered_below = df[df[variable] <= threshold]
            stat_above = stat_func(filtered_above[outcome]) if filtered_above[outcome].size >= minn else np.nan
            stat_below = stat_func(filtered_below[outcome]) if filtered_below[outcome].size >= minn else np.nan
            stats_above.append(stat_above)
            stats_below.append(stat_below)
        return stats_above, stats_below

    @staticmethod
    def get_statistic_functions(outcome, oname, graphtype):
        if graphtype == 'c':
            stat_func = np.mean
            ci_func = TLGraphGenerator.bootstrap_mean_confidence_interval
            y_label = 'Average ' + oname
        elif graphtype == 'm':
            stat_func = np.median
            ci_func = TLGraphGenerator.bootstrap_median_confidence_interval
            y_label = 'Median ' + oname
        elif graphtype == 'p':
            stat_func = np.mean  # Mean of binary data gives proportion
            ci_func = lambda data: smp.proportion_confint(data.sum(), data.size, alpha=0.05, method='wilson')
            y_label = 'Proportion of ' + outcome
        else:
            raise ValueError(f"Invalid graphtype '{graphtype}' specified.")
        return stat_func, ci_func, y_label

    @staticmethod
    def bootstrap_mean_confidence_interval(data, num_boots=1000, ci=95):
        samples = np.random.choice(data, size=(num_boots, len(data)), replace=True)
        boot_means = np.mean(samples, axis=1)
        return np.percentile(boot_means, [(100 - ci) / 2, 100 - (100 - ci) / 2])

    @staticmethod
    def bootstrap_median_confidence_interval(data, num_boots=1000, ci=95):
        samples = np.random.choice(data, size=(num_boots, len(data)), replace=True)
        boot_medians = np.median(samples, axis=1)
        return np.percentile(boot_medians, [(100 - ci) / 2, 100 - (100 - ci) / 2])


if __name__ == '__main__':
    working_directory = input("Enter the working directory containing 'input_parameters.xlsx': ")
    try:
        generator = TLGraphGenerator(working_directory)
        generator.load_parameters()
        generator.generate_graphs()
    except Exception as e:
        print(f"Error: {e}")
