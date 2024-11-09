import mesa
import random


class Tree(mesa.Agent):
    def __init__(self, unique_id, model, pos, tree_density):
        super().__init__(unique_id, model)
        self.pos = pos
        self.status = "Fine"
        # foi adicionado o argumento "tree_density, que é a densidade inicial da floresta"
        self.tree_density = tree_density
    

    def can_grow(self, cord):
        # essa função previne que o reflorestamento ultrapasse a densidade inicial
        n1_number = 0
        n2_number = 0
        n1_tree = 0
        n2_tree = 0
        visited_cells = set()
        # é feita uma busca em largura para estimar a "densidade local"
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
            # a escolha desse return se dá para tentar restringir as limitações de estarmos tratando com inteiros
            return (n1_tree < self.tree_density * n1_number) and (n2_tree < self.tree_density * n2_number)
        return False


    def tree_reproduction(self):
        neighbors1_number = 0
        neighbors2_number = 0
        neighbors_tree = 1
        visited_cells = set()
        # aqui a lógica é parecida, são feitas duas bfs
        # a primeira estima uma probabilidade de nascimento de uma nova árvora, e a segunda realiza o reflorestamento
        if self.status == 'Fine':
            for neighbor1 in self.model.grid.iter_neighbors(self.pos, True):
                neighbors1_number += 1
                if neighbor1 not in visited_cells and neighbor1.status == 'Fine':
                    visited_cells.add(neighbor1)
                    neighbors_tree += 1
                for neighbor2 in self.model.grid.iter_neighbors(neighbor1.pos, True):
                    neighbors2_number += 1
                    if neighbor2 not in visited_cells and neighbor2.status == 'Fine':
                        visited_cells.add(neighbor2)
                        neighbors_tree += 1
            visited_cells = set()
            # cálculo de probabilidade
            neighbors_number = neighbors1_number + neighbors2_number + 1
            if (neighbors_tree/neighbors_number) < self.tree_density:
                expected_trees = (neighbors_number *
                                  self.tree_density) - neighbors_tree
                n1_reproduction_rate = (
                    expected_trees/(2 * neighbors1_number * neighbors_number))
                n2_reproduction_rate = (
                    expected_trees/(2 * neighbors2_number * neighbors_number))
                # reprodução das árvores
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
a implementação de reflorestamento funciona, porém no processo de desenvolvimento 
do reflorestamento, provavelmente sobrepusermos alguns métodos para estimar a 
suscetibilidade do nascimento de árvores. Em breve isso será revisto e corrigido.
Além disso, as redundâncias como os for's monstuosos e os if's infinitos também
serão analisados com cuidado, para uma melhor compreensão do código.
'''
