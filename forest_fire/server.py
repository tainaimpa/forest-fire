import mesa
import mesa.visualization
from forest_fire.tree import Tree, terra
from forest_fire.model import ForestFire

# Ajuste do tamanho do grid e da tela
GRID_WIDTH = 10
GRID_HEIGHT = 10        
CANVAS_WIDTH = 500
CANVAS_HEIGHT = 500

# Definindo as cores baseadas no status das árvores
COLORS = {
    "Burning": "#FF0000",  # Cor para árvores em chamas
    "Burned": "#3D2B1F",   # Cor para árvores queimadas
    "Fine": "#00AA00",     # Cor para árvores saudáveis
}

def tree_portrayal(agent):
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

    # Se o agente for do tipo 'terra'
    if isinstance(agent, terra):
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

        portrayal["w"] = 1  # Largura da célula no grid
        portrayal["h"] = 1  # Altura da célula no grid
        portrayal["x"] = x
        portrayal["y"] = y
           

    # Se o agente for uma árvore
    elif isinstance(agent, Tree):
        image = agent.get_image()  # Caminho da imagem da árvore
        portrayal["Color"] = COLORS.get(agent.status, "#E3966B")  # Cor da árvore com base no status
        portrayal["Shape"] = image  # A árvore será representada como um quadrado (ou outra forma, dependendo da imagem)
        portrayal["Scale"] = 1.1
        portrayal["Filled"] = "true"
        portrayal["Layer"] = 1
        portrayal["w"] = 1  # Largura da célula no grid (pode ser ajustada)
        portrayal["h"] = 1  # Altura da célula no grid (pode ser ajustada)
        portrayal["x"] = x
        portrayal["y"] = y

    return portrayal

canvas_element = mesa.visualization.CanvasGrid(
    tree_portrayal, GRID_WIDTH, GRID_HEIGHT, CANVAS_WIDTH, CANVAS_HEIGHT
)

tree_chart = mesa.visualization.ChartModule(
    [{"Label": label, "Color": color} for label, color in COLORS.items()]
)

pie_chart = mesa.visualization.PieChartModule(
    [{"Label": label, "Color": color} for label, color in COLORS.items()]
)

model_params = {
    "width": GRID_WIDTH,
    "height": GRID_HEIGHT,
    "tree_density": mesa.visualization.Slider("Tree Density", 0.65, 0.01, 1.0, 0.01),
}

server = mesa.visualization.ModularServer(
    ForestFire, [canvas_element, tree_chart, pie_chart], "Forest Fire", model_params
)
