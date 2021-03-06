import pygame
pygame.init()

WIDTH, HEIGHT = 700, 500
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pong")

FPS = 60

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREY = (200, 200, 200)

PADDLE_WIDTH, PADDLE_HEIGHT = 20, 100
BALL_RADIUS = 7

WINNING_SCORE = 5

bounceSound = pygame.mixer.Sound('bounce.wav')


def game_text(text, size, color):
    game_font = pygame.font.Font("pressStart2P.ttf", size)
    message = game_font.render(text, 1, color)
    return message


class Paddle():
    COLOR = WHITE
    VEL = 4

    def __init__(self, x, y, width, height):
        self.x = self.original_x = x
        self.y = self.original_y = y
        self.width = width
        self.height = height

    def draw(self, win):
        pygame.draw.rect(win, self.COLOR, (self.x, self.y, self.width, self.height))

    def move(self, up=True):
        if up:
            self.y -= self.VEL
        else:
            self.y += self.VEL

    def reset(self):
        self.x = self.original_x
        self.y = self.original_y


class Ball():
    INIT_VEL = 5
    COLOR = WHITE

    def __init__(self, x, y, radius):
        self.x = self.original_x = x
        self.y = self.original_y = y
        self.radius = radius
        self.x_vel = self.INIT_VEL
        self.y_vel = 0

    def draw(self, win):
        pygame.draw.circle(win, self.COLOR, (self.x, self.y), self.radius)

    def move(self):
        self.x += self.x_vel
        self.y += self.y_vel

    def reset(self):
        self.x = self.original_x
        self.y = self.original_y
        self.y_vel = 0
        self.x_vel *= -1


class Button():
    global button_width, button_height
    button_width = 150
    button_height = 100

    def __init__(self, text, x, y, color):
        self.text = text
        self.x = x
        self.y = y
        self.color = color
        self.width = button_width
        self.height = button_height

    def draw(self, win):
        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.height))
        text = game_text(self.text, 10, BLACK)
        win.blit(text, (self.x + round(button_width/2) - round(text.get_width()/2), self.y + round(button_height/2) -round(text.get_height()/2)))

    def hover(self, pos):
        x1 = pos[0]
        y1 = pos[1]
        if self.x <= x1 <= self.x + self.width and self.y <= y1 <= self.y + self.height:
            return True
        else:
            return False


def draw(win, paddles, ball, left_score, right_score):
    win.fill(BLACK)

    left_score_text = game_text(f"{left_score}", 40, WHITE)
    right_score_text = game_text(f"{right_score}", 40, WHITE)
    win.blit(left_score_text, (WIDTH//4 - left_score_text.get_width()//2, 20))
    win.blit(right_score_text, (3*WIDTH//4 - right_score_text.get_width()//2, 20))

    for paddle in paddles:
        paddle.draw(win)

    for i in range(10, HEIGHT, HEIGHT//20):
        if i % 2 == 1:
            continue
        pygame.draw.rect(win, WHITE, (WIDTH//2 - 5, i, 10, HEIGHT//20))

    ball.draw(win)
    pygame.display.update()


def handle_collision(ball, left_paddle, right_paddle, accel, max_speed):
    if ball.y + ball.radius >= HEIGHT:
        bounceSound.play()
        ball.y_vel *= -1
    elif ball.y - ball.radius <= 0:
        bounceSound.play()
        ball.y_vel *= -1

    if ball.x_vel < 0:
        if ball.y >= left_paddle.y and ball.y <= left_paddle.y + left_paddle.height:
            if ball.x - ball.radius <= left_paddle.x + left_paddle.width:
                bounceSound.play()
                ball.x_vel *= -1

                middle_y = left_paddle.y + left_paddle.height/2
                difference_in_y = middle_y - ball.y
                reduction_factor = (left_paddle.height/2)/ball.INIT_VEL
                y_vel = difference_in_y / reduction_factor
                ball.y_vel = -1*y_vel

                if abs(ball.x_vel) <= max_speed:
                    ball.x_vel += accel

    else:
        if ball.y >= right_paddle.y and ball.y <= right_paddle.y + right_paddle.height:
            if ball.x + ball.radius >= right_paddle.x:
                bounceSound.play()
                ball.x_vel *= -1

                middle_y = right_paddle.y + right_paddle.height/2
                difference_in_y = middle_y - ball.y
                reduction_factor = (right_paddle.height/2)/ball.INIT_VEL
                y_vel = difference_in_y / reduction_factor
                ball.y_vel = -1*y_vel

                if abs(ball.x_vel) <= max_speed:
                    ball.x_vel -= accel


def handle_paddle_movement(keys, left_paddle, right_paddle):
    if keys[pygame.K_w] and left_paddle.y - left_paddle.VEL >= 0:
        left_paddle.move(up=True)
    if keys[pygame.K_s] and left_paddle.y + left_paddle.height + left_paddle.VEL <= HEIGHT:
        left_paddle.move(up=False)

    if keys[pygame.K_UP] and right_paddle.y - right_paddle.VEL >= 0:
        right_paddle.move(up=True)
    if keys[pygame.K_DOWN] and right_paddle.y + right_paddle.height + right_paddle.VEL <= HEIGHT:
        right_paddle.move(up=False)


def local_multiplayer():
    run = True
    clock = pygame.time.Clock()

    left_paddle = Paddle(10, HEIGHT//2 - PADDLE_HEIGHT//2, PADDLE_WIDTH, PADDLE_HEIGHT)
    right_paddle = Paddle(WIDTH - 10 - PADDLE_WIDTH, HEIGHT//2 - PADDLE_HEIGHT//2, PADDLE_WIDTH, PADDLE_HEIGHT)
    ball = Ball(WIDTH//2, HEIGHT//2, BALL_RADIUS)

    accel = 0.25
    max_speed = 15

    left_score = 0
    right_score = 0

    while run:
        clock.tick(FPS)

        draw(WIN, [left_paddle, right_paddle], ball, left_score, right_score)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break

        keys = pygame.key.get_pressed()
        handle_paddle_movement(keys, left_paddle, right_paddle)

        ball.move()
        handle_collision(ball, left_paddle, right_paddle, accel, max_speed)
        
        if ball.x < 0:
            right_score += 1
            ball.reset()
            right_paddle.reset()
            left_paddle.reset()
        elif ball.x > WIDTH:
            left_score += 1
            ball.reset()
            right_paddle.reset()
            left_paddle.reset()

        
        won = False
        if left_score >= WINNING_SCORE:
            won = True
            win_text = "Left Player Won!"
        elif right_score >= WINNING_SCORE:
            won = True
            win_text = "Right Player Won!"


        if won:
            text = game_text(win_text, 25, WHITE)
            WIN.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2 - text.get_height()//2))
            pygame.display.update()
            pygame.time.delay(5000)
            ball.reset()
            left_paddle.reset()
            right_paddle.reset()
            left_score = 0
            right_score = 0


def online_multiplayer():
    run = True
    clock = pygame.time.Clock()

    while run:
        clock.tick(FPS)
        WIN.fill(BLACK)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break

        temp_text = game_text("Online multiplayer mode is in development", 15, WHITE)
        WIN.blit(temp_text, (WIDTH/2 - temp_text.get_width()/2, HEIGHT/2 - temp_text.get_height()/2))

        pygame.display.update()


def single_player():
    run = True
    clock = pygame.time.Clock()

    left_paddle = Paddle(10, HEIGHT//2 - PADDLE_HEIGHT//2, PADDLE_WIDTH, PADDLE_HEIGHT)
    wall = Paddle(WIDTH - 5, 0, 5, HEIGHT)
    ball = Ball(WIDTH//2, HEIGHT//2, BALL_RADIUS)

    ball.y_vel = 0.5
    accel = 0.25
    max_speed = 15

    hits_text = "Hits:"
    hits = 0

    while run:
        clock.tick(FPS)

        draw(WIN, [left_paddle, wall], ball, hits_text, hits)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break

        keys = pygame.key.get_pressed()
        handle_paddle_movement(keys, left_paddle, wall)

        ball.move()
        handle_collision(ball, left_paddle, wall, accel, max_speed)

        if ball.x < 0:
            ball.reset()
            left_paddle.reset()
            hits = 0
            ball.x_vel = Ball.INIT_VEL
            ball.y_vel = 0.5
        elif ball.y >= left_paddle.y and ball.y <= left_paddle.y + left_paddle.height:
            if ball.x - ball.radius <= left_paddle.x + left_paddle.width:
                hits += 1


buttons = [Button("Local Co-Op", WIDTH/3 - button_width, HEIGHT/2 + button_height, WHITE), Button("Online", WIDTH/2 - button_width/2, HEIGHT/2 + button_height, WHITE), Button("Practice Mode", 2 * WIDTH/3, HEIGHT/2 + button_height, WHITE)]


def main_menu():
    run = True
    while run:
        WIN.fill(BLACK)

        text = game_text("Main Menu", 50, WHITE)
        WIN.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//10))

        mini_ball = Ball(WIDTH/2, HEIGHT/2 - 40, 5)
        mini_ball.draw(WIN)

        mini_paddle_width = 10
        mini_paddle_length = 50
        mini_paddle_left = Paddle(WIDTH/2 - 100, HEIGHT/2 - mini_paddle_length/2 - 40, mini_paddle_width, mini_paddle_length)
        mini_paddle_left.draw(WIN)

        mini_paddle_right = Paddle(WIDTH/2 + 100, HEIGHT/2 - mini_paddle_length/2 - 40, mini_paddle_width, mini_paddle_length)
        mini_paddle_right.draw(WIN)

        for button in buttons:
            button.draw(WIN)
            pos = pygame.mouse.get_pos()

            if button.hover(pos) == True:
                button.color = GREY
            else:
                button.color = WHITE
            
        if any(button.hover(pos) for button in buttons):
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
        else:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    run = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                if buttons[0].hover(pos) == True:
                    local_multiplayer()
                if buttons[1].hover(pos) == True:
                    online_multiplayer()
                if buttons[2].hover(pos) == True:
                    single_player()

    pygame.quit()

main_menu()
