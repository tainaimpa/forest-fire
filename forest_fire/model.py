import mesa
from typing import Literal

from forest_fire.tree import Tree
from forest_fire.biome import biomes


class ForestFire(mesa.Model):
    def __init__(
        self,
        biome_name: Literal["Default"], 
        width=100,
        height=100,
        tree_density=0,
        rainy_season=False
    ):
        super().__init__()
        self.biome = biomes[biome_name]
        self.width = width
        self.height = height
        self.tree_density = self.biome.density if tree_density == 0 else tree_density
        self.schedule = mesa.time.RandomActivation(self)
        self.grid = mesa.space.MultiGrid(self.width, self.height, torus=False)
        self.rainy_season = rainy_season
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
        for _contents, pos in self.grid.coord_iter():
            size = self.biome.size.sort_value()
            color = self.biome.color
            tree = Tree(self.next_id(), self, pos, size, color)
            if self.random.random() < self.tree_density:
                if pos[0] == 0:  # set first column to Burning
                    tree.status = "Burning"
                else:
                    tree.status = "Fine"
            else:
                tree.status = "Burned"
            self.schedule.add(tree)
            self.grid.place_agent(tree, pos)

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
