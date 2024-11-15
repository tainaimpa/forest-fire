import mesa
from typing import Literal
from forest_fire.tree import Tree, Terra
from forest_fire.biome import biomes

class ForestFire(mesa.Model):
    def __init__(self, width=70, height=70, tree_density=0.65):
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
                "Fine": lambda model: self.count_type(model, "Fine", agent_type=Tree),
                "Burning": lambda model: self.count_type(model, "Burning", agent_type=Tree),
                "Burned": lambda model: self.count_type(model, "Burned", agent_type=Tree),
                "Terra": lambda model: self.count_type(model, agent_type=Terra),  # Conta o número de agentes do tipo Terra
                "Total": lambda model: self.count_type(model, agent_type=Tree)  # Conta o número total de árvores
            }
        )   

        # Inicializa o grid com terra
        for contents, (x, y) in self.grid.coord_iter():
            terra_agent = Terra((x, y), self)
            self.grid.place_agent(terra_agent, (x, y))

        self._initialize_trees()

        # Coleta os dados iniciais
        self.datacollector.collect(self)

    def count_type(self, model, status=None, agent_type=None):
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

    def _initialize_trees(self):
        """
        Inicializa as árvores no grid com status e características de acordo com o bioma.
        Algumas árvores começam com o status "Burning".
        """
        for _contents, pos in self.grid.coord_iter():
            # Determina se a árvore vai ser plantada ou não
            if self.random.random() > self.tree_density:
                continue
            
            size = self.biome.fauna_size.sort_value()  # Tamanho da árvore conforme o bioma
            color = self.biome.fauna_color  # Cor do bioma para a árvore
            img_path = f'forest_fire/images/{self.biome.code}' # Caminho para a imagem do bioma
            tree = Tree(self.next_id(), self, pos, size, color, img_path)

            self.schedule.add(tree)
            self.grid.place_agent(tree, pos)
            # Adiciona fogo em uma árvore na primeira linha ou posição aleatória
            # TODO: atualizar isso com a branch de Inícios de incêndio quando possível.
            if pos[0] == 0 and self.random.random() < 0.1:
                tree.status = "Burning"
            else:
                tree.status = "Fine"

    def step(self):
        """
        Realiza um passo no modelo, atualizando os status das árvores.
        A cada passo, verifica as interações da árvore com a terra.
        """
        self.schedule.step()  # Avança o passo do modelo
        self.datacollector.collect(self)  # Coleta dados após cada passo

    def get_neighbors(self, pos, include_center=False):
        """
        Função que retorna os vizinhos de uma posição (posição do agente no grid).
        """
        return self.grid.get_neighbors(pos, include_center)
