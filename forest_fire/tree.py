import mesa
import random


class Tree(mesa.Agent):
    def __init__(self, unique_id, model, pos, tree_density, reprod_speed=1, size=10):
        super().__init__(unique_id, model)
        self.pos = pos
        self.status = "Fine"
        self.tree_density = tree_density
        self.reprod_speed = reprod_speed
        self.size = size
        self.CO_emission = 0
        self.CO_sequestered = 0 
        
    def bfs(self,cord):
        number_of_first_level_neighbors = 0
        number_of_second_level_neighbors = 0
        number_of_first_level_trees = 0
        number_of_second_level_trees = 0
        visited_cells = set()
        for neighbor1 in self.model.grid.iter_neighbors(cord, True):
            if neighbor1 not in visited_cells:
                visited_cells.add(neighbor1)
                number_of_first_level_neighbors += 1
                if neighbor1.status == 'Fine':
                    visited_cells.add(neighbor1)
                    number_of_first_level_trees += 1
            for neighbor2 in self.model.grid.iter_neighbors(neighbor1.pos, True):
                if neighbor2 not in visited_cells:
                    visited_cells.add(neighbor2)
                    number_of_second_level_neighbors += 1
                    if neighbor2.status == 'Fine':
                        number_of_second_level_trees += 1
        return (number_of_first_level_neighbors, number_of_second_level_neighbors, number_of_first_level_trees, number_of_second_level_trees,visited_cells)

    def can_grow(self, cord):
        if cord.status != 'Burned':
            return False
        number_of_first_level_neighbors, number_of_second_level_neighbors, number_of_first_level_trees, number_of_second_level_trees,visited_cells = self.bfs(cord.pos)        
        # A escolha desse return se dá para tentar restringir as limitações de estarmos tratando com inteiros
        return (number_of_first_level_trees < self.tree_density * number_of_first_level_neighbors) and (number_of_second_level_trees < self.tree_density * number_of_second_level_neighbors) 


    def tree_reproduction(self):
        if self.status != 'Fine':
                return
        number_of_first_level_neighbors, number_of_second_level_neighbors, number_of_first_level_trees, number_of_second_level_trees,visited_cells = self.bfs(self.pos)            
        number_of_trees = number_of_first_level_trees + number_of_second_level_trees

        # Cálculo da velocidade de reflorestamento
        neighbors_number = number_of_first_level_neighbors + number_of_second_level_neighbors + 1 
        if (number_of_trees) >= self.tree_density * neighbors_number:
            return
        expected_trees = (neighbors_number *
                            self.tree_density) - number_of_trees 
        n1_reproduction_rate = (
            expected_trees/(number_of_first_level_neighbors * neighbors_number))*self.reprod_speed
        n2_reproduction_rate = (
            expected_trees/(number_of_second_level_neighbors * neighbors_number))*self.reprod_speed

        # Reprodução das árvores
        visited_cells = set()
        for neighbor1 in self.model.grid.iter_neighbors(self.pos, True):
            if neighbor1 not in visited_cells:
                visited_cells.add(neighbor1)
                if random.uniform(0, 1) < n1_reproduction_rate and self.can_grow(neighbor1):
                    neighbor1.status = 'Fine'
                    neighbor1.CO_sequestered += neighbor1.size * 2  # Sequestro incremental de CO2
                '''# Cada árvore viva sequestra 2kg de CO2 por unidade de tamanho'''
            for neighbor2 in self.model.grid.iter_neighbors(neighbor1.pos, True):
                if neighbor2 not in visited_cells:
                    visited_cells.add(neighbor2)
                    if random.uniform(0, 1) < n2_reproduction_rate and self.can_grow(neighbor2):
                        neighbor2.status = 'Fine'
                        neighbor2.CO_sequestered += neighbor2.size * 2 # Sequestro incremental de CO2

    def step(self):
        if self.status == "Burning":
            for neighbor in self.model.grid.iter_neighbors(self.pos, True):
                if neighbor.status == "Fine":
                    neighbor.status = "Burning"
            # Cálculo de CO2 emitido na queima da árvore
            self.CO_emission = self.size * 20 * 0.5 * 3.67 # Biomassa x 0.5 x 3.67
            self.status = "Burned"

        self.tree_reproduction()

