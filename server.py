import re
import sys

from bokeh.io import curdoc
from bokeh.layouts import column, row
from bokeh.models import Dropdown, RadioButtonGroup, Slider, Div, Button

from plots import Plotter, AnalysisData, BarPlotType

menu = [("PacBio 1", "pacbio_m54238_180628_014238"), ("PacBio 2", "pacbio_m54238_180903_015530"),
        ("PacBio 3", "pacbio_m54238_180901_011437"), ("PacBio 4", "pacbio_m54238_180902_013549"),
        ("Illumina 1", "illumina_D1_S1_L001_R1_001"), ("Nanopore 1", "nanopore_GM24385_3")]

datasets = {
    #"nanopore_GM24385": AnalysisData("df_output_5_nanopore_nanopore_GM24385_11_batch_1.csv", 5, False, None, ""),  # TEST
    #"nanopore_GM24385/summary": AnalysisData("sb_analysis_GM24385_3.csv"),  # TEST
    #"nanopore_test/summary": AnalysisData("sb_analysis_GM24385_111.csv"),  # TEST
    "pacbio_m54238_180628_014238": AnalysisData("data/df_output_m54238_180628_014238.csv"),
    "pacbio_m54238_180628_014238/summary": AnalysisData("data/sb_analysis_m54238_180628_014238.csv"),
    "pacbio_m54238_180903_015530": AnalysisData("data/df_output_m54238_180903_015530.csv"),
    "pacbio_m54238_180903_015530/summary": AnalysisData("data/sb_analysis_m54238_180903_015530.csv"),
    "pacbio_m54238_180901_011437": AnalysisData("data/df_output_m54238_180901_011437.csv"),
    "pacbio_m54238_180901_011437/summary": AnalysisData("data/sb_analysis_m54238_180901_011437.csv"),
    "pacbio_m54238_180902_013549": AnalysisData("data/df_output_m54238_180902_013549.csv"),
    "pacbio_m54238_180902_013549/summary": AnalysisData("data/sb_analysis_m54238_180902_013549.csv"),
    "illumina_D1_S1_L001_R1_001": AnalysisData("data/df_output_D1_S1_L001_R1_001.csv"),
    "illumina_D1_S1_L001_R1_001/summary": AnalysisData("data/sb_analysis_D1_S1_L001_R1_001.csv"),
    "nanopore_GM24385_3": AnalysisData("data/df_output_nanopore_GM24385_3.csv", nanopore=True),
    "nanopore_GM24385_3/summary": AnalysisData("data/sb_analysis_GM24385_3.csv", nanopore=True),
    "nanopore_GM24385_3/bins": AnalysisData("data/df_output_nanopore_GM24385_3_bins.csv", nanopore=True),
    "nanopore_GM24385_3/bin_stats": AnalysisData("data/nanopore_GM24385_3_bin_stats.csv", nanopore=True)

}

NAME = menu[0][0]
DATASET = menu[0][1]
K = 5
MARGIN = 5

radio_button_group = RadioButtonGroup(labels=["K = 5", "K = 6", "K = 7", "K = 8", "K = 9"], active=0)
refresh_button = Button(label = "Refresh", button_type = "danger")
barplot_button_group = RadioButtonGroup(labels=["Reads", "Bases"], active=0)
margin_slider = Slider(start=1, end=100, value=5, step=1, title="Margin Size (%):")
lower = datasets[DATASET].bin_lower
upper = datasets[DATASET].bin_upper
print(upper, lower)

bin_slider = Slider(start=lower, end=upper, value=lower, step=1, title="Bin")

dropdown = Dropdown(label=NAME, button_type="warning", menu=menu, css_classes=["dropdown"])
plotter = Plotter(datasets[DATASET + "/summary"], datasets[DATASET])
dataset_div = Div(text="""<button type="button" style="font-size:110%;background-color:#F0AD4E;border-radius:4px;border:none;text-align: center; line-height: 20px;color:white;font:calibri">    Selected dataset: {}<p/>""".format(menu[0][0]))
print(sys.getsizeof(plotter))

def on_dropdown_change(event):
    global DATASET
    DATASET = event.item
    global NAME
    NAME = list(filter(lambda e:e[1]==DATASET,menu))[0][0]
    dropdown.label = NAME
    plotter.create_lineplot(datasets[DATASET + "/summary"], new=False)
    plotter.create_gc_plot(datasets[DATASET], new=False)
    plotter.create_kmer_plot(datasets[DATASET], K, new=False)
    print(sys.getsizeof(plotter))
    if datasets[DATASET].nanopore:
        print("TRU")
        global lower, upper
        lower = datasets[DATASET + "/bins"].bin_lower
        upper = datasets[DATASET + "/bins"].bin_upper
        bin_slider.start = lower
        bin_slider.end = upper
        bin_slider.value = lower

        plotter.create_ci_plot(datasets[DATASET + "/bins"])
        plotter.bar_plot(datasets[DATASET + "/bin_stats"], plot_type=BarPlotType.READS)
        curdoc().remove_root(curdoc().roots[1])
        curdoc().add_root(column(children=[plotter.ci_plot, row(plotter.barplot,barplot_button_group), plotter.kmer_plot, radio_button_group, bin_slider, refresh_button, plotter.data_table]))


def radiogroup_click(attr,old,new):
    switch_k()
    plotter.create_kmer_plot(datasets[DATASET], K, new=False)


def switch_k():
    active_radio = radio_button_group.active  ##Getting radio button value
    global K
    K = active_radio + 5
    print("New k ", K)
    print(sys.getsizeof(plotter))
    if K != 5:
        bin_slider.disabled = True
    else:
        bin_slider.disabled = False


def gc_plot_refresh(attr, old, new):
    print(old, new)
    print("hello")


def bin_slider_change():
    radio_button_group.active = 0
    switch_k()
    print("test change to 5")
    plotter.create_kmer_plot(datasets[DATASET + "/bins"], K, bin=bin_slider.value, new=False)


def barplot_button_change(attr, old, new):
    if new == 0:
        plotter.bar_plot(datasets[DATASET + "/bin_stats"], BarPlotType.READS, new=False)
    else:
        plotter.bar_plot(datasets[DATASET + "/bin_stats"], BarPlotType.BASES, new=False)


plotter.kmer_ds.selected.on_change(
          "indices", plotter.update_selected
    )

refresh_button.on_click(bin_slider_change)
barplot_button_group.on_change("active", barplot_button_change)
dropdown.on_click(on_dropdown_change)
radio_button_group.on_change("active", radiogroup_click)
margin_slider.on_change("value", gc_plot_refresh)

common_plots = column(children=[column(dropdown), plotter.lineplot, plotter.gc_plot])
kmers = column(children=[column(radio_button_group), plotter.kmer_plot])
curdoc().add_root(common_plots)
curdoc().add_root(kmers)
