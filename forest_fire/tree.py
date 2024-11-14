import mesa

class terra(mesa.Agent):
    def __init__(self, pos, model):

        super().__init__(pos, model)
        self.pos = pos
 


class Tree(mesa.Agent):
    def __init__(self, unique_id, model, pos, size: float, color: str):
        super().__init__(unique_id, model)
        self.pos = pos
        self.status = "Fine"
        self.size = size
        self.color = color
        
    def step(self):
        if self.status == "Burning":
            for neighbor in self.model.grid.iter_neighbors(self.pos, True):
                if neighbor.status == "Fine":
                    neighbor.status = "Burning"
            self.status = "Burned"

    def get_image(self):
        """
        Retorna a imagem associada com base no tamanho da árvore.
        """
        if self.size <= 3:
            image_path = "forest_fire/images/arvore11.png" # Imagem para árvores bem pequenas
        elif self.size <= 5:
            image_path = "forest_fire/images/arvore22.png" # Imagem para árvores pequenas  
        elif self.size <= 7:
            image_path = "forest_fire/images/arvore33.png" # Imagem para árvores média
        elif self.size <= 9:
            image_path = "forest_fire/images/arvore44.png" # Imagem para árvores grandes 
        else:
            image_path = "forest_fire/images/arvore55.png" # Imagem para árvores bem grandes         

        return image_path
    


