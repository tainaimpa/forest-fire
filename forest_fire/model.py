import mesa

from forest_fire.tree import Tree


class ForestFire(mesa.Model):
    def __init__(
        self,
        width=100,
        height=100,
        tree_density=0.65,
        reprod_speed=1, # Implementação do reprod_speed
    ):
        super().__init__()
        self.width = width
        self.height = height
        self.tree_density = tree_density
        self.schedule = mesa.time.RandomActivation(self)
        self.grid = mesa.space.SingleGrid(self.width, self.height, torus=False)
        self.reprod_speed = reprod_speed # Implementação do reprod_speed

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
        # tree_den foi adicionado para guardar a densidade inicial da floresta.
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
