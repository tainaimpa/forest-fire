import mesa

from forest_fire.tree import Tree
from forest_fire.obstacles import Lake, Corridor, Obstacle
from forest_fire.ground import Ground
from mesa import Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
import random
import numpy as np
from scipy import ndimage


class ForestFire(mesa.Model):
    def __init__(
        self,
        width=100,
        height=100,
        tree_density=0.65,
        water_density=0.15,
        num_of_lakes=1,
        obstacles=True,
        corridor=True
    ):
        super().__init__()
        self.width = width
        self.height = height
        self.tree_density = tree_density
        self.water_density = water_density
        self.num_of_lakes = num_of_lakes
        self.obstacles = obstacles
        self.corridor = corridor
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
        types = [Ground, Corridor, Obstacle]
        weights_list = [0.5, 0.1, 0.1]
        if not self.obstacles:
            types.remove(Obstacle)
            weights_list.pop()
        if not self.corridor:
            types.remove(Corridor)
            weights_list.pop()
        
        for _ in range(self.num_of_lakes):
            self._initialize_lake_organic()
        for _contents, pos in self.grid.coord_iter():
            if random.random() < self.tree_density:
                agent = Tree(self.next_id(), self, pos)
                if pos[0] == 0:  # set first column to Burning
                    agent.status = "Burning"
                self.schedule.add(agent)
                if self.grid.is_cell_empty(pos):
                    self.grid.place_agent(agent, pos)
            elif random.random() < self.water_density**2:
                agent = Lake(self.next_id(), self, pos)
                if self.grid.is_cell_empty(pos):
                    self.schedule.add(agent)
                    self.grid.place_agent(agent, pos)
            else:
                agent_type = random.choices(
                    types, 
                    weights=weights_list)[0]
                agent = agent_type(self.next_id(), self, pos)
                self.schedule.add(agent)
                if self.grid.is_cell_empty(pos):
                    self.grid.place_agent(agent, pos)
                
    def _initialize_lake(self):
        self.lake_size = int(self.water_density*50)
        x, y = random.randint(0, self.width - 1), random.randint(0, self.height - 1)
        center_lake = Lake(self.next_id(), self, (x, y))
        self.schedule.add(center_lake)
        self.grid.place_agent(center_lake, (x,y))
        
        for pos in self.grid.iter_neighborhood((x,y), moore=True, radius=self.lake_size):
            lake = Lake(self.next_id(), self, pos)
            self.schedule.add(lake)
            self.grid.place_agent(lake, pos)

    def _initialize_lake_organic(self):
        self.lake_size = int(self.water_density * 100)
        x, y = random.randint(0, self.width - 1), random.randint(0, self.height - 1)
        center_lake = Lake(self.next_id(), self, (x, y))
        self.schedule.add(center_lake)
        self.grid.place_agent(center_lake, (x, y))

        # Generate noise field using NumPy
        noise_scale = 0.1
        shape = (self.width, self.height)
        noise_field = np.random.randn(*shape) * noise_scale

        # Apply smoothing (optional)
        smoothed_noise = ndimage.convolve(noise_field, np.ones((3, 3)) / 9, mode='reflect')

        # Iterate through neighborhood and add lake cells based on noise
        for pos in self.grid.iter_neighborhood((x, y), moore=False, radius=self.lake_size):
            noise_value = smoothed_noise[pos[1]][pos[0]]
            if noise_value > 1e-15:  # Adjust threshold for desired lake shape
                lake = Lake(self.next_id(), self, pos)
                self.schedule.add(lake)
                self.grid.place_agent(lake, pos)

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
