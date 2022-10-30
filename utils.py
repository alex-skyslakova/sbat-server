import pandas as pd


def get_n_percent(df, n, tail=False):
    """
    Function to extract top (tail=False) or bottom (tail=True) n percent of data sorted by strand bias.
    :param df: dataframe from which we want to extract part of data
    :param n: number of percent of data we want to extract
    :param tail: if false, data are taken from top of the dataset, else from tail
    :return: DataFrame containing top or bottom n% of input DF

    """
    if tail:
        return df.tail(int(len(df) * (n / 100)))
    else:
        return df.head(int(len(df) * (n / 100)))



class CalculatedGCData:
    def __init__(self):
        self.upper_gc = []
        self.upper_biases = []
        self.lower_gc = []
        self.lower_biases = []
        self.kmers = []

def calculate_gc_plot_data(df_all, margin):
    if df_all is None:
        return None
    data = CalculatedGCData()
    #print(df_all["k"].unique())
    #print(df_all["k"])
    for i in df_all["k"].unique():
        df = df_all[df_all["k"] == i]
        if df is None or len(get_n_percent(df, margin).index) == 0:
            # skip DF if it's None or has too little values for retrieving N percent
            continue
        data.kmers.append(i)
        df_head = get_n_percent(df, margin)  # get N percent with the highest bias
        #print("head is ", df_head)
        data.upper_gc.append(None if len(df_head.index) == 0 else round(df_head["GC_%"].mean(), 2))
        data.upper_biases.append(None if len(df_head.index) == 0 else round(df_head["strand_bias_%"].mean(), 2))

        df_tail = get_n_percent(df, margin, True)  # get N percent with the lowest bias
        data.lower_gc.append(None if len(df_head.index) == 0 else round(df_tail["GC_%"].mean(), 2))
        data.lower_biases.append(None if len(df_head.index) == 0 else round(df_tail["strand_bias_%"].mean(), 2))

    if not data.kmers:  # no dataframe is big enough to provide data
        return None
    return data


def select_more_frequent(row, seq=False):
    """
    Fuction to return count (sequence if seq=True) of sequence or its rev. complement based on which is more frequent.
    :param row: one row of DataFrame with SB statistics
    :param seq: if true, sequence is returned instead of its count
    :return: count/sequence of more frequent out of seq and its rev. compl.
    """
    if row["seq_count"] > row["rev_complement_count"]:
        if seq:
            return row["seq"]
        return row["seq_count"]
    else:
        if seq:
            return row["rev_complement"]
        return row["rev_complement_count"]
