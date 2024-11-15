import mesa

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
                if isinstance(neighbor, Tree) and neighbor.status == "Fine":
                    neighbor.status = "Burning"
            self.status = "Burned"
