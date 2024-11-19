from forest_fire.stats import Stats

default_size = Stats(15, 5) # Estatísticas do tamanho padrão para as árvores

class Biome():
    '''
    Representa um bioma.
    '''
    def __init__(self, code: str, density: float, humidity: float, temperature: float, 
                 size: Stats = default_size, tree_color: str = "#00AA00", ground_color = "#6B4423", img_path: str = None):
        '''
        Params:
            - density (float)
                Densidade das árvores no bioma.
            - humidity (float)
                Umidade absoluta do bioma em g/m³.
            - temperature (float)
                Temperatura média do bioma em Celsius.
            - size (Stats)
                Tamanho das árvores em metros.
            - tree_color (str)
                Cor das árvores em hexadecimal.
            - ground_color (str)
                Cor da terra em hexadecimal.
            - img_path (str)
                Caminho do diretório da imagem.
        '''
        self.code = code
        self.density = density
        self.humidity = humidity
        self.temperature = temperature
        self.size = size
        self.tree_color = tree_color # ajustar as cores
        self.ground_color = ground_color
        self.img_path = img_path
        

default   = Biome('default', 0.65, 15, 26,)
amazonia  = Biome('amazonia', 0.83, 25, 27, Stats(40, 10), tree_color="#009933", img_path='forest_fire/static/images/amazonia') 
atlantica = Biome('atlantica', 0.80, 20, 26, Stats(35,  5), tree_color="#00AA00", img_path='forest_fire/static/images/atlantica')
cerrado   = Biome('cerrado', 0.25, 10, 28, Stats(10,  5), tree_color="#67B921", img_path='forest_fire/static/images/cerrado')
caatinga  = Biome('caatinga', 0.08,  6, 39, Stats( 6,  2), tree_color="#cccc00", img_path='forest_fire/static/images/caatinga')  
pantanal  = Biome('pantanal', 0.50, 20, 28, Stats(20, 10), tree_color="#339966", img_path='forest_fire/static/images/pantanal')

biomes = {
    "Default" : default,
    "Amazônia": amazonia,
    "Cerrado" : cerrado,
    "Caatinga": caatinga,
    "Pantanal": pantanal,
    "Mata Atlântica" : atlantica
}