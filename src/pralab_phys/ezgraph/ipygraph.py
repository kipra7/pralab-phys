
import pandas as pd
from ipywidgets import interact, Select, IntSlider

from .ezgraph_2d import EZGraph

class EZGraphDisplay:
    """DataFrameを受け取り、2次元グラフを描画するためのクラス
    """

    def _gen_graph(self, x_axis, y_axis):
        graph = EZGraph(xax_title = self.x_axis.value, yax_title= self.y_axis.value, width=self.width.value, namedisplay=False)
        graph.add_graph(self.df[x_axis], self.df[y_axis])
        graph.show()

    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.x_axis = Select(options=df.columns, description='X軸', rows = 4)
        self.y_axis = Select(options=df.columns, description='Y軸', rows = 4)
        self.width = IntSlider(value=800, min=400, max=1200, step=500, description='Width')
        interact(self._gen_graph, x_axis = self.x_axis, y_axis = self.y_axis, width = self.width)