from mesa import Agent


class Ground(Agent): # Occupies the cells without trees
    def __init__(self, unique_id, model, pos):
        super().__init__(unique_id, model)
        self.pos = pos
        self.status = 'Ground'
        self.burnable = False