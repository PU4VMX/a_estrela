from game import JogoTux
from mapa import retorna_mapa_jogo

if __name__ == "__main__":
    mapa_jogo = retorna_mapa_jogo()
    game = JogoTux(mapa_jogo)
    game.executar()
