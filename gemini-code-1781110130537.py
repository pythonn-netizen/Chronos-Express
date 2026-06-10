import pygame
import random
import sys

# Inicialização do motor do jogo
pygame.init()

# Configurações da tela
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Chronos Express - Beta")
clock = pygame.time.Clock()

# Paleta de Cores (Estilo Neon/Cyberpunk simples)
BLACK = (20, 20, 20)
WHITE = (255, 255, 255)
CYAN = (0, 255, 255)    # Nosso Herói (Jogador)
YELLOW = (255, 255, 0)  # Bateria Temporal (Coletável)
GREEN = (0, 255, 0)     # Máquina do Tempo (Base de Entrega)
RED = (255, 50, 50)     # Cor do Desespero (Timer final)

# Fontes para a interface
font = pygame.font.SysFont("Arial", 24, bold=True)
large_font = pygame.font.SysFont("Arial", 48, bold=True)

# Variáveis globais do "Mundo"
LOOP_TIME = 30 # O mundo acaba em 30 segundos!
deliveries_made = 0
time_left = LOOP_TIME

class Player:
    def __init__(self):
        self.size = 30
        self.reset_pos()
        self.speed = 5.0 # Velocidade inicial
        self.has_item = False

    def reset_pos(self):
        # Volta pro centro do mapa quando o mundo reseta
        self.x, self.y = WIDTH // 2, HEIGHT // 2
        self.has_item = False

    def move(self, keys):
        # Suporta tanto Setas quanto WASD
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.x -= self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.x += self.speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.y -= self.speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.y += self.speed
        
        # Impede o jogador de sair da tela (Colisão com bordas)
        self.x = max(0, min(WIDTH - self.size, self.x))
        self.y = max(0, min(HEIGHT - self.size, self.y))

    def draw(self, surface):
        pygame.draw.rect(surface, CYAN, (self.x, self.y, self.size, self.size))

class Collectible:
    def __init__(self):
        self.size = 20
        self.spawn()

    def spawn(self):
        # Nasce em um lugar aleatório da tela
        self.x = random.randint(50, WIDTH - 50)
        self.y = random.randint(50, HEIGHT - 50)
        self.active = True

    def draw(self, surface):
        if self.active:
            pygame.draw.circle(surface, YELLOW, (self.x, self.y), self.size // 2)

class Base:
    def __init__(self):
        self.w, self.h = 80, 80
        self.x, self.y = 50, 50 # Fica fixa no canto superior esquerdo

    def draw(self, surface):
        pygame.draw.rect(surface, GREEN, (self.x, self.y, self.w, self.h), 3)

# Instanciando os objetos do jogo
player = Player()
item = Collectible()
base = Base()

# Controle de tempo real (Delta Time)
last_ticks = pygame.time.get_ticks()

# --- LOOP PRINCIPAL ---
running = True
while running:
    screen.fill(BLACK) # Limpa a tela frame a frame
    
    # 1. Checagem de Eventos (Fechar o jogo)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # 2. Lógica do Cronômetro do Fim do Mundo
    current_ticks = pygame.time.get_ticks()
    dt = (current_ticks - last_ticks) / 1000.0 # Converte milissegundos para segundos
    last_ticks = current_ticks
    time_left -= dt

    # 3. Movimentação
    keys = pygame.key.get_pressed()
    player.move(keys)

    # 4. Colisão Jogador -> Coletável
    if item.active and not player.has_item:
        # Lógica simples de aproximação
        if abs((player.x + player.size/2) - item.x) < 25 and abs((player.y + player.size/2) - item.y) < 25:
            item.active = False
            player.has_item = True

    # 5. Colisão Jogador -> Base de Entrega
    if player.has_item:
        # Checa se o centro do jogador está dentro do quadrado da base
        if (base.x < player.x < base.x + base.w) and (base.y < player.y < base.y + base.h):
            deliveries_made += 1
            player.has_item = False
            item.spawn()
            player.speed += 0.8 # UPGRADE! O jogador fica mais rápido a cada entrega

    # 6. O LOOP TEMPORAL (O tempo acabou!)
    if time_left <= 0:
        time_left = LOOP_TIME # Reseta o tempo
        player.reset_pos()    # Reseta o jogador
        item.spawn()          # Troca o item de lugar
        # Nota: Não resetamos player.speed nem deliveries_made!

    # 7. Renderização (Desenhar tudo na tela)
    base.draw(screen)
    item.draw(screen)
    player.draw(screen)

    # 8. Interface de Usuário (UI)
    # Muda a cor do timer para vermelho quando faltam 5 segundos ou menos
    timer_color = RED if time_left <= 5 else WHITE
    timer_text = large_font.render(f"{max(0, int(time_left))}s", True, timer_color)
    score_text = font.render(f"Entregas Salvas: {deliveries_made}", True, WHITE)
    
    # Aviso para o jogador saber o que fazer
    if player.has_item:
        status_text = font.render("BATERIA COLETADA! CORRA PARA A BASE VERDE!", True, YELLOW)
        screen.blit(status_text, (WIDTH//2 - status_text.get_width()//2, HEIGHT - 40))

    screen.blit(timer_text, (WIDTH - 100, 20))
    screen.blit(score_text, (WIDTH - 250, 80))

    # Atualiza a tela e define o FPS
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()