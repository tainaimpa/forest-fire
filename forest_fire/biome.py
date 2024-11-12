from forest_fire.stats import Stats

default_fauna_size = Stats(15, 5) # Estatísticas do tamanho padrão para as árvores

class Biome():
    '''
    Representa um bioma.
    '''
    def __init__(self, density: float, humidity: float, temperature: float, fauna_size: Stats = default_fauna_size, fauna_color: str = "#00AA00"):
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
        self.density = density
        self.humidity = humidity
        self.temperature = temperature
        self.fauna_size = fauna_size
        self.fauna_color = fauna_color # TODO: Implementar variação de cor

cerrado = Biome(0.5, 10, 25, Stats(6, 2.5), "#67B921")

biomes = {
    "Cerrado": cerrado
}