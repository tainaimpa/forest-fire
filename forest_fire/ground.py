from mesa import Agent

class Terra(Agent):
    """
    O agente terra preenche todo o grid.
    Ele altera sua cor dependendo do status da árvore sobre ele.
    """
    def __init__(self, pos, model, color, img_path: str = None):
        super().__init__(pos, model)
        self.pos = pos
        self.img_path = img_path
        self.color = color  # Cor padrão da terra (terra nua)
        self.status = "Terra"
        self.burnable = False
    
    def get_image(self):
        return f"{self.img_path}/terra.png"
    
    def step(self):
        pass

class Ground(Terra): # Occupies the cells without trees
    def __init__(self, unique_id, model, pos):
        super().__init__(pos, model, "#6B4423")
        self.pos = pos
        self.status = 'Ground'