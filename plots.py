from typing import List

from bokeh.models import ColumnDataSource, HoverTool
from bokeh.plotting import figure

import utils
import pandas as pd

class AnalysisData:
    def __init__(self, dataset, k, nanopore, bin=None, link=None):
        self.dataset = dataset
        self.df = pd.read_csv(dataset)
        self.k = k
        self.nanopore = nanopore
        self.bin = bin
        self.link = link
        self.plotter = Plotter()


class Plotter:
    def __init__(self):
        pass

    def lineplot(self, data: AnalysisData):
        if data.bin is not None:
            x_axis = "Bin"
            title = 'Statistics of Strand Bias among Bins for K={}'.format(data.k)
        else:
            x_axis = "K"
            title = 'Mean and Median of Strand Bias for Different Sizes of K'

        plot = figure(
            plot_height=500,
            plot_width=800,
            title=title,
            tools="crosshair, pan,reset, save,wheel_zoom, box_select, "
                  "poly_select, tap, box_zoom",
        )

        ds = ColumnDataSource(data.df)
        mean = plot.line(data.df[x_axis.lower()], data.df["bias_mean"], line_color="green", legend_label="Mean",
                         line_width=3)
        median = plot.line(data.df[x_axis.lower()], data.df["bias_median"], line_color="blue",
                           legend_label="Median",
                           line_width=3)
        modus = plot.line(data.df[x_axis.lower()], data.df["bias_modus"], line_color="pink", legend_label="Mode",
                          line_width=3)
        perc_5 = plot.line(data.df[x_axis.lower()], data.df["percentile_5"], line_color="orange",
                           legend_label="5th Percentile", line_width=3)
        perc_95 = plot.line(data.df[x_axis.lower()], data.df["percentile_95"], line_color="red",
                            legend_label="95th Percentile", line_width=3)

        plot.add_tools(
            HoverTool(tooltips="Median Strand Bias: @y {}: @x".format(x_axis), renderers=[median], mode="vline"))
        plot.add_tools(HoverTool(tooltips="Mean Strand Bias: @y {}: @x".format(x_axis), renderers=[mean], mode="vline"))
        plot.add_tools(
            HoverTool(tooltips="Mode Strand Bias: @y {}: @x".format(x_axis), renderers=[modus], mode="vline"))
        plot.add_tools(
            HoverTool(tooltips="5th Percentile of Strand Bias: @y {}: @x".format(x_axis), renderers=[perc_5],
                      mode="vline"))
        plot.add_tools(
            HoverTool(tooltips="95th Percentile of Strand Bias: @y {}: @x".format(x_axis), renderers=[perc_95],
                      mode="vline"))

        plot.legend.click_policy = "hide"
        plot.xaxis.axis_label = "Bins"
        plot.yaxis.axis_label = "Strand Bias [%]"
        plot.xaxis.axis_label_text_font_size = "15pt"
        plot.yaxis.axis_label_text_font_size = "15pt"
        plot.title.text_font_size = "15pt"
        return plot

    def gc_plot(self, data: AnalysisData, margin):

        plot = figure(
            plot_height=500,
            plot_width=1000,
            title="Strand Bias Levels in Relation to GC Percentage",
            tools="crosshair, pan,reset, save,wheel_zoom, box_select, "
                  "poly_select, tap, box_zoom",
        )

        tooltips = [
            ("Average GC Content (%)", "@x"),
            ("Average Strand Bias", "@y"),
        ]

        plot.add_tools(
            HoverTool(
                tooltips=tooltips,
            )
        )

        plot.inverted_triangle(data.df.upper_gc,
                               data.df.upper_biases,
                               color="red",
                               fill_color="red",
                               size=10,
                               legend_label="GC Content vs Strand Bias in Top {}% of SB Score".format(margin))
        plot.triangle(data.df.lower_gc,
                      data.df.lower_biases,
                      color="green",
                      fill_color="green",
                      size=10,
                      legend_label="GC Content vs Strand Bias in Bottom {}% of SB Score".format(margin))
        plot.legend.location = "top_left"
        return plot

    def calculate_gc_plot_data(self, dfs, margin):
        start_k = min(x.k for x in dfs)
        if all(x is None for x in dfs):
            return None
        data = CalculatedGCData()

        for i, df in enumerate(dfs):
            if df is None or len(utils.get_n_percent(df, margin).index) == 0:
                # skip DF if it's None or has too little values for retrieving N percent
                continue
            data.kmers.append(i + start_k)
            df_head = utils.get_n_percent(df, margin)  # get N percent with the highest bias
            data.upper_gc.append(None if len(df_head.index) == 0 else round(df_head["GC_%"].mean(), 2))
            data.upper_biases.append(None if len(df_head.index) == 0 else round(df_head["strand_bias_%"].mean(), 2))

            df_tail = utils.get_n_percent(df, margin, True)  # get N percent with the lowest bias
            data.lower_gc.append(None if len(df_head.index) == 0 else round(df_tail["GC_%"].mean(), 2))
            data.lower_biases.append(None if len(df_head.index) == 0 else round(df_tail["strand_bias_%"].mean(), 2))

        if not data.kmers:  # no dataframe is big enough to provide data
            return None
        return data