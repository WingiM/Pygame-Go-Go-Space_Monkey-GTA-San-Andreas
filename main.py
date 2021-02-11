import os
import random
import sys
import pygame

pygame.init()
size = width, height = 1200, 800
screen = pygame.display.set_mode(size)
pygame.display.set_caption('Go Go Space Monkey')

bonuses = ['Multiple Shot', 'Lower Cooldown', 'Auto Shot']
active_bonuses = bonuses.copy()
FPS = 120
coords = [(random.random() * width, random.random() * height) for i in range(1000)]
multiplier = 15
spawn_enemies = FPS
score = 0
with open('highscore.txt', mode='r') as f:
    try:
        high = int(f.readline())
    except ValueError:
        high = score - 1
speeds = [0, 0, 0, 0]
can_pick = False

clock = pygame.time.Clock()
all_sprites = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
projectile_group = pygame.sprite.Group()


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(*all_sprites)
        self.bonuses = dict.fromkeys(bonuses, 0)
        self.start_x, self.start_y = x, y
        self.hp = 3
        self.invulnerable = 0
        self.death_time = FPS * 2
        self.killed = 0
        self.invulnerability_duration = FPS * 5
        self.cooldown = 0
        self.cd_time = FPS
        self.cd_time_fixed = FPS
        self.speed = 600
        self.image = player_image
        self.rect = self.image.get_rect()
        self.rect.y = y
        self.rect.x = x

    def check(self):
        if self.rect.x <= 0:
            self.rect.x = 0
        elif self.rect.x + self.rect.w >= width:
            self.rect.x = width - self.rect.w

        if self.rect.y <= 0:
            self.rect.y = 0
        elif self.rect.y + self.rect.h >= height:
            self.rect.y = height - self.rect.h

    def attack(self):
        if not self.cooldown and not self.killed:
            if self.bonuses['Multiple Shot'] == 0:
                Projectile(self.rect.x + self.rect.w, self.rect.y + self.rect.h // 2, 'ally', vy=0)
            elif self.bonuses['Multiple Shot'] == 1:
                Projectile(self.rect.x + self.rect.w, self.rect.y + self.rect.h // 2, 'ally', vy=1)
                Projectile(self.rect.x + self.rect.w, self.rect.y + self.rect.h // 2, 'ally', vy=-1)
            else:
                Projectile(self.rect.x + self.rect.w, self.rect.y + self.rect.h // 2, 'ally', vy=1)
                Projectile(self.rect.x + self.rect.w, self.rect.y + self.rect.h // 2, 'ally', vy=-1)
                Projectile(self.rect.x + self.rect.w, self.rect.y + self.rect.h // 2, 'ally', vy=0)
            self.cooldown = self.cd_time

    def move(self, up, down, left, right, time):
        if not self.killed:
            self.rect.y += (down - up) * self.speed * time
            self.rect.x += (right - left) * self.speed * time
            self.check()

    def lower_cd(self):
        self.cd_time = max(10, self.cd_time // 2)
        if self.cd_time == 10:
            active_bonuses.remove('Lower Cooldown')

    def upgrade_shooting(self):
        self.bonuses['Multiple Shot'] += 1
        if self.bonuses['Multiple Shot'] == 2:
            active_bonuses.remove('Multiple Shot')

    def kill(self):
        global active_bonuses
        self.cd_time = self.cd_time_fixed
        self.bonuses = dict.fromkeys(bonuses, 0)
        active_bonuses = bonuses.copy()
        self.hp -= 1
        self.image = explosion
        self.killed = self.death_time

    def respawn(self):
        self.rect.x = self.start_x
        self.rect.y = self.start_y
        self.image = player_image

    def update(self):
        if self.cooldown:
            self.cooldown -= 1
        if self.invulnerable:
            self.invulnerable -= 1
        if self.killed:
            self.killed -= 1
            if not self.killed:
                self.respawn()
                self.invulnerable = self.invulnerability_duration


class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, vy=0):
        super().__init__(enemy_group, all_sprites)
        self.death_time = FPS // 2
        self.killed = 0
        self.vx = -200
        self.image = enemy_image
        self.rect = self.image.get_rect()
        self.x, self.y = x, y
        self.rect.x, self.rect.y = x, y
        self.vy = vy
        self.up = FPS

    def move(self, time):
        if not self.killed:
            self.x += self.vx * time
            self.y += self.vy * time

    def update(self):
        self.rect.x, self.rect.y = int(self.x), int(self.y)
        if self.up:
            self.up -= 1
            if not self.up:
                self.up = FPS
                self.vy = -self.vy
        if self.killed:
            self.killed -= 1
            if not self.killed:
                enemy_group.remove(self)
                all_sprites.remove(self)

    def kill(self):
        self.image = explosion
        self.killed = self.death_time


class Projectile(pygame.sprite.Sprite):
    def __init__(self, x, y, t, vy=0):
        super().__init__(projectile_group, all_sprites)
        self.x, self.y = x, y
        self.vy = vy
        self.type = t
        if self.type == 'ally':
            self.vx = 5
            self.image = shot
        else:
            self.vx = -5
            self.image = enemy_shot
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def update(self):
        self.rect = self.rect.move(self.vx, self.vy)


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


explosion = pygame.transform.scale(load_image('explosion.png'), (100, 50))
player_image = pygame.transform.scale(load_image('ufo.png'), (100, 50))
enemy_image = pygame.transform.scale(load_image('enemy.png'), (100, 50))
enemy_shot = pygame.transform.scale(load_image('enemy_shot.png'), (30, 10))
shot = pygame.transform.scale(load_image('shot.png'), (30, 10))
pygame.display.set_icon(load_image('monkey.png'))


def update_background():
    global coords
    coords = list(map(lambda x: (x[0] - 5 if x[0] > 0 else width - x[0], x[1]), coords))


def terminate():
    pygame.quit()
    sys.exit()


def start_screen():
    fon = pygame.transform.scale(load_image('start.png'), (width, height))
    screen.blit(fon, (5, 0))
    while True:
        for eve in pygame.event.get():
            if eve.type == pygame.QUIT:
                terminate()
            elif eve.type == pygame.KEYDOWN or \
                    eve.type == pygame.MOUSEBUTTONDOWN:
                return  # начинаем игру
        pygame.display.flip()
        clock.tick(FPS)


start_screen()
player = Player(0, 400)
all_sprites.add(player)
bonus_text = None
bonus_text_time = FPS
bonus_text_current_time = 0
bonus_name = None
while True:
    time_delta = clock.get_time() / 1000.0
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            terminate()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                player.attack()

    keys = pygame.key.get_pressed()

    w = keys[pygame.K_w]
    s = keys[pygame.K_s]
    a = keys[pygame.K_a]
    d = keys[pygame.K_d]
    if player.bonuses['Auto Shot'] and keys[pygame.K_SPACE]:
        player.attack()

    player.move(w, s, a, d, time_delta)

    if spawn_enemies:
        spawn_enemies -= 1
    else:
        enemy_vy = random.choice(speeds)
        enemy_x = 1200
        enemy_y = random.randint(enemy_vy + 100, height - (enemy_vy + 100))
        Projectile(enemy_x, enemy_y + 25, 'enemy')
        for i in range(5):
            Enemy(enemy_x, enemy_y, enemy_vy)
            enemy_x += 150
        if multiplier // 1.1 >= 3:
            multiplier //= 1.1
            speeds.append(random.choice([100, 200, 300]))
        else:
            multiplier = 3
        spawn_enemies = FPS * multiplier

    for enemy in enemy_group:
        can_pick = True
        enemy.move(time_delta)
        if enemy.rect.x <= -enemy.rect.w:
            all_sprites.remove(enemy)
            enemy_group.remove(enemy)
        elif col := pygame.sprite.spritecollideany(enemy, projectile_group):
            if col.type == 'ally' and not enemy.killed:
                score += 100
                if random.choice([0, 1, 0, 0]):
                    Projectile(enemy.rect.x, enemy.rect.y + enemy.rect.h // 2, 'enemy')
                enemy.kill()
                col.kill()

    for proj in projectile_group:
        if proj.rect.x > width:
            proj.kill()

    if collide := pygame.sprite.spritecollideany(player, projectile_group):
        if collide.type != 'ally' and not player.killed and not player.invulnerable:
            player.kill()

    player_collide_enemy = pygame.sprite.spritecollideany(player, enemy_group)
    if player_collide_enemy and not player.killed and not player.invulnerable and not player_collide_enemy.killed:
        player.kill()
        player_collide_enemy.kill()

    if not len(enemy_group) and can_pick and not player.killed:
        if active_bonuses:
            bonus = random.choice(active_bonuses)
            if bonus == 'Auto Shot':
                player.bonuses[bonus] += 1
                active_bonuses.remove('Auto Shot')
            elif bonus == 'Multiple Shot':
                player.upgrade_shooting()
            elif bonus == 'Lower Cooldown':
                player.lower_cd()
            can_pick = False
            bonus_text_current_time = bonus_text_time
            bonus_name = bonus

    screen.fill((0, 0, 0))

    score_font = pygame.font.Font(None, 50)
    score_text = score_font.render(f'SCORE: {score}', True, (255, 255, 255))
    hp_text = score_font.render(f'HP: {player.hp}', True, (255, 0, 0))
    high_text = score_font.render(f'HI-SCORE: {high}', True, (255, 255, 255))
    if bonus_text_current_time:
        bonus_text_current_time -= 1
        bonus_text = score_font.render(f'You gained: {bonus_name}', True, (255, 255, 255))
        screen.blit(bonus_text, (width // 2 - bonus_text.get_width() // 2, height // 2 - bonus_text.get_height() // 2))
    screen.blit(score_text, (0, 0))
    screen.blit(hp_text, (width // 2 - hp_text.get_width() // 2, 0))
    screen.blit(high_text, (width - high_text.get_width(), 0))

    for i in coords:
        screen.fill('white', (*i, 1, 1))
    if player.hp != 0:
        if player.invulnerable:
            pygame.draw.circle(screen, (66, 172, 173),
                               (player.rect.x + player.rect.w // 2, player.rect.y + player.rect.h // 2),
                               player.rect.w // 2)
        update_background()
        all_sprites.draw(screen)
        all_sprites.update()
    else:
        font = pygame.font.Font(None, width // 10)
        text = font.render('Game Over!', True, (255, 255, 255))
        screen.blit(text, (width // 2 - text.get_width() // 2, height // 2 - text.get_height() // 2))
        if high < score:
            with open('highscore.txt', mode='w') as f1:
                print(score, file=f1)
    clock.tick(FPS)
    pygame.display.flip()