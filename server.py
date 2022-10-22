import re

from bokeh.io import curdoc
from bokeh.layouts import column
from bokeh.models import Dropdown, RadioButtonGroup, Slider

from plots import Plotter, AnalysisData


menu = [("pacbio 1", "pacbio_m54238_180628_014238"), ("pacbio 3", "pacbio_m54238_180903_015530")]

datasets = {
    #"nanopore_GM24385": AnalysisData("df_output_5_nanopore_nanopore_GM24385_11_batch_1.csv", 5, False, None, ""),  # TEST
    #"nanopore_GM24385/summary": AnalysisData("sb_analysis_GM24385_3.csv"),  # TEST
    #"nanopore_test/summary": AnalysisData("sb_analysis_GM24385_111.csv"),  # TEST
    "pacbio_m54238_180628_014238": AnalysisData("data/df_output_m54238_180628_014238.csv"),
    "pacbio_m54238_180628_014238/summary": AnalysisData("data/sb_analysis_m54238_180628_014238.csv"),
    "pacbio_m54238_180903_015530": AnalysisData("data/df_output_m54238_180903_015530.csv"),
    "pacbio_m54238_180903_015530/summary": AnalysisData("data/sb_analysis_m54238_180903_015530.csv")

}


DATASET = menu[1][1]
K = 5
MARGIN = 5

radio_button_group = RadioButtonGroup(labels=["K = 5", "K = 6", "K = 7", "K = 8", "K = 9", "K = 10"], active=0)
margin_slider = Slider(start=1, end=100, value=5, step=1, title="Margin Size (%):")

dropdown = Dropdown(label="Select dataset", button_type="warning", menu=menu)
plotter = Plotter(datasets[DATASET + "/summary"], datasets[DATASET])

def on_dropdown_change(event):
    global DATASET
    DATASET = event.item
    plotter.create_lineplot(datasets[DATASET + "/summary"], new=False)
    plotter.create_gc_plot(datasets[DATASET], new=False)
    plotter.create_kmer_plot(datasets[DATASET], K, new=False)


def radiogroup_click(attr,old,new):
    active_radio=radio_button_group.active ##Getting radio button value
    global K
    K = active_radio + 5
    plotter.create_kmer_plot(datasets[DATASET], K, new=False)


def gc_plot_refresh(attr, old, new):
    print(old, new)
    print("hello")


dropdown.on_click(on_dropdown_change)
radio_button_group.on_change("active", radiogroup_click)
margin_slider.on_change("value", gc_plot_refresh)
curdoc().add_root(column(children=[column(dropdown), plotter.lineplot, plotter.gc_plot, column(radio_button_group), plotter.kmer_plot]))
