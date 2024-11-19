import mesa
import random 
from forest_fire.tree import Tree


class ForestFire(mesa.Model):
    def __init__(
        self,
        width=100,
        height=100,
        tree_density=0.65,
        wind_direction="N",  # Direção do vento: "none", "north", "south", "east", "west"
        wind_intensity=0.5  # Intensidade do vento: 0 (sem vento) a 1 (vento muito forte)
    ):
        super().__init__()
        self.width = width
        self.height = height
        self.tree_density = tree_density
        self.wind_direction = wind_direction
        self.wind_intensity = wind_intensity 
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
            tree = Tree(self.next_id(), self, pos)
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
        for agent in self.schedule.agents:
            if agent.status == "Burning":
                self.propagate_fire(agent)
        self.schedule.step()
        self.datacollector.collect(self)

    def propagate_fire(self, agent):
        for neighbor in agent.model.grid.iter_neighbors(agent.pos, True):
            if neighbor.status == "Fine":

                alpha = 70 + self.wind_intensity*25
                beta = 35 - self.wind_intensity*15

                dx = neighbor.pos[0] - agent.pos[0]
                dy = neighbor.pos[1] - agent.pos[1]

                if (dx, dy) == self._get_wind_vector():
                    if random.randint(0, 100) > beta:
                        neighbor.status = "Burning"
                else:
                    if random.randint(0, 100) > alpha:
                        neighbor.status = "Burning"

        agent.status = "Burned"

    def _get_wind_vector(self):
        """
        Retorna o vetor de direção do vento com base na configuração.
        """
        if self.wind_direction == "S":
            return (0, -1)  # Para cima
        if self.wind_direction == "N":
            return (0, 1)  # Para baixo
        if self.wind_direction == "E":
            return (1, 0)  # Para a direita
        if self.wind_direction == "W":
            return (-1, 0)  # Para a esquerda
        return (0, 0)

    @staticmethod
    def count_type(model, status):
        count = 0
        for tree in model.schedule.agents:
            if tree.status == status:
                count += 1
        return count
