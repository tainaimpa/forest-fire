import mesa

# Dicionário de cores para cada status da árvore
COLORS = {
    "Fine": "#00AA00",
    "Burning": "#FF0000",  # Cor para árvores queimando (vermelho)
    "Burned": "#3D2B1F"    # Cor para árvores queimadas (marrom escuro)
}

class Terra(mesa.Agent):
    """
    O agente terra preenche todo o grid.
    Ele altera sua cor dependendo do status da árvore sobre ele.
    """
    def __init__(self, pos, model, color: str, img_path: str = None):
        super().__init__(pos, model)
        self.pos = pos
        self.img_path = img_path
        self.color = "#E3966B"  # Cor padrão da terra (terra nua)
               
    def update_color(self):
        """
        Atualiza a cor da terra de acordo com o status da árvore sobre ela.
        Se não houver árvore, usa a imagem padrão 'terra.png'.
        """
        # Obtém os agentes na célula atual (no caso, pode haver apenas uma árvore)
        agents_in_cell = self.model.grid.get_cell_list_contents([self.pos])
        
        # Procura por uma árvore na célula
        tree = None
        for agent in agents_in_cell:
            if isinstance(agent, Tree):
                tree = agent
                break  # Só há uma árvore por célula, então podemos sair do loop

        # Se houver uma árvore, atualize a imagem/cor da terra com base no seu status

        if tree:
            if tree.status == "Fine":
                # Se a árvore estiver "Fine", a terra terá a cor do bioma
                self.color = self.model.biome.color  # Define a cor da terra como a cor do bioma
                self.img_path = None  # Não precisamos de imagem, apenas a cor
            else:
                # Para os status "Burning" e "Burned", usamos as cores associadas
                self.color = COLORS.get(tree.status, "#E3966B")  # A cor associada ao status da árvore
                self.img_path = None  # Não precisamos de imagem, apenas a cor
        
        else:
            # Se não houver árvore, verificamos o bioma
            if self.model.biome.name != "Default":
                # Se o bioma não for "Default", usamos a imagem da terra associada ao bioma
                self.color = None  # Não usamos cor, porque vamos usar a imagem da terra
                self.img_path = f"{self.model.biome.img_path}/terra.png"
            else:
                # Se o bioma for "Default", mantemos a cor padrão da terra
                self.color = "#E3966B"  # Cor padrão da terra
                self.img_path = None  # Não usamos imagem
        
    def step(self):
        """
        Atualiza a cor da terra a cada passo.
        """
        self.update_color()
        
class Tree(mesa.Agent):
    """
    A árvore é um agente que pode ter diferentes estados, como 'Fine', 'Burning' ou 'Burned'.
    Ela também tem uma imagem que depende do seu tamanho.
    """
    def __init__(self, unique_id, model, pos, size: float, color: str, img_path: str = None):
        super().__init__(unique_id, model)
        self.pos = pos
        self.status = "Fine"  # Status inicial da árvore
        self.size = size
        self.color = color  # Cor da árvore, geralmente vinda do bioma
        self.img_path = img_path

    def step(self):
        """
        A cada passo, a árvore pode pegar fogo e propagar o fogo para as árvores vizinhas.
        """
        if self.status == "Burning":
            for neighbor in self.model.grid.iter_neighbors(self.pos, True):
                if neighbor.status == "Fine":
                    neighbor.status = "Burning"
            self.status = "Burned"
