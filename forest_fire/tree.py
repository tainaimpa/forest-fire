import mesa
import random


class Tree(mesa.Agent):
    def __init__(self, unique_id, model, pos, tree_density, reprod_speed=1):
        super().__init__(unique_id, model)
        self.pos = pos
        self.status = "Fine"
        # Foi adicionado o argumento "tree_density", que é a densidade inicial da floresta.
        # Foi adicionado o argumento "reprod_speed", que é um parâmetro que controla a velocidade de reprodução das árvores.
        self.tree_density = tree_density
        self.reprod_speed = reprod_speed
    

    def can_grow(self, cord):
        # Essa função previne que o reflorestamento ultrapasse a densidade inicial.
        n1_number = 0
        n2_number = 0
        n1_tree = 0
        n2_tree = 0
        visited_cells = set()
        # É feita uma busca em largura para estimar a "densidade local".
        if cord.status == 'Burned':
            for neighbor1 in self.model.grid.iter_neighbors(cord.pos, True):
                if neighbor1 not in visited_cells:
                    visited_cells.add(neighbor1)
                    n1_number += 1
                    if neighbor1.status == 'Fine':
                        visited_cells.add(neighbor1)
                        n1_tree += 1
                for neighbor2 in self.model.grid.iter_neighbors(neighbor1.pos, True):
                    if neighbor2 not in visited_cells:
                        visited_cells.add(neighbor2)
                        n2_number += 1
                        if neighbor2.status == 'Fine':
                            n2_tree += 1
            # A escolha desse return se dá para tentar restringir as limitações de estarmos tratando com inteiros
            return (n1_tree < self.tree_density * n1_number) and (n2_tree < self.tree_density * n2_number) 
        return False


    def tree_reproduction(self):
        neighbors1_number = 0
        neighbors2_number = 0
        neighbors_tree_fine = 1 
        visited_cells = set()
        # Aqui a lógica é parecida com a da função anterior, são feitas duas bfs.
        # A primeira estima uma probabilidade de nascimento de uma nova árvore, e a segunda realiza o reflorestamento.
        if self.status == 'Fine':
            for neighbor1 in self.model.grid.iter_neighbors(self.pos, True):
                neighbors1_number += 1
                if neighbor1 not in visited_cells and neighbor1.status == 'Fine':
                    visited_cells.add(neighbor1)
                    neighbors_tree_fine += 1
                for neighbor2 in self.model.grid.iter_neighbors(neighbor1.pos, True):
                    neighbors2_number += 1
                    if neighbor2 not in visited_cells and neighbor2.status == 'Fine':
                        visited_cells.add(neighbor2)
                        neighbors_tree_fine += 1
            visited_cells = set()
            # Cálculo da velocidade de reflorestamento
            neighbors_number = neighbors1_number + neighbors2_number + 1 
            if (neighbors_tree_fine/neighbors_number) < self.tree_density:
                expected_trees = (neighbors_number *
                                  self.tree_density) - neighbors_tree_fine 
                n1_reproduction_rate = (
                    expected_trees/(neighbors1_number * neighbors_number))*self.reprod_speed
                n2_reproduction_rate = (
                    expected_trees/(neighbors2_number * neighbors_number))*self.reprod_speed
                # Reprodução das árvores
                for neighbor1 in self.model.grid.iter_neighbors(self.pos, True):
                    if neighbor1 not in visited_cells:
                        visited_cells.add(neighbor1)
                        if random.uniform(0, 1) < n1_reproduction_rate and self.can_grow(neighbor1):
                            neighbor1.status = 'Fine'
                    for neighbor2 in self.model.grid.iter_neighbors(neighbor1.pos, True):
                        if neighbor2 not in visited_cells:
                            visited_cells.add(neighbor2)
                            if random.uniform(0, 1) < n2_reproduction_rate and self.can_grow(neighbor2):
                                neighbor2.status = 'Fine'

    def step(self):
        if self.status == "Burning":
            for neighbor in self.model.grid.iter_neighbors(self.pos, True):
                if neighbor.status == "Fine":
                    neighbor.status = "Burning"
            self.status = "Burned"
        self.tree_reproduction()



'''
Recados do Tomaz e da Suelen:
    Implementamos um parâmetro chamado "reprod_speed" que controla a velocidade com que a floresta se reproduz
    e a interface visual para que o usuário o controle. Além disso, ajustamos os comentários para facilitar a leitura
    do código.
'''
