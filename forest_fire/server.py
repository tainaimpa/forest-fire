import mesa

from forest_fire.model import ForestFire
from forest_fire.tree import Tree
from forest_fire.cloud import Cloud
from forest_fire.fireman import Fireman

GRID_WIDTH = 100
GRID_HEIGHT = 100
CANVAS_WIDTH = 500
CANVAS_HEIGHT = 500

COLORS = {
    "Fine": "#00AA00",
    "Burning": "#FF0000",
    "Burned": "#3D2B1F",
    "Extinguished": "#FFFFFF",
    "Cloud": "#A0A0A0", # TODO nuvens cheias mais escuras 
    "Fireman": "#00A8FF" 
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

def fireman_portrayal(fireman):
    """
    Define como o agente 'Fireman' será exibido na visualização do modelo.
    """
    (x, y) = fireman.pos
    return {
        "Shape": "circle",
        "r": 0.5,                     
        "Filled": True,         
        "Layer": 1,
        "x": x,
        "y": y,  
        "Color":COLORS["Fireman"],                                 
    }



canvas_element = mesa.visualization.CanvasGrid(
    lambda agent: tree_portrayal(agent) if isinstance(agent, Tree) else (
        cloud_portrayal(agent) if isinstance(agent, Cloud) else (
            fireman_portrayal(agent) if isinstance(agent, Fireman) else default_portrayal(agent)
        )
    ),
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
    "tree_density": mesa.visualization.Slider("Tree Density", 0.0, 0.0, 1.0, 0.01),
    "cloud_quantity": mesa.visualization.Slider("Cloud Quantity", 0, 0, 30, 1),
    "fireman_quantity": mesa.visualization.Slider("Fireman Quantity", 0, 0, 1000, 50)
}

server = mesa.visualization.ModularServer(
    ForestFire, [canvas_element, tree_chart, pie_chart], "Forest Fire", model_params
)
