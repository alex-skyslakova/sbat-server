import os
import statistics
from enum import Enum
from math import sqrt
from typing import List

from bokeh.io import curdoc, show
from bokeh.models import ColumnDataSource, HoverTool, Whisker, TableColumn, StringFormatter, NumberFormatter, DataTable
from bokeh.plotting import figure

import utils
import pandas as pd

class BarPlotType(Enum):
    BASES = "Bases"
    READS = "Reads"


class AnalysisData:
    def __init__(self, dataset, k=None, nanopore=None, bin=None,bin_total=None, link=None):
        self.dataset = dataset
        self.df = pd.read_csv(dataset)
        self.k = k
        self.nanopore = nanopore
        self.bin = bin

        if "bins" in dataset and nanopore:
            print("been there")
            self.bin_lower = self.df.bin.min()
            self.bin_upper = self.df.bin.max()
        else:
            self.bin_lower, self.bin_upper = 0, 1
        self.bin_total = self.dataset
        self.link = link


class Plotter:
    def __init__(self, data_summary, data):
        self.lineplot_ids = []
        self.lineplot = None
        self.create_lineplot(data_summary)
        self.gc_plot = None
        self.create_gc_plot(data, 5)
        self.kmer_plot = None

        self.ci_plot = None
        self.barplot = None
        self.data_table = self.create_data_table()
        self.kmer_df = None
        self.kmer_ds = ColumnDataSource()
        self.create_kmer_plot(data, 5)
        if data.nanopore:
            self.bar_plot(data, plot_type=BarPlotType.READS)
            self.ci_plot = self.create_ci_plot(data)

    def create_lineplot(self, data: AnalysisData, new=True):
        if data.bin is not None:
            x_axis = "Bin"
            title = 'Statistics of strand bias among time bins for K={}'.format(data.k)
        else:
            x_axis = "K"
            title = 'Statistics of strand bias for different sizes of K'

        if self.lineplot is None or new:
            self.lineplot = figure(
                plot_height=400,
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
            HoverTool(tooltips="Median strand bias: @y {}: @x".format(x_axis), renderers=[median], mode="vline"))
        self.lineplot.add_tools(
            HoverTool(tooltips="Mean strand bias: @y {}: @x".format(x_axis), renderers=[mean], mode="vline"))
        self.lineplot.add_tools(
            HoverTool(tooltips="Mode strand bias: @y {}: @x".format(x_axis), renderers=[modus], mode="vline"))
        self.lineplot.add_tools(
            HoverTool(tooltips="5th percentile of strand bias: @y {}: @x".format(x_axis), renderers=[perc_5],
                      mode="vline"))
        self.lineplot.add_tools(
            HoverTool(tooltips="95th percentile of strand bias: @y {}: @x".format(x_axis), renderers=[perc_95],
                      mode="vline"))

        self.lineplot.legend.click_policy = "hide"
        self.lineplot.xaxis.axis_label = x_axis
        self.lineplot.yaxis.axis_label = "Strand Bias [%]"
        self.lineplot.xaxis.axis_label_text_font_size = "15pt"
        self.lineplot.yaxis.axis_label_text_font_size = "15pt"
        self.lineplot.title.text_font_size = "15pt"

        return self.lineplot

    def create_gc_plot(self, data: AnalysisData, margin=5, new=True):
        try:
            gc_data = utils.calculate_gc_plot_data(data.df, margin)
        except Exception:
            print("failed on data ", data.df, data.df.info())
            return

        if self.gc_plot is None or new:
            self.gc_plot = figure(
                plot_height=400,
                plot_width=800,
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

    def create_kmer_plot(self, data: AnalysisData, K, new=True, bin=None):
        if data is None:
            return


        if self.kmer_plot is None or new:
            self.kmer_plot = figure(
                plot_height=400,
                plot_width=800,
                title="K-mers in Descending Frequency Order in Relation to Strand Bias",
                tools="crosshair, pan,reset, save,wheel_zoom, box_select, "
                      "poly_select, tap, box_zoom, lasso_select",
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

        if bin is not None:
            if self.ci_plot is None:
                self.create_ci_plot(data, new=new)
            self.kmer_df = data.df[data.df.bin == bin].copy()
        else:
            self.kmer_df = data.df[data.df.k == K].copy()

        self.kmer_df["more_freq_count"] = self.kmer_df.apply(lambda row: utils.select_more_frequent(row),
                                                             axis=1)
        # get more frequent out of k-mer and its rev. complement
        self.kmer_df = self.kmer_df.sort_values(by=['more_freq_count'], ascending=False, ignore_index=True)
        self.kmer_ds.data = self.kmer_df
        self.kmer_plot.circle(
            "index",
            "strand_bias_%",
            source=self.kmer_ds,
            name="Strand bias of k-mers in relation to frequency",
            legend_label="Strand bias of k-mers in relation to frequency",
            color="green",
        )

        self.kmer_plot.yaxis.axis_label = "Strand Bias [%]"
        self.kmer_plot.xaxis.axis_label_text_font_size = "15pt"
        self.kmer_plot.yaxis.axis_label_text_font_size = "15pt"
        self.kmer_plot.title.text_font_size = "15pt"
        return self.kmer_plot

    def create_ci_plot(self, data, z=1.96, new=True):
        if new:
            self.ci_plot = figure(width=800, height=400, title="Confidence Intervals among Different Bins")
        else:
            self.ci_plot.renderers = []

        self.ci_plot.y_range.start = 0
        base, lower, upper, mean = [], [], [], []
        for i, bin in enumerate(list(data.df.bin.unique())):
            valid = data.df[data.df["bin"] == bin]["strand_bias_%"]
            valid_mean = valid.mean()
            stdev = statistics.stdev(valid)
            confidence_interval = z * stdev / sqrt(len(valid))
            lower.append(valid_mean - confidence_interval)
            upper.append(valid_mean + confidence_interval)
            base.append(bin)
            mean.append(valid_mean)
            self.ci_plot.circle(x=bin, y=valid_mean, color='#f44336')

        source_error = ColumnDataSource(data=dict(base=base, lower=lower, upper=upper))
        self.ci_plot.add_layout(
            Whisker(source=source_error, base="base", upper="upper", lower="lower")
        )

        # add hover just to the two box renderers
        self.ci_plot.add_tools(
            HoverTool(renderers=self.ci_plot.renderers,
                      tooltips=[
                          ('Bin', '@base'),
                          ('Mean', '@mean'),
                          ('2.5th Percentile', '@lower'),
                          ('97.5th Percentile', '@upper')
                      ])
        )

        self.ci_plot.xaxis.axis_label = "Time bins"
        self.ci_plot.yaxis.axis_label = "Strand Bias [%]"
        self.ci_plot.legend.location = "top_left"
        self.ci_plot.xaxis.axis_label_text_font_size = "15pt"
        self.ci_plot.yaxis.axis_label_text_font_size = "15pt"
        self.ci_plot.title.text_font_size = "15pt"

    def bar_plot(self, data, plot_type: BarPlotType, new=True):
        if new:
            self.barplot = figure(width=800, height=400, title="Distribution of {} among time bins".format(plot_type.value.lower()))
        else:
            self.barplot.renderers = []

        self.barplot.vbar(x=data.df.bin, top=data.df[plot_type.value.lower()], width=0.5, legend_label="Number of {} per time bin".format(plot_type.value.lower()))
        self.barplot.add_tools(
            HoverTool(renderers=self.barplot.renderers,
                      tooltips=[
                          ("Bin", '@x'),
                          (plot_type.value, '@top')
                      ])
        )

        self.barplot.xaxis.axis_label = "Time bin"
        self.barplot.yaxis.axis_label = "Number of {} in bin".format(plot_type.value)
        self.barplot.legend.location = "top_left"
        self.barplot.xaxis.axis_label_text_font_size = "15pt"
        self.barplot.yaxis.axis_label_text_font_size = "15pt"
        self.barplot.title.text_font_size = "15pt"

    def create_data_table(self):
        columns = [
            TableColumn(
                field="seq",
                title="K-mer",
                formatter=StringFormatter(),
                width=200
            ),
            TableColumn(
                field="seq_count",
                title="K-mer Frequency",
                formatter=NumberFormatter(format="0,0"),
                width=400
            ),
            TableColumn(
                field="rev_complement",
                title="Reverse Complement",
                formatter=StringFormatter(),
            ),
            TableColumn(
                field="rev_complement_count",
                title="Complement Frequency",
                formatter=NumberFormatter(format="0,0"),
            ),
            TableColumn(
                field="strand_bias_%",
                title="Strand Bias (%)",
                formatter=NumberFormatter(format="0[.]0000"),
            ),
            TableColumn(
                field="GC_%",
                title="GC Content (%)",
                formatter=NumberFormatter(format="0[.]00"),
            )
        ]

        return DataTable(columns=columns, width=900)

    def update_selected(self, attrname, old, new):
        """
        Called upon selecting datapoints from marked anomaly on graph. Function updates
        selected column in dataframe.
        """
        self.kmer_df["selected"] = False
        selected_df = self.kmer_df.iloc[new]
        self.data_table.source.data = selected_df

    def download_selected(self):
        """
        Is triggered by pushing download button. Saves dataframe to ./labeled folder
        under loaded file filename + "-labeled.csv" extension. Filters dataframe
        according to "days to download" field.
        """

        download_df = self.kmer_vs_sb_df[self.kmer_vs_sb_df["selected"]]
        if not os.path.isdir("selected"):
            os.makedirs("selected")

        filename = self.filename + "-labeled.csv"
        download_df.to_csv(
            os.path.join("selected/", filename),
            index=False,
        )
        print("Downloading dataset.")