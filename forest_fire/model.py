import mesa
from typing import Literal
from forest_fire.cloud import Cloud
from forest_fire.tree import Tree, Terra
from forest_fire.biome import biomes

class ForestFire(mesa.Model):
    def __init__(
        self,
        biome_name: str, 
        width=100,
        height=100,
        tree_density=0,
        rainy_season=False,
        cloud_quantity=0,
    ):
        super().__init__()

        # Recupera o bioma escolhido
        self.biome = biomes[biome_name]
        self.width = width
        self.height = height
        self.tree_density = self.biome.density if tree_density == 0 else tree_density

        # Agendamento de eventos
        self.schedule = mesa.time.RandomActivation(self)
        
        # Cria o grid de árvores
        self.grid = mesa.space.MultiGrid(self.width, self.height, torus=False)
        
        self.rainy_season = rainy_season
        self.cloud_quantity = cloud_quantity

        # Inicializa o coletor de dados
        self.datacollector = mesa.DataCollector(
            model_reporters={
                "Fine": lambda model: self.count_type(model, "Fine", agent_type=Tree),
                "Burning": lambda model: self.count_type(model, "Burning", agent_type=Tree),
                "Burned": lambda model: self.count_type(model, "Burned", agent_type=Tree),
                "Terra": lambda model: self.count_type(model, agent_type=Terra),  # Conta o número de agentes do tipo Terra
                "Total": lambda model: self.count_type(model, agent_type=Tree),  # Conta o número total de árvores
                "Clouds": lambda model: self.count_type(model, agent_type=Cloud),
            }
        )   

        # Inicializa o grid com terra
        for contents, (x, y) in self.grid.coord_iter():
            terra_agent = Terra((x, y), self, self.biome.img_path)
            self.grid.place_agent(terra_agent, (x, y))

        self._initialize_trees()
        
        if rainy_season:
            self._initialize_clouds(cloud_quantity)   #TODO associar a biomas 

        # Coleta os dados iniciais
        self.datacollector.collect(self)

    def _initialize_trees(self):
        """
        Inicializa as árvores no grid com status e características de acordo com o bioma.
        Algumas árvores começam com o status "Burning".
        """
        for _contents, pos in self.grid.coord_iter():
            size = self.biome.size.sort_value()  # Tamanho da árvore conforme o bioma
            color = self.biome.color  # Cor do bioma para a árvore
            tree = Tree(self.next_id(), self, pos, size, color)

            # Determina se a árvore vai ser plantada com fogo ou não
            if self.random.random() < self.tree_density:
                self.schedule.add(tree)
                self.grid.place_agent(tree, pos)
                # Adiciona fogo em uma árvore na primeira linha ou posição aleatória
                if pos[0] == 0 and self.random.random() < 0.1:
                    tree.status = "Burning"
                else:
                    tree.status = "Fine"
            else:
                tree.status = "Burned"  # Algumas árvores começam como "Burned"

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
        """
        Realiza um passo no modelo, atualizando os status das árvores.
        A cada passo, verifica as interações da árvore com a terra.
        """
        self.schedule.step()  # Avança o passo do modelo
        self.datacollector.collect(self)  # Coleta dados após cada passo
        
        # Adiciona novas nuvens com tamanhos variados a cada 10 passos
        if self.rainy_season and self.schedule.steps % 10 == 0:
            self._initialize_clouds(5)  # Adiciona 5 novas nuvens a cada 10 passos
            

    def get_neighbors(self, pos, include_center=False):
        """
        Função que retorna os vizinhos de uma posição (posição do agente no grid).
        """
        return self.grid.get_neighbors(pos, include_center)
    
    @staticmethod
    def count_type(model, status=None, agent_type=None):
        """
        Conta o número de agentes de um determinado status ou tipo (se `status` ou `agent_type` forem fornecidos).
        """
        count = 0
        # Itera sobre todos os agentes no agendador
        for agent in model.schedule.agents:
            # Verifica se o tipo de agente corresponde ao tipo fornecido
            if isinstance(agent, agent_type):
                # Se o status não for fornecido, conta todos os agentes do tipo fornecido
                # Caso contrário, verifica se o status do agente corresponde.
                if (not status) or agent.status == status:
                    count += 1
        return count
