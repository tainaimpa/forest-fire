import mesa
from forest_fire.model import ForestFire
from forest_fire.tree import Tree, Terra
from forest_fire.obstacles import Obstacle, Corridor, Puddle, Lake
from forest_fire.cloud import Cloud
from forest_fire.fireman import Fireman

# Ajuste do tamanho do grid e da tela
GRID_WIDTH = 75
GRID_HEIGHT = 75
CANVAS_WIDTH = 750
CANVAS_HEIGHT = 750

# Definindo as cores baseadas no status das árvores
COLORS = {
    "Fine": "#148c39", #green
    "Burning": "#cf0f0f", # Cor para árvores queimando (vermelho)
    "Burned": "#3D2B1F", # Cor para árvores queimadas (marrom escuro)
    "Lake": "#3A77F0", #blue
    "Corridor": "#8FBF3C",
    "Obstacle": "#6E6E6E",
    "Cloud": "#A0A0A0",  # TODO nuvens cheias mais escuras 
    "Terra": "#6B4423",
    "Extinguished": "#FFFFFF",
    "Fireman": "#00A8FF" 
}

def agent_portrayal(agent):
    """
    Função que determina como um agente (árvore ou terra) será representado no grid.

    :param agent: O agente a ser desenhado (pode ser uma árvore ou terra)
    :return: Um dicionário com as propriedades para renderização do agente
    """
    # Verifica se o agente é 'None' (caso o grid tenha uma célula vazia)
    if not agent:
        return 

    x, y = agent.pos
    
    if isinstance(agent, Obstacle) or isinstance(agent, Corridor) or isinstance(agent, Puddle) or isinstance(agent, Lake):
        return {
            "Shape": "rect",
            "w": 1,
            "h": 1,
            "Filled": True,
            "Layer": 10,
            "x": x,
            "y": y,
            "Color": COLORS[agent.status],
        }

    if isinstance(agent, Terra):
        # A cor e a imagem da Terra já são gerenciadas pela classe Terra
        # A função update_color() é chamada no método step() de Terra
        # Se a Terra tem uma imagem associada, usa a imagem
        
        # Obtém as árvores na célula atual
        trees_in_cell = agent.model.get_cell_items([agent.pos], [Tree])
        tree = None if len(trees_in_cell) == 0 else trees_in_cell[0]
        
        obstacles_in_cell = agent.model.get_cell_items([agent.pos], [Obstacle, Corridor, Puddle, Lake])
        
        shape = 'rect'
        color = agent.color if agent.color else COLORS["Terra"]
        if tree:
            if tree.status == 'Fine':
                color = tree.color if tree.color else COLORS["Fine"]
            else:
                color = COLORS[tree.status]
        elif len(obstacles_in_cell) != 0:
            obstacle = obstacles_in_cell[0]
            color = COLORS[obstacle.status] 
        elif agent.img_path:
            shape = agent.get_image()
        
        return {
            "x": x,
            "y": y,
            "w": 1,
            "h": 1,
            "Layer": 0,
            "Filled": True,
            "Shape": shape,  # Forma da Terra (imagem ou retângulo)
            "Color": color,  # Cor da Terra
        }

    if isinstance(agent, Tree):
        image = agent.get_image()  # Obtém o caminho da imagem da árvore
        color = agent.color if agent.color else COLORS["Fine"]
        if agent.status != "Fine":
            color = COLORS[agent.status]
                
        return {
            "x" : x,
            "y" : y,
            "w" : 1,
            "h" : 1,
            "Layer" : 1,
            "Filled": True,
            "Shape": image if image else 'rect',
            "Color": color
        }

    if isinstance(agent, Cloud):
            return {
                "Shape": "circle",
                "r": agent.size,  
                "Filled": True,
                "Layer": 20,
                "x": x,
                "y": y,
                "Color": COLORS["Cloud"], 
            }
    
    if isinstance(agent, Fireman):
        return {
            "Shape": "circle",
            "r": 0.5,                     
            "Filled": True,         
            "Layer": 1,
            "x": x,
            "y": y,  
            "Color":COLORS["Fireman"],                                 
        }

canvas_element = mesa.visualization.CanvasGrid(lambda agent: agent_portrayal(agent), GRID_WIDTH, GRID_HEIGHT, CANVAS_WIDTH, CANVAS_HEIGHT)

canvas_element = mesa.visualization.CanvasGrid(
    lambda agent: agent_portrayal(agent),
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
    "tree_density": mesa.visualization.Slider("Tree Density", 0.65, 0.01, 1.0, 0.01),
    "random_fire" : mesa.visualization.Checkbox("Random Fire Start", True),
    "position_fire": mesa.visualization.Choice("Fire Start Direction","Top", ["Top", "Bottom", "Left", "Right", "Middle"]),
    "tree_density": mesa.visualization.Slider("Tree Density", 0, 0, 1.0, 0.01, description="If the value is 0, the biome density will be used."),
    "cloud_quantity": mesa.visualization.Slider("Cloud Quantity", 0, 0, 30, 1),
    "fireman_quantity": mesa.visualization.Slider("Fireman Quantity", 0, 0, 1000, 50),
    "reprod_speed": mesa.visualization.Slider("Reproduction Rate", 1, 0.0, 1.0, 0.1), 
    "water_density": mesa.visualization.Slider("Water Density", 0.15, 0, 1.0, 0.01),
    "num_of_lakes": mesa.visualization.Slider("Number of Lakes", 1, 0, 10, 1), 
    "corridor_density": mesa.visualization.Slider("Corridor Density", 0.15, 0, 1.0, 0.01), 
    "obstacles_density": mesa.visualization.Slider("Obstacles Density", 0.15, 0, 1.0, 0.01),
    "obstacles": mesa.visualization.Checkbox("Obstacles", True),
    "corridor": mesa.visualization.Checkbox("Corridor", True),
    "individual_lakes": mesa.visualization.Checkbox("Individual Lakes", True),
    "wind_direction": mesa.visualization.Choice("Wind Direction", "N", ["N", "S", "E", "W"]),
    "wind_intensity": mesa.visualization.Slider("Wind Intensity", 0.5, 0.0, 1.0, 0.1),
}

server = mesa.visualization.ModularServer(
    ForestFire, [canvas_element, tree_chart, pie_chart], "Forest Fire", model_params
)
