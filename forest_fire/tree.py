from mesa import Agent


class Tree(Agent):
    def __init__(self, unique_id, model, pos):
        super().__init__(unique_id, model)
        self.pos = pos
        self.status = "Fine"
        self.burnable = True

    def step(self):
        if self.status == "Burning":
            for neighbor in self.model.grid.iter_neighbors(self.pos, moore=True):
                if neighbor.status == "Fine" and neighbor.burnable:
                    neighbor.status = "Burning"
            self.status = "Burned"


class Obstacle(Tree):
    def __init__(self, unique_id, model, pos):
        super().__init__(unique_id, model, pos)
        self.burnable = False
        self.status = "Obstacle"

class Lake(Tree):
    def __init__(self, unique_id, model, pos):
        super().__init__(unique_id, model, pos)
        self.burnable = False

class Corridor(Tree):
    def __init__(self, unique_id, model, pos):
        super().__init__(unique_id, model, pos)
        self.burnable = True
        self.spread_rate = 2.0
        self.status = "Corridor"