import pygame
import random
import math
from enum import Enum

# Initialize Pygame
pygame.init()

# Get the mobile screen size
display_info = pygame.display.Info()
WINDOW_WIDTH = display_info.current_w
WINDOW_HEIGHT = display_info.current_h
LANE_WIDTH = WINDOW_WIDTH // 3

# Scale factors based on screen size
SCALE_FACTOR = min(WINDOW_WIDTH / 800, WINDOW_HEIGHT / 600)
BASE_UNIT = int(40 * SCALE_FACTOR)  # Base unit for scaling elements
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (147, 0, 211)

class EnemyType(Enum):
    BASIC = 1
    ARMORED = 2
    BOSS = 3

class Bullet:
    def __init__(self, x, y, split=False):
        self.width = int(10 * SCALE_FACTOR)
        self.height = int(20 * SCALE_FACTOR)
        self.x = x
        self.y = y
        self.speed = int(10 * SCALE_FACTOR)
        self.split = split
        if split:
            self.width = int(8 * SCALE_FACTOR)
            self.height = int(16 * SCALE_FACTOR)
            
    def move(self):
        self.y -= self.speed
        
    def draw(self, screen):
        color = PURPLE if self.split else YELLOW
        pygame.draw.rect(screen, color, (self.x, self.y, self.width, self.height))

class Player:
    def __init__(self):
        self.width = BASE_UNIT
        self.height = BASE_UNIT
        self.x = WINDOW_WIDTH // 2
        self.y = WINDOW_HEIGHT - int(100 * SCALE_FACTOR)
        self.speed = int(5 * SCALE_FACTOR)
        self.health = 100
        self.max_health = 100
        self.damage = 1
        self.score = 0
        self.currency = 0
        self.bullets = []
        self.split_shot = False
        self.shoot_timer = 0
        self.shoot_delay = 20
        
    def shoot(self):
        if self.shoot_timer <= 0:
            if self.split_shot:
                # Create three split bullets
                self.bullets.append(Bullet(self.x, self.y, True))
                self.bullets.append(Bullet(self.x - int(20 * SCALE_FACTOR), self.y, True))
                self.bullets.append(Bullet(self.x + int(20 * SCALE_FACTOR), self.y, True))
            else:
                # Create single bullet
                self.bullets.append(Bullet(self.x + self.width//2 - int(5 * SCALE_FACTOR), self.y))
            self.shoot_timer = self.shoot_delay
            
    def update(self):
        self.shoot_timer -= 1
        # Update bullets
        for bullet in self.bullets[:]:
            bullet.move()
            if bullet.y < 0:
                self.bullets.remove(bullet)
                
    def move(self, keys, mouse_pos):
        # Touch/mouse movement
        target_x = mouse_pos[0] - self.width//2
        if abs(target_x - self.x) > self.speed:
            if target_x > self.x:
                self.x = min(self.x + self.speed, WINDOW_WIDTH - self.width)
            else:
                self.x = max(self.x - self.speed, 0)
                
        # Keyboard movement (optional)
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.x = max(self.x - self.speed, 0)
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.x = min(self.x + self.speed, WINDOW_WIDTH - self.width)
            
    def draw(self, screen):
        # Draw player
        pygame.draw.rect(screen, BLUE, (self.x, self.y, self.width, self.height))
        
        # Draw bullets
        for bullet in self.bullets:
            bullet.draw(screen)
            
        # Health bar
        bar_width = self.width
        bar_height = int(10 * SCALE_FACTOR)
        pygame.draw.rect(screen, RED, (self.x, self.y - bar_height - int(10 * SCALE_FACTOR), 
                                     bar_width, bar_height))
        pygame.draw.rect(screen, GREEN, (self.x, self.y - bar_height - int(10 * SCALE_FACTOR),
                                       bar_width * (self.health / self.max_health), bar_height))

class Enemy:
    def __init__(self, enemy_type):
        self.type = enemy_type
        base_size = int(30 * SCALE_FACTOR)
        self.width = base_size
        self.height = base_size
        self.x = random.randint(0, WINDOW_WIDTH - self.width)
        self.y = -self.height
        
        if self.type == EnemyType.BASIC:
            self.health = 1
            self.damage = 1
            self.speed = int(3 * SCALE_FACTOR)
            self.color = RED
        elif self.type == EnemyType.ARMORED:
            self.health = 3
            self.damage = 1
            self.speed = int(2 * SCALE_FACTOR)
            self.color = YELLOW
        else:  # BOSS
            self.health = 5
            self.damage = 2
            self.speed = int(1 * SCALE_FACTOR)
            self.width = int(50 * SCALE_FACTOR)
            self.height = int(50 * SCALE_FACTOR)
            self.color = WHITE
            
    def move(self):
        self.y += self.speed
        
    def draw(self, screen):
        if self.type == EnemyType.BASIC:
            pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        elif self.type == EnemyType.ARMORED:
            pygame.draw.polygon(screen, self.color, [
                (self.x, self.y + self.height),
                (self.x + self.width/2, self.y),
                (self.x + self.width, self.y + self.height)
            ])
        else:  # BOSS
            pygame.draw.circle(screen, self.color, 
                             (self.x + self.width//2, self.y + self.height//2), 
                             self.width//2)

class Shop:
    def __init__(self):
        self.upgrades = {
            "Health": 50,
            "Damage": 100,
            "Split Shot": 200
        }
        self.font = pygame.font.Font(None, int(36 * SCALE_FACTOR))
        
    def draw(self, screen, player):
        button_height = int(40 * SCALE_FACTOR)
        button_width = int(200 * SCALE_FACTOR)
        y_pos = int(10 * SCALE_FACTOR)
        
        for upgrade, cost in self.upgrades.items():
            # Draw button background
            button_rect = pygame.Rect(10, y_pos, button_width, button_height)
            pygame.draw.rect(screen, (100, 100, 100), button_rect)
            pygame.draw.rect(screen, WHITE, button_rect, 2)
            
            # Draw text
            text = f"{upgrade}: ${cost}"
            text_surface = self.font.render(text, True, WHITE)
            text_rect = text_surface.get_rect(center=button_rect.center)
            screen.blit(text_surface, text_rect)
            
            y_pos += button_height + int(10 * SCALE_FACTOR)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.FULLSCREEN)
        pygame.display.set_caption("Survival Game")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, int(36 * SCALE_FACTOR))
        
        self.player = Player()
        self.enemies = []
        self.shop = Shop()
        self.wave = 1
        self.wave_timer = 0
        self.spawn_rate = 60
        self.running = True
        self.shop_active = False
        self.high_score = self.load_high_score()
        
    def load_high_score(self):
        try:
            with open("highscore.txt", "r") as f:
                return int(f.read())
        except:
            return 0
            
    def save_high_score(self):
        with open("highscore.txt", "w") as f:
            f.write(str(max(self.high_score, self.player.score)))
            
    def spawn_enemy(self):
        if self.wave_timer <= 0:
            enemy_type = random.choices(
                [EnemyType.BASIC, EnemyType.ARMORED, EnemyType.BOSS],
                weights=[0.7, 0.2, 0.1]
            )[0]
            self.enemies.append(Enemy(enemy_type))
            self.wave_timer = max(20, self.spawn_rate - self.wave)
            
    def handle_collisions(self):
        # Check bullet collisions
        for bullet in self.player.bullets[:]:
            for enemy in self.enemies[:]:
                if (bullet.y < enemy.y + enemy.height and
                    bullet.y + bullet.height > enemy.y and
                    bullet.x < enemy.x + enemy.width and
                    bullet.x + bullet.width > enemy.x):
                    enemy.health -= self.player.damage
                    if enemy.health <= 0:
                        self.player.score += enemy.type.value * 10
                        self.player.currency += enemy.type.value
                        self.enemies.remove(enemy)
                    if bullet in self.player.bullets:
                        self.player.bullets.remove(bullet)
                    break
        
        # Check player collisions
        for enemy in self.enemies[:]:
            if (enemy.y + enemy.height > self.player.y and
                enemy.x < self.player.x + self.player.width and
                enemy.x + enemy.width > self.player.x):
                self.player.health -= enemy.damage
                self.enemies.remove(enemy)
                pygame.time.wait(100)
                continue
                
            if enemy.y > WINDOW_HEIGHT:
                self.enemies.remove(enemy)
                
    def handle_shop(self):
        if self.shop_active:
            mouse_pos = pygame.mouse.get_pos()
            mouse_click = pygame.mouse.get_pressed()[0]
            
            button_height = int(40 * SCALE_FACTOR)
            y_pos = int(10 * SCALE_FACTOR)
            button_width = int(200 * SCALE_FACTOR)
            
            for upgrade, cost in self.shop.upgrades.items():
                button_rect = pygame.Rect(10, y_pos, button_width, button_height)
                if (button_rect.collidepoint(mouse_pos) and
                    mouse_click and
                    self.player.currency >= cost):
                    
                    if upgrade == "Health":
                        self.player.health = min(self.player.health + 50, 
                                               self.player.max_health)
                    elif upgrade == "Damage":
                        self.player.damage += 1
                    elif upgrade == "Split Shot":
                        self.player.split_shot = True
                        
                    self.player.currency -= cost
                    pygame.time.wait(200)
                    
                y_pos += button_height + int(10 * SCALE_FACTOR)
                
    def run(self):
        while self.running:
            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p:
                        self.shop_active = not self.shop_active
                    elif event.key == pygame.K_ESCAPE:
                        self.running = False
                        
            if not self.shop_active:
                # Game logic
                keys = pygame.key.get_pressed()
                mouse_pos = pygame.mouse.get_pos()
                self.player.move(keys, mouse_pos)
                self.player.shoot()  # Automatic shooting
                self.player.update()
                
                self.wave_timer -= 1
                self.spawn_enemy()
                
                for enemy in self.enemies:
                    enemy.move()
                    
                self.handle_collisions()
                
                if self.player.score > self.wave * 100:
                    self.wave += 1
                    self.spawn_rate = max(20, self.spawn_rate - 5)
                    
                if self.player.health <= 0:
                    self.save_high_score()
                    self.running = False
            else:
                self.handle_shop()
                
            # Drawing
            self.screen.fill(BLACK)
            
            # Draw lanes
            for i in range(1, 3):
                pygame.draw.line(self.screen, WHITE, 
                               (i * LANE_WIDTH, 0), 
                               (i * LANE_WIDTH, WINDOW_HEIGHT))
                
            self.player.draw(self.screen)
            
            for enemy in self.enemies:
                enemy.draw(self.screen)
                
            # Draw HUD
            score_text = self.font.render(f"Score: {self.player.score}", True, WHITE)
            high_score_text = self.font.render(f"High: {self.high_score}", True, WHITE)
            wave_text = self.font.render(f"Wave: {self.wave}", True, WHITE)
            currency_text = self.font.render(f"${self.player.currency}", True, WHITE)
            
            # Position HUD elements with scaling
            padding = int(10 * SCALE_FACTOR)
            self.screen.blit(score_text, (padding, WINDOW_HEIGHT - int(40 * SCALE_FACTOR)))
            self.screen.blit(high_score_text, (int(200 * SCALE_FACTOR), WINDOW_HEIGHT - int(40 * SCALE_FACTOR)))
            self.screen.blit(wave_text, (WINDOW_WIDTH - int(150 * SCALE_FACTOR), WINDOW_HEIGHT - int(40 * SCALE_FACTOR)))
            self.screen.blit(currency_text, (WINDOW_WIDTH - int(150 * SCALE_FACTOR), padding))
            
            if self.shop_active:
                self.shop.draw(self.screen)
                
            pygame.display.flip()
            self.clock.tick(FPS)
            
        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()