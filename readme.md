# 🎮 Algoritmo A* - Visualização com Tux

- Júlia Vieira Lopes Tavares
- Vinicius Marques Santos Silva

### Link de Visualização do Video
- https://youtu.be/sYYHnHJ5EXg

Este projeto implementa uma visualização interativa do algoritmo de busca A* (A-estrela) utilizando Python e Pygame. O personagem Tux navega por um mapa em busca do menor caminho até o objetivo, demonstrando o funcionamento do algoritmo em tempo real. 

##  Pré-requisitos

### Python
Certifique-se de ter o Python 3.7 ou superior instalado em seu sistema.


## Instalação e Execução

### 1. Clone ou baixe o projeto
```bash
git clone <url-do-repositorio>
cd a_estrela
```

### 2. Instale as dependências
```bash
pip install -r requirements.txt
```

### 3. Execute o programa
```bash
python main.py
```

## Como Funciona

### Mapa
O jogo utiliza um sistema de grid com diferentes tipos de células:
- **C**: Posição inicial do Tux (personagem)
- **S**: Destino final (saída)
- **B**: Barreiras intransponíveis (só podem ser atravessadas com a fruta mágica)
- **A**: Semi-barreiras (custo extra para atravessar)
- **F**: Fruta mágica (permite atravessar barreiras)
- **_**: Espaços vazios (livres para movimentação)

### Algoritmo A*
O algoritmo A* é uma técnica de busca heurística que encontra o caminho mais eficiente entre dois pontos. Ele utiliza:
- **Custo G**: Distância percorrida desde o início
- **Heurística H**: Estimativa da distância até o objetivo (distância de Manhattan)
- **Custo F**: Soma de G + H (custo total estimado)

### Visualização em Tempo Real
Durante a execução, você pode observar:
- **Azul**: Nó atual sendo processado
- **Verde**: Nós na lista aberta (candidatos a serem avaliados)
- **Vermelho**: Nós na lista fechada (já processados)
- **Amarelo**: Vizinhos sendo avaliados no momento
- **Valores G, H, F**: Custos calculados para cada posição

## Controles

- **R**: Reiniciar a simulação
- **ESC**: Sair do programa


## Personalização

### Modificando o Mapa
Edite o arquivo `mapa.py` para criar seus próprios mapas:

```python
def retorna_mapa_jogo():
    return [
        ["C", "_", "_", "_", "B", "_"],
        ["_", "B", "_", "_", "_", "_"],
        ["_", "_", "F", "_", "_", "_"],
        ["_", "_", "_", "B", "B", "_"],
        ["_", "_", "_", "A", "_", "_"],
        ["_", "_", "_", "_", "_", "S"],
    ]
```

### Ajustando Velocidade
No arquivo `game.py`, modifique as seguintes variáveis:
- `delay_passo_auto`: Velocidade da animação do movimento
- `delay_animacao`: Velocidade da animação dos sprites

## Conceitos Educacionais

Este projeto demonstra:
- **Algoritmos de busca**: Implementação prática do A*
- **Estruturas de dados**: Uso de heaps, listas e conjuntos
- **Programação orientada a objetos**: Classes bem estruturadas
- **Interface gráfica**: Desenvolvimento com Pygame
- **Visualização de algoritmos**: Representação visual de conceitos abstratos

##  Solução de Problemas

### Erro de módulo não encontrado
```bash
pip install pygame
```

### Problemas com áudio
Certifique-se de que os arquivos de som estão na pasta `elementos/sons_supertux/`

### Performance lenta
Ajuste a variável `delay_passo_auto` no arquivo `game.py` para um valor menor

