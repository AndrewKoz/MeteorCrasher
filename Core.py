import pygame
import random
import os


class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((50, 40))
        self.image = pygame.transform.scale(player_img, (50, 40))
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.radius = 20
        # pygame.draw.circle(self.image, RED, self.rect.center, self.radius)
        self.rect.centerx = WIDTH // 2
        self.rect.bottom = HEIGHT - 10
        self.speedx = 0
        self.shield = 100
        self.shoot_delay = 250
        self.last_shoot = pygame.time.get_ticks()

    def update(self):
        self.speedx = 0
        keystate = pygame.key.get_pressed()
        if keystate[pygame.K_LEFT]:
            self.speedx = -8
        if keystate[pygame.K_RIGHT]:
            self.speedx = 8
        if keystate[pygame.K_SPACE]:
            self.shoot()
        self.rect.x += self.speedx
        # Ограничения на выход за пределы поля
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.left < 0:
            self.rect.left = 0

    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shoot > self.shoot_delay:
            self.last_shoot = now
            bullet = Bullet(self.rect.centerx, self.rect.top)
            all_sprites.add(bullet)
            bullets.add(bullet)
            choise = random.choice(result_shoot_sounds)
            pygame.mixer.Sound.set_volume(choise, 0.3)
            choise.play()


class Mob(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image_orig = random.choice(meteor_images_list)
        self.image_orig.set_colorkey(BLACK)
        self.image = self.image_orig.copy()
        self.rect = self.image.get_rect()
        self.radius = int(self.rect.width / 2)
        # pygame.draw.circle(self.image, RED, self.rect.center, self.radius)
        self.rect.x = random.randrange(WIDTH - self.rect.width)
        self.rect.y = random.randrange(-100, -40)
        self.speedy = random.randrange(1, 7)
        self.speedx = random.randrange(-2, 2)
        self.rot = 0
        self.rot_speed = random.randrange(-8, 8)
        self.last_update = pygame.time.get_ticks()

    def update(self):
        self.rect.y += self.speedy
        self.rect.x += self.speedx
        self.rotate()
        # Условия на вылет за пределы поля
        if self.rect.top > HEIGHT + 20:
            self.rect.x = random.randrange(WIDTH - self.rect.width)
            self.rect.y = random.randrange(-150, -100)
            self.speedy = random.randrange(1, 8)
            self.speedx = random.randrange(-3, 3)
        if self.rect.left > WIDTH or self.rect.right < 0:
            self.rect.x = random.randrange(WIDTH - self.rect.width)
            self.rect.y = random.randrange(-150, -100)
            self.speedy = random.randrange(1, 8)
            self.speedx = random.randrange(-3, 3)

    def rotate(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > 50:
            self.last_update = now
            self.rot = (self.rot + self.rot_speed) % 360
            new_image = pygame.transform.rotate(self.image_orig, self.rot)
            old_center = self.rect.center
            self.image = new_image
            self.rect = self.image.get_rect()
            self.rect.center = old_center


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(bullet_img, (10, 20))
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.bottom = y
        self.rect.centerx = x
        self.speedy = -10

    def update(self):
        self.rect.y += self.speedy
        if self.rect.bottom < 0:
            self.kill()


class Explosion(pygame.sprite.Sprite):
    def __init__(self, center, size):
        pygame.sprite.Sprite.__init__(self)
        self.size = size
        self.image = explosion_anim[self.size][0]
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.frame = 0
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 50

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame += 1
            if self.frame == len(explosion_anim[self.size]):
                self.kill()
            else:
                center = self.rect.center
                self.image = explosion_anim[self.size][self.frame]
                self.rect = self.image.get_rect()
                self.rect.center = center


def show_start_screen():
    screen.blit(background_img, background_rect)
    draw_text(screen, "Meteor Fighter!", 57, WIDTH // 2, HEIGHT // 4)
    draw_text(screen, "Arrow keys move, space to fire, Esc to quit", 20,
              WIDTH // 2, HEIGHT // 2)
    draw_text(screen, "Press a key to begin", 18, WIDTH // 2, HEIGHT * 3 // 4)
    pygame.display.flip()
    pygame.time.delay(300)
    waiting = True
    pygame.event.clear()
    while waiting:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.quit()
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.KEYUP:
                waiting = False
                start_sound.play()


def draw_text(surf, text, size, x, y):
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, WHITE)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surf.blit(text_surface, text_rect)


def draw_shield_bar(surf, x, y, pct):
    if pct < 0:
        pct = 0
    BAR_LENGTH = 100
    BAR_HEIGHT = 10
    fill = (pct / 100) * BAR_LENGTH
    outline_rect = pygame.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)
    fill_rect = pygame.Rect(x, y, fill, BAR_HEIGHT)
    pygame.draw.rect(surf, RED, fill_rect)
    pygame.draw.rect(surf, WHITE, outline_rect, 2)


def show_score_screen(score):
    screen.fill(BLACK)
    seconds_survived = score % 60
    minutes_survived = score // 60
    draw_text(screen, "You survived %d minutes and %d seconds" % (minutes_survived, seconds_survived), 26, 240, 300)
    draw_text(screen, "Press a key to return to start screen", 20, WIDTH // 2, HEIGHT * 3 // 4)
    pygame.display.flip()
    pygame.time.delay(1000)
    pygame.event.clear()
    waiting = True
    while waiting:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.quit()
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.KEYUP:
                waiting = False
    end_sound.play()
    pygame.time.delay(500)


def newmob():
    m = Mob()
    all_sprites.add(m)
    mobs.add(m)


# Цвета (R, G, B)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

# Константы
WIDTH = 480
HEIGHT = 600
FPS = 60

# Создание окна и тд
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Meteor Fighter!")
clock = pygame.time.Clock()
font_name = pygame.font.match_font('arial')

# Работа с файлами
game_folder = os.path.dirname(__file__)
img_folder = os.path.join(game_folder, 'img')
snd_folder = os.path.join(game_folder, 'sounds')
# Работа со звуком, загрузка аудиофайлов
pygame.mixer.music.load(os.path.join(snd_folder, 'SPEEDYSPACE8-bitloop.ogg'))
pygame.mixer.music.set_volume(0.6)
shoot_sounds = []
expl_sounds = []
normal_expl_sounds = []
normal_shoot_sounds = []
# Загрузка наборов звуков стрельбы и взрывов
# Нормальные звуки:
for snd in ['Explosion_sound_1.wav']:
    normal_expl_sounds.append(pygame.mixer.Sound(os.path.join(snd_folder, snd)))
for snd_2 in ['Laser_sound_1.ogg']:
    normal_shoot_sounds.append(pygame.mixer.Sound(os.path.join(snd_folder, snd_2)))
# Пшековые звуки
for snd in ['pshekel_1.ogg', 'pshekel_2.ogg', 'pshekel_3.ogg', 'pshekel_4.ogg']:
    expl_sounds.append(pygame.mixer.Sound(os.path.join(snd_folder, snd)))
for snd_2 in ['pshek_1.ogg', 'pshek_2.ogg', 'pshek_3.ogg', 'pshek_4.ogg', 'pshek_5.ogg']:
    shoot_sounds.append(pygame.mixer.Sound(os.path.join(snd_folder, snd_2)))
start_sound = pygame.mixer.Sound(os.path.join(snd_folder, 'kto_pshek_1.ogg'))
end_sound = pygame.mixer.Sound(os.path.join(snd_folder, 'pshik_1.ogg'))
# Здесь определяются итоговые звуки
result_expl_sounds = normal_expl_sounds
result_shoot_sounds = normal_shoot_sounds
result_start_sound = start_sound
result_end_sound = end_sound
pygame.mixer.Sound.set_volume(result_start_sound, 0.3)
pygame.mixer.Sound.set_volume(result_end_sound, 0.4)
# Изображения метеоров
meteor_images_list = []
meteor_images_names = ["meteorGrey_big1.png", "meteorGrey_big2.png", "meteorGrey_big3.png", "meteorGrey_big4.png",
                       "meteorGrey_med1.png", "meteorGrey_med2.png", "meteorGrey_small1.png", "meteorGrey_small2.png",
                       "meteorGrey_tiny1.png", "meteorGrey_tiny2.png"]
for img in meteor_images_names:
    meteor_images_list.append(pygame.image.load(os.path.join(img_folder, img)).convert())
# Изображение фона
background_img = pygame.image.load(os.path.join(img_folder, "darkPurple.png")).convert()
background_img = pygame.transform.scale(background_img, (WIDTH, HEIGHT))
background_rect = background_img.get_rect()
# Изображение игрока
player_img = pygame.image.load(os.path.join(img_folder, "playerShip3_blue.png")).convert()
# Изображение снаряда
bullet_img = pygame.image.load(os.path.join(img_folder, "laserRed16.png")).convert()
# Штуки со взрывами
explosion_anim = dict()
explosion_anim['large'] = []
explosion_anim['small'] = []
for i in range(9):
    filename = 'regularExplosion0{}.png'.format(i)
    img = pygame.image.load(os.path.join(img_folder, filename)).convert()
    img.set_colorkey(BLACK)
    img_large = pygame.transform.scale(img, (75, 75))
    explosion_anim['large'].append(img_large)
    img_small = pygame.transform.scale(img, (32, 32))
    explosion_anim['small'].append(img_small)

# Создание обьектов
all_sprites = pygame.sprite.Group()
# Игрок
player = Player()
all_sprites.add(player)
# Мобы
mobs = pygame.sprite.Group()
for i in range(8):
    newmob()
# Пули
bullets = pygame.sprite.Group()
# Счёт
score = 0
# Запускаем музыку
pygame.mixer.music.play(-1)

# Переменные состояния игры
game_over = False
runGame = True

show_start_screen()
# Цикл игры
start_sound.play()
time_tracker = 0
while runGame:
    if game_over:
        show_score_screen(score)
        show_start_screen()
        game_over = False
        all_sprites = pygame.sprite.Group()
        player = Player()
        all_sprites.add(player)
        mobs = pygame.sprite.Group()
        for i in range(8):
            newmob()
        bullets = pygame.sprite.Group()
        score = 0

    clock.tick(FPS)
    time_tracker += 1
    if time_tracker % 60 == 0:
        time_tracker = 0
        score += 1
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            pygame.quit()
        if event.type == pygame.QUIT:
            runGame = False
    # Обновление
    all_sprites.update()
    # Проверка, не ударил ли моб игрока
    hits = pygame.sprite.spritecollide(player, mobs, True, pygame.sprite.collide_circle)
    for hit in hits:
        expl = Explosion(hit.rect.center, 'small')
        choise = random.choice(result_expl_sounds)
        pygame.mixer.Sound.set_volume(choise, 0.3)
        choise.play()
        all_sprites.add(expl)
        player.shield -= hit.radius * 2
        if player.shield <= 0:
            game_over = True
        newmob()
    # Проверка, не попала ли пуля в моба
    hits_of_bullets = pygame.sprite.groupcollide(mobs, bullets, True, True)
    for hit in hits_of_bullets:
        expl = Explosion(hit.rect.center, 'large')
        choise = random.choice(result_expl_sounds)
        pygame.mixer.Sound.set_volume(choise, 0.3)
        choise.play()
        all_sprites.add(expl)
        newmob()
    # Рендеринг
    screen.fill(BLACK)
    screen.blit(background_img, background_rect)
    all_sprites.draw(screen)
    draw_text(screen, str(score), 18, WIDTH // 2, 10)
    draw_shield_bar(screen, 5, 5, player.shield)
    # Делаем флип
    pygame.display.flip()

pygame.quit()
