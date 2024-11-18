import random
from typing import Literal, Callable

class Stats():
    '''
    Lida com uma classe de números dada a relação de seus valores médios e desvio padrão.
    '''
    
    def __init__(self, mean_value: float, standart_deviation: float, type: Literal["int", "float", "hex"] = "float", sort_value: Callable = None):
        '''
        Params:
            - type ("int" | "float" | "hex")
                Tipo do valor
            - mean_value (float)
                Valor médio
            - standart_deviation (float)
                Desvio padrão
            - sort_value (Callable) (opcional)
                Função para sorteio de um valor
        '''
        self.mean_value = mean_value
        self.standart_deviation = standart_deviation
        self.type = type
        self.sort_value = sort_value if sort_value else self.default_sort_value
        
    def default_sort_value(self):
        '''
        Sorteia um número que respeite o valor médio e variância.
        
        Returns:
            - value (self.type): Valor sorteado
        '''
        value = random.normalvariate(self.mean_value, self.standart_deviation)
        if self.type == "float":
            return value
        if self.type == "int":
            return int(value)
        if self.type == "hex":
            # Converte para hexadecimal, limitando o valor para o máximo em hexadecimal,
            # removendo o prefixo "0x" e preenchendo com zeros à esquerda se necessário
            return "#"+hex(max(0, min(0xFFFFFFFF, int(value))))[2:].zfill(8).upper()