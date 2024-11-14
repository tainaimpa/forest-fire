import mesa
from forest_fire.tree import Tree, terra
from forest_fire.model import ForestFire

# Ajuste do tamanho do grid e da tela
GRID_WIDTH = 25
GRID_HEIGHT = 25        
CANVAS_WIDTH = 500
CANVAS_HEIGHT = 500

COLORS = {
    "Burning": "#FF0000",
    "Burned": "#3D2B1F",
}

def tree_portrayal(tree):
    if not tree:
        return
    portrayal = {}
    x, y = tree.pos

    if isinstance(tree, terra):
        portrayal["Layer"] = 0  # A camada do quadrado (grid)
        portrayal["x"] = x
        portrayal["y"] = y
        portrayal["Color"] = "#99FF99"
        portrayal["Filled"] = True
        portrayal["w"] = 1  # Tamanho da célula (grid)
        portrayal["h"] = 1
        portrayal["Shape"] = "rect"

    else:
        # Pega a posição da árvore
        
        color = COLORS.get(tree.status, "#FFFFFF")  # Cor padrão branca se status não for encontrado
        # Obtém o caminho da imagem associada ao tamanho da árvore
        image = tree.get_image()  # Imagem associada ao tamanho da árvore
        
        # Criação do dicionário de propriedades para a árvore


        # Desenha o quadrado colorido (grid) primeiro
        portrayal["Color"] = color  # Cor do grid associada à árvore
        portrayal["w"] = 1  # Tamanho da célula (grid)
        portrayal["h"] = 1
        portrayal["Layer"] = 1  # A camada do quadrado (grid)
        portrayal["x"] = x
        portrayal["y"] = y
        portrayal["Filled"] = True
        """
        ARRUMAR:
        Não está gerando os retângulos com as cores das árvores
        apenas colocando a imagem da árvore.
        """
        
        # Agora, colocamos a imagem da árvore (com fundo transparente)
        portrayal["Shape"] = image  
        portrayal["Image_File"] = image  # Caminho da imagem
        portrayal["w"] = 1  # Tamanho da imagem
        portrayal["h"] = 1  # Tamanho da imagem
        portrayal["Layer"] = 1  # Coloca a imagem sobre o quadrado colorido

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
