import pgzrun
import os
import random

from pgzhelper import *

WIDTH = 800
HEIGHT = 800

GRAVITY = 0.5
JUMP_HEIGHT = 10
WIN_SCORE = 100

def get_files_in_folder(folder_path):
    file_list = []
    for root, dirs, files in os.walk(f'images/{folder_path}'):
        for file in files:
            file_list.append(os.path.join(root.replace('images/',''), file.split('.')[0]))
    return file_list

player_idle_anim = get_files_in_folder('player_idle')
player_crouch_anim = get_files_in_folder('player_crouch')
player_jump_anim = get_files_in_folder('player_jump')
player_run_anim = get_files_in_folder('player_run')
player_shoot_anim = get_files_in_folder('player_shoot')
player_run_with_gun_anim = get_files_in_folder('player_run_with_gun')
player_jump_with_gun_anim = get_files_in_folder('player_jump_with_gun')
player_death_anim = get_files_in_folder('player_death')

IDLE_STATE = 'idle'
SHOOT_STATE = 'shoot'
MOVE_STATE = 'move'
MOVE_SHOOT_STATE = 'move_shoot'
JUMP_STATE = 'jump'
JUMP_SHOOT_STATE = 'jump_shoot'

player = Actor(player_idle_anim[0])
player.images = player_idle_anim
player.scale = 0.25
player.vy = 0
player.state = IDLE_STATE
player.ground = HEIGHT - player.height

bullets = []

score = 0


# just random picture, not going to draw it
cursor = Actor(player_idle_anim[0])

def on_mouse_move(pos):
    cursor.pos = pos

def player_change_state(state):
    if player.state != state:
        player.state = state


def player_idle():
    if player.images != player_idle_anim:
        player.images = player_idle_anim
        
def player_shoot():
    if player.images != player_shoot_anim:
        player.images = player_shoot_anim
    
    bullet = Actor('bullet/tile000.png')
    bullet.pos = player.pos
    bullet.angle = bullet.angle_to(cursor)
    bullets.append(bullet)
    
        
def player_move():
    if player.images != player_run_anim:
        player.images = player_run_anim


def player_move_shoot():
    curr_index = 0
    if player.images == player_run_anim:
        curr_index = player.images.index(player.image)
        
    if player.images != player_run_with_gun_anim:
        player.images = player_run_with_gun_anim
        player.image = player.images[curr_index]

    bullet = Actor('bullet/tile000.png')
    bullet.pos = player.pos
    bullet.angle = bullet.angle_to(cursor)
    bullets.append(bullet)


def player_jump():
    if player.images != player_jump_anim:
        player.images = player_jump_anim
        player.vy = -JUMP_HEIGHT

    
    player.vy += GRAVITY  
    player.y += player.vy  
    
    if player.y >= player.ground:
        player_change_state(IDLE_STATE)



def player_jump_shoot():
    curr_index = 0
    if player.images == player_jump_anim:
        curr_index = player.images.index(player.image)
        
    if player.images != player_jump_with_gun_anim:
        player.images = player_jump_with_gun_anim
        player.image = player.images[curr_index]
    
    
    bullet = Actor('bullet/tile000.png')
    bullet.pos = player.pos
    bullet.angle = bullet.angle_to(cursor)
    bullets.append(bullet)
    
    player.vy += GRAVITY  
    player.y += player.vy  
    
    if player.y >= player.ground:
        player_change_state(IDLE_STATE)


enemies = []

def spawn_enemy():
    enemy = Actor('ghost/tile000')
    enemy.scale = 2
    EDGES = ['top', 'bottom', 'left', 'right']
    edge = random.choice(EDGES)
    if edge == 'top':
        enemy.bottom = 0
        enemy.x = random.randint(0, WIDTH)
    elif edge == 'bottom':
        enemy.top = HEIGHT
        enemy.x = random.randint(0, WIDTH)
    elif edge == 'left':
        enemy.right = 0
        enemy.y = random.randint(0, HEIGHT)
    elif edge == 'right':
        enemy.left = WIDTH
        enemy.y = random.randint(0, HEIGHT)
    enemies.append(enemy)

def update_enemy():
    for enemy in enemies:
        enemy.angle = enemy.direction_to(player)
        if enemy.angle >= 90 and enemy.angle <= 270:
            enemy.angle -= 180
            enemy.flip_x = True
        else:
            enemy.flip_x = False
        enemy.move_towards(player, 1)
    
def player_update():
    if player.state == IDLE_STATE:
        player_idle()
    elif player.state == SHOOT_STATE:
        player_shoot()
    elif player.state == MOVE_STATE:
        player_move()
    elif player.state == MOVE_SHOOT_STATE:
        player_move_shoot()
    elif player.state == JUMP_STATE:
        player_jump()
    elif player.state == JUMP_SHOOT_STATE:
        player_jump_shoot()

def on_key_down(key):
    is_jumping = player.state == JUMP_STATE or player.state == JUMP_SHOOT_STATE
    
    if key == keys.SPACE and not is_jumping:
        player_change_state(JUMP_STATE)

def update_bullets():
    for bullet in bullets:
        bullet.move_forward(10)
        
        if bullet.x < 0 or bullet.x > WIDTH or bullet.y < 0 or bullet.y > HEIGHT:
            bullets.remove(bullet)
            continue

        for enemy in enemies:
            if bullet.collide_pixel(enemy):
                enemies.remove(enemy)
                bullets.remove(bullet)
                global score
                score += 1
                break

def check_win():
    if score >= WIN_SCORE:
        screen.draw.text('YOU WIN', (HEIGHT / 2, WIDTH / 2), fontsize = 60)
        return True

def update():
    player_update()
    player.animate()
    
    if len(enemies) < 20 and random.randint(0, 100) < 10:
        spawn_enemy()
    
    update_enemy()
    update_bullets()
    
    if keyboard.e:
        if player.state == JUMP_SHOOT_STATE:
            pass
        elif player.state == JUMP_STATE:
            player_change_state(JUMP_SHOOT_STATE)
        elif keyboard.a or keyboard.left or keyboard.d or keyboard.right:
            player_change_state(MOVE_SHOOT_STATE)
        else:
            player_change_state(SHOOT_STATE)
    elif keyboard.a or keyboard.left:
        if player.state != JUMP_STATE:
            player_change_state(MOVE_STATE)
        player.flip_x = True
        player.x -= 5
    elif keyboard.d or keyboard.right:
        if player.state != JUMP_STATE:
            player_change_state(MOVE_STATE)
        player.flip_x = False
        player.x += 5


    if player.y >= HEIGHT - player.height / 2:  
        player.y = HEIGHT - player.height / 2 
        player.vy = 0 


def draw():
    if check_win() != True:
        screen.clear()
        screen.draw.text(f'Score : {score}', (0, 0), fontsize=24)

        player.draw()
        for bullet in bullets:
            bullet.draw()

        for enemy in enemies:
            enemy.draw()

pgzrun.go()
