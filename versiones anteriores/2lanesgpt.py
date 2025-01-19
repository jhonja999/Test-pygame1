import pygame
import random

# Inicializar Pygame
pygame.init()

# Configuración de pantalla
WIDTH, HEIGHT = 400, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Juego Expandido")
clock = pygame.time.Clock()

# Colores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)

# Clases principales
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((50, 30))
        self.image.fill(RED)
        self.rect = self.image.get_rect(center=(WIDTH // 2, HEIGHT - 50))
        self.speed = 5
        self.health = 3
        self.weapon_level = 1
        self.shoot_timer = 0  # Controla la cadencia de disparo

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] and self.rect.left > 0:  # Mover a la izquierda con A
            self.rect.x -= self.speed
        if keys[pygame.K_d] and self.rect.right < WIDTH:  # Mover a la derecha con D
            self.rect.x += self.speed

        # Disparos automáticos cada cierto tiempo
        if self.shoot_timer <= 0:
            for bullet in self.shoot():
                bullets.add(bullet)
                all_sprites.add(bullet)
            self.shoot_timer = 20  # Tiempo entre disparos
        else:
            self.shoot_timer -= 1

    def shoot(self):
        bullets = []
        if self.weapon_level == 1:
            bullets.append(Bullet(self.rect.centerx, self.rect.top))
        elif self.weapon_level == 2:
            bullets.append(Bullet(self.rect.centerx - 10, self.rect.top))
            bullets.append(Bullet(self.rect.centerx + 10, self.rect.top))
        elif self.weapon_level == 3:
            bullets.append(Bullet(self.rect.centerx - 15, self.rect.top))
            bullets.append(Bullet(self.rect.centerx, self.rect.top))
            bullets.append(Bullet(self.rect.centerx + 15, self.rect.top))
        return bullets
    
    def draw_health(self, surface):
        font = pygame.font.SysFont(None, 24)
        health_text = font.render(f"Vidas: {self.health}", True, WHITE)
        surface.blit(health_text, (10, HEIGHT - 30))

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((5, 10))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect(center=(x, y))

    def update(self):
        self.rect.y -= 5
        if self.rect.bottom < 0:
            self.kill()

class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((30, 30))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect(center=(random.randint(30, WIDTH - 30), 0))
        self.speed = random.randint(2, 4)
        self.health = random.randint(1, 3)  # Vidas del enemigo

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.kill()

    def draw_health(self, surface):
        font = pygame.font.SysFont(None, 20)
        health_text = font.render(f"{self.health}", True, RED)
        surface.blit(health_text, (self.rect.x, self.rect.y - 15))
        
class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((15, 15))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect(center=(x, y))

    def update(self):
        self.rect.y += 2
        if self.rect.top > HEIGHT:
            self.kill()

class Buff(pygame.sprite.Sprite):
    def __init__(self, x, y, buff_type):
        super().__init__()
        self.image = pygame.Surface((20, 20))
        if buff_type == "health":
            self.image.fill(RED)
        elif buff_type == "weapon":
            self.image.fill(BLUE)
        self.rect = self.image.get_rect(center=(x, y))
        self.buff_type = buff_type

    def update(self):
        self.rect.y += 2
        if self.rect.top > HEIGHT:
            self.kill()

# Inicializar grupos de sprites
player = Player()
bullets = pygame.sprite.Group()
enemies = pygame.sprite.Group()
coins = pygame.sprite.Group()
buffs = pygame.sprite.Group()
all_sprites = pygame.sprite.Group(player)

# Variables del juego
running = True
score = 0
coins_collected = 0
level = 1
spawn_timer = 30

# Funciones auxiliares
def spawn_enemy():
    enemy = Enemy()
    enemies.add(enemy)
    all_sprites.add(enemy)

def spawn_coin(x, y):
    coin = Coin(x, y)
    coins.add(coin)
    all_sprites.add(coin)

def spawn_buff(x, y):
    buff_type = random.choice(["health", "weapon"])
    buff = Buff(x, y, buff_type)
    buffs.add(buff)
    all_sprites.add(buff)

# Bucle principal
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Spawn de enemigos
    spawn_timer -= 1
    if spawn_timer <= 0:
        spawn_enemy()
        spawn_timer = max(20, 30 - level * 2)  # Enemigos más rápidos con el nivel

    # Actualizar sprites
    all_sprites.update()

    # Colisiones
    hits = pygame.sprite.groupcollide(enemies, bullets, False, True)
    for enemy, bullets_hit in hits.items():
        enemy.health -= len(bullets_hit)
        if enemy.health <= 0:
            enemy.kill()
            score += 10
            if random.random() < 0.5:  # Probabilidad de soltar moneda
                spawn_coin(enemy.rect.x, enemy.rect.y)
            elif random.random() < 0.3:  # Probabilidad de soltar buff
                spawn_buff(enemy.rect.x, enemy.rect.y)

    # Colisión entre jugador y monedas
    coin_hits = pygame.sprite.spritecollide(player, coins, True)
    coins_collected += len(coin_hits)

    # Colisión entre jugador y buffs
    buff_hits = pygame.sprite.spritecollide(player, buffs, True)
    for buff in buff_hits:
        if buff.buff_type == "health":
            player.health = min(player.health + 1, 3)  # Máximo de 3 vidas
        elif buff.buff_type == "weapon":
            player.weapon_level = min(player.weapon_level + 1, 3)  # Máximo nivel de arma

    # Colisión entre jugador y enemigos
    enemy_hits = pygame.sprite.spritecollide(player, enemies, True)
    if enemy_hits:
        player.health -= 1
        if player.health <= 0:
            running = False

    # Incrementar nivel
    if score // 100 > level:
        level += 1

    # Dibujar pantalla
    screen.fill(BLACK)
    all_sprites.draw(screen)

    # Mostrar puntuaciones y vidas
    font = pygame.font.SysFont(None, 36)
    text = font.render(f"Puntos: {score} Monedas: {coins_collected} Nivel: {level}", True, WHITE)
    screen.blit(text, (10, 10))
    player.draw_health(screen)
    for enemy in enemies:
        enemy.draw_health(screen)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
