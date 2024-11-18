import mesa
from forest_fire.tree import Tree

class Fireman(mesa.Agent):

    def __init__(self, unique_id, model, pos):
        super().__init__(unique_id, model)
        self.pos = pos

    def  put_out_fire(self, tree):
        """Apaga o fogo em uma árvore se estiver queimando."""
        if tree.status == "Burning":
            tree.status = "Extinguished"

    def step(self):

        """Apaga fogo na célula onde está o bombeiro e nas células vizinhas."""

        # Apaga o fogo na árvore da célula onde o bombeiro está
        current_cell = self.model.grid.get_cell_list_contents([self.pos])
        for agent in current_cell:
            if isinstance(agent, Tree) and agent.status == "Burning":
                self.put_out_fire(agent)  

        # Movimenta-se para uma árvore vizinha em chamas e apaga o fogo
        neighbors = self.model.grid.get_neighbors(self.pos, moore=True, include_center=False)
        burning_trees = [agent for agent in neighbors if isinstance(agent, Tree) and agent.status == "Burning"]

        if burning_trees:
            target_tree = burning_trees[0]
            self.model.grid.move_agent(self, target_tree.pos)
            self.put_out_fire(target_tree)
        else:
            pass