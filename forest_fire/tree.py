import mesa
import random

from forest_fire.obstacles import Lake, Corridor
from forest_fire.ground import Ground

class Tree(mesa.Agent):
    def __init__(self, unique_id, model, pos, tree_density, reprod_speed=1):
        super().__init__(unique_id, model)
        self.pos = pos
        self.status = "Fine"
        self.burnable = True
        self.tree_density = tree_density
        self.reprod_speed = reprod_speed
        
    def change_burned_tree_to_ground(self, burned_tree):
        pos = burned_tree.pos
        self.model.grid.remove_agent(burned_tree)
        self.model.schedule.remove(burned_tree)
        ground = Ground(self.model.next_id(), self.model, pos)
        self.model.grid.place_agent(ground, pos)
        self.model.schedule.add(ground)
    
    def grow_tree(self, growable_agent):
        pos = growable_agent.pos
        self.model.grid.remove_agent(growable_agent)
        self.model.schedule.remove(growable_agent)
        tree = Tree(self.model.next_id(), self.model, pos, self.model.tree_density, self.model.reprod_speed)
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
        if isinstance(cord, Ground) or (isinstance(cord, Tree) and cord.status == 'Burned'):
            n_first_level_neighbors, n_second_level_neighbors, n_first_level_trees, n_second_level_trees = self.bfs(cord.pos)
            # A escolha desse return se dá para tentar restringir as limitações de estarmos tratando com inteiros
            return (n_first_level_trees + n_second_level_trees < self.tree_density * (n_first_level_neighbors + n_second_level_neighbors))
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
        expected_trees = (neighbors_number *
                            self.tree_density) - n_trees
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
                        self.change_burned_tree_to_ground(neighbor2)
            if random.uniform(0, 1) < n1_reproduction_rate and self.can_grow(neighbor1):
                    self.grow_tree(neighbor1)                
            # Transforma todas as árvores vizinhas queimadas em ground
            elif isinstance(neighbor1, Tree) and neighbor1.status == 'Burned':
                self.change_burned_tree_to_ground(neighbor1)

    def step(self):
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
                    for neighbor_c in self.model.grid.iter_neighbors(neighbor.pos, moore=True):
                        if neighbor_c.status == "Fine" and neighbor_c.burnable:
                            neighbor_c.status = "Burning"
            self.status = "Burned"
            
        self.tree_reproduction()
