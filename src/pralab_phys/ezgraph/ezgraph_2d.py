import plotly.graph_objects as go

class EZGraph(go.Figure):

    def __init__(self, name:str = "", width:int = 800, height:int = 600):
        super().__init__()

        self.update_layout(width=width, height=height)


    def add_plot():
        pass


''' testcode
a = EZGraph()
a.write_html("test.png")
'''