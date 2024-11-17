import mesa
import mesa.visualization
from forest_fire.tree import Tree, Terra
from forest_fire.model import ForestFire
from forest_fire.tree import Tree
from forest_fire.cloud import Cloud

# Ajuste do tamanho do grid e da tela
GRID_WIDTH = 10
GRID_HEIGHT = 10    
CANVAS_WIDTH = 500
CANVAS_HEIGHT = 500

# Definindo as cores baseadas no status das árvores
COLORS = {
    "Fine": "#00AA00",
    "Burning": "#FF0000",
    "Burned": "#3D2B1F",
    "Cloud": "#A0A0A0",  # TODO nuvens cheias mais escuras 
}

def agent_portrayal(agent):
    """
    Função que determina como um agente (árvore ou terra) será representado no grid.

    :param agent: O agente a ser desenhado (pode ser uma árvore ou terra)
    :return: Um dicionário com as propriedades para renderização do agente
    """
    # Verifica se o agente é 'None' (caso o grid tenha uma célula vazia)
    if not agent:
        return {}

    portrayal = {}
    
    x, y = agent.pos
    
    # Características comuns a todos agentes
    portrayal["x"] = x
    portrayal["y"] = y

    # Se o agente for do tipo 'Terra'
    if isinstance(agent, Terra):
        # Verifica se há uma árvore diretamente sobre a terra
        agents_in_cell = agent.model.grid.get_cell_list_contents([agent.pos])
        
        # Procura por uma árvore na célula de terra
        tree_in_cell = None
        for agent in agents_in_cell:
            if isinstance(agent, Tree):  # Se encontrar uma árvore, armazena
                tree_in_cell = agent
                break

        # Se houver uma árvore sobre a terra, a cor da terra será a cor da árvore
        if tree_in_cell:
            portrayal["Color"] = COLORS.get(tree_in_cell.status, "#E3966B")  # Cor da árvore 
            portrayal["Shape"] = "rect"
            portrayal["Filled"] = "true"
            portrayal["Layer"] = 0
  
        else:
            """
            Acrescentar: Mudança da terra de acordo com o bioma.
            Substituir pela imagem transparente (para que a terra mude de acordo com a influência das
            células vizinhas, com condições: se 5 células vizinhas terem árvores queimadas então a terra
            recebe no layer 0 a cor da árvore - simulando que o fogo se alastra pela terra visualmente). 
            """
            sem_arvore = "forest_fire/images/cerrado/terra.png"
            portrayal["Shape"] = sem_arvore  # imagem da terra no bioma selecionado
            portrayal["Filled"] = "true"
            portrayal["Layer"] = 0
            
        portrayal["w"] = 1  # Largura da célula no grid (pode ser ajustada)
        portrayal["h"] = 1  # Altura da célula no grid (pode ser ajustada)
           

    # Se o agente for uma árvore
    elif isinstance(agent, Tree):
        image = agent.get_image()  # Caminho da imagem da árvore
        portrayal["Color"] = COLORS.get(agent.status, "#E3966B")  # Cor da árvore com base no status
        portrayal["Shape"] = image if image else 'rect'  # A árvore será representada como um quadrado (ou outra forma, dependendo da imagem)
        portrayal["Scale"] = 1.1
        portrayal["Filled"] = "true"
        portrayal["Layer"] = 1
        portrayal["w"] = 1  # Largura da célula no grid (pode ser ajustada)
        portrayal["h"] = 1  # Altura da célula no grid (pode ser ajustada)
        
    # Se o agente for uma nuvem
    elif isinstance(agent, Cloud):
        portrayal["Shape"] = 'circle'
        portrayal["r"] = agent.size
        portrayal["Filled"] = "true"
        portrayal["Layer"] = 2
        portrayal["color"] = COLORS["Cloud"]

    return portrayal

canvas_element = mesa.visualization.CanvasGrid(
    lambda agent: agent_portrayal(agent),
    GRID_WIDTH, GRID_HEIGHT, CANVAS_WIDTH, CANVAS_HEIGHT
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
