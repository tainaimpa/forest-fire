import mesa

from forest_fire.model import ForestFire
from forest_fire.tree import Tree
from forest_fire.cloud import Cloud

GRID_WIDTH = 100
GRID_HEIGHT = 100
CANVAS_WIDTH = 750
CANVAS_HEIGHT = 750

COLORS = {
    "Fine": "#148c39", #green
    "Burning": "#cf0f0f", #red
    "Burned": "#3D2B1F", #black
    "Lake": "#3A77F0", #blue
    "Corridor": "#8FBF3C",
    "Obstacle": "#6E6E6E",
    "Ground": "#8E5E30", #ligth earthy color
    "Cloud": "#A0A0A0",  # TODO nuvens cheias mais escuras 
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
        "Color": tree.color if tree.status == "Fine" else COLORS[tree.status],
    }

def cloud_portrayal(cloud):
    """Cloud portrayal function."""
    if not cloud:
        return None

    (x, y) = cloud.pos
    return {
        "Shape": "circle",
        "r": cloud.size,  
        "Filled": True,
        "Layer": 20,
        "x": x,
        "y": y,
        "Color": COLORS["Cloud"],
    }



canvas_element = mesa.visualization.CanvasGrid(
    lambda agent: cloud_portrayal(agent) if isinstance(agent, Cloud) else tree_portrayal(agent),
    GRID_WIDTH, GRID_HEIGHT, CANVAS_WIDTH, CANVAS_HEIGHT
)
# TODO adicionar o numero de nuvens e um novo grafico para arvores apagadas  
tree_chart = mesa.visualization.ChartModule(
    [{"Label": label, "Color": color} for (label, color) in COLORS.items() if label in ["Fine", "Burning", "Burned"]]
)

pie_chart = mesa.visualization.PieChartModule(
    [{"Label": label, "Color": color} for (label, color) in COLORS.items() if label in ["Fine", "Burning", "Burned"]]
)

model_params = {
    "rainy_season": mesa.visualization.Checkbox("Estação chuvosa", False),
    "biome_name": mesa.visualization.Choice("Biome", "Default", ["Default","Amazônia","Caatinga","Cerrado","Pantanal","Mata Atlântica"]), 
    "width": GRID_WIDTH,
    "height": GRID_HEIGHT,
    "tree_density": mesa.visualization.Slider("Tree Density", 0, 0, 1.0, 0.01, description="If the value is 0, the biome density will be used."),
    "cloud_quantity": mesa.visualization.Slider("Cloud Quantity", 0, 0, 30, 1),
    "reprod_speed": mesa.visualization.Slider("Reproduction Rate", 1, 0.0, 1.0, 0.1), 
    "water_density": mesa.visualization.Slider("Water Density", 0.15, 0, 1.0, 0.01),
    "num_of_lakes": mesa.visualization.Slider("Number of Lakes", 1, 0, 10, 1),
    "obstacles": mesa.visualization.Checkbox("Obstacles", True),
    "corridor": mesa.visualization.Checkbox("Corridor", True),
    "individual_lakes": mesa.visualization.Checkbox("Individual Lakes", True),
}

server = mesa.visualization.ModularServer(
    ForestFire, [canvas_element, tree_chart, pie_chart], "Forest Fire", model_params
)
