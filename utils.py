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