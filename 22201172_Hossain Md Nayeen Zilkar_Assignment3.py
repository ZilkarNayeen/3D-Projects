from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math
import random

GRID_LENGTH=600
fovY=120
pos=[0,500,500]
angle_x = 45
angle_y=0
follow= False #3rd person player follow 
player_x= 0.0
player_y =0.0
player_angle=0.0
player_life = 5
game_score=0
bullets_missed= 0

NUM_ENEMIES=5
enemies=[]
bullets=[]
cheat_mode=False
auto_follow=False
game_over=False

def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18):
    glColor3f(1, 1, 1)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(font, ord(ch))
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def draw_shapes():
    global player_x,player_y,player_angle
    global enemies,bullets,cheat_mode,game_over

    if game_over:
        glPushMatrix()
        glTranslatef(player_x,player_y, 15)
        glRotatef(90,1,0,0)
        glColor3f(0.8,0.2, 0.2)
        glutSolidCube(30)
        glPopMatrix()
    else:
        glPushMatrix()
        glTranslatef(player_x,player_y, 0)
        glRotatef(player_angle,0,0, 1)

        # Legs
        for offset in (-10,10):
            glPushMatrix()
            glColor3f(0.0,0.0,1.0)
            glTranslatef(offset,0,15)
            gluCylinder(gluNewQuadric(),6,6,50,16,16)
            glPopMatrix()
        # Body
        glPushMatrix()
        glColor3f(0.0,1.0,0.0)
        glTranslatef(0,0,65)
        glScalef(40,24,60)
        glutSolidCube(1)
        glPopMatrix()

        # Head
        glPushMatrix()
        glColor3f(0.0,0.0,0.0)
        glTranslatef(0,0,110)
        glutSolidSphere(12,20,20)
        glPopMatrix()
        # Hands
        for offset in (-12,12):
            glPushMatrix()
            glColor3f(1.0,0.8,0.6)
            glTranslatef(offset,20,65)
            glRotatef(-90,1,0,0)
            gluCylinder(gluNewQuadric(),4,4,40,16, 16)
            glPopMatrix()
        # Gun
        glPushMatrix()
        glColor3f(0.1, 0.1, 0.1)
        glTranslatef(0, 30, 80)
        glRotatef(-90, 1, 0, 0)
        gluCylinder(gluNewQuadric(), 3.5, 3.5, 40, 16, 2)
        glTranslatef(0, 0, 40)
        glutSolidCube(6)
        glPopMatrix()
        glPopMatrix()
    for enemy in enemies:
        glPushMatrix()
        glTranslatef(enemy['x'], enemy['y'], 0)
        glScalef(enemy['scale'], enemy['scale'], enemy['scale'])
        glPushMatrix()
        glColor3f(1.0,0.0,0.0)
        glTranslatef(0, 0, 40)
        glutSolidSphere(30, 20, 20)
        glPopMatrix()
        glPushMatrix()
        glColor3f(0.0, 0.0, 0.0)
        glTranslatef(0, 0, 80)
        glutSolidSphere(20, 20, 20)
        glPopMatrix()
        glPopMatrix()

    for bullet in bullets:
        if not bullet['active']:
            continue
        glPushMatrix()
        glColor3f(1.0, 1.0, 0.0)
        glTranslatef(bullet['x'], bullet['y'], bullet['z'])
        glutSolidCube(10)
        glPopMatrix()

def keyboardListener(key, x, y):
    global player_x,player_y, player_angle
    global cheat_mode,auto_follow, game_over
    global player_life, game_score,bullets_missed,enemies,bullets

    if game_over and (key == b'r' or key == b'R'):
        player_x, player_y, player_angle = 0.0,0.0,0.0
        player_life =5
        game_score=0
        bullets_missed= 0
        game_over =False
        cheat_mode= False
        auto_follow=False
        bullets = []
        enemies = []
        for i in range(NUM_ENEMIES):
            enemies.append({
                'x': random.randint(-GRID_LENGTH+50, GRID_LENGTH-50),
                'y': random.randint(-GRID_LENGTH+50, GRID_LENGTH-50),
                'scale': 1.0,
                'growing': True,
                'speed': random.uniform(0.2, 0.5)
            })
        return

    if game_over:
        return
    step = 20.0
    if key in (b'w', b'W'):
        player_x+= step * math.sin(math.radians(player_angle))
        player_y+= step * math.cos(math.radians(player_angle))
        player_x =max(min(player_x, GRID_LENGTH - 50), -GRID_LENGTH + 50)
        player_y=max(min(player_y, GRID_LENGTH - 50), -GRID_LENGTH + 50)

    if key in (b's', b'S'):
        player_x-=step * math.sin(math.radians(player_angle))
        player_y-= step * math.cos(math.radians(player_angle))
        player_x =max(min(player_x, GRID_LENGTH - 50), -GRID_LENGTH + 50)
        player_y=max(min(player_y, GRID_LENGTH - 50), -GRID_LENGTH + 50)

    if key in (b'a', b'A'):
        player_angle= (player_angle + 5.0) % 360
    if key in (b'd', b'D'):
        player_angle =(player_angle - 5.0) % 360

    if key in (b'c', b'C'):
        cheat_mode=not cheat_mode
    if key in (b'v', b'V'):
        if cheat_mode:
            auto_follow=not auto_follow


def specialKeyListener(key, x, y):
    global angle_x, angle_y
    if key == GLUT_KEY_UP:
        angle_x = min(angle_x + 5, 90)
    if key == GLUT_KEY_DOWN:
        angle_x = max(angle_x - 5, 10)
    if key == GLUT_KEY_LEFT:
        angle_y = (angle_y + 5) % 360
    if key == GLUT_KEY_RIGHT:
        angle_y = (angle_y - 5) % 360

def mouseListener(button, state, x, y):
    global bullets, game_over, follow
    if game_over:
        return
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        rad = math.radians(player_angle)
        gun_x = player_x + 30 * math.sin(rad)
        gun_y = player_y + 30 * math.cos(rad)
        bullets.append({
            'x': gun_x,
            'y': gun_y,
            'z': 80,
            'angle': player_angle,
            'distance': 0,
            'active': True
        })
    if button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
        follow = not follow


def setupCamera():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(fovY, 1.0, 0.1, 2000)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    if follow:
        rad_angle = math.radians(player_angle)
        cam_x =player_x - 100* math.sin(rad_angle)
        cam_y= player_y -100*math.cos(rad_angle)
        cam_z= 150
        look_x =player_x+200*math.sin(rad_angle)
        look_y=player_y +200*math.cos(rad_angle)
        if cheat_mode and auto_follow:
            look_x= player_x+200*math.sin(math.radians(player_angle))
            look_y= player_y+200*math.cos(math.radians(player_angle))
        gluLookAt(cam_x, cam_y, cam_z, look_x, look_y, 100, 0, 0, 1)
    else:
        rad_angle_x = math.radians(angle_x)
        rad_angle_y = math.radians(angle_y)
        distance = int(GRID_LENGTH * 1.4)
        cam_x = distance * math.sin(rad_angle_y) * math.cos(rad_angle_x)
        cam_y = distance * math.cos(rad_angle_y) * math.cos(rad_angle_x)
        cam_z = distance * math.sin(rad_angle_x)
        gluLookAt(cam_x, cam_y, cam_z, 0, 0, 0, 0, 0, 1)

def idle():
    global enemies, bullets, player_angle
    global player_life, game_score, bullets_missed, game_over
    if game_over:
        glutPostRedisplay()
        return

    for enemy in enemies:
        dx=player_x-enemy['x']
        dy=player_y-enemy['y']
        dist = math.sqrt(dx*dx + dy*dy) + 1e-5
        if not cheat_mode:
            enemy['x']+=(dx/dist) * enemy['speed']
            enemy['y']+=(dy/dist) * enemy['speed']
        if enemy['growing']:
            enemy['scale']+=0.01
            if enemy['scale']>=1.3:
                enemy['growing']=False
        else:
            enemy['scale']-= 0.01
            if enemy['scale'] <=0.7:
                enemy['growing'] = True
        if dist < 50:
            player_life-= 1
            enemy['x']= random.randint(-GRID_LENGTH+50, GRID_LENGTH-50)
            enemy['y']=random.randint(-GRID_LENGTH+50, GRID_LENGTH-50)
            enemy['scale'] = 1.0
            if player_life <= 0:
                game_over=True

    new_bullets = []
    for bullet in bullets:
        if not bullet['active']:
            continue
        speed=20.0
        rad= math.radians(bullet['angle'])
        bullet['x'] +=speed *math.sin(rad)
        bullet['y'] +=speed*math.cos(rad)
        bullet['distance']+=speed
        if (abs(bullet['x']) >GRID_LENGTH or
            abs(bullet['y'])> GRID_LENGTH or
            bullet['distance'] > 800):
            bullet['active'] = False
            if not cheat_mode:
                bullets_missed += 1
                if bullets_missed >= 10:
                    game_over = True
            continue
        hit =False
        for enemy in enemies:
            dx= bullet['x']-enemy['x']
            dy=bullet['y']-enemy['y']
            if math.sqrt(dx*dx+dy*dy) < 40:
                bullet['active']=False
                game_score+= 10
                enemy['x']=random.randint(-GRID_LENGTH+50, GRID_LENGTH-50)
                enemy['y']=random.randint(-GRID_LENGTH+50, GRID_LENGTH-50)
                enemy['scale'] = 1.0
                hit=True
                break
        if not hit:
            new_bullets.append(bullet)
    bullets[:] = new_bullets
    if cheat_mode:
        player_angle = (player_angle + 2) % 360
        for enemy in enemies:
            dx=enemy['x'] - player_x
            dy=enemy['y'] - player_y
            angle_to_enemy = math.degrees(math.atan2(dx, dy))
            if angle_to_enemy< 0:
                angle_to_enemy+=360
            diff=abs(player_angle-angle_to_enemy)
            if diff<10 or diff>350:
                rad = math.radians(player_angle)
                gun_x =player_x+30 * math.sin(rad)
                gun_y= player_y+30 * math.cos(rad)
                bullets.append({
                    'x': gun_x,
                    'y': gun_y,
                    'z': 80,
                    'angle': player_angle,
                    'distance': 0,
                    'active': True
                })
                break

    glutPostRedisplay()


def showScreen():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glViewport(0,0,500,500)
    setupCamera()
    glEnable(GL_DEPTH_TEST)
    square = 50
    for i in range(-GRID_LENGTH, GRID_LENGTH, square):
        for j in range(-GRID_LENGTH, GRID_LENGTH, square):
            if ((i+j)//square) %2==0:
                glColor3f(0.9,0.8,1.0)
            else:
                glColor3f(1, 1, 1)
            glBegin(GL_QUADS)
            glVertex3f(i,j, 0)
            glVertex3f(i +square, j,0)
            glVertex3f(i +square, j+square, 0)
            glVertex3f(i, j+square, 0)
            glEnd()
    wall_h = 100
    glBegin(GL_QUADS)
    glColor3f(0, 1, 0)
    glVertex3f(-GRID_LENGTH, GRID_LENGTH, 0)
    glVertex3f(GRID_LENGTH, GRID_LENGTH, 0)
    glVertex3f(GRID_LENGTH, GRID_LENGTH, wall_h)
    glVertex3f(-GRID_LENGTH, GRID_LENGTH, wall_h)
    glColor3f(0, 0, 1)
    glVertex3f(-GRID_LENGTH, -GRID_LENGTH, 0)
    glVertex3f(GRID_LENGTH, -GRID_LENGTH, 0)
    glVertex3f(GRID_LENGTH, -GRID_LENGTH, wall_h)
    glVertex3f(-GRID_LENGTH, -GRID_LENGTH, wall_h)
    glColor3f(1, 1, 1)
    glVertex3f(GRID_LENGTH, -GRID_LENGTH, 0)
    glVertex3f(GRID_LENGTH, GRID_LENGTH, 0)
    glVertex3f(GRID_LENGTH, GRID_LENGTH, wall_h)
    glVertex3f(GRID_LENGTH, -GRID_LENGTH, wall_h)
    glColor3f(0, 1, 1)
    glVertex3f(-GRID_LENGTH, -GRID_LENGTH, 0)
    glVertex3f(-GRID_LENGTH, GRID_LENGTH, 0)
    glVertex3f(-GRID_LENGTH, GRID_LENGTH, wall_h)
    glVertex3f(-GRID_LENGTH, -GRID_LENGTH, wall_h)
    glEnd()

    draw_shapes()
    draw_text(10, 470, f"Life: {player_life}")
    draw_text(10, 440, f"Score: {game_score}")
    draw_text(10, 410, f"Missed: {bullets_missed}")
    if cheat_mode:
        draw_text(10, 380, "CHEAT MODE")
    if auto_follow and cheat_mode:
        draw_text(10, 350, "AUTO FOLLOW")
    if game_over:
        draw_text(200, 250, "GAME OVER - Press R", GLUT_BITMAP_TIMES_ROMAN_24)
    glutSwapBuffers()


def main():
    global enemies
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(500, 500)
    glutInitWindowPosition(0, 0)
    glutCreateWindow(b"3D OpenGL Game")
    for _ in range(NUM_ENEMIES):
        enemies.append({
            'x': random.randint(-GRID_LENGTH+50, GRID_LENGTH-50),
            'y': random.randint(-GRID_LENGTH+50, GRID_LENGTH-50),
            'scale': 1.0,
            'growing': True,
            'speed': random.uniform(0.2, 0.5)
        })
    glutDisplayFunc(showScreen)
    glutKeyboardFunc(keyboardListener)
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    glutIdleFunc(idle)
    glutMainLoop()


if __name__ == "__main__":
    main()
