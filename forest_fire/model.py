import mesa

from forest_fire.tree import Tree


class ForestFire(mesa.Model):
    def __init__(
        self,
        width=100,
        height=100,
        tree_density=0.65,
        # Parâmetro "random_fire" define se o foco de incendio será aleatório ou não.
        random_fire=True,
        # Parâmetro "position_fire" permite ao usuário escolher onde começará o fogo: à esquerda, direita, cima, baixo ou meio.
        position_fire="left"
    ):
        super().__init__()
        self.width = width
        self.height = height
        self.tree_density = tree_density
        self.random_fire = random_fire
        self.position_fire = position_fire 
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
        # tree_den foi adicionado para guardar a densidade inicial da floresta
        tree_den = self.tree_density
        #é criada uma lista com os focos de incêndio
        fire_list = [] 
        # Se o usuário escolher por focos aleatórios:
        if self.random_fire:
        #é sorteado um valor para a quantidade de focos de incêndio iniciais
            g = self.random.randint(1, 5)
            for _ in range(g):
                #são sorteadas e adicionadas ao fire_list posições aleatórias
                fire_list.append((self.random.randint(0, self.width-1),
                                self.random.randint(0, self.height-1)))
        else: #se não for aleatório, o usuário poderá decidir a direção por onde começar o incêndio.
            if self.position_fire == "left":
                fire_list = [(0, y) for y in range(self.height-1)]
            elif self.position_fire == "right":
                fire_list = [(self.width - 1, y) for y in range(self.height-1)]
            elif self.position_fire == "top":
                fire_list = [(x, 0) for x in range(self.width-1)]
            elif self.position_fire == "bottom":
                fire_list = [(x, self.height - 1) for x in range(self.width-1)]
            elif self.position_fire == "middle":
                fire_list = [(x, y) for x in range(self.width//2-10,self.width//2+10) for y in range(self.height//2-10, self.height//2+10)]

        for _contents, pos in self.grid.coord_iter():
            tree = Tree(self.next_id(), self, pos, tree_den)
            if self.random.random() < self.tree_density:
                if tree.pos in fire_list:  # implementa os focos de incêndio
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
