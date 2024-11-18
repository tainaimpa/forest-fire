import mesa

from forest_fire.model import ForestFire
from forest_fire.tree import Tree

GRID_WIDTH = 100
GRID_HEIGHT = 100
CANVAS_WIDTH = 500
CANVAS_HEIGHT = 500

COLORS = {
    "Fine": "#00AA00",
    "Burning": "#FF0000",
    "Burned": "#3D2B1F",
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
        "Layer": 1,
        "x": x,
        "y": y,
        "Color": COLORS["Cloud"],
    }

# Criando o gráfico de CO2 separadamente
co2_chart = mesa.visualization.ChartModule(
    [{"Label": "CO2(Kg)", "Color": "#000000"}],
)

canvas_element = mesa.visualization.CanvasGrid(
    lambda agent: tree_portrayal(agent) if isinstance(agent, Tree) else cloud_portrayal(agent),
    GRID_WIDTH, GRID_HEIGHT, CANVAS_WIDTH, CANVAS_HEIGHT
)
# TODO adicionar o numero de nuvens e um novo grafico para arvores apagadas  
tree_chart = mesa.visualization.ChartModule(
    [{"Label": label, "Color": color} for (label, color) in COLORS.items()]
)

pie_chart = mesa.visualization.PieChartModule(
    [{"Label": label, "Color": color} for (label, color) in COLORS.items()]
)

model_params = {
    "rainy_season": mesa.visualization.Checkbox("Estação chuvosa", False),
    "biome_name": mesa.visualization.Choice("Biome", "Default", ["Default","Amazônia","Caatinga","Cerrado","Pantanal","Mata Atlântica"]), 
    "width": GRID_WIDTH,
    "height": GRID_HEIGHT,
    "tree_density": mesa.visualization.Slider("Tree Density", 0.65, 0.01, 1.0, 0.01),
    "reprod_speed": mesa.visualization.Slider("Reproduction Rate", 1, 0.0, 1.0, 0.1),
    "cloud_quantity": mesa.visualization.Slider("Cloud Quantity", 0, 0, 30, 1),
}

server = mesa.visualization.ModularServer(
    ForestFire, [canvas_element, tree_chart, pie_chart, co2_chart], "Forest Fire", model_params
)
