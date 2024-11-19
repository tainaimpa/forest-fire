from forest_fire.stats import Stats

default_size = Stats(15, 5) # Estatísticas do tamanho padrão para as árvores

class Biome():
    '''
    Representa um bioma.
    '''
    def __init__(self, density: float, humidity: float, temperature: float, CO2_emission_factor:float, size: Stats = default_size, color: str = "#00AA00"):
        '''
        Params:
            - density (float)
                Densidade das árvores no bioma.
            - humidity (float)
                Umidade absoluta do bioma em g/m³.
            - temperature (float)
                Temperatura média do bioma em Celsius.
            - size (Stats)
                Tamanho da fauna em metros.
            - color (Stats)
                Cor da fauna em hexadecimal.
        '''
        self.density = density
        self.humidity = humidity
        self.temperature = temperature
        self.CO2_emission_factor = CO2_emission_factor
        self.size = size
        self.color = color # ajustar as cores
        self.humidity_loss_per_tree = 0.108 * (self.temperature / 30) * (self.density / 0.5)

    def calculate_final_humidity(self, num_arvores_queimadas):
        """
        Calcula a umidade final do bioma após a queima de um número específico de árvores.
        :param num_arvores_queimadas: Número de árvores queimadas durante o incêndio.
        :return: A umidade final do bioma.
        """
        # Calcula a perda total de umidade
        total_lost = self.loss_per_tree() * num_arvores_queimadas
        # Calcula a umidade final do bioma após o incêndio
        final_humidity = self.humidity - total_lost

        # Evita que a umidade se torne negativa
        if final_humidity < 0:
            final_humidity = 0

        return final_humidity
        

default   = Biome(0.65, 15, 26, 1.0)
amazonia  = Biome(0.83, 25, 27, 1.5, Stats(40, 10), "#009933") 
atlantica = Biome(0.80, 20, 26, 1.3, Stats(35,  5), "#00AA00")
cerrado   = Biome(0.25, 10, 28, 0.8, Stats(10,  5), "#67B921")
caatinga  = Biome(0.08,  6, 39, 0.5, Stats( 6,  2), "#cccc00")  
pantanal  = Biome(0.50, 20, 28, 1.0, Stats(20, 10), "#339966")

biomes = {
    "Default" : default,
    "Amazônia": amazonia,
    "Cerrado" : cerrado,
    "Caatinga": caatinga,
    "Pantanal": pantanal,
    "Mata Atlântica" : atlantica
}