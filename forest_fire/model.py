import mesa
from typing import Literal
from forest_fire.tree import Tree, terra
from forest_fire.biome import biomes

class ForestFire(mesa.Model):
    def __init__(
        self,
        width = 70,
        height = 70,
        tree_density=0.65,
    ):
        super().__init__()

        # Recupera o bioma escolhido
        self.biome = biomes["Cerrado"]
        self.width = width
        self.height = height
        self.tree_density = tree_density

        # Agendamento de eventos
        self.schedule = mesa.time.RandomActivation(self)
        
        # Cria o grid de árvores
        self.grid = mesa.space.MultiGrid(self.width, self.height, torus=False)

        # Inicializa o coletor de dados
        self.datacollector = mesa.DataCollector(
            model_reporters={
                "Fine": lambda model: self.count_type(model, "Fine"),
                "Burning": lambda model: self.count_type(model, "Burning"),
                "Burned": lambda model: self.count_type(model, "Burned"),
            }
        )
        for contents, (x,y) in self.grid.coord_iter():
            n = terra( (x,y), self)
            self.grid.place_agent(n, (x,y))

        self._initialize_trees()

        # Coleta os dados iniciais
        self.datacollector.collect(self)

    def _initialize_trees(self):
        """
        Inicializa as árvores no grid com status e características de acordo com o bioma.
        """
        for _contents, pos in self.grid.coord_iter():
            size = self.biome.fauna_size.sort_value()  # Tamanho da árvore conforme o bioma
            color = self.biome.fauna_color  # Cor do bioma para a árvore
            tree = Tree(self.next_id(), self, pos, size, color)

            # Determina se a árvore vai ser plantada com fogo ou não
            if self.random.random() < self.tree_density:
                self.schedule.add(tree)
                self.grid.place_agent(tree, pos)
                if pos[0] == 0:  # Coloca fogo nas árvores da primeira linha
                    tree.status = "Burning"
                else:
                    tree.status = "Fine"
            else:
                tree.status = "Burned"  # Algumas árvores começam como "Burned"
            


    def step(self):
        """
        Realiza um passo no modelo, atualizando os status das árvores.
        """
        self.schedule.step()
        self.datacollector.collect(self)

    @staticmethod
    def count_type(model, status):
        """
        Conta o número de árvores de um determinado status (Fine, Burning, Burned).
        """
        count = 0
        for tree in model.schedule.agents:
            if tree.status == status:
                count += 1
        return count

