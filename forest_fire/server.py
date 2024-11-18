import mesa
import mesa.visualization
from forest_fire.tree import Tree, Terra
from forest_fire.model import ForestFire
from forest_fire.cloud import Cloud

# Ajuste do tamanho do grid e da tela
GRID_WIDTH = 30
GRID_HEIGHT = 30    
CANVAS_WIDTH = 500
CANVAS_HEIGHT = 500

# Definindo as cores baseadas no status das árvores
COLORS = {
    "Cloud": "#A0A0A0",  # TODO nuvens cheias mais escuras 
    "Fine": "#00AA00",
    "Burning": "#FF0000",  # Cor para árvores queimando (vermelho)
    "Burned": "#3D2B1F"    # Cor para árvores queimadas (marrom escuro)
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

    if type(agent) is Terra:
         # A cor e a imagem da Terra já são gerenciadas pela classe Terra
        # A função update_color() é chamada no método step() de Terra
        # Se a Terra tem uma imagem associada, usa a imagem
        if agent.img_path:
            shape = "image"
            file = agent.img_path 
            color = None
            
        else:
            shape = "rect" 
            color = agent.color
            file = None
        return {
            "x": x,
            "y": y,
            "w": 1,
            "h": 1,
            "Layer": 0,
            "Filled": True,
            "Shape": shape,  # Forma da Terra (imagem ou retângulo)
            "Image_File": file,
            "Color": color,  # Cor da Terra
        }

    if type(agent) is Tree:
        
        image = agent.get_image()  # Obtém o caminho da imagem da árvore
        shape = "image"  # Usando 'image' para a árvore
                
        return {"x" : x,
                "y" : y,
                "w" : 1,
                "h" : 1,
                "Layer" : 1,
                "Filled": True,
                "Shape": shape,
                 "Image File": image }
                #"Color": agent.color if agent.color else "#00AA00" }

    if type(agent) is Cloud:
            return {
        "Shape": "circle",
        "r": agent.size,  
        "Filled": True,
        "Layer": 20,
        "x": x,
        "y": y,
        "Color": COLORS["Cloud"], }

canvas_element = mesa.visualization.CanvasGrid(agent_portrayal, GRID_WIDTH, GRID_HEIGHT, CANVAS_WIDTH, CANVAS_HEIGHT
)

# TODO adicionar o numero de nuvens e um novo grafico para arvores apagadas  
tree_chart = mesa.visualization.ChartModule(
    [{"Label": label, "Color": color} for label, color in COLORS.items()]
)

pie_chart = mesa.visualization.PieChartModule(
    [{"Label": label, "Color": color} for label, color in COLORS.items()]
)

model_params = {
    "rainy_season": mesa.visualization.Checkbox("Estação chuvosa", False),
    "biome_name": mesa.visualization.Choice("Biome", "Default", ["Default","Amazônia","Caatinga","Cerrado","Pantanal","Mata Atlântica"]), 
    "width": GRID_WIDTH,
    "height": GRID_HEIGHT,
    "tree_density": mesa.visualization.Slider("Tree Density", 0.0, 0.0, 1.0, 0.01),
    "cloud_quantity": mesa.visualization.Slider("Cloud Quantity", 0, 0, 30, 1),
}

server = mesa.visualization.ModularServer(
    ForestFire, [canvas_element, tree_chart, pie_chart], "Forest Fire", model_params
)
