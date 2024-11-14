import mesa

class terra(mesa.Agent):
    """
    O agente terra preenche todo o grid.
    Ele altera sua cor dependendo do status da árvore sobre ele.
    """
    def __init__(self, pos, model):
        super().__init__(pos, model)
        self.pos = pos
        self.color = "#E3966B"  # Cor inicial da terra (terra nua)

    def update_color(self):
        """
        Atualiza a cor da terra de acordo com o status da árvore sobre ela.
        """
        # Obtém os agentes na célula atual (no caso, pode haver apenas uma árvore)
        agents_in_cell = self.model.grid.get_cell_list_contents([self.pos])
        
        # Procura por uma árvore na célula
        tree = None
        for agent in agents_in_cell:
            if isinstance(agent, Tree):
                tree = agent
                break  # Só há uma árvore por célula, então podemos sair do loop

        # Se houver uma árvore, atualize a cor da terra com base no seu status

        if tree:
            self.color = tree.color  # Cor da árvore saudável
        else:
            self.color = "#E3966B"  # Caso não haja árvore, mantém a cor original

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
    def __init__(self, unique_id, model, pos, size: float, color: str):
        super().__init__(unique_id, model)
        self.pos = pos
        self.status = "Fine"  # Status inicial da árvore
        self.size = size
        self.color = color  # Cor da árvore, geralmente vinda do bioma

    def step(self):
        """
        A cada passo, a árvore pode pegar fogo e propagar o fogo para as árvores vizinhas.
        """
        if self.status == "Burning":
            for neighbor in self.model.get_neighbors(self.pos, True):
                if isinstance(neighbor, Tree) and neighbor.status == "Fine":
                    neighbor.status = "Burning"  # Propaga o fogo
            self.status = "Burned"  # A árvore queimada não pega mais fogo

    def get_image(self):
        """
        Retorna a imagem associada com base no tamanho da árvore.
        """
        if self.size <= 3:
            image_path = "forest_fire/images/arvore11.png"  # Imagem para árvores bem pequenas
        elif self.size <= 5:
            image_path = "forest_fire/images/arvore22.png"  # Imagem para árvores pequenas
        elif self.size <= 7:
            image_path = "forest_fire/images/arvore33.png"  # Imagem para árvores média
        elif self.size <= 9:
            image_path = "forest_fire/images/arvore44.png"  # Imagem para árvores grandes
        else:
            image_path = "forest_fire/images/arvore55.png"  # Imagem para árvores bem grandes

        return image_path
