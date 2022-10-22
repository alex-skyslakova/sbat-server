from typing import List

from bokeh.io import curdoc
from bokeh.models import ColumnDataSource, HoverTool
from bokeh.plotting import figure

import utils
import pandas as pd


class AnalysisData:
    def __init__(self, dataset, k=None, nanopore=None, bin=None, link=None):
        self.dataset = dataset
        self.df = pd.read_csv(dataset)
        self.k = k
        self.nanopore = nanopore
        self.bin = bin
        self.link = link

        if "sb" not in dataset:
            self.df['seq_count'] = pd.to_numeric(self.df['seq_count'], errors='coerce')
            self.df['rev_complement_count'] = pd.to_numeric(self.df['rev_complement_count'], errors='coerce')
            self.df['ratio'] = pd.to_numeric(self.df['ratio'], errors='coerce')
            self.df['GC_%'] = pd.to_numeric(self.df['GC_%'], errors='coerce')
            self.df['strand_bias_%'] = pd.to_numeric(self.df['strand_bias_%'], errors='coerce')


class Plotter:
    def __init__(self, data_summary, data):
        self.lineplot_ids = []
        self.lineplot = None
        self.create_lineplot(data_summary)
        self.gc_plot = None
        self.create_gc_plot(data, 5)
        self.kmer_plot = self.create_kmer_plot(data, 5)

    def create_lineplot(self, data: AnalysisData, new=True):
        if data.bin is not None:
            x_axis = "Bin"
            title = 'Statistics of Strand Bias among Bins for K={}'.format(data.k)
        else:
            x_axis = "K"
            title = 'Statistics of Strand Bias for Different Sizes of K'

        if new:
            self.lineplot = figure(
                plot_height=500,
                plot_width=800,
                title=title,
                tools="crosshair, pan,reset, save,wheel_zoom, box_select, "
                      "poly_select, tap, box_zoom",
            )

        else:
            self.lineplot.renderers = []

        ds = ColumnDataSource(data.df)
        mean = self.lineplot.line(data.df[x_axis.lower()], data.df["bias_mean"], line_color="green",
                                  legend_label="Mean",
                                  line_width=3, name="Mean")
        self.lineplot_ids.append(mean.id)
        median = self.lineplot.line(data.df[x_axis.lower()], data.df["bias_median"], line_color="blue",
                                    legend_label="Median",
                                    line_width=3,
                                    name="Median")
        modus = self.lineplot.line(data.df[x_axis.lower()], data.df["bias_modus"], line_color="pink",
                                   legend_label="Mode",
                                   line_width=3,
                                   name="Mode")
        perc_5 = self.lineplot.line(data.df[x_axis.lower()], data.df["percentile_5"], line_color="orange",
                                    legend_label="5th Percentile", line_width=3, name="5th Percentile")
        perc_95 = self.lineplot.line(data.df[x_axis.lower()], data.df["percentile_95"], line_color="red",
                                     legend_label="95th Percentile", line_width=3, name="95th Percentile")

        self.lineplot.add_tools(
            HoverTool(tooltips="Median Strand Bias: @y {}: @x".format(x_axis), renderers=[median], mode="vline"))
        self.lineplot.add_tools(
            HoverTool(tooltips="Mean Strand Bias: @y {}: @x".format(x_axis), renderers=[mean], mode="vline"))
        self.lineplot.add_tools(
            HoverTool(tooltips="Mode Strand Bias: @y {}: @x".format(x_axis), renderers=[modus], mode="vline"))
        self.lineplot.add_tools(
            HoverTool(tooltips="5th Percentile of Strand Bias: @y {}: @x".format(x_axis), renderers=[perc_5],
                      mode="vline"))
        self.lineplot.add_tools(
            HoverTool(tooltips="95th Percentile of Strand Bias: @y {}: @x".format(x_axis), renderers=[perc_95],
                      mode="vline"))

        self.lineplot.legend.click_policy = "hide"
        self.lineplot.xaxis.axis_label = x_axis
        self.lineplot.yaxis.axis_label = "Strand Bias [%]"
        self.lineplot.xaxis.axis_label_text_font_size = "15pt"
        self.lineplot.yaxis.axis_label_text_font_size = "15pt"
        self.lineplot.title.text_font_size = "15pt"

        return self.lineplot

    def create_gc_plot(self, data: AnalysisData, margin=5, new=True):
        print(data.dataset)
        print(data.dataset)
        try:
            gc_data = utils.calculate_gc_plot_data(data.df, margin)
        except Exception:
            print("failed on data ", data.df, data.df.info())
            return

        if new:
            self.gc_plot = figure(
                plot_height=500,
                plot_width=1000,
                title="Strand Bias Levels in Relation to GC Percentage",
                tools="crosshair, pan,reset, save,wheel_zoom, box_select, "
                      "poly_select, tap, box_zoom",
            )
        else:
            self.gc_plot.renderers = []

        tooltips = [
            ("Average GC Content (%)", "@x"),
            ("Average Strand Bias", "@y"),
            ("K", "@desc")
        ]

        self.gc_plot.add_tools(
            HoverTool(
                tooltips=tooltips,
            )
        )

        source = ColumnDataSource(data=dict(
            x=gc_data.upper_gc,
            y=gc_data.upper_biases,
            desc=data.df["k"].unique(),
        ))

        self.gc_plot.scatter('x',
                             'y',
                             color="red",
                             fill_color="red",
                             size=10,
                             legend_label="GC Content vs Strand Bias in Top {}% of SB Score".format(margin),
                             marker="inverted_triangle",
                             source=source)

        source = ColumnDataSource(data=dict(
            x=gc_data.lower_gc,
            y=gc_data.lower_biases,
            desc=[5, 6, 7, 8, 9],
        ))
        self.gc_plot.scatter('x',
                             'y',
                             color="green",
                             fill_color="green",
                             size=10,
                             legend_label="GC Content vs Strand Bias in Bottom {}% of SB Score".format(margin),
                             marker="triangle",
                             source=source)
        self.gc_plot.xaxis.axis_label = "GC Content [%]"
        self.gc_plot.yaxis.axis_label = "Strand Bias [%]"
        self.gc_plot.legend.location = "top_left"
        self.gc_plot.xaxis.axis_label_text_font_size = "15pt"
        self.gc_plot.yaxis.axis_label_text_font_size = "15pt"
        self.gc_plot.title.text_font_size = "15pt"
        return self.gc_plot

    def create_kmer_plot(self, data: AnalysisData, K, new=True):
        if data is None:
            return
        if data.nanopore:  # TODO
            pass
        else:
            size = K
            df = data.df[data.df.k == size].copy()
            if new:
                self.kmer_plot = figure(
                    plot_height=500,
                    plot_width=1000,
                    title="K-mers in Descending Frequency Order in Relation to Strand Bias",
                    tools="crosshair, pan,reset, save,wheel_zoom, box_select, "
                          "poly_select, tap, box_zoom",
                )
            else:
                self.kmer_plot.renderers = []

            tooltips = [
                ("K-mer", "@seq"),
                ("Frequency", "@seq_count"),
                ("Complement", "@rev_complement"),
                ("Frequency", "@rev_complement_count"),
                ("Strand Bias (%)", "@{strand_bias_%}"),
                ("GC Content (%)", "@{GC_%}"),
            ]

            self.kmer_plot.add_tools(
                HoverTool(
                    tooltips=tooltips,
                )
            )
            df["more_freq_count"] = df.apply(lambda row: utils.select_more_frequent(row),
                                             axis=1)
            # get more frequent out of k-mer and its rev. complement
            df = df.sort_values(by=['more_freq_count'], ascending=False)
            df["index"] = range(1, len(df) + 1)

            ds = ColumnDataSource(df)

            self.kmer_plot.circle(
                "index",
                "strand_bias_%",
                source=ds,
                name="Strand bias of k-mers of size {} in relation with frequency".format(size),
                legend_label="Strand bias of k-mers of size {} in relation with frequency".format(size),
                color="green",
            )

            self.kmer_plot.yaxis.axis_label = "Strand Bias [%]"
            self.kmer_plot.xaxis.axis_label_text_font_size = "15pt"
            self.kmer_plot.yaxis.axis_label_text_font_size = "15pt"
            self.kmer_plot.title.text_font_size = "15pt"
            return self.kmer_plot
