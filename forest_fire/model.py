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
        corridor=True,
        individual_lakes=True,
        reprod_speed=1, 
    ):
        super().__init__()
        self.width = width
        self.height = height
        self.tree_density = tree_density
        self.water_density = water_density
        self.num_of_lakes = num_of_lakes
        self.obstacles = obstacles
        self.corridor = corridor
        self.individual_lakes = individual_lakes
        self.schedule = mesa.time.RandomActivation(self)
        self.grid = mesa.space.SingleGrid(self.width, self.height, torus=False)
        self.reprod_speed = reprod_speed 

        self.datacollector = mesa.DataCollector(
            model_reporters={
                "Fine": lambda model: self.count_type(model, "Fine"),
                "Burning": lambda model: self.count_type(model, "Burning"),
                "Burned": lambda model: self.count_type(model, "Burned"),
            }
        )

        self._initialize_trees()

        self.datacollector.collect(self)

    def _initialize_trees(self):
        for _ in range(self.num_of_lakes):
            self._initialize_lake_organic()
        for _contents, pos in self.grid.coord_iter():
            if random.random() < self.tree_density:
                agent = Tree(self.next_id(), self, pos, self.tree_density, self.reprod_speed)
                if pos[0] == 0:  # set first column to Burning
                    agent.status = "Burning"
                self.schedule.add(agent)
                if self.grid.is_cell_empty(pos):
                    self.grid.place_agent(agent, pos)
            elif self.individual_lakes and random.random() < self.water_density**2:
                self._initialize_water(pos)
            else:
                self._initialize_other_agent(pos)
                    
    def _initialize_other_agent(self, pos):
        def get_types_and_weights():
            types = ["Ground", "Corridor", "Obstacle"]
            weights_list = [0.5, 0.1, 0.1]
            if not self.obstacles:
                types.remove("Obstacle")
                weights_list.pop()
            if not self.corridor:
                types.remove("Corridor")
                weights_list.pop()
            return types, weights_list
            
        types, weights_list = get_types_and_weights()
            
        agent_type = random.choices(types, weights=weights_list)[0]
        match agent_type:
            case "Ground":
                self._initialize_ground(pos)
            case "Corridor":
                self._initialize_corridor(pos)
            case "Obstacle":
                self._initialize_obstacle(pos)
                
    def _initialize_ground(self, pos):
        ground = Ground(self.next_id(), self, pos)
        if self.grid.is_cell_empty(pos):
            self.schedule.add(ground)
            self.grid.place_agent(ground, pos)
            
    def _initialize_water(self, pos):
        water = Lake(self.next_id(), self, pos)
        if self.grid.is_cell_empty(pos):
            self.schedule.add(water)
            self.grid.place_agent(water, pos)
            
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
        self.lake_size = int(self.water_density * 50)
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
                if self.grid.is_cell_empty(pos):
                    self.schedule.add(lake)
                    self.grid.place_agent(lake, pos)           

    def _initialize_obstacle(self, pos):
        obstacle = Obstacle(self.next_id(), self, pos)
        self.schedule.add(obstacle)
        if self.grid.is_cell_empty(pos):
            self.grid.place_agent(obstacle, pos)
    
    def _initialize_corridor(self, pos):
        corridor = Corridor(self.next_id(), self, pos)
        self.schedule.add(corridor)
        if self.grid.is_cell_empty(pos):
            self.grid.place_agent(corridor, pos)

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
