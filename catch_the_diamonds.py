import sys
import random
import time
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *


WIDTH, HEIGHT = 800, 600
DiamondSize = 20
Catcher_width = 60
Catcher_height = 16
Size = 40
StartingSpeed = 150
Acceleratiom = 10

class GameState:
    def __init__(self):
        self.reset()
        
    def reset(self):
        self.score = 0
        self.game_over = False
        self.paused = False
        self.catcher_x = WIDTH // 2
        self.diamond_x = random.randint(DiamondSize, WIDTH - DiamondSize)
        self.diamond_y = HEIGHT
        self.diamond_color = self.random_vibrant_color()
        self.diamond_speed = StartingSpeed
        self.last_time = time.time()
        print("Starting Over")
    
    def random_vibrant_color(self):
        colors = [
            (1.0, 0.0, 0.0),  # Red
            (0.0, 1.0, 0.0),  # Green
            (0.0, 0.0, 1.0),  # Blue
            (1.0, 1.0, 0.0),  # Yellow
            (1.0, 0.5, 0.0),  # Orange
            (0.5, 0.0, 1.0)   # Purple
        ]
        return random.choice(colors)

game_state = GameState()

def draw_pixel(x, y):
    glBegin(GL_POINTS)
    glVertex2f(x, y)
    glEnd()

def draw_line_midpoint(x1, y1, x2, y2):
    dx = abs(x2 - x1)
    dy = abs(y2 - y1)
    steep = dy > dx
    
    if steep:
        x1, y1 = y1, x1
        x2, y2 = y2, x2
        dx, dy = dy, dx
    
    if x1 > x2:
        x1, x2 = x2, x1
        y1, y2 = y2, y1
    
    y_step = 1 if y1 < y2 else -1
    d = 2 * dy - dx
    y = y1
    
    for x in range(x1, x2 + 1):
        if steep:
            draw_pixel(y, x)
        else:
            draw_pixel(x, y)
        
        if d > 0:
            y += y_step
            d -= 2 * dx
        d += 2 * dy

def draw_diamond(x, y, size, color):
    glColor3f(*color)
    draw_line_midpoint(x, y - size, x + size, y)
    draw_line_midpoint(x + size, y, x, y + size)
    draw_line_midpoint(x, y + size, x - size, y)
    draw_line_midpoint(x - size, y, x, y - size)

def draw_catcher(x, width, height, color):
    glColor3f(*color)
    y_pos = height
    draw_line_midpoint(x - width//2, y_pos, x + width//2, y_pos)
    draw_line_midpoint(x - width//2, y_pos, x - width//2 + 10, y_pos - height)
    draw_line_midpoint(x + width//2, y_pos, x + width//2 - 10, y_pos - height)
    draw_line_midpoint(x - width//2 + 10, y_pos - height, x + width//2 - 10, y_pos - height)

def draw_button(x, y, size, shape, color):
    glColor3f(*color)
    if shape == "left_arrow":
        draw_line_midpoint(x, y, x + size, y - size//2)
        draw_line_midpoint(x, y, x + size, y + size//2)
        draw_line_midpoint(x + size, y - size//2, x + size, y + size//2)
    elif shape == "play":
        draw_line_midpoint(x, y - size//2, x + size, y)
        draw_line_midpoint(x + size, y, x, y + size//2)
    elif shape == "pause":
        draw_line_midpoint(x, y - size//2, x, y + size//2)
        draw_line_midpoint(x + size//2, y - size//2, x + size//2, y + size//2)
    elif shape == "cross":
        draw_line_midpoint(x - size//2, y - size//2, x + size//2, y + size//2)
        draw_line_midpoint(x - size//2, y + size//2, x + size//2, y - size//2)

def check_collision():
    diamond_left = game_state.diamond_x - DiamondSize
    diamond_right = game_state.diamond_x + DiamondSize
    diamond_bottom = game_state.diamond_y - DiamondSize
    diamond_top = game_state.diamond_y + DiamondSize
    
    catcher_left = game_state.catcher_x - Catcher_width//2
    catcher_right = game_state.catcher_x + Catcher_width//2
    catcher_bottom = 0
    catcher_top = Catcher_height
    
    return (diamond_left < catcher_right and
            diamond_right > catcher_left and
            diamond_bottom < catcher_top and
            diamond_top > catcher_bottom)

def update_game():
    if game_state.paused or game_state.game_over:
        return
    
    current_time = time.time()
    delta_time = current_time - game_state.last_time
    game_state.last_time = current_time
    
    game_state.diamond_y -= game_state.diamond_speed * delta_time
    
    if game_state.diamond_y - DiamondSize <= Catcher_height:
        if check_collision():
            game_state.score += 1
            game_state.diamond_speed += Acceleratiom
            print(f"Score: {game_state.score}")
            game_state.diamond_x = random.randint(DiamondSize, WIDTH - DiamondSize)
            game_state.diamond_y = HEIGHT
            game_state.diamond_color = game_state.random_vibrant_color()
        else:
            game_state.game_over = True
            print(f"Game Over! Final Score: {game_state.score}")

def display():
    glClear(GL_COLOR_BUFFER_BIT)
    
    #  buttons
    draw_button(50, HEIGHT - 50, Size, "left_arrow", (0, 0.8, 0.8))
    if game_state.paused:
        draw_button(WIDTH // 2, HEIGHT - 50, Size, "play", (1.0, 0.75, 0))
    else:
        draw_button(WIDTH // 2, HEIGHT - 50, Size, "pause", (1.0, 0.75, 0))
    draw_button(WIDTH - 50, HEIGHT - 50, Size, "cross", (1.0, 0, 0))
    
    #  diamond
    if not game_state.game_over:
        draw_diamond(game_state.diamond_x, game_state.diamond_y, DiamondSize, game_state.diamond_color)
    
    #  catcher
    catcher_color = (1, 0, 0) if game_state.game_over else (1, 1, 1)
    draw_catcher(game_state.catcher_x, Catcher_width, Catcher_height, catcher_color)
    
    glutSwapBuffers()

def keyboard(key, x, y):
    if key == b'\x1b':  
        print(f"Goodbye! Final Score: {game_state.score}")
        glutLeaveMainLoop()
    elif key == b' ':
        game_state.paused = not game_state.paused
    glutPostRedisplay()

def special_keys(key, x, y):
    if not game_state.paused and not game_state.game_over:
        if key == GLUT_KEY_LEFT and game_state.catcher_x - Catcher_width//2 > 0:
            game_state.catcher_x -= 10
        elif key == GLUT_KEY_RIGHT and game_state.catcher_x + Catcher_width//2 < WIDTH:
            game_state.catcher_x += 10
    glutPostRedisplay()

def mouse(button, state, x, y):
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        gl_y = HEIGHT - y
        
        # Left arrow
        if (50 - Size//2 <= x <= 50 + Size//2 and 
            HEIGHT - 50 - Size//2 <= gl_y <= HEIGHT - 50 + Size//2):
            game_state.reset()
            glutPostRedisplay()
        
        # Play/pause
        elif (WIDTH//2 - Size//2 <= x <= WIDTH//2 + Size//2 and 
              HEIGHT - 50 - Size//2 <= gl_y <= HEIGHT - 50 + Size//2):
            game_state.paused = not game_state.paused
        
        # Cross
        elif (WIDTH - 50 - Size//2 <= x <= WIDTH - 50 + Size//2 and 
              HEIGHT - 50 - Size//2 <= gl_y <= HEIGHT - 50 + Size//2):
            print(f"Goodbye! Final Score: {game_state.score}")
            glutLeaveMainLoop()
    
    glutPostRedisplay()

def idle():
    update_game()
    glutPostRedisplay()

def main():
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
    glutInitWindowSize(WIDTH, HEIGHT)
    glutCreateWindow(b"Catch the Diamonds!")
    
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(0, WIDTH, 0, HEIGHT)
    glMatrixMode(GL_MODELVIEW)
    
    glutDisplayFunc(display)
    glutKeyboardFunc(keyboard)
    glutSpecialFunc(special_keys)
    glutMouseFunc(mouse)
    glutIdleFunc(idle)
    
    glClearColor(0.0, 0.0, 0.0, 1.0)
    glPointSize(1.0)
    
    glutMainLoop()

if __name__ == "__main__":
    main()
