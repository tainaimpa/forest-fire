import mesa

from forest_fire.model import ForestFire

GRID_WIDTH = 100
GRID_HEIGHT = 100
CANVAS_WIDTH = 500
CANVAS_HEIGHT = 500

COLORS = {
    "Fine": "#00AA00", #green
    "Burning": "#cf0f0f", #red
    "Burned": "#3D2B1F", #black
    "Lake": "#3babe6", #blue
    "Corridor": "orange",
    "Obstacle": "grey",
    "Ground": "#dcc9a4" #ligth earthy color
}


def tree_portrayal(tree):
    if not tree:
        return

    (x, y) = tree.pos
    return {
        "Shape": "rect",
        "w": 1,
        "h": 1,
        "Filled": True,
        "Layer": 0,
        "x": x,
        "y": y,
        "Color": COLORS[tree.status],
    }


canvas_element = mesa.visualization.CanvasGrid(
    tree_portrayal, GRID_WIDTH, GRID_HEIGHT, CANVAS_WIDTH, CANVAS_HEIGHT
)

tree_chart = mesa.visualization.ChartModule(
    [{"Label": label, "Color": color} for (label, color) in COLORS.items()]
)

pie_chart = mesa.visualization.PieChartModule(
    [{"Label": label, "Color": color} for (label, color) in COLORS.items() if label in ["Fine", "Burning", "Burned"]]
)

model_params = {
    "width": GRID_WIDTH,
    "height": GRID_HEIGHT,
    "tree_density": mesa.visualization.Slider("Tree Density", 0.65, 0.01, 1.0, 0.01),
}

server = mesa.visualization.ModularServer(
    ForestFire, [canvas_element, tree_chart, pie_chart], "Forest Fire", model_params
)
