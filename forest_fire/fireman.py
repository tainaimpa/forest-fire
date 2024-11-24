import mesa
from forest_fire.tree import Tree, Terra

class Fireman(mesa.Agent):

    def __init__(self, unique_id, model, pos):
        super().__init__(unique_id, model)
        self.pos = pos
        self.burnable = False
        self.status = "Fireman"

    def  put_out_fire(self, tree):
        """Apaga o fogo em uma árvore se estiver queimando."""
        if tree.status == "Burning":
            tree.status = "Fine"

    def step(self):

        """
        Apaga fogo na célula onde está o bombeiro e, caso haja uma árvore no entorno pegando fogo, 
        se desloca para ela e apaga. Caso contrário, vai para uma árvore ou terra do entorno aleatória.
        """

        # Apaga o fogo na árvore da célula onde o bombeiro está
        current_cell = self.model.grid.get_cell_list_contents([self.pos])
        for agent in current_cell:
            if isinstance(agent, Tree) and agent.status == "Burning":
                self.put_out_fire(agent)  

        # Movimenta-se para uma árvore vizinha em chamas e apaga o fogo
        neighbors = self.model.grid.get_neighbors(self.pos, moore=True, include_center=False)
        burning_trees = [agent for agent in neighbors if isinstance(agent, Tree) and agent.status == "Burning"]

        if len(burning_trees) != 0:
            target_tree = burning_trees[0]
            self.model.grid.move_agent(self, target_tree.pos)
            self.pos = target_tree.pos
            self.put_out_fire(target_tree)
        else:
            # Caso não haja árvores em chamas, mover para uma célula com Terra ou Árvore
            neighbors2 = self.model.grid.get_neighborhood(self.pos, moore=True, include_center=False)
            valid_neighbors = [
                pos for pos in neighbors2
                if any(isinstance(agent, (Terra, Tree)) for agent in self.model.grid.get_cell_list_contents([pos]))
            ]

            if valid_neighbors:
                new_pos = self.random.choice(valid_neighbors)
                self.model.grid.move_agent(self, new_pos)