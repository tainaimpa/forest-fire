import mesa


class Tree(mesa.Agent):
    def __init__(self, unique_id, model, pos, size=10): # Os tamanhos serão definidos na parte de Biomas
        super().__init__(unique_id, model)
        self.pos = pos
        self.status = "Fine"
        self.size = size
        self.CO_emission = 0

    def step(self):
        if self.status == "Burning":
            for neighbor in self.model.grid.iter_neighbors(self.pos, True):
                if neighbor.status == "Fine":
                    neighbor.status = "Burning"
            # Cálculo de CO2 emitido na queima da árvore
            self.CO_emission = self.size * 20 * 0.5 * 3.67 # Biomassa x 0.5 x 3.67
            self.status = "Burned"
            
