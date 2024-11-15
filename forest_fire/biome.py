from forest_fire.stats import Stats

default_fauna_size = Stats(15, 5) # Estatísticas do tamanho padrão para as árvores

class Biome():
    '''
    Representa um bioma.
    '''
    def __init__(self, code: str, density: float, humidity: float, temperature: float, 
                 fauna_size: Stats = default_fauna_size, fauna_color: str = "#00AA00"):
        '''
        Params:
            - density (float)
                Densidade das árvores no bioma.
            - humidity (float)
                Umidade absoluta do bioma em g/m³.
            - temperature (float)
                Temperatura média do bioma em Celsius.
            - fauna_size (Stats)
                Tamanho da fauna em metros.
            - fauna_color (Stats)
                Cor da fauna em hexadecimal.
        '''
        self.code = code
        self.density = density
        self.humidity = humidity
        self.temperature = temperature
        self.fauna_size = fauna_size
        self.fauna_color = fauna_color 
        
cerrado = Biome('cerrado', 0.5, 10, 25, Stats(6, 2.5), "#67B921")
amazonia = Biome('amazonia', 0.9, 30, 27, Stats(8, 3), "#009933")  
caatinga = Biome('caatinga', 0.2, 3, 30, Stats(4, 2), "#cccc00")  
pantanal = Biome('pantanal', 0.3, 35, 28, Stats(7, 3), "#339966")

biomes = {
    "Cerrado": cerrado,
    "Amazônia": amazonia,
    "Caatinga": caatinga,
    "Pantanal": pantanal
}