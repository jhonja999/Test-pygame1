import pygame
import random
import math
from enum import Enum

# Initialize Pygame
pygame.init()

# Screen setup with auto-scaling
display_info = pygame.display.Info()
WIDTH = display_info.current_w
HEIGHT = display_info.current_h
SCALE_FACTOR = min(WIDTH/800, HEIGHT/600)
BASE_UNIT = int(40 * SCALE_FACTOR)
LANE_WIDTH = WIDTH // 3

# Game constants
FPS = 60
PIXEL_SIZE = max(2, int(4 * SCALE_FACTOR))  # Size for pixelated effects

# Colors (8-bit palette)
COLORS = {
    'black': (0, 0, 0),
    'white': (236, 236, 236),
    'red': (216, 40, 0),
    'green': (0, 228, 54),
    'blue': (0, 116, 236),
    'yellow': (236, 200, 0),
    'purple': (200, 0, 236),
    'cyan': (0, 236, 236),
}

class ParticleEffect:
    def __init__(self, x, y, color, particle_count=8):
        self.particles = []
        for _ in range(particle_count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 5)
            self.particles.append({
                'x': x,
                'y': y,
                'dx': math.cos(angle) * speed,
                'dy': math.sin(angle) * speed,
                'life': random.randint(10, 20),
                'color': color
            })

    def update(self):
        for particle in self.particles[:]:
            particle['x'] += particle['dx']
            particle['y'] += particle['dy']
            particle['life'] -= 1
            if particle['life'] <= 0:
                self.particles.remove(particle)

    def draw(self, screen):
        for particle in self.particles:
            x = int(particle['x'])
            y = int(particle['y'])
            pygame.draw.rect(screen, particle['color'], 
                           (x, y, PIXEL_SIZE, PIXEL_SIZE))

class PowerUpType(Enum):
    HEALTH = 1
    WEAPON = 2
    SHIELD = 3
    SPEED = 4

class PowerUp:
    def __init__(self, x, y, power_type):
        self.width = BASE_UNIT//2
        self.height = BASE_UNIT//2
        self.x = x
        self.y = y
        self.type = power_type
        self.speed = int(3 * SCALE_FACTOR)
        self.pulse = 0
        self.pulse_dir = 1
        # Definir el color basado en el tipo de powerup
        self.color = {
            PowerUpType.HEALTH: COLORS['red'],
            PowerUpType.WEAPON: COLORS['yellow'],
            PowerUpType.SHIELD: COLORS['cyan'],
            PowerUpType.SPEED: COLORS['green']
        }[power_type]

    def update(self):
        self.y += self.speed
        # Pulsing effect
        self.pulse += 0.1 * self.pulse_dir
        if abs(self.pulse) >= 1:
            self.pulse_dir *= -1

    def draw(self, screen):
        size_mod = int(4 * self.pulse)
        pygame.draw.rect(screen, self.color, 
                        (self.x - size_mod//2, 
                         self.y - size_mod//2,
                         self.width + size_mod, 
                         self.height + size_mod))
class Player:
    def __init__(self):
        self.width = BASE_UNIT
        self.height = BASE_UNIT
        self.x = WIDTH//2 - self.width//2
        self.y = HEIGHT - int(100 * SCALE_FACTOR)
        self.base_speed = int(6 * SCALE_FACTOR)
        self.speed = self.base_speed
        self.health = 100
        self.max_health = 100
        self.shield = 0
        self.max_shield = 50
        self.damage = 1
        self.score = 0
        self.currency = 0
        self.weapon_level = 1
        self.bullets = []
        self.shoot_timer = 0
        self.shoot_delay = 15
        self.effects = []
        self.invulnerable = 0
        self.speed_boost_timer = 0

    def update(self):
        # Update shooting cooldown
        if self.shoot_timer > 0:
            self.shoot_timer -= 1

        # Update speed boost
        if self.speed_boost_timer > 0:
            self.speed_boost_timer -= 1
            if self.speed_boost_timer <= 0:
                self.speed = self.base_speed

        # Update invulnerability
        if self.invulnerable > 0:
            self.invulnerable -= 1

        # Update effects
        for effect in self.effects[:]:
            effect.update()
            if not effect.particles:
                self.effects.remove(effect)

        # Update bullets
        for bullet in self.bullets[:]:
            bullet['y'] -= bullet['speed']
            if bullet['y'] < -10:
                self.bullets.remove(bullet)

    def shoot(self):
        if self.shoot_timer <= 0:
            bullet_patterns = {
                1: [(0, 0)],
                2: [(-10, 0), (10, 0)],
                3: [(-15, 0), (0, -5), (15, 0)],
                4: [(-20, 0), (-7, -3), (7, -3), (20, 0)],
                5: [(-20, 0), (-10, -3), (0, -5), (10, -3), (20, 0)]
            }
            
            pattern = bullet_patterns[min(self.weapon_level, 5)]
            for offset_x, offset_y in pattern:
                self.bullets.append({
                    'x': self.x + self.width//2 + offset_x,
                    'y': self.y + offset_y,
                    'width': int(4 * SCALE_FACTOR),
                    'height': int(8 * SCALE_FACTOR),
                    'speed': int(10 * SCALE_FACTOR),
                    'damage': self.damage
                })
            
            self.shoot_timer = self.shoot_delay

    def draw(self, screen):
        # Draw player ship (8-bit style)
        color = COLORS['white'] if self.invulnerable % 4 < 2 else COLORS['blue']
        
        # Ship body
        pygame.draw.rect(screen, color, 
                        (self.x, self.y, self.width, self.height))
        
        # Ship details
        detail_color = COLORS['cyan']
        pygame.draw.rect(screen, detail_color,
                        (self.x + self.width//4, 
                         self.y + self.height//4,
                         self.width//2, 
                         self.height//2))

        # Draw bullets
        for bullet in self.bullets:
            pygame.draw.rect(screen, COLORS['yellow'],
                           (bullet['x'], bullet['y'], 
                            bullet['width'], bullet['height']))

        # Draw effects
        for effect in self.effects:
            effect.draw(screen)

        # Draw health bar
        bar_width = self.width
        bar_height = int(6 * SCALE_FACTOR)
        pygame.draw.rect(screen, COLORS['red'],
                        (self.x, self.y - bar_height*2,
                         bar_width, bar_height))
        pygame.draw.rect(screen, COLORS['green'],
                        (self.x, self.y - bar_height*2,
                         bar_width * (self.health/self.max_health),
                         bar_height))

        # Draw shield bar if has shield
        if self.shield > 0:
            pygame.draw.rect(screen, COLORS['blue'],
                           (self.x, self.y - bar_height*3,
                            bar_width * (self.shield/self.max_shield),
                            bar_height))

class Enemy:
    TYPES = {
        'basic': {
            'health': 2,
            'speed': 2,
            'size': 1,
            'color': COLORS['red'],
            'points': 10,
            'shape': 'rect'
        },
        'fast': {
            'health': 1,
            'speed': 5,
            'size': 0.8,
            'color': COLORS['yellow'],
            'points': 15,
            'shape': 'triangle'
        },
        'tank': {
            'health': 5,
            'speed': 2,
            'size': 1.2,
            'color': COLORS['purple'],
            'points': 20,
            'shape': 'diamond'
        },
        'boss': {
            'health': 20,
            'speed': 1,
            'size': 2,
            'color': COLORS['cyan'],
            'points': 50,
            'shape': 'circle'
        }
    }

    def __init__(self, enemy_type):
        specs = self.TYPES[enemy_type]
        self.type = enemy_type
        base_size = int(30 * SCALE_FACTOR * specs['size'])
        self.width = base_size
        self.height = base_size
        self.x = random.randint(0, WIDTH - self.width)
        self.y = -self.height
        self.health = specs['health']
        self.max_health = specs['health']
        self.speed = int(specs['speed'] * SCALE_FACTOR)
        self.color = specs['color']
        self.points = specs['points']
        self.shape = specs['shape']
        self.movement_pattern = random.choice(['straight', 'sine', 'zigzag'])
        self.time = 0

    def update(self):
        self.time += 1
        if self.movement_pattern == 'straight':
            self.y += self.speed
        elif self.movement_pattern == 'sine':
            self.y += self.speed
            self.x += math.sin(self.time * 0.1) * 2
        elif self.movement_pattern == 'zigzag':
            self.y += self.speed
            self.x += math.cos(self.time * 0.1) * 3

    def draw(self, screen):
        if self.shape == 'rect':
            pygame.draw.rect(screen, self.color,
                           (self.x, self.y, self.width, self.height))
        elif self.shape == 'triangle':
            points = [
                (self.x + self.width//2, self.y),
                (self.x, self.y + self.height),
                (self.x + self.width, self.y + self.height)
            ]
            pygame.draw.polygon(screen, self.color, points)
        elif self.shape == 'diamond':
            points = [
                (self.x + self.width//2, self.y),
                (self.x + self.width, self.y + self.height//2),
                (self.x + self.width//2, self.y + self.height),
                (self.x, self.y + self.height//2)
            ]
            pygame.draw.polygon(screen, self.color, points)
        elif self.shape == 'circle':
            pygame.draw.circle(screen, self.color,
                             (self.x + self.width//2,
                              self.y + self.height//2),
                             self.width//2)

        # Health bar for bosses and tanks
        if self.type in ['boss', 'tank']:
            bar_width = self.width
            bar_height = int(4 * SCALE_FACTOR)
            pygame.draw.rect(screen, COLORS['red'],
                           (self.x, self.y - bar_height - 2,
                            bar_width, bar_height))
            pygame.draw.rect(screen, COLORS['green'],
                           (self.x, self.y - bar_height - 2,
                            bar_width * (self.health/self.max_health),
                            bar_height))

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Retro Space Shooter")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, int(36 * SCALE_FACTOR))
        
        self.background_stars = [
            {'x': random.randint(0, WIDTH),
             'y': random.randint(0, HEIGHT),
             'speed': random.uniform(0.5, 2)}
            for _ in range(50)
        ]
        
        self.reset_game()
        self.load_high_score()

    def reset_game(self):
        self.player = Player()
        self.enemies = []
        self.powerups = []
        self.effects = []
        self.wave = 1
        self.wave_timer = 0
        self.spawn_rate = 60
        self.running = True
        self.paused = False
        self.game_over = False
        self.score = 0

    def load_high_score(self):
        try:
            with open("highscore.txt", "r") as f:
                self.high_score = int(f.read())
        except:
            self.high_score = 0

    def save_high_score(self):
        with open("highscore.txt", "w") as f:
            f.write(str(max(self.high_score, self.score)))

    def spawn_enemy(self):
        if self.wave_timer <= 0:
            enemy_types = ['basic', 'fast', 'tank', 'boss']
            weights = [0.5, 0.3, 0.15, 0.05]
            
            # Adjust weights based on wave
            weights = [w * (1 + self.wave * 0.1) for w in weights]
            
            enemy_type = random.choices(enemy_types, weights=weights)[0]
            self.enemies.append(Enemy(enemy_type))
            self.wave_timer = max(20, self.spawn_rate - self.wave * 2)

    def spawn_powerup(self, x, y):
        if random.random() < 0.3:  # 30% chance to spawn powerup
            power_type = random.choice(list(PowerUpType))
            self.powerups.append(PowerUp(x, y, power_type))

    def handle_collisions(self):
        # Bullet-enemy collisions
        for enemy in self.enemies[:]:
            for bullet in self.player.bullets[:]:
                if (bullet['y'] < enemy.y + enemy.height and
                    bullet['y'] + bullet['height'] > enemy.y and
                    bullet['x'] < enemy.x + enemy.width and
                    bullet['x'] + bullet['width'] > enemy.x):
                    
                    enemy.health -= bullet['damage']
                    if bullet in self.player.bullets:
                        self.player.bullets.remove(bullet)
                    
                    # Spawn hit effect
                    self.effects.append(
                        ParticleEffect(
                            bullet['x'], 
                            bullet['y'], 
                            COLORS['yellow']
                        )
                    )
                    
                    if enemy.health <= 0:
                        self.score += enemy.points * self.wave
                        self.spawn_powerup(enemy.x, enemy.y)
                        self.effects.append(
                            ParticleEffect(
                                enemy.x + enemy.width//2,
                                enemy.y + enemy.height//2,
                                enemy.color,
                                particle_count=12
                            )
                        )
                        if enemy in self.enemies:
                            self.enemies.remove(enemy)
                    break

        # Player-enemy collisions
        if self.player.invulnerable <= 0:
            for enemy in self.enemies[:]:
                if (self.player.y < enemy.y + enemy.height and
                    self.player.y + self.player.height > enemy.y and
                    self.player.x < enemy.x + enemy.width and
                    self.player.x + self.player.width > enemy.x):
                    
                    # Handle shield first if available
                    if self.player.shield > 0:
                        self.player.shield = max(0, self.player.shield - 20)
                    else:
                        self.player.health -= 20
                    
                    self.effects.append(
                        ParticleEffect(
                            enemy.x + enemy.width//2,
                            enemy.y + enemy.height//2,
                            COLORS['red'],
                            particle_count=15
                        )
                    )
                    
                    self.player.invulnerable = 60  # 1 second of invulnerability
                    if enemy in self.enemies:
                        self.enemies.remove(enemy)

        # Player-powerup collisions
        for powerup in self.powerups[:]:
            if (self.player.y < powerup.y + powerup.height and
                self.player.y + self.player.height > powerup.y and
                self.player.x < powerup.x + powerup.width and
                self.player.x + self.player.width > powerup.x):
                
                if powerup.type == PowerUpType.HEALTH:
                    self.player.health = min(self.player.max_health,
                                           self.player.health + 30)
                elif powerup.type == PowerUpType.WEAPON:
                    self.player.weapon_level = min(5, self.player.weapon_level + 1)
                elif powerup.type == PowerUpType.SHIELD:
                    self.player.shield = min(self.player.max_shield,
                                           self.player.shield + 30)
                elif powerup.type == PowerUpType.SPEED:
                    self.player.speed = self.player.base_speed * 1.5
                    self.player.speed_boost_timer = 300  # 5 seconds
                
                self.effects.append(
                    ParticleEffect(
                        powerup.x + powerup.width//2,
                        powerup.y + powerup.height//2,
                        powerup.color,
                        particle_count=10
                    )
                )
                
                if powerup in self.powerups:
                    self.powerups.remove(powerup)

    def update_background(self):
        # Update star positions
        for star in self.background_stars:
            star['y'] += star['speed']
            if star['y'] > HEIGHT:
                star['y'] = 0
                star['x'] = random.randint(0, WIDTH)

    def draw_background(self):
        # Draw stars
        for star in self.background_stars:
            size = 2 if star['speed'] > 1 else 1
            pygame.draw.rect(self.screen, COLORS['white'],
                           (int(star['x']), int(star['y']), size, size))
        
        # Draw dividing lines for lanes
        for i in range(1, 3):
            x = i * LANE_WIDTH
            pygame.draw.line(self.screen, COLORS['blue'],
                           (x, 0), (x, HEIGHT), 1)

    def draw_hud(self):
        # Score
        score_text = self.font.render(f"Score: {self.score}", True, COLORS['white'])
        self.screen.blit(score_text, (10, 10))
        
        # High Score
        high_score_text = self.font.render(f"High: {self.high_score}", True, COLORS['white'])
        self.screen.blit(high_score_text, (10, 50))
        
        # Wave
        wave_text = self.font.render(f"Wave {self.wave}", True, COLORS['white'])
        wave_rect = wave_text.get_rect(midtop=(WIDTH//2, 10))
        self.screen.blit(wave_text, wave_rect)
        
        # Weapon Level
        weapon_text = self.font.render(f"Weapon Lvl: {self.player.weapon_level}", True, COLORS['yellow'])
        self.screen.blit(weapon_text, (WIDTH - 200, 10))
        
   

    def run(self):
        while self.running:
            current_time = pygame.time.get_ticks()
            
            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.paused = not self.paused
                    elif event.key == pygame.K_r and self.game_over:
                        self.reset_game()
                    
                    # Solo permitir salir cuando el juego está pausado
                    if event.key == pygame.K_q and self.paused:  # Tecla 'Q' para salir solo cuando está pausado
                        self.running = False  # Detiene el bucle del juego
                        
            # Si el juego está pausado o ha terminado, dibuja la pantalla correspondiente
            if self.paused or self.game_over:
                self.draw_pause_screen() if self.paused else self.draw_game_over_screen()
                pygame.display.flip()
                continue

            # Lógica del juego
            keys = pygame.key.get_pressed()
            mouse_pos = pygame.mouse.get_pos()
            
            # Movimiento del jugador
            if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                self.player.x = max(0, self.player.x - self.player.speed)
            if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                self.player.x = min(WIDTH - self.player.width,
                                    self.player.x + self.player.speed)
            
            # Movimiento alternativo con el mouse
            if pygame.mouse.get_pressed()[0]:  # Botón izquierdo del mouse
                target_x = mouse_pos[0] - self.player.width // 2
                if abs(target_x - self.player.x) > self.player.speed:
                    if target_x > self.player.x:
                        self.player.x = min(self.player.x + self.player.speed, WIDTH - self.player.width)
                    else:
                        self.player.x = max(self.player.x - self.player.speed, 0)
            
            # Disparo automático
            self.player.shoot()
            
            # Actualizar los elementos del juego
            self.player.update()
            self.update_background()
            
            for enemy in self.enemies:
                enemy.update()
            for powerup in self.powerups:
                powerup.update()
            for effect in self.effects[:]:
                effect.update()
                if not effect.particles:
                    self.effects.remove(effect)
            
            # Generar enemigos
            self.wave_timer -= 1
            self.spawn_enemy()
            
            # Manejar colisiones
            self.handle_collisions()
            
            # Comprobar progresión de olas
            if self.score >= self.wave * 1000:
                self.wave += 1
                self.spawn_rate = max(20, self.spawn_rate - 2)
            
            # Comprobar fin del juego
            if self.player.health <= 0:
                self.game_over = True
                self.save_high_score()
                continue
            
            # Dibujar
            self.screen.fill(COLORS['black'])
            self.draw_background()
            
            # Dibujar los elementos del juego
            self.player.draw(self.screen)
            for enemy in self.enemies:
                enemy.draw(self.screen)
            for powerup in self.powerups:
                powerup.draw(self.screen)
            for effect in self.effects:
                effect.draw(self.screen)
            
            self.draw_hud()
            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()

    def draw_pause_screen(self):
        s = pygame.Surface((WIDTH, HEIGHT))
        s.set_alpha(128)
        s.fill(COLORS['black'])
        self.screen.blit(s, (0, 0))
        
        pause_text = self.font.render("PAUSED", True, COLORS['white'])
        text_rect = pause_text.get_rect(center=(WIDTH//2, HEIGHT//2))
        self.screen.blit(pause_text, text_rect)
        
        continue_text = self.font.render("Press ESC to continue, o Q para salir", True, COLORS['white'])
        continue_rect = continue_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 50))
        self.screen.blit(continue_text, continue_rect)

    def draw_game_over_screen(self):
        s = pygame.Surface((WIDTH, HEIGHT))
        s.set_alpha(128)
        s.fill(COLORS['black'])
        self.screen.blit(s, (0, 0))
        
        game_over_text = self.font.render("GAME OVER", True, COLORS['red'])
        text_rect = game_over_text.get_rect(center=(WIDTH//2, HEIGHT//2 - 50))
        self.screen.blit(game_over_text, text_rect)
        
        score_text = self.font.render(f"Final Score: {self.score}", True, COLORS['white'])
        score_rect = score_text.get_rect(center=(WIDTH//2, HEIGHT//2))
        self.screen.blit(score_text, score_rect)
        
        if self.score > self.high_score:
            new_high_text = self.font.render("New High Score!", True, COLORS['yellow'])
            high_rect = new_high_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 50))
            self.screen.blit(new_high_text, high_rect)
        
        restart_text = self.font.render("Press R to restart", True, COLORS['white'])
        restart_rect = restart_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 100))
        self.screen.blit(restart_text, restart_rect)

if __name__ == "__main__":
    game = Game()
    game.run()