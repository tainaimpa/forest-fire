import mesa
from typing import Literal
from forest_fire.cloud import Cloud
from forest_fire.tree import Tree, Terra
from forest_fire.biome import biomes
from forest_fire.obstacles import Lake, Corridor, Obstacle
import random
import numpy as np
from scipy import ndimage

class ForestFire(mesa.Model):
    def __init__(
        self,
        biome_name: Literal["Default"], 
        width=100,
        height=100,
        rainy_season=False,
        imagens=False,
        cloud_quantity=0,
        tree_density=0.65,
        random_fire = True,
        position_fire = "Top",
        water_density=0.15,
        num_of_lakes=1,
        corridor_density=0.15,
        obstacles_density=0.15,
        obstacles=True,
        corridor=True,
        individual_lakes=True,
        reprod_speed=1, 
    ):
        super().__init__()

        # Recupera o bioma escolhido
        self.biome = biomes[biome_name]
        self.width = width
        self.height = height
        self.tree_density = tree_density
        self.random_fire = random_fire
        self.position_fire = position_fire 
        self.tree_density = self.biome.density if tree_density == 0 else tree_density
        self.rainy_season = rainy_season
        self.cloud_quantity = cloud_quantity
        self.reprod_speed = reprod_speed
        self.water_density = water_density
        self.num_of_lakes = num_of_lakes
        self.corridor_density = corridor_density
        self.corridor_radius = self.biome.corridor_radius
        self.obstacles_density = obstacles_density
        self.obstacles = obstacles
        self.corridor = corridor
        self.individual_lakes = individual_lakes
        
        self.schedule = mesa.time.RandomActivation(self)
        self.grid = mesa.space.MultiGrid(self.width, self.height, torus=False)
        
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
            color = self.biome.ground_color
            img_path = self.biome.img_path
            terra_agent = Terra((x, y), self, color, img_path)
            self.grid.place_agent(terra_agent, (x, y))

        self._initialize_trees()
        
        if rainy_season:
            self._initialize_clouds(cloud_quantity)   #TODO associar a biomas 

        # Coleta os dados iniciais
        self.datacollector.collect(self)

    def _initialize_trees(self):
        fire_list = [] 

        if self.random_fire:
            g = self.random.randint(1, 7)
            for _ in range(g):
                fire_list.append((self.random.randint(0, self.width-1),
                                self.random.randint(0, self.height-1)))
        else:
            if self.position_fire == "Left":
                fire_list = [(0, y) for y in range(self.height-1)]
            elif self.position_fire == "Right":
                fire_list = [(self.width - 1, y) for y in range(self.height-1)]
            elif self.position_fire == "Bottom":
                fire_list = [(x, 0) for x in range(self.width-1)]
            elif self.position_fire == "Top":
                fire_list = [(x, self.height - 1) for x in range(self.width-1)]
            elif self.position_fire == "Middle":
                fire_list = [(x, y) for x in range(self.width//2-5,self.width//2+5) for y in range(self.height//2-5, self.height//2+5)]

        for _ in range(self.num_of_lakes):
            self._initialize_lake_organic()

        for _contents, pos in self.grid.coord_iter():
            size = self.biome.size.sort_value() # Tamanho da árvore conforme o bioma
            color = self.biome.tree_color  # Cor do bioma para a árvore
            img_path = self.biome.img_path # Diretório das imagens do bioma
            
            if self.random.random() < self.tree_density:
                agent = Tree(self.next_id(), self, pos, size, color, self.tree_density, img_path, self.reprod_speed)
                if agent.pos in fire_list:   
                    agent.status = "Burning"
                
                lakes_in_cell = self.get_cell_items([pos], [Lake])
                if len(lakes_in_cell) == 0:
                    self.grid.place_agent(agent, pos)
                    self.schedule.add(agent)
                
            elif self.individual_lakes and random.random() < self.water_density**2:
                self._initialize_water(pos)
                
            else:
                self._initialize_other_agent(pos)
                    
    def _initialize_other_agent(self, pos):
        def get_types_and_weights():
            none_weight = max(1-self.corridor_density-self.obstacles_density, 0)
            types = ["None", "Corridor", "Obstacle"]
            weights_list = [none_weight, self.corridor_density, self.obstacles_density]
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
            case "Corridor":
                self._initialize_corridor(pos, self.corridor_radius)
            case "Obstacle":
                self._initialize_obstacle(pos)
            case "None":
                 pass
            
    def _initialize_water(self, pos):
        water = Lake(self.next_id(), self, pos)
        self.grid.place_agent(water, pos)
        self.schedule.add(water)
            
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
                self.grid.place_agent(lake, pos)           
                self.schedule.add(lake)

    def _initialize_obstacle(self, pos):
        obstacle = Obstacle(self.next_id(), self, pos)
        self.schedule.add(obstacle)
        self.grid.place_agent(obstacle, pos)
    
    def _initialize_corridor(self, pos, corridor_radius):
        corridor = Corridor(self.next_id(), self, pos, corridor_radius)
        if self.biome.humidity < 11:
            burning_probability = 0.01
            if random.random() < burning_probability:
                size = self.biome.size.sort_value() # Tamanho da árvore conforme o bioma
                color = self.biome.tree_color  # Cor do bioma para a árvore
                img_path = self.biome.img_path # Diretório das imagens do bioma
                corridor = Tree(self.next_id(), self, pos, size, color, self.tree_density, img_path, self.reprod_speed)
                corridor.status = "Burning"
        self.schedule.add(corridor)
        self.grid.place_agent(corridor, pos)

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
            
    def _probabilistic_fire(self):
        '''
        Inicia um foco de incêndio probabilisticamente
        '''
        pass
            
    def get_cell_items(self, positions: list, types: list):
        agents_in_cell = self.grid.get_cell_list_contents(positions)
              
        filtered_agents = []
        for agent in agents_in_cell:
            for tp in types:
                if isinstance(agent, tp):
                    filtered_agents.append(agent)
        return filtered_agents

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
            
        if self.biome.humidity < 11 and not self.corridor and self.schedule.steps % 5 == 0:
            self._probabilistic_fire()
            
    
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
