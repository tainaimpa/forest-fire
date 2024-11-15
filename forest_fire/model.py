import mesa

from forest_fire.tree import Tree
from forest_fire.obstacles import Lake, Corridor, Obstacle
from forest_fire.ground import Ground
from mesa import Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
import random


class ForestFire(mesa.Model):
    def __init__(
        self,
        width=100,
        height=100,
        tree_density=0.65,
    ):
        super().__init__()
        self.width = width
        self.height = height
        self.tree_density = tree_density
        self.schedule = mesa.time.RandomActivation(self)
        self.grid = mesa.space.SingleGrid(self.width, self.height, torus=False)

        self.datacollector = mesa.DataCollector(
            model_reporters={
                "Fine": lambda model: self.count_type(model, "Fine"),
                "On Fire": lambda model: self.count_type(model, "Burning"),
                "Burned": lambda model: self.count_type(model, "Burned"),
            }
        )

        self._initialize_trees()

        self.datacollector.collect(self)

    def _initialize_trees(self):
        for _contents, pos in self.grid.coord_iter():
            if random.random() < self.tree_density:
                agent_type = random.choices(
                    [Tree, Lake, Corridor, Obstacle], 
                    weights=[0.7, 0.1, 0.1, 0.1]
                )[0]
                agent = agent_type(self.next_id(), self, pos)
                if isinstance(agent, Tree) and pos[0] == 0:  # set first column to Burning
                    agent.status = "Burning"
                self.schedule.add(agent)
                if not self.grid.is_cell_empty(pos):
                    self.grid.remove_agent(_contents)
                self.grid.place_agent(agent, pos)
            else:
                ground = Ground(self.next_id(), self, pos)
                self.schedule.add(ground)
                self.grid.place_agent(ground, pos)

    def step(self):
        self.schedule.step()
        self.datacollector.collect(self)

    @staticmethod
    def count_type(model, status):
        count = 0
        for tree in model.schedule.agents:
            if tree.status == status:
                count += 1
        return count
