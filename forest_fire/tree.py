import mesa
import random

from forest_fire.obstacles import Lake, Corridor

class Tree(mesa.Agent):
    def __init__(self, unique_id, model, pos):
        super().__init__(unique_id, model)
        self.pos = pos
        self.status = "Fine"
        self.burnable = True

    def step(self):
        if self.status == "Burning":
            for neighbor in self.model.grid.iter_neighbors(self.pos, moore=True):
                if isinstance(neighbor, Lake):
                    self.status = "Burned"
            if self.status == "Burning":
                for neighbor in self.model.grid.iter_neighbors(self.pos, moore=True):
                    if neighbor.status == "Fine" and neighbor.burnable:
                        neighbor.status = "Burning"
                    if neighbor.status == 'Corridor' and neighbor.burnable:
                        neighbor.status = "Burned"
                        for neighbor_c in self.model.grid.iter_neighbors(neighbor.pos, moore=True):
                            if neighbor_c.status == "Fine" and neighbor_c.burnable:
                                neighbor_c.status = "Burning"
            self.status = "Burned"