import mesa
import random

from forest_fire.obstacles import Lake, Corridor, Obstacle, Puddle
from forest_fire.ground import Terra

# Dicionário de cores para cada status da árvore
COLORS = {
    "Fine": "#00AA00",
    "Burning": "#FF0000",  # Cor para árvores queimando (vermelho)
    "Burned": "#3D2B1F",    # Cor para árvores queimadas (marrom escuro)
}
                
class Tree(mesa.Agent):
    """
    A árvore é um agente que pode ter diferentes estados, como 'Fine', 'Burning' ou 'Burned'.
    Ela também tem uma imagem que depende do seu tamanho.
    """
    def __init__(self, unique_id, model, pos, size: float, color: str, tree_density, img_path: str = None, reprod_speed=1):
        super().__init__(unique_id, model)
        self.pos = pos
        self.status = "Fine"  # Status inicial da árvore
        self.size = size
        self.color = color # Cor da árvore, geralmente vinda do bioma
        self.burnable = True
        self.img_path = img_path
        self.tree_density = tree_density
        self.reprod_speed = reprod_speed
        self.CO2_emission = 0
        self.CO2_sequestered = 0
        
    def remove_burned_tree(self, burned_tree):
        self.model.grid.remove_agent(burned_tree)
        self.model.schedule.remove(burned_tree)
    
    def grow_tree(self, growable_agent):
        pos = growable_agent.pos
        if isinstance(growable_agent, Tree):                
            growable_agent.CO2_sequestered += growable_agent.size * 0.1  #  Sequestra 0.1kg de CO2 por unidade de tamanho
        if not isinstance(growable_agent, Terra):
            self.model.grid.remove_agent(growable_agent)
            self.model.schedule.remove(growable_agent)
        size = self.model.biome.size.sort_value()
        color = self.model.biome.tree_color
        tree = Tree(self.model.next_id(), self.model, pos, size, color, self.model.tree_density, self.model.biome.img_path, self.model.reprod_speed)
        self.model.grid.place_agent(tree, pos)
        self.model.schedule.add(tree)
        self.model.num_fine_trees += 1
        
    def search_neighbours(self, pos):
        x, y = pos
        first_level_directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        second_level_directions = [(-2, 0), (2, 0), (0, -2), (0, 2), (-1, -1), (-1, 1), (1, -1), (1, 1)]
        
        n_first_level_neighbors = 0
        n_second_level_neighbors = 0
        n_first_level_trees = 0
        n_second_level_trees = 0
        
        for d1 in first_level_directions:
            dx, dy = d1
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.model.width and 0 <= ny < self.model.height:
                n_first_level_neighbors += 1
                cell_agents = self.model.grid.get_cell_list_contents([(nx, ny)])
                for agent in cell_agents:
                    if isinstance(agent, Tree) and agent.status == 'Fine':
                        n_first_level_trees += 1
                        break # Só existe uma árvore por célula
        
        for d2 in second_level_directions:
            dx, dy = d2
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.model.width and 0 <= ny < self.model.height:
                n_second_level_neighbors += 1
                cell_agents = self.model.grid.get_cell_list_contents([(nx, ny)])
                for agent in cell_agents:
                    if isinstance(agent, Tree) and agent.status == 'Fine':
                        n_second_level_trees += 1
                        break # Só existe uma árvore por célula
        
        return (n_first_level_neighbors, n_second_level_neighbors, n_first_level_trees, n_second_level_trees)
    
    def grow_neighbour_trees(self, pos, n1_reprod_rate, n2_reprod_rate):
        x, y = pos
        first_level_directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        second_level_directions = [(-2, 0), (2, 0), (0, -2), (0, 2), (-1, -1), (-1, 1), (1, -1), (1, 1)]
        
        for d1 in first_level_directions:
            dx, dy = d1
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.model.width and 0 <= ny < self.model.height:
                cell_agents = self.model.grid.get_cell_list_contents([(nx, ny)])
                for agent in cell_agents:
                    if random.uniform(0, 1) < n1_reprod_rate and self.can_grow(agent):
                        self.grow_tree(agent)                
                    # Transforma todas as árvores vizinhas queimadas em terra
                    elif isinstance(agent, Tree) and agent.status == 'Burned':
                        self.remove_burned_tree(agent)
        
        for d2 in second_level_directions:
            dx, dy = d2
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.model.width and 0 <= ny < self.model.height:
                cell_agents = self.model.grid.get_cell_list_contents([(nx, ny)])
                for agent in cell_agents:
                    if random.uniform(0, 1) < n2_reprod_rate and self.can_grow(agent):
                        self.grow_tree(agent)
                    # Transforma todas as árvores vizinhas queimadas em terra
                    elif isinstance(agent, Tree) and agent.status == 'Burned':
                        self.remove_burned_tree(agent)
                        

    def can_grow(self, cord):
        obstacles_in_cell = self.model.get_cell_items([cord.pos], [Obstacle, Corridor, Puddle, Lake, Tree])
        no_obstacles = len(obstacles_in_cell) == 0 # Se não tem obstáculo, então só tem terra que pode crescer
        if (isinstance(cord, Tree) and cord.status == 'Burned') or no_obstacles:
            n_first_level_neighbors, n_second_level_neighbors, n_first_level_trees, n_second_level_trees = self.search_neighbours(cord.pos)
            # A escolha desse return se dá para tentar restringir as limitações de estarmos tratando com inteiros
            return (n_first_level_trees < n_first_level_neighbors * self.tree_density) and (n_second_level_trees < n_second_level_neighbors * self.tree_density)
        return False

    def tree_reproduction(self):
        if self.status != 'Fine':
            return

        n_first_level_neighbors, n_second_level_neighbors, n_first_level_trees, n_second_level_trees = self.search_neighbours(self.pos)            
        n_trees = n_first_level_trees + n_second_level_trees

        # Cálculo da velocidade de reflorestamento
        neighbors_number = n_first_level_neighbors + n_second_level_neighbors + 1 
        if (n_trees) >= self.tree_density * neighbors_number:
            return
        expected_trees = (neighbors_number * self.tree_density) - n_trees
        n1_reproduction_rate = (
            expected_trees/(n_first_level_neighbors * neighbors_number))*self.reprod_speed
        n2_reproduction_rate = (
            expected_trees/(n_second_level_neighbors * neighbors_number))*self.reprod_speed

        self.grow_neighbour_trees(self.pos, n1_reproduction_rate, n2_reproduction_rate)

    def step(self):
        """
        A cada passo, a árvore pode pegar fogo e propagar o fogo para as árvores vizinhas.
        """
        if self.status == "Burning":
            for neighbor in self.model.grid.iter_neighbors(self.pos, moore=False):
                if isinstance(neighbor, Lake):
                    self.status = "Burned"
                    return
                
            for neighbor in self.model.grid.iter_neighbors(self.pos, moore=True):
                if neighbor.status == "Fine" and neighbor.burnable:
                    neighbor.status = "Burning"
                    self.model.num_fine_trees -= 1
                elif neighbor.status == "Corridor" and neighbor.burnable:
                    neighbor.status = "Burned"
                    for neighbor_c in self.model.grid.iter_neighbors(neighbor.pos, moore=True, radius=neighbor.radius):
                        if neighbor_c.status == "Fine" and neighbor_c.burnable:                          
                            neighbor_c.status = "Burning"
                            self.model.num_fine_trees -= 1
        
             # Cálculo de CO2 emitido na queima da árvore
            self.CO2_emission = self.size * 20 * 0.5 * 3.67 # Biomassa x 0.5 x 3.67
            self.status = "Burned"
           
            
        self.tree_reproduction()
    
    def get_image(self):
        """
        Retorna a imagem associada com base no tamanho da árvore.
        Acrescentar: imagem de acordo com o bioma.
        """
        if not self.img_path:
            return None
        
        if self.size <= 8:
            img_file = 'arvore1.png'  # Imagem para árvores bem pequenas
        elif self.size <= 15:
            img_file = 'arvore2.png'  # Imagem para árvores pequenas
        elif self.size <= 30:
            img_file = 'arvore3.png'  # Imagem para árvores média
        elif self.size <= 40:
            img_file = 'arvore4.png'  # Imagem para árvores grandes
        else:
            img_file = 'arvore5.png'  # Imagem para árvores bem grandes

        image= f"{self.img_path}/{img_file}"#self.model.biome.img_path

        # Adicione um print para depurar
        print(f"Image Path for Tree: {image}")  
        
        return image