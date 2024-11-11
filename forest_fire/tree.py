import mesa


class Tree(mesa.Agent):
    def __init__(self, unique_id, model, pos, tamanho=50): #tamanho é temporário (esperando biomas)
        super().__init__(unique_id, model)
        self.pos = pos
        self.status = "Fine"
        self.tamanho = tamanho
        self.CO_emission = 0

    def step(self):
        if self.status == "Burning":
            for neighbor in self.model.grid.iter_neighbors(self.pos, True):
                if neighbor.status == "Fine":
                    neighbor.status = "Burning"
            self.CO_emission = self.tamanho * 3
            self.status = "Burned"
            
