import pandas as pd
from pharmacy_sim import Experiment

def get_example_csv(filename="example.csv"):
    """
    Create an example CSV file you can use.
    This creates 3 experiments with different simulation
    parameters.

    Params:
    ------
    filename: str, optional (default='example.csv')
        The name and path to the CSV file.
    """
    # each column is defined as a seperate list
    names = ["standard", "busy_day", "flu_season"]
    counters = [3, 4, 3]
    arrival_lambda = [1.3, 1.75, 1.6]
    choice_p = [0.6, 0.6, 0.2]
    travel_time = [30, 40, 30]
    travel_noise = [10, 10, 10]
    check_interval = [60, 90, 30]

    # empty dataframe
    df_experiments = pd.DataFrame()

    # create new columns from lists
    df_experiments["experiment"] = names
    df_experiments["n_counters"] = counters
    df_experiments["arrival_lambda"] = arrival_lambda
    df_experiments["choice_p"] = choice_p
    df_experiments["travel_time"] = travel_time
    df_experiments["travel_noise"] = travel_noise
    df_experiments["check_interval"] = check_interval

    return df_experiments


def create_experiments(df_experiments):
    '''
    Returns dictionary of Experiment objects based on contents of a dataframe

    Params:
    ------
    df_experiments: pandas.DataFrame
        Dataframe of experiments. First two columns are id, name followed by 
        variable names.  No fixed width.

    Returns:
    --------
    dict
    '''
    experiments = {}
    exp_dict = df_experiments[df_experiments.columns[1:]].T.to_dict()
    exp_names = df_experiments[df_experiments.columns[0]].T.to_list()
    
    print(exp_dict)
    print(exp_names)

    # loop through params and create Experiment objects.
    for name, params in zip(exp_names, exp_dict.values()):
        print(name)
        experiments[name] = Experiment(**params)
    
    return experiments