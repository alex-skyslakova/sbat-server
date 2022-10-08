from bokeh.io import curdoc
from bokeh.layouts import column
from bokeh.models import Dropdown

from plots import Plotter, AnalysisData


menu = [("Illumina xyz", "illumina_xyz"), ("Item 2", "nanopore_GM24385"), ("Item 3", "item_3")]

datasets = {
    "nanopore_GM24385": AnalysisData("df_output_5_nanopore_nanopore_GM24385_11_batch_1.csv", 5, True, 1, "")
}


DATASET = menu[0][1]
K = 5



dropdown = Dropdown(label="Select dataset", button_type="warning", menu=menu)
plotter = Plotter()

def on_dropdown_change(event):
    DATASET = event.item
    print(DATASET)


dropdown.on_click(on_dropdown_change)
doc = curdoc()
doc.add_root(column(children=[dropdown]))


class CalculatedGCData:
    def __init__(self):
        self.upper_gc = []
        self.upper_biases = []
        self.lower_gc = []
        self.lower_biases = []
        self.kmers = []
