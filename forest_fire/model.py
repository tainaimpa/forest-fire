import mesa
from typing import Literal
from forest_fire.cloud import Cloud
from forest_fire.tree import Tree
from forest_fire.biome import biomes


class ForestFire(mesa.Model):
    def __init__(
        self,
        biome_name: Literal["Default"], 
        width=100,
        height=100,
        reprod_speed=1, 
        tree_density=0,
        rainy_season=False,
        cloud_quantity=0,

    ):
        super().__init__()
        self.biome = biomes[biome_name]
        self.width = width
        self.height = height
        self.tree_density = self.biome.density if tree_density == 0 else tree_density
        self.schedule = mesa.time.RandomActivation(self)

        self.reprod_speed = reprod_speed 
        self.grid = mesa.space.MultiGrid(self.width, self.height, torus=False)
        self.rainy_season = rainy_season
        self.cloud_quantity = cloud_quantity
        self.datacollector = mesa.DataCollector(
            model_reporters={
                "Fine": lambda model: self.count_type(model, "Fine"),
                "Burning": lambda model: self.count_type(model, "Burning"),
                "Burned": lambda model: self.count_type(model, "Burned"),
                "CO2(Kg)": lambda model: self.count_CO2(model),
                "Clouds": lambda model: self.count_clouds(model),
            }
        )
        
        self._initialize_trees()
        if rainy_season:
            self._initialize_clouds(cloud_quantity)   #TODO associar a biomas 

        self.datacollector.collect(self)

    def _initialize_trees(self):
        tree_den = self.tree_density
        for _contents, pos in self.grid.coord_iter():
            size = self.biome.size.sort_value()
            color = self.biome.color
            tree = Tree(self.next_id(), self, pos, tree_den, self.reprod_speed,size,color)
  
            if self.random.random() < self.tree_density:
                if pos[0] == 0:  # set first column to Burning
                    tree.status = "Burning"
                else:
                    tree.status = "Fine"
            else:
                tree.status = "Burned"
            self.schedule.add(tree)
            self.grid.place_agent(tree, pos)

    def _initialize_clouds(self, cloud_count):
        """Inicializa nuvens no grid com tamanhos e posições aleatórias."""
        for _ in range(cloud_count):
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            direction = (self.random.choice([-1, 0, 1]), self.random.choice([-1, 0, 1]))
            cloud_size = self.random.randint(2, 5)
            cloud = Cloud(self.next_id(), (x, y), self, size=cloud_size, color="gray", direction=direction, full=False)
            self.schedule.add(cloud)
            self.grid.place_agent(cloud, (x, y))

    def step(self):
        """Atualiza o modelo a cada passo."""
        self.schedule.step()
        self.datacollector.collect(self)
        
        # Adiciona novas nuvens com tamanhos variados a cada 10 passos
        if self.rainy_season and self.schedule.steps % 10 == 0:
            self._initialize_clouds(5)  # Adiciona 5 novas nuvens a cada 10 passos

    @staticmethod
    def count_type(model, status):
        count = 0
        for tree in model.schedule.agents:
            if isinstance(tree, Tree) and tree.status == status:
                count += 1
        return count

    @staticmethod
    def count_clouds(model):
        """Conta o número de nuvens no modelo."""
        count = 0
        for cloud in model.schedule.agents:
            if isinstance(cloud, Cloud):
                count += 1
        return count

    @staticmethod
    def count_CO2(model):
        CO_emission_total = 0
        for tree in model.schedule.agents:
            CO_emission_total += tree.CO_emission * model.biome.CO2_emission_factor
            CO_emission_total -= tree.CO_sequestered * model.biome.CO2_emission_factor
        return CO_emission_total


