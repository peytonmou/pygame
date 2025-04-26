import pygame, sys, math, random
from random import randint

pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Find the Treasure!')

WHITE = (255,255,255)
BLACK = (0,0,0)
BLUE = (0,0,255)
RED = (255,0,0)
YELLOW = (255,255,0)
GREEN = (0,255,0)
PURPLE = (147,0,211)
GOLD = (255,215,0)

font = pygame.font.Font(None, 36)
large_font = pygame.font.Font(None, 84)
title_font = pygame.font.Font('freesansbold.ttf', 48)
background = pygame.image.load('forest.jpg')
background = pygame.transform.scale(background, (WIDTH, HEIGHT))

class GameProgress:
    def __init__(self):
        self.consecutive_wins = 0
        self.current_difficulty = 'easy'
        self.unlocked_levels = ['easy']   
    
    def add_win(self):
        self.consecutive_wins += 1
        if self.consecutive_wins >= 1:
            if self.current_difficulty == 'easy' and 'medium' not in self.unlocked_levels:
                self.unlocked_levels.append('medium')            
            elif self.current_difficulty == 'medium' and 'hard' not in self.unlocked_levels:
                self.unlocked_levels.append('hard')              
            elif self.current_difficulty == 'hard' and 'master' not in self.unlocked_levels:
                self.unlocked_levels.append('master')              
    
    def reset_streak(self):
        self.consecutive_wins = 0

class GameStats:
    def __init__(self):
        self.games_played = 0
        self.games_won = 0
        self.master_won = 0

    def add_game(self, won, is_master=False):
        self.games_played += 1
        if won:
            self.games_won += 1
            if is_master:
                self.master_won += 1

    def get_stats(self):
        return f'Games Played: {self.games_played} | Wins: {self.games_won}'

class Dragon:
    def __init__(self, x, y, dragon_id=None):
        self.image = pygame.image.load('dragon.png')
        self.image = pygame.transform.scale(self.image, (80,80))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y 
        self.x = x
        self.y = y 
        self.original_pos = (x,y)
        self.speed = 5
        self.fire_cooldown = 0
        self.fireballs = []  
        self.dragon_id = dragon_id 

    def update(self):
        # smoothly and gradually move up and down, 150 pixels distance
        self.rect.y = self.original_pos[1] + math.sin(pygame.time.get_ticks() * 0.002) * 150

        # 2% chance per second to shoot fireball
        if self.fire_cooldown > 0:
            self.fire_cooldown -= 1
        elif random.random() < 0.02:
            self.shoot_fireballs()        
        for fireball in self.fireballs[:]:
            # move the fireball
            fireball['x'] -= 5
            # remove when moving out of screen
            if fireball['x'] < 0:
                self.fireballs.remove(fireball)  

    def shoot_fireballs(self):
        fireball_start_x = self.rect.x + 10
        fireball_start_y = self.rect.y + self.rect.height // 2
        self.fireballs.append({'x': fireball_start_x, 'y': fireball_start_y})
        self.fire_cooldown = 60    # interval between shootings

    def draw(self, screen):
        screen.blit(self.image, (self.rect.x, self.rect.y))
        for fireball in self.fireballs:
            pygame.draw.circle(screen, RED, (int(fireball['x']), int(fireball['y'])), 10)
            pygame.draw.circle(screen, YELLOW, (int(fireball['x']), int(fireball['y'])), 4)

class Ghost:
    def __init__(self, x, y, speed):
        self.rect = pygame.Rect(x, y, 40, 40)
        self.original_pos = (x, y)
        self.speed = speed 
        self.direction = 1
        self.distance = 300
    
    def update(self):
        self.rect.x += self.speed * self.direction
        if abs(self.rect.x - self.original_pos[0]) > self.distance:
            self.direction *= -1
    
    def draw(self, screen):
        ghost_surface = pygame.Surface((40,40), pygame.SRCALPHA)
        pygame.draw.ellipse(ghost_surface, (200,200,255,180), (0,0,40,30))
        pygame.draw.rect(ghost_surface, (200,200,255,180), (0,15,40,15))
        pygame.draw.circle(ghost_surface, BLACK, (15,15),4)
        pygame.draw.circle(ghost_surface, BLACK, (25,15), 4)
        screen.blit(ghost_surface, self.rect) 

class Firework:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.color = self.random_bright_color()
        self.particles = []
        self.create_explosion()
        self.is_active = True 
        self.lifetime = 60
    
    def random_bright_color(self):
        return (randint(100,255), randint(100,255), randint(100,255))
    
    def create_explosion(self):
        num_particles = randint(200,300)
        for _ in range(num_particles):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(1, 5)
            dx = math.cos(angle) * speed
            dy = math.sin(angle) * speed 

            self.particles.append({
                'x': self.x,
                'y': self.y,
                'dx': dx,
                'dy': dy,
                'size': random.uniform(1,3),
                'alpha': 255,
                'decay_rate': random.uniform(0.5, 1)})
            
    def update(self):
        for particle in self.particles[:]:
            particle['x'] += particle['dx']
            particle['y'] += particle['dy']
            particle['dy'] += 0.1
            particle['alpha'] -= particle['decay_rate']

            if particle['alpha'] <= 0:
                self.particles.remove(particle) 
        self.lifetime -= 1 

        if not self.particles or self.lifetime <= 0:
            self.is_active = False 
    
    def draw(self, screen):
        for particle in self.particles:
            particle_surface = pygame.Surface((particle['size']*2, particle['size']*2), pygame.SRCALPHA)
            pygame.draw.circle(
                particle_surface,
                self.color + (int(particle['alpha']),),(int(particle['size']), int(particle['size'])),int(particle['size']))           
            screen.blit(particle_surface,(int(particle['x'] - particle['size']), int(particle['y'] - particle['size'])))

class DancingNumbers:
    def __init__(self, x, y):
        self.x = x
        self.y = y 
        self.numbers = [
            {'value': '2', 'x': x, 'y': y, 'phase': 0, 'scale': 1.0},
            {'value': '0', 'x': x+60, 'y': y, 'phase': 0.5, 'scale': 1.0},
            {'value': '2', 'x': x+120, 'y': y, 'phase': 1.0, 'scale': 1.0},
            {'value': '4', 'x': x+180, 'y': y, 'phase': 1.5, 'scale': 1.0}]
        self.five = {'value': '5', 'x': WIDTH+50, 'y': y, 'phase': 0, 'scale': 1.0}
        self.font = pygame.font.Font(None, 120)
        self.animation_speed = 0.1
        self.transition_started = False
        self.transition_speed = 0.01
        self.start_time = pygame.time.get_ticks()
        self.movement_speed = 6
    
    def update(self):
        current_time = pygame.time.get_ticks()
        elapsed_seconds = (current_time - self.start_time) / 1000

        if elapsed_seconds > 3 and not self.transition_started:
            self.transition_started = True 
        
        for num in self.numbers:
            num['phase'] += self.animation_speed
            num['y'] = self.y + math.sin(num['phase']) * 30
            num['scale'] = 1.0 + math.sin(num['phase'] * 0.5) * 0.2 
        
        if self.transition_started:
            if self.numbers[3]['x'] < WIDTH + 50:
                self.numbers[3]['x'] += self.movement_speed
            
            elif self.five['x'] > self.x + 180:
                self.five['x'] -= self.movement_speed
            
            else:
                self.five['phase'] += self.animation_speed
                self.five['y'] = self.y + math.sin(self.five['phase']) * 30
                self.five['scale'] = 1.0 + math.sin(self.five['phase'] * 0.5) * 0.2 
    
    def draw(self, screen):
        for num in self.numbers[:-1]:
            text = self.font.render(num['value'], True, GREEN)
            scaled_text = pygame.transform.scale(text, (int(text.get_width() * num['scale']), int(text.get_height() * num['scale']))) 
            screen.blit(scaled_text, (num['x'] - scaled_text.get_width()//2, num['y'] - scaled_text.get_height()//2))
        
        if self.numbers[3]['x'] < WIDTH + 50:
            text = self.font.render('4', True, GREEN)
            scaled_text = pygame.transform.scale(text, (int(text.get_width() * self.numbers[3]['scale']), int(text.get_height() * self.numbers[3]['scale'])))
            screen.blit(scaled_text, (self.numbers[3]['x'] - scaled_text.get_width()//2, self.numbers[3]['y'] - scaled_text.get_height()//2))
        
        if self.transition_started:
            text = self.font.render('5', True, GREEN)
            scaled_text = pygame.transform.scale(text, (int(text.get_width() * self.five['scale']),int(text.get_height() * self.five['scale'])))
            screen.blit(scaled_text, (self.five['x'] - scaled_text.get_width()//2, self.five['y'] - scaled_text.get_height()//2))
    
def get_difficulty_settings(difficulty):
    settings = {'easy':{'ghosts':1, 'traps':1, 'dragons':0, 'ghost_speed':2, 'velocity':5},
        'medium':{'ghosts':1, 'traps':1, 'dragons':1, 'ghost_speed':2, 'velocity':5},
        'hard':{'ghosts':2, 'traps':1, 'dragons':1, 'ghost_speed':3, 'velocity':5},
        'master':{'ghosts':2, 'traps':2, 'dragons':2, 'ghost_speed':3, 'velocity':5}}
    return settings[difficulty]

def initialize_game_state(difficulty='easy'):
    settings = get_difficulty_settings(difficulty)
    occupied_positions = []
    character_pos = (WIDTH//2, HEIGHT//2)
    occupied_positions.append(character_pos)

    def generate_valid_position():
        while True:
            pos = (random.randint(100, WIDTH-100), random.randint(100, HEIGHT-100))
            valid = all(math.dist(pos, existing_pos) >= 200 for existing_pos in occupied_positions)
            if valid:
                return pos

    trap_poss = [generate_valid_position() for _ in range(settings['traps'])]
    occupied_positions.extend(trap_poss)
    ghost_poss = [generate_valid_position() for _ in range(settings['ghosts'])]
    occupied_positions.extend(ghost_poss) 

    game_state = {
        'character': pygame.Rect(375, 275, 50, 50),
        'velocity': settings['velocity'],
        'movement_trace': [],
        'treasure_pos': random.choice([(700,500),(100,100),(700,100),(700,500)]),
        'traps': [pygame.Rect(x, y, 50, 50) for x, y in trap_poss],
        'ghosts': [Ghost(x, y, settings['ghost_speed']) for x, y in ghost_poss],
        'dragons': [Dragon(WIDTH - 100, HEIGHT//3, i) for i in range(settings['dragons'])],
        'current_story_index': 0,
        'game_over': False,
        'current_animation': None,
        'game_won': False,
        'master_level': False,
        'master_won': False,
        'difficulty': difficulty}
    return game_state 

def handle_gameplay(game_state):
    keys = pygame.key.get_pressed()
    if keys[pygame.K_UP]: game_state['character'].y -= game_state['velocity']
    if keys[pygame.K_DOWN]: game_state['character'].y += game_state['velocity']
    if keys[pygame.K_LEFT]: game_state['character'].x -= game_state['velocity']
    if keys[pygame.K_RIGHT]: game_state['character'].x += game_state['velocity']
    
    game_state['movement_trace'].append((game_state['character'].centerx, game_state['character'].centery))
    if len(game_state['movement_trace']) > 20:
        game_state['movement_trace'].pop(0) 
    
    for ghost in game_state['ghosts']:
        ghost.update()
        if game_state['character'].colliderect(ghost.rect):
            handle_game_over(game_state, False)
            return 
        
    for dragon in game_state['dragons']:
        dragon.update() 
        if game_state['character'].colliderect(dragon.rect):
            handle_game_over(game_state, False)
            return 
        for fireball in dragon.fireballs:
            fireball_rect = pygame.Rect(fireball['x']-4, fireball['y']-4, 8,8)
            if game_state['character'].colliderect(fireball_rect):
                handle_game_over(game_state, False)
                return 
    if game_state['character'].colliderect(pygame.Rect(*game_state['treasure_pos'], 40, 40)):
        handle_game_over(game_state, True)
        return 
    
    for trap in game_state['traps']:
        if game_state['character'].colliderect(trap):
            handle_game_over(game_state, False)
            return 

    # ensure character stay within screen
    game_state['character'].x = max(0, min(WIDTH - game_state['character'].width, game_state['character'].x))
    game_state['character'].y = max(0, min(HEIGHT - game_state['character'].height, game_state['character'].y))

def handle_game_over(game_state, won):
    game_state['game_over'] = True
    game_state['game_won'] = won
    game_state['current_story_index'] = 1 if won else 2
    game_state['master_level'] = game_state['difficulty'] == 'master'
    if game_state['master_level']:
        game_state['master_won'] = won 

def draw_button(surface, rect, text, text_surface, hover=False):
    border_color = GREEN if hover else WHITE
    pygame.draw.rect(surface, BLACK, rect)  # Button background
    pygame.draw.rect(surface, border_color, rect, 3, border_radius=10)  # Border with rounded corners
        
    if hover:
        highlight = pygame.Surface((rect.width-6, rect.height-6), pygame.SRCALPHA)
        pygame.draw.rect(highlight, (255, 255, 255, 30), highlight.get_rect(), border_radius=8)
        surface.blit(highlight, (rect.x+3, rect.y+3))
        
    text_pos = (rect.centerx - text_surface.get_width() // 2,
                   rect.centery - text_surface.get_height() // 2)
    surface.blit(text_surface, text_pos) 

def draw_difficulty_selection(progress):
    screen.fill(BLACK)
    title = font.render('Select Difficulty Level', True, WHITE)
    screen.blit(title, (WIDTH//2 - title.get_width()//2, 50))

    buttons = {}
    y_pos = 150
    mouse_pos = pygame.mouse.get_pos() 

    for difficulty in ['easy', 'medium', 'hard', 'master']:
        button = pygame.Rect(WIDTH//2-100, y_pos, 200, 50)

        if difficulty in progress.unlocked_levels:
            text_surface = font.render(difficulty.title(), True, WHITE)
            hover = button.collidepoint(mouse_pos)

            border_color = GREEN if hover else WHITE 
            pygame.draw.rect(screen, BLACK, button)
            pygame.draw.rect(screen, border_color, button, 3, border_radius=10)

            if hover:
                highlight = pygame.Surface((button.width-6, button.height-6), pygame.SRCALPHA)
                pygame.draw.rect(highlight, (255,255,255,30), highlight.get_rect(), border_radius=8)
                screen.blit(highlight, (button.x+3, button.y+3))
           
            text_pos = (button.centerx - text_surface.get_width()//2,
                        button.centery - text_surface.get_height()//2)
            screen.blit(text_surface, text_pos)
            buttons[difficulty] = button
        
        else:
            pygame.draw.rect(screen, (100,100,100), button)
            text_surface = font.render(difficulty.title(), True, (150,150,150))
            text_pos = (button.centerx - text_surface.get_width()//2,
                        button.centery - text_surface.get_height()//2)
            screen.blit(text_surface, text_pos)

        y_pos += 70
    
    pygame.display.flip()
    return buttons      

def draw_game_over_buttons():
    play_again_text = font.render("Play Again", True, WHITE)
    quit_text = font.render("Quit", True, WHITE)
    play_again_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 60, 200, 50)
    quit_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 120, 200, 50)

    mouse_pos = pygame.mouse.get_pos()
    draw_button(screen, play_again_button, 'Play Again', play_again_text, play_again_button.collidepoint(mouse_pos))
    draw_button(screen, quit_button, 'Quit', quit_text, quit_button.collidepoint(mouse_pos))
    pygame.display.flip()
    return play_again_button, quit_button             

def get_character_choice():
    texts = {
        'title': title_font.render('Find the Treasure!', True, GREEN),
        'question': font.render('Are you a lady or a gentleman?', True, WHITE),
        'lady': font.render('Lady', True, WHITE),
        'gentleman': font.render('Gentleman', True, WHITE),}
    
    buttons = {
        'lady': pygame.Rect(WIDTH//2 - 100, HEIGHT//2 - 40, 200, 50),
        'gentleman': pygame.Rect(WIDTH//2-100, HEIGHT//2 + 40, 200, 50),}

    while True:
        screen.fill(BLACK)    
        screen.blit(texts['title'], (WIDTH // 2 - texts['title'].get_width() // 2, 100))
        screen.blit(texts['question'], (WIDTH // 2 - texts['question'].get_width() // 2, 210))
        
        mouse_pos = pygame.mouse.get_pos()
        for role, button in buttons.items():
            draw_button(screen, button, role.capitalize(), texts[role], button.collidepoint(mouse_pos))
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()           
            if event.type == pygame.MOUSEBUTTONDOWN:
                for role, button in buttons.items():
                    if button.collidepoint(event.pos):
                        return role 

def main():
    character_type = get_character_choice() 
    character_image = pygame.image.load(f'{character_type}.png')
    character_image = pygame.transform.scale(character_image, (50, 50))  

    treasure_image = pygame.image.load('treasure.png')
    treasure_image = pygame.transform.scale(treasure_image, (50, 50))
    trap_image = pygame.image.load('trap.png')
    trap_image = pygame.transform.scale(trap_image, (50, 50))
    dragon_image = pygame.image.load('dragon.png')
    dragon_image = pygame.transform.scale(dragon_image, (80,80))
    story_texts = ["", "Victory!", "Game Over"]
    dancing_numbers = DancingNumbers(WIDTH//2 - 80, HEIGHT//2 - 170)
    
    game_stats = GameStats()
    game_progress = GameProgress()
    clock = pygame.time.Clock()
    running = True
    fireworks = [] 
    
    while running:
        buttons = draw_difficulty_selection(game_progress)
        difficulty_selected = False

        while not difficulty_selected and running:
            buttons = draw_difficulty_selection(game_progress)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    break 

                if event.type == pygame.MOUSEBUTTONDOWN:
                    for diff, button in buttons.items():
                        if button.collidepoint(event.pos):
                            game_progress.current_difficulty = diff
                            difficulty_selected = True 
                            break 
        if not running:
            break 

        game_state = initialize_game_state(game_progress.current_difficulty)

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False 
                    break 

                if game_state['game_over'] and event.type == pygame.MOUSEBUTTONDOWN:
                    play_again_button, quit_button = draw_game_over_buttons()
                    if play_again_button.collidepoint(event.pos):
                        if game_state['game_won']:
                            game_progress.add_win()                           
                        else:
                            game_progress.reset_streak()
                        game_stats.add_game(game_state['game_won'], is_master=game_state['master_won'])
                        break 

                    elif quit_button.collidepoint(event.pos):
                        running = False
                        break 

            if not running or (game_state['game_over'] and event.type==pygame.MOUSEBUTTONDOWN):
                break 

            if not game_state['game_over']:
                handle_gameplay(game_state)
            screen.blit(background, (0,0))

            if game_state['movement_trace']:
                for i in range(len(game_state['movement_trace']) - 1):
                    pygame.draw.aaline(screen, WHITE, game_state['movement_trace'][i], game_state['movement_trace'][i+1])        
            screen.blit(character_image, game_state['character'].topleft)
            screen.blit(treasure_image, game_state['treasure_pos'])

            for trap in game_state['traps']:
                screen.blit(trap_image, trap.topleft)            
            for ghost in game_state['ghosts']:
                ghost.draw(screen)           
            for dragon in game_state['dragons']:
                dragon.draw(screen)
            
            story_surface = large_font.render(story_texts[game_state['current_story_index']], True, GREEN)
            screen.blit(story_surface, (WIDTH//2 - story_surface.get_width()//2, HEIGHT//2-60))
            stats_text = font.render(f"{game_stats.get_stats()}", True, WHITE)
            screen.blit(stats_text, (20, HEIGHT - 40))
            
            difficulty_text = font.render(f"Mode: {game_state['difficulty'].title()}", True, WHITE)
            screen.blit(difficulty_text, (WIDTH - 200, HEIGHT - 40))
            
            dark_overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            dark_overlay.fill((0,0,0,80)) 
          
            if game_state['game_over']:
                screen.blit(dark_overlay, (0,0))
                play_again_button, quit_button = draw_game_over_buttons()

                if game_state['game_won']:
                    if random.random() < 0.1:
                        fireworks.append(Firework(randint(100, WIDTH-100), randint(100, HEIGHT//2)))
                
                    for firework in fireworks[:]:
                        firework.update()
                        firework.draw(screen)
                    
                    fireworks = [firework for firework in fireworks if firework.is_active]                  
                    
                    if game_state['master_won'] and game_state['master_level']:
                        dancing_numbers.update()
                        dancing_numbers.draw(screen)                       
                
            pygame.display.flip()
            clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main() 