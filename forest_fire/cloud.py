import mesa
from forest_fire.tree import Tree

class SmoothWalker(mesa.Agent):
    """
    Agente que se move suavemente em uma direção e pode mudar sua direção
    gradualmente após alguns passos.
    """

    def __init__(self, unique_id, pos, model, size=1.0, direction=(0, 0), change_rate=0.1):
        super().__init__(unique_id, model)
        self.pos = pos
        self.size = size
        self.direction = direction  
        self.change_rate = change_rate 

    def random_move(self):
        """Move o agente suavemente na direção atual."""
        x, y = self.pos
        dx, dy = self.direction
        new_pos = ((x + dx) % self.model.width, (y + dy) % self.model.height)
        self.model.grid.move_agent(self, new_pos)
        self.pos = new_pos

        if self.random.random() < self.change_rate:
            self.change_direction()

    def change_direction(self):
        """Muda a direção de movimento do agente suavemente."""
        new_dx = self.direction[0] + self.random.choice([-1, 0, 1])
        new_dy = self.direction[1] + self.random.choice([-1, 0, 1])
        self.direction = (max(-1, min(new_dx, 1)), max(-1, min(new_dy, 1)))

class Cloud(SmoothWalker):
    def __init__(self, unique_id, pos, model, size, color, direction, full=False, speed=.2, direction_change_rate=0.1):
        super().__init__(unique_id, pos, model, size=size, direction=direction, change_rate=0.1)
        self.color = color
        self.full = full  
        self.speed = speed  
        self.direction_change_rate = direction_change_rate  

    def step(self):
        """Move a nuvem e verifica se ela deve se unir com outras ou se precisa apagar o fogo."""
        
        if self.pos is not None:
            # Verifica se a nuvem está na borda do grid e a remove se necessário
            if self.pos[0] == 0 or self.pos[0] == self.model.width - 1 or self.pos[1] == 0 or self.pos[1] == self.model.height - 1:
                self.model.grid.remove_agent(self)
                self.model.schedule.remove(self)
                return 
            self.controlled_move()            
            self.rain()
            self.check_and_merge()

    def controlled_move(self):
        """
        Move a nuvem de forma controlada, ajustando sua direção gradualmente.
        """
        x, y = self.pos
        dx, dy = self.direction
        new_x = int((x + dx * self.speed) % self.model.width) 
        new_y = int((y + dy * self.speed) % self.model.height) 
        new_pos = (new_x, new_y)
        self.model.grid.move_agent(self, new_pos)
        self.pos = new_pos
        if self.random.random() < self.direction_change_rate:
            self.change_direction()

    def rain(self):
        """Simula a chuva """
        x, y = self.pos
        range_ = self.size + 3
        for dx in range(-range_, range_ + 1):
            for dy in range(-range_, range_ + 1):
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.model.width and 0 <= ny < self.model.height:
                    # Verifica se é uma árvore e se está queimando
                    tree = self.model.grid.get_cell_list_contents([(nx, ny)])
                    for t in tree:
                        if isinstance(t, Tree) and t.status == "Burning":
                            t.status = "Fine"  # Apaga o fogo
    
    def check_and_merge(self):
        """Verifica se há nuvens próximas e as funde em uma única nuvem maior."""
        if self.pos is not None:
            for neighbor in self.model.grid.get_neighbors(self.pos, moore=True):
                if type(neighbor) is Cloud:
                    self.size += neighbor.size
                    self.full = self.size >= size_to_rain 
                    self.model.grid.remove_agent(neighbor)  
                    self.model.schedule.remove(neighbor)    