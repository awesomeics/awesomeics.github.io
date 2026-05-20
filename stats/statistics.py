import matplotlib.pyplot as plt
import pandas as pd
from yaml import safe_load
import numpy as np

# Set output format: PDF for papers, PNG for website
OUTPUT_FORMAT = 'png'  
# Decide whether to show the plots or not. Set to False for website. 
VERBOSE = False


def paper_per_type_vs_year(yml_file_path, cat, cumulative=False, filename="", keep_only = []):
    """
    Plots the number of papers per type (journal, conference, etc.) over the years.
    
    Parameters:
    yml_file_path (str): The path to the YAML file containing the paper data.
    cat (str): The column name for the category to group by.
    cumulative (bool): Whether to plot cumulative counts. Default is False.
    
    Returns:
    None: Displays a plot of the number of papers per type over the years.
    """

    if not filename:
        filename = f'stats/figures/papers_per_{cat}_over_years.{OUTPUT_FORMAT}'

    # Load the YAML file
    with open(yml_file_path, 'r') as file:
        data = safe_load(file)
    
    df = pd.DataFrame(data)
    
    # consider that elements in "cat" may be lists, so we need to explode them
    if df[cat].apply(lambda x: isinstance(x, list)).any():
        df = df.explode(cat)
    
    if cat == "protocol":
        # Renames to improve visualization 
        rename_dict = {
            "Modbus/RTU": "Modbus Serial",
            "Modbus/ASCII": "Modbus Serial",
            "Modbus": "Modbus/TCP",
            "OPC UA": "OPC",
            "IEC 104": "IEC 104/61850",
            "IEC 61850": "IEC 104/61850",
            "Profinet": "Others",
            "Profibus": "Others",
            "MQTT": "Others",
            "FINS": "Others",
            "ISO-TSAP/S7": "Others",
            "WirelessHART": "Others",
            "Proprietary": "Others", 
            "EtherCAT": "Others",
            "Not specified": "Others",
            "CIP": "Ethernet/IP",
        }
        df[cat] = df[cat].replace(rename_dict)

    # if keep_only is not empty, filter the paper_counts to keep only the categories in keep_only
    if keep_only:
        df = df[df[cat].isin(keep_only)]

    # Group by year and type, then count the number of papers
    paper_counts = df.groupby(['year', cat]).size().reset_index(name='count')


    # drop 2026
    #paper_counts = paper_counts[paper_counts['year'] < 2026]

    if cumulative:
        # for every year, sum the counts of all previous years for each category
        paper_counts['count'] = paper_counts.groupby(cat)['count'].cumsum()
        # for years with no papers, we need to fill the count with the previous year's count
        # do this manually by iterating over the years and categories
        years = sorted(paper_counts['year'].unique())
        categories = sorted(paper_counts[cat].unique())
        for category in categories:
            last_count = 0
            for year in years:
                if not ((paper_counts['year'] == year) & (paper_counts[cat] == category)).any():
                    paper_counts = pd.concat(
                        [
                            paper_counts,
                            pd.DataFrame([{'year': year, cat: category, 'count': last_count}])
                        ],
                        ignore_index=True,
                    )
                else:
                    last_count = paper_counts[(paper_counts['year'] == year) & (paper_counts[cat] == category)]['count'].values[0]
        

    # Create a line plot using seaborn
    plt.figure(figsize=(12, 6))

    plt.rcParams.update({'font.size': 15})
    
    # Pivot data to have years as x and categories as separate columns
    pivot = paper_counts.pivot(index='year', columns=cat, values='count').fillna(0)
    for column in pivot.columns:
        line, = plt.plot(pivot.index, pivot[column], marker='o', label=str(column))
        # # Add linear fit for each column
        # z = np.polyfit(pivot.index, pivot[column], 1)
        # p = np.poly1d(z)
        # #plt.plot(pivot.index, p(pivot.index), linestyle='--', alpha=0.7, color=line.get_color())
    plt.legend(title='Testbed Type')

    # add vertical dotted line for 2021; only for paper version
    if OUTPUT_FORMAT == 'pdf':
        plt.axvline(x=2021, color='gray', linestyle='--', alpha=0.5)
    
    # Set plot labels and title
    #plt.title('Number of Papers per Type Over the Years')
    plt.xlabel('Year')
    plt.ylabel('Number of Papers')
    plt.legend(title='Testbed Type')

    # set one tick every to years
    plt.xticks(np.arange(paper_counts['year'].min(), paper_counts['year'].max() + 1, 2))

    # Show the plot
    plt.tight_layout()
    plt.grid(alpha=0.2)
    plt.savefig(filename, bbox_inches='tight', dpi=300)
    if VERBOSE: plt.show()



def number_of_data_type_over_time(yml_file_path, cat, cumulative=False, filename="", keep_only = []):

    if not filename:
        filename = f'stats/figures/{cat}_over_time.{OUTPUT_FORMAT}'

    # Load the YAML file
    with open(yml_file_path, 'r') as file:
        data = safe_load(file)
    
    df = pd.DataFrame(data)
    
    # create a new column "source_count" with the size of the list in the "cat" column, if it's a list, otherwise 1
    df['source_count'] = df[cat].apply(lambda x: len(x) if isinstance(x, list) else 1)
    

    # if keep_only is not empty, filter the paper_counts to keep only the categories in keep_only
    if keep_only:
        df = df[df[cat].isin(keep_only)]

    # Group by year and type, then source_count the number of papers
    paper_counts = df.groupby(['year', 'source_count']).size().reset_index(name='count')

    # drop 2026
    #paper_counts = paper_counts[paper_counts['year'] < 2026]

    if cumulative:
        # for every year, sum the counts of all previous years for each category
        paper_counts['count'] = paper_counts.groupby('source_count')['count'].cumsum()
        # for years with no papers, we need to fill the count with the previous year's count
        # do this manually by iterating over the years and categories
        years = sorted(paper_counts['year'].unique())
        categories = sorted(paper_counts['source_count'].unique())
        for category in categories:
            last_count = 0
            for year in years:
                if not ((paper_counts['year'] == year) & (paper_counts['source_count'] == category)).any():
                    paper_counts = pd.concat(
                        [
                            paper_counts,
                            pd.DataFrame([{'year': year, 'source_count': category, 'count': last_count}])
                        ],
                        ignore_index=True,
                    )
                else:
                    last_count = paper_counts[(paper_counts['year'] == year) & (paper_counts['source_count'] == category)]['count'].values[0]
        

    # Create a stacked bar plot
    plt.figure(figsize=(12, 6))

    plt.rcParams.update({'font.size': 15})
    
    # Pivot data to have years as x and categories as separate columns
    pivot = paper_counts.pivot(index='year', columns='source_count', values='count').fillna(0)
    # Convert to percentages (each year sums to 100%)
    pivot_pct = pivot.div(pivot.sum(axis=1), axis=0) * 100

    num_colors_needed = len(pivot_pct.columns)
    # Generate a color palette with the required number of colors that spans from a light blue to a dark blue
    colors_to_use = plt.cm.Blues(np.linspace(0.3, 0.9, num_colors_needed))

    pivot_pct.plot(kind='bar', stacked=True, ax=plt.gca(), color=colors_to_use)
    
    # Set plot labels and title
    #plt.title('Number of Papers per Type Over the Years')
    plt.xlabel('Year')
    plt.ylabel('Percentage (%)')
    if cat == "data_type": cat = "Data Type"
    if cat == "attacks": cat = "Attack Type"
    plt.legend(title=f'{cat} Count')

    # set one tick every to years
    #plt.xticks(np.arange(paper_counts['year'].min(), paper_counts['year'].max() + 1, 2))

    # Show the plot
    plt.tight_layout()
    plt.grid(alpha=0.2)
    plt.savefig(filename, bbox_inches='tight', dpi=300)
    if VERBOSE:
        plt.show()


def dataset_vs_testbed_over_time(yml_file_path_dataset, yml_file_path_testbed, cumulative=False, two_axis=False):
    """
    Plot the number of datasets and testbeds over time, to see if there is a correlation between the two.
    
    Parameters:
    yml_file_path_dataset (str): The path to the YAML file containing the dataset data.
    yml_file_path_testbed (str): The path to the YAML file containing the testbed data.
    cumulative (bool): Whether to plot cumulative counts. Default is False.
    two_axis (bool): Whether to use two y-axes for the plot. Default is False.
    """

    # Load the YAML files
    with open(yml_file_path_dataset, 'r') as file:
        dataset_data = safe_load(file)
    
    with open(yml_file_path_testbed, 'r') as file:
        testbed_data = safe_load(file)
    
    df_dataset = pd.DataFrame(dataset_data)
    df_testbed = pd.DataFrame(testbed_data)
    
    # Group by year and count
    dataset_counts = df_dataset.groupby('year').size().reset_index(name='datasets')
    testbed_counts = df_testbed.groupby('year').size().reset_index(name='testbeds')
    
    # Apply cumulative if requested
    if cumulative:
        dataset_counts['datasets'] = dataset_counts['datasets'].cumsum()
        testbed_counts['testbeds'] = testbed_counts['testbeds'].cumsum()
    
    # Merge on year
    merged = pd.merge(dataset_counts, testbed_counts, on='year', how='outer').fillna(0)
    
    # Create a figure with one or two y-axes
    fig, ax1 = plt.subplots(figsize=(12, 6))
    plt.rcParams.update({'font.size': 15})
    
    if two_axis:
        # Plot datasets on the first y-axis
        color1 = 'tab:blue'
        ax1.set_xlabel('Year', fontsize=16)
        ax1.set_ylabel('Number of Datasets', color=color1, fontsize=16)
        line1 = ax1.plot(merged['year'], merged['datasets'], marker='o', color=color1, label='Datasets')
        ax1.tick_params(axis='x', labelsize=15)
        ax1.tick_params(axis='y', labelcolor=color1, labelsize=15)
        # Create second y-axis for testbeds
        ax2 = ax1.twinx()
        color2 = 'tab:orange'
        ax2.set_ylabel('Number of Testbeds', color=color2, fontsize=16)
        line2 = ax2.plot(merged['year'], merged['testbeds'], marker='s', color=color2, label='Testbeds')
        ax2.tick_params(axis='y', labelcolor=color2, labelsize=15)

        # Add legend
        lines = line1 + line2
        labels = [l.get_label() for l in lines]
        ax1.legend(lines, labels, loc='upper left')
    else:
        ax1.set_xlabel('Year', fontsize=16)
        ax1.set_ylabel('Number of Items', fontsize=16)
        ax1.plot(merged['year'], merged['datasets'], marker='o', color='tab:blue', label='Datasets')
        ax1.plot(merged['year'], merged['testbeds'], marker='s', color='tab:orange', label='Testbeds')
        ax1.tick_params(axis='x', labelsize=15)
        ax1.tick_params(axis='y', labelsize=15)
        ax1.legend(loc='upper left')
    
    # Add grid
    ax1.grid(alpha=0.2)

    # add vertical dotted line for 2021; only for paper version
    if OUTPUT_FORMAT == 'pdf':
        plt.axvline(x=2021, color='gray', linestyle='--', alpha=0.5)
    
    # Set x-ticks
    ax1.set_xticks(np.arange(merged['year'].min(), merged['year'].max() + 1, 2))
    
    plt.tight_layout()
    plt.savefig(f'stats/figures/datasets_vs_testbeds_over_time.{OUTPUT_FORMAT}', bbox_inches='tight', dpi=300)
    if VERBOSE:
        plt.show()

# Example usage:
dataset_vs_testbed_over_time('_data/datasets.yml', '_data/testbeds.yml', cumulative=True, two_axis=False)
paper_per_type_vs_year('_data/testbeds.yml', "category", cumulative=True)
paper_per_type_vs_year('_data/testbeds.yml', "protocol", cumulative=True)
number_of_data_type_over_time('_data/datasets.yml', "data_type", cumulative=False)
number_of_data_type_over_time('_data/datasets.yml', "attacks", cumulative=False)
