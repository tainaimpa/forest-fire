from mesa import Agent

class Obstacle(Agent): # Create a general obstacle
    def __init__(self, unique_id, model, pos):
        super().__init__(unique_id, model)
        self.burnable = False
        self.pos = pos
        self.status = "Obstacle"
        
class Puddle(Obstacle):
    def __init__(self, unique_id, model, pos):
        super().__init__(unique_id, model)
        self.burnable = True
        self.status = "Wet"
        
    def step(self):
        if self.status == 'Steaming' and self.width != 1:
            for neighbor in self.model.grid.iter_neighbors(self.width, True):
                if neighbor.status == "Wet":
                    neighbor.status = "Steaming"
            self.status = "Evaporated"
            
class Lake(Obstacle):
    def __init__(self, unique_id, model, pos):
        super().__init__(unique_id, model, pos)
        self.burnable = False
        self.status = "Lake"

class Corridor(Obstacle):
    def __init__(self, unique_id, model, pos, radius=1):
        super().__init__(unique_id, model, pos)
        self.burnable = True
        self.spread_rate = 2.0
        self.status = "Corridor"
        self.radius = radius
        
    def step(self):
        if self.status == "Burned":
            self.model.grid.remove_agent(self)
            self.model.schedule.remove(self)