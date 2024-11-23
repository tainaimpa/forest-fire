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
        
    def remove_burned_tree(self, burned_tree):
        self.model.grid.remove_agent(burned_tree)
        self.model.schedule.remove(burned_tree)
    
    def grow_tree(self, growable_agent):
        pos = growable_agent.pos
        if not isinstance(growable_agent, Terra):
            self.model.grid.remove_agent(growable_agent)
            self.model.schedule.remove(growable_agent)
        size = self.model.biome.size.sort_value()
        color = self.model.biome.tree_color
        tree = Tree(self.model.next_id(), self.model, pos, size, color, self.model.tree_density, self.model.biome.img_path, self.model.reprod_speed)
        self.model.grid.place_agent(tree, pos)
        self.model.schedule.add(tree)
    
    def bfs(self,cord):
        n_first_level_neighbors = 0
        n_second_level_neighbors = 0
        n_first_level_trees = 0
        n_second_level_trees = 0
        visited_cells = set()
        
        for neighbor1 in self.model.grid.iter_neighbors(cord, True):
            if neighbor1 not in visited_cells:
                visited_cells.add(neighbor1)
                n_first_level_neighbors += 1
                if neighbor1.status == 'Fine':
                    visited_cells.add(neighbor1)
                    n_first_level_trees += 1
            for neighbor2 in self.model.grid.iter_neighbors(neighbor1.pos, True):
                if neighbor2 not in visited_cells:
                    visited_cells.add(neighbor2)
                    n_second_level_neighbors += 1
                    if neighbor2.status == 'Fine':
                        n_second_level_trees += 1
        return (n_first_level_neighbors, n_second_level_neighbors, n_first_level_trees, n_second_level_trees)

    def can_grow(self, cord):
        obstacles_in_cell = self.model.get_cell_items([cord.pos], [Obstacle, Corridor, Puddle, Lake, Tree])
        no_obstacles = len(obstacles_in_cell) == 0 # Se não tem obstáculo, então só tem terra que pode crescer
        if (isinstance(cord, Tree) and cord.status == 'Burned') or no_obstacles:
            n_first_level_neighbors, n_second_level_neighbors, n_first_level_trees, n_second_level_trees = self.bfs(cord.pos)
            # A escolha desse return se dá para tentar restringir as limitações de estarmos tratando com inteiros
            return ((n_first_level_trees + n_second_level_trees) < (self.tree_density * (n_first_level_neighbors + n_second_level_neighbors) * 0.9))
        return False

    def tree_reproduction(self):
        if self.status != 'Fine':
            return
        n_first_level_neighbors, n_second_level_neighbors, n_first_level_trees, n_second_level_trees = self.bfs(self.pos)            
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

        # Reprodução das árvores
        visited_cells = set()
        for neighbor1 in self.model.grid.iter_neighbors(self.pos, True):
            if neighbor1 not in visited_cells:
                visited_cells.add(neighbor1)
            for neighbor2 in self.model.grid.iter_neighbors(neighbor1.pos, True):
                if neighbor2 not in visited_cells:
                    visited_cells.add(neighbor2)
                    if random.uniform(0, 1) < n2_reproduction_rate and self.can_grow(neighbor2):
                        self.grow_tree(neighbor2)
                    # Transforma todas as árvores vizinhas queimadas em ground
                    elif isinstance(neighbor2, Tree) and neighbor2.status == 'Burned':
                        self.remove_burned_tree(neighbor2)
            if random.uniform(0, 1) < n1_reproduction_rate and self.can_grow(neighbor1):
                    self.grow_tree(neighbor1)                
            # Transforma todas as árvores vizinhas queimadas em ground
            elif isinstance(neighbor1, Tree) and neighbor1.status == 'Burned':
                self.remove_burned_tree(neighbor1)

    def step(self):
        """
        A cada passo, a árvore pode pegar fogo e propagar o fogo para as árvores vizinhas.
        """
        if self.status == "Burning":
            for neighbor in self.model.grid.iter_neighbors(self.pos, moore=True):
                if isinstance(neighbor, Lake):
                    self.status = "Burned"
                    return
                
            for neighbor in self.model.grid.iter_neighbors(self.pos, moore=True):
                if neighbor.status == "Fine" and neighbor.burnable:
                    neighbor.status = "Burning"
                elif neighbor.status == "Corridor" and neighbor.burnable:
                    neighbor.status = "Burned"
                    for neighbor_c in self.model.grid.iter_neighbors(neighbor.pos, moore=True, radius=neighbor.radius):
                        if neighbor_c.status == "Fine" and neighbor_c.burnable:                          
                            neighbor_c.status = "Burning"
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
