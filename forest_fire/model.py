import mesa

from forest_fire.tree import Tree


class ForestFire(mesa.Model):
    def __init__(
        self,
        width=100,
        height=100,
        tree_density=0.65,
        reprod_speed=1, 
    ):
        super().__init__()
        self.width = width
        self.height = height
        self.tree_density = tree_density
        self.schedule = mesa.time.RandomActivation(self)
        self.grid = mesa.space.SingleGrid(self.width, self.height, torus=False)
        self.reprod_speed = reprod_speed 

        self.datacollector = mesa.DataCollector(
            model_reporters={
                "Fine": lambda model: self.count_type(model, "Fine"),
                "Burning": lambda model: self.count_type(model, "Burning"),
                "Burned": lambda model: self.count_type(model, "Burned"),
                "CO2(Kg)": lambda model: self.count_CO2(model)
            }
        )

        self._initialize_trees()

        self.datacollector.collect(self)

    def _initialize_trees(self):
        tree_den = self.tree_density
        for _contents, pos in self.grid.coord_iter():
            tree = Tree(self.next_id(), self, pos, tree_den, self.reprod_speed)
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

    @staticmethod
    def count_CO2(model):
        CO_emission_total = 0
        for tree in model.schedule.agents:
            CO_emission_total += tree.CO_emission
            CO_emission_total -= tree.CO_sequestered
        return CO_emission_total


