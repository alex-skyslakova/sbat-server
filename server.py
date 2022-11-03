import sys

from bokeh.io import curdoc
from bokeh.layouts import column, row
from bokeh.models import Dropdown, RadioButtonGroup, Slider, Div, Button, Spacer
from bokeh.server.server import Server
from bokeh.themes import Theme
from tornado.ioloop import IOLoop
from plots import Plotter, AnalysisData, BarPlotType

menu = [("PacBio m54238_180628_014238", "pacbio_m54238_180628_014238"), ("PacBio m54238_180903_015530", "pacbio_m54238_180903_015530"),
        ("PacBio m54238_180901_011437", "pacbio_m54238_180901_011437"), ("PacBio m54238_180902_013549", "pacbio_m54238_180902_013549"),
        ("PacBio m64011_181218_235052", "pacbio_m64011_181218_235052"), ("PacBio m64011_181227_224151", "pacbio_m64011_181227_224151"),
        ("Illumina D1_S1_L001_R1_001", "illumina_D1_S1_L001_R1_001"),("Illumina D1_S1_L001_R1_002", "illumina_D1_S1_L001_R1_002"),
        ("Illumina D1_S1_L001_R1_003", "illumina_D1_S1_L001_R1_003"), ("Illumina D1_S1_L001_R1_004", "illumina_D1_S1_L001_R1_004"),
        ("Illumina MPHG002_S1_L001_R1_001", "illumina_MPHG002_S1_L001_R1_001"), ("Illumina MPHG002_S1_L001_R2_001", "illumina_MPHG002_S1_L001_R2_001"),
        ("Nanopore 1", "nanopore_GM24385_3")]

datasets = {
    "pacbio_m54238_180628_014238": AnalysisData("data/df_output_m54238_180628_014238.csv"),
    "pacbio_m54238_180628_014238/summary": AnalysisData("data/sb_analysis_m54238_180628_014238.csv"),
    "pacbio_m54238_180903_015530": AnalysisData("data/df_output_m54238_180903_015530.csv"),
    "pacbio_m54238_180903_015530/summary": AnalysisData("data/sb_analysis_m54238_180903_015530.csv"),
    "pacbio_m54238_180901_011437": AnalysisData("data/df_output_m54238_180901_011437.csv"),
    "pacbio_m54238_180901_011437/summary": AnalysisData("data/sb_analysis_m54238_180901_011437.csv"),
    "pacbio_m54238_180902_013549": AnalysisData("data/df_output_m54238_180902_013549.csv"),
    "pacbio_m54238_180902_013549/summary": AnalysisData("data/sb_analysis_m54238_180902_013549.csv"),
    "pacbio_m64011_181218_235052": AnalysisData("data/df_output_m64011_181218_235052.csv"),
    "pacbio_m64011_181218_235052/summary": AnalysisData("data/sb_analysis_m64011_181218_235052.csv"),
    "pacbio_m64011_181227_224151": AnalysisData("data/df_output_m64011_181227_224151.csv"),
    "pacbio_m64011_181227_224151/summary": AnalysisData("data/sb_analysis_m64011_181227_224151.csv"),
    "illumina_D1_S1_L001_R1_001": AnalysisData("data/df_output_D1_S1_L001_R1_001.csv"),
    "illumina_D1_S1_L001_R1_001/summary": AnalysisData("data/sb_analysis_D1_S1_L001_R1_001.csv"),
    "illumina_D1_S1_L001_R1_002": AnalysisData("data/df_output_D1_S1_L001_R1_002.csv"),
    "illumina_D1_S1_L001_R1_002/summary": AnalysisData("data/sb_analysis_D1_S1_L001_R1_002.csv"),
    "illumina_D1_S1_L001_R1_003": AnalysisData("data/df_output_D1_S1_L001_R1_003.csv"),
    "illumina_D1_S1_L001_R1_003/summary": AnalysisData("data/sb_analysis_D1_S1_L001_R1_003.csv"),
    "illumina_D1_S1_L001_R1_004": AnalysisData("data/df_output_D1_S1_L001_R1_004.csv"),
    "illumina_D1_S1_L001_R1_004/summary": AnalysisData("data/sb_analysis_D1_S1_L001_R1_004.csv"),
    "illumina_MPHG002_S1_L001_R1_001": AnalysisData("data/df_output_MPHG002_S1_L001_R1_001.csv"),
    "illumina_MPHG002_S1_L001_R1_001/summary": AnalysisData("data/sb_analysis_MPHG002_S1_L001_R1_001.csv"),
    "illumina_MPHG002_S1_L001_R2_001": AnalysisData("data/df_output_MPHG002_S1_L001_R2_001.csv"),
    "illumina_MPHG002_S1_L001_R2_001/summary": AnalysisData("data/sb_analysis_MPHG002_S1_L001_R2_001.csv"),
    "nanopore_GM24385_3": AnalysisData("data/df_output_nanopore_GM24385_3.csv", nanopore=True),
    "nanopore_GM24385_3/summary": AnalysisData("data/sb_analysis_GM24385_3.csv", nanopore=True),
    "nanopore_GM24385_3/bins": AnalysisData("data/df_output_nanopore_GM24385_3_bins.csv", nanopore=True),
    "nanopore_GM24385_3/bin_stats": AnalysisData("data/nanopore_GM24385_3_bin_stats.csv", nanopore=True)

}

NAME = menu[0][0]
DATASET = menu[0][1]
K = 5
MARGIN = 5
dropdown = Dropdown(label=NAME, button_type="warning", menu=menu, align='center')
refresh_button = Button(label="Refresh", button_type="warning")
radio_button_group = RadioButtonGroup(labels=["K = 5", "K = 6", "K = 7", "K = 8", "K = 9"], active=0, button_type="warning", width=800)
barplot_button_group = RadioButtonGroup(labels=["Reads", "Bases"], active=0, width=200)


def modify_doc(doc):
    doc.clear()
    doc.theme = Theme(filename="./theme.yml")

    global DATASET, K, NAME, MARGIN
    lower = datasets[DATASET].bin_lower
    upper = datasets[DATASET].bin_upper
    print(upper, lower)

    bin_slider = Slider(start=lower, end=upper, value=lower, step=1, title="Bin", bar_color="orange")
    plotter = Plotter(datasets[DATASET + "/summary"], datasets[DATASET])

    def on_dropdown_change(event):

        print("dropdown_change")
        global DATASET, NAME
        DATASET = event.item
        NAME = list(filter(lambda e: e[1] == DATASET, menu))[0][0]
        dropdown.label = NAME
        plotter.create_lineplot(datasets[DATASET + "/summary"], new=False)
        plotter.create_gc_plot(datasets[DATASET], new=False)
        plotter.create_kmer_plot(datasets[DATASET], K, new=False)
        print(sys.getsizeof(plotter))
        if datasets[DATASET].nanopore:
            data = datasets[DATASET + "/bins"]
            bin_slider.start = data.bin_lower
            bin_slider.end = data.bin_upper
            bin_slider.value = data.bin_lower

            plotter.create_ci_plot(data)
            plotter.bar_plot(datasets[DATASET + "/bin_stats"], plot_type=BarPlotType.READS)
            doc.remove_root(curdoc().roots[1])
            doc.add_root(column(
                children=[plotter.ci_plot,Spacer(height=50), plotter.barplot, row(Spacer(width=20), barplot_button_group),Spacer(height=50), column(plotter.kmer_plot,
                          radio_button_group, bin_slider, refresh_button), plotter.data_table]))
        else:
            doc.remove_root(curdoc().roots[1])
            doc.add_root(column(
                children=[plotter.kmer_plot, radio_button_group, plotter.data_table]))

    def radiogroup_click(attr, old, new):
        switch_k()
        plotter.create_kmer_plot(datasets[DATASET], K, new=False)

    def switch_k():
        active_radio = radio_button_group.active  ##Getting radio button value
        global K
        K = active_radio + 5
        if K != 5:
            bin_slider.disabled = True
        else:
            bin_slider.disabled = False

    def bin_slider_change():
        radio_button_group.active = 0
        switch_k()
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

    common_plots = column(children=[Spacer(height=10),row(Spacer(width=250), dropdown), Spacer(height=10), plotter.lineplot,Spacer(height=50), plotter.gc_plot,Spacer(height=50)])
    kmers = column(children=[plotter.kmer_plot, radio_button_group, plotter.data_table])
    doc.add_root(common_plots)
    doc.add_root(kmers)


def bk_worker():
    server = Server({'/bkapp': modify_doc}, io_loop=IOLoop(), allow_websocket_origin=["*"])
    server.start()
    server.io_loop.start()



