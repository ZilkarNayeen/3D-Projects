from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math
import random
import time
import sys

# Game Configuration
WORLD_SIZE = 200
BUILDING_COUNT = 15
TREE_COUNT = 25

# Game State
game_running = True
score = 0
kills = 0
wave = 1
game_time = 0
paused = False

# Difficulty
difficulty_level = 0

# Level up state
leveling_up = False

# Player System
class Player:
    def __init__(self):
        self.pos = [0, 0, 8]
        self.angle = 0
        self.health = 100
        self.max_health = 100
        self.stamina = 100
        self.max_stamina = 100
        self.stamina_regen = 0.2
        self.speed = 0.8
        self.weapon = "rifle"
        self.ammo = {"rifle": 120, "shotgun": 24, "sniper": 15}
        self.last_shot = 0
        self.crosshair_bob = 0
        self.vel_z = 0
        self.on_ground = True
        self.crouching = False
        self.dodging = False
        self.dodge_timer = 0
        self.dodge_duration = 10
        self.dodge_speed = 2.0
        self.dodge_cost = 25
        self.dodge_direction = 0
        self.attack_cost = {"rifle": 2, "shotgun": 5, "sniper": 10}
        
    def move(self, forward=0, strafe=0):
        # Calculate movement with proper trigonometry
        move_x = forward * math.cos(math.radians(self.angle)) + strafe * math.cos(math.radians(self.angle + 90))
        move_y = forward * math.sin(math.radians(self.angle)) + strafe * math.sin(math.radians(self.angle + 90))
        
        new_x = self.pos[0] + move_x * self.speed
        new_y = self.pos[1] + move_y * self.speed
        
        # Collision detection with buildings and world boundaries
        if not self.check_collision(new_x, new_y):
            self.pos[0] = new_x
            self.pos[1] = new_y
            self.crosshair_bob += 0.3  # Walking animation
    
    def check_collision(self, x, y):
        # World boundaries
        if abs(x) > WORLD_SIZE or abs(y) > WORLD_SIZE:
            return True
        
        # Building collisions
        for building in buildings:
            if (building["x"] - building["width"]/2 - 5 < x < building["x"] + building["width"]/2 + 5 and
                building["y"] - building["depth"]/2 - 5 < y < building["y"] + building["depth"]/2 + 5):
                return True
        return False
    
    def shoot(self):
        current_time = glutGet(GLUT_ELAPSED_TIME)
        weapon_cooldown = {"rifle": 150, "shotgun": 800, "sniper": 1200}
        
        if (current_time - self.last_shot > weapon_cooldown[self.weapon] and 
            (infinite_ammo or self.ammo[self.weapon] > 0) and
            self.stamina >= self.attack_cost[self.weapon]):
            self.last_shot = current_time
            if not infinite_ammo:
                self.ammo[self.weapon] -= 1
            self.stamina -= self.attack_cost[self.weapon]
            
            bullet_z = self.pos[2] - (1 if self.crouching else 2)
            bullet_damage = {"rifle": 35, "shotgun": 15, "sniper": 85}[self.weapon]
            bullet_speed = {"rifle": 4.0, "shotgun": 2.5, "sniper": 6.0}[self.weapon]
            bullet_range = {"rifle": 150, "shotgun": 40, "sniper": 300}[self.weapon]
            
            if self.weapon == "shotgun":
                # Shotgun fires multiple pellets
                for i in range(8):
                    spread = random.uniform(-15, 15)
                    bullets.append(Bullet(self.pos[0], self.pos[1], bullet_z, 
                                        self.angle + spread, bullet_damage, bullet_speed, bullet_range))
            else:
                bullets.append(Bullet(self.pos[0], self.pos[1], bullet_z, 
                                    self.angle, bullet_damage, bullet_speed, bullet_range))
    
    def jump(self):
        if self.on_ground and not self.crouching:
            self.vel_z = 1.0
            self.on_ground = False
    
    def dodge(self):
        if self.stamina >= self.dodge_cost and not self.dodging and self.on_ground and not self.crouching:
            self.stamina -= self.dodge_cost
            self.dodging = True
            self.dodge_timer = self.dodge_duration
            self.dodge_direction = self.angle  # Dodge forward

# Bullet System
class Bullet:
    def __init__(self, x, y, z, angle, damage, speed, range_):
        self.pos = [x, y, z]
        self.angle = angle
        self.damage = damage
        self.speed = speed
        self.range = range_
        self.traveled = 0
        self.active = True
    
    def update(self):
        if not self.active:
            return False
            
        # Move bullet
        dx = math.cos(math.radians(self.angle)) * self.speed
        dy = math.sin(math.radians(self.angle)) * self.speed
        
        self.pos[0] += dx
        self.pos[1] += dy
        self.traveled += self.speed
        
        # Check range
        if self.traveled > self.range:
            self.active = False
            return False
            
        # Check building collisions
        for building in buildings:
            if (building["x"] - building["width"]/2 < self.pos[0] < building["x"] + building["width"]/2 and
                building["y"] - building["depth"]/2 < self.pos[1] < building["y"] + building["depth"]/2 and
                self.pos[2] < building["height"]):
                self.active = False
                return False
        
        return True

# Enemy System
class Enemy:
    def __init__(self, x, y):
        self.pos = [x, y, 6]
        self.angle = 0
        self.health = 80 + difficulty_level * 20
        self.max_health = self.health
        self.speed = 0.3 + difficulty_level * 0.02
        self.bullet_damage = 35 + difficulty_level * 5
        self.bullet_speed = 4.0
        self.bullet_range = 150
        self.attack_cooldown = 1000 - difficulty_level * 100
        self.state = "patrol"  # patrol, chase, attack
        self.last_seen_player = [0, 0]
        self.patrol_target = [x + random.uniform(-30, 30), y + random.uniform(-30, 30)]
        self.last_shot = 0
        self.detection_range = 60
        self.attack_range = 40
        
    def update(self):
        if self.health <= 0:
            return False
            
        # Calculate distance to player
        dx = player.pos[0] - self.pos[0]
        dy = player.pos[1] - self.pos[1]
        dist_to_player = math.sqrt(dx*dx + dy*dy)
        
        # Line of sight check (simplified)
        has_line_of_sight = dist_to_player < self.detection_range
        
        # State machine
        if has_line_of_sight and dist_to_player < self.detection_range:
            self.state = "chase"
            self.last_seen_player = [player.pos[0], player.pos[1]]
        elif self.state == "chase" and dist_to_player > self.detection_range * 1.5:
            self.state = "patrol"
        
        # Movement based on state
        if self.state == "chase":
            # Move toward player
            if dist_to_player > 5:
                move_x = (dx / dist_to_player) * self.speed
                move_y = (dy / dist_to_player) * self.speed
                
                new_x = self.pos[0] + move_x
                new_y = self.pos[1] + move_y
                
                if not self.check_collision(new_x, new_y):
                    self.pos[0] = new_x
                    self.pos[1] = new_y
                    self.angle = math.degrees(math.atan2(dy, dx))
            
            # Attack if close enough
            if dist_to_player < self.attack_range:
                current_time = glutGet(GLUT_ELAPSED_TIME)
                if current_time - self.last_shot > self.attack_cooldown:  # Shoot every second
                    self.shoot_at_player()
                    self.last_shot = current_time
                    
        elif self.state == "patrol":
            # Move toward patrol target
            px = self.patrol_target[0] - self.pos[0]
            py = self.patrol_target[1] - self.pos[1]
            patrol_dist = math.sqrt(px*px + py*py)
            
            if patrol_dist < 10:
                # Choose new patrol target
                self.patrol_target = [self.pos[0] + random.uniform(-40, 40), 
                                    self.pos[1] + random.uniform(-40, 40)]
            else:
                move_x = (px / patrol_dist) * self.speed * 0.5
                move_y = (py / patrol_dist) * self.speed * 0.5
                
                new_x = self.pos[0] + move_x
                new_y = self.pos[1] + move_y
                
                if not self.check_collision(new_x, new_y):
                    self.pos[0] = new_x
                    self.pos[1] = new_y
        
        return True
    
    def check_collision(self, x, y):
        # Same collision as player
        if abs(x) > WORLD_SIZE or abs(y) > WORLD_SIZE:
            return True
        for building in buildings:
            if (building["x"] - building["width"]/2 - 3 < x < building["x"] + building["width"]/2 + 3 and
                building["y"] - building["depth"]/2 - 3 < y < building["y"] + building["depth"]/2 + 3):
                return True
        return False
    
    def shoot_at_player(self):
        # Enemy shoots at player
        dx = player.pos[0] - self.pos[0]
        dy = player.pos[1] - self.pos[1]
        angle = math.degrees(math.atan2(dy, dx))
        enemy_bullets.append(Bullet(self.pos[0], self.pos[1], self.pos[2], angle, self.bullet_damage, self.bullet_speed, self.bullet_range))
    
    def take_damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            return True  # Enemy died
        return False

class Boss(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.health = 300 + difficulty_level * 100
        self.max_health = self.health
        self.speed = 0.35 + difficulty_level * 0.02
        self.bullet_damage = 50 + difficulty_level * 10
        self.bullet_speed = 5.0
        self.bullet_range = 200
        self.attack_cooldown = 700 - difficulty_level * 50
        self.detection_range = 100
        self.attack_range = 70
        self.charge_cooldown = 5000
        self.last_charge = 0
        self.charging = False
        self.charge_speed = self.speed * 2
        self.charge_duration = 20
        self.charge_timer = 0

    def update(self):
        if self.health <= 0:
            return False

        current_time = glutGet(GLUT_ELAPSED_TIME)
            
        # Calculate distance to player
        dx = player.pos[0] - self.pos[0]
        dy = player.pos[1] - self.pos[1]
        dist_to_player = math.sqrt(dx*dx + dy*dy)
        
        # Line of sight check (simplified)
        has_line_of_sight = dist_to_player < self.detection_range
        
        # State machine
        if has_line_of_sight and dist_to_player < self.detection_range:
            self.state = "chase"
            self.last_seen_player = [player.pos[0], player.pos[1]]
        elif self.state == "chase" and dist_to_player > self.detection_range * 1.5:
            self.state = "patrol"
        
        # Movement based on state
        if self.state == "chase":
            if self.charging:
                # Charging movement
                move_x = (dx / dist_to_player) * self.charge_speed
                move_y = (dy / dist_to_player) * self.charge_speed
                new_x = self.pos[0] + move_x
                new_y = self.pos[1] + move_y
                if not self.check_collision(new_x, new_y):
                    self.pos[0] = new_x
                    self.pos[1] = new_y
                self.charge_timer -= 1
                if self.charge_timer <= 0:
                    self.charging = False
            else:
                # Normal chase
                if dist_to_player > 5:
                    move_x = (dx / dist_to_player) * self.speed
                    move_y = (dy / dist_to_player) * self.speed
                    
                    new_x = self.pos[0] + move_x
                    new_y = self.pos[1] + move_y
                    
                    if not self.check_collision(new_x, new_y):
                        self.pos[0] = new_x
                        self.pos[1] = new_y
                        self.angle = math.degrees(math.atan2(dy, dx))
                
                # Charge attack if cooldown allows and close enough
                if dist_to_player < 30 and current_time - self.last_charge > self.charge_cooldown:
                    self.charging = True
                    self.charge_timer = self.charge_duration
                    self.last_charge = current_time
                
                # Shoot if in range
                if dist_to_player < self.attack_range:
                    if current_time - self.last_shot > self.attack_cooldown:
                        self.shoot_at_player()
                        self.last_shot = current_time
                    
        elif self.state == "patrol":
            # Move toward patrol target
            px = self.patrol_target[0] - self.pos[0]
            py = self.patrol_target[1] - self.pos[1]
            patrol_dist = math.sqrt(px*px + py*py)
            
            if patrol_dist < 10:
                # Choose new patrol target
                self.patrol_target = [self.pos[0] + random.uniform(-40, 40), 
                                    self.pos[1] + random.uniform(-40, 40)]
            else:
                move_x = (px / patrol_dist) * self.speed * 0.5
                move_y = (py / patrol_dist) * self.speed * 0.5
                
                new_x = self.pos[0] + move_x
                new_y = self.pos[1] + move_y
                
                if not self.check_collision(new_x, new_y):
                    self.pos[0] = new_x
                    self.pos[1] = new_y
        
        return True

    def shoot_at_player(self):
        dx = player.pos[0] - self.pos[0]
        dy = player.pos[1] - self.pos[1]
        angle = math.degrees(math.atan2(dy, dx))
        enemy_bullets.append(Bullet(self.pos[0], self.pos[1], self.pos[2], angle, self.bullet_damage, self.bullet_speed, self.bullet_range))
        enemy_bullets.append(Bullet(self.pos[0], self.pos[1], self.pos[2], angle + 10, self.bullet_damage, self.bullet_speed, self.bullet_range))
        enemy_bullets.append(Bullet(self.pos[0], self.pos[1], self.pos[2], angle - 10, self.bullet_damage, self.bullet_speed, self.bullet_range))

# Game Objects
player = Player()
bullets = []
enemy_bullets = []
enemies = []
buildings = []
trees = []
pickups = []

# Environment variables
time_of_day = 12.0  # 0-24 hours
day_cycle_speed = 0.005
flashlight_on = False
first_person = True  # Start in first person for better immersion

# Cheat modes
god_mode = False
infinite_ammo = False

# Input flags
forward = False
backward = False
strafe_left = False
strafe_right = False
turn_left = False
turn_right = False
shooting = False

# Window dimensions
window_width = 1000
window_height = 800

def generate_world():
    """Generate buildings and trees for the world"""
    global buildings, trees
    
    # Generate buildings
    buildings = []
    for _ in range(BUILDING_COUNT):
        x = random.uniform(-WORLD_SIZE + 30, WORLD_SIZE - 30)
        y = random.uniform(-WORLD_SIZE + 30, WORLD_SIZE - 30)
        width = random.uniform(15, 35)
        depth = random.uniform(15, 35)
        height = random.uniform(20, 45)
        buildings.append({"x": x, "y": y, "width": width, "depth": depth, "height": height})
    
    # Generate trees
    trees = []
    for _ in range(TREE_COUNT):
        x = random.uniform(-WORLD_SIZE + 10, WORLD_SIZE - 10)
        y = random.uniform(-WORLD_SIZE + 10, WORLD_SIZE - 10)
        # Make sure trees don't spawn inside buildings
        collision = False
        for building in buildings:
            if (building["x"] - building["width"]/2 - 10 < x < building["x"] + building["width"]/2 + 10 and
                building["y"] - building["depth"]/2 - 10 < y < building["y"] + building["depth"]/2 + 10):
                collision = True
                break
        if not collision:
            height = random.uniform(12, 20)
            trees.append({"x": x, "y": y, "height": height})

def spawn_enemies():
    """Spawn enemies around the map"""
    for _ in range(min(8, wave * 2)):
        # Spawn away from player
        while True:
            x = random.uniform(-WORLD_SIZE + 20, WORLD_SIZE - 20)
            y = random.uniform(-WORLD_SIZE + 20, WORLD_SIZE - 20)
            dist = math.sqrt((x - player.pos[0])**2 + (y - player.pos[1])**2)
            if dist > 50:  # Far enough from player
                # Check not inside building
                collision = False
                for building in buildings:
                    if (building["x"] - building["width"]/2 < x < building["x"] + building["width"]/2 and
                        building["y"] - building["depth"]/2 < y < building["y"] + building["depth"]/2):
                        collision = True
                        break
                if not collision:
                    enemies.append(Enemy(x, y))
                    break

def spawn_boss():
    """Spawn a boss away from player"""
    while True:
        x = random.uniform(-WORLD_SIZE + 20, WORLD_SIZE - 20)
        y = random.uniform(-WORLD_SIZE + 20, WORLD_SIZE - 20)
        dist = math.sqrt((x - player.pos[0])**2 + (y - player.pos[1])**2)
        if dist > 80:  # Farther from player
            # Check not inside building
            collision = False
            for building in buildings:
                if (building["x"] - building["width"]/2 < x < building["x"] + building["width"]/2 and
                    building["y"] - building["depth"]/2 < y < building["y"] + building["depth"]/2):
                    collision = True
                    break
            if not collision:
                enemies.append(Boss(x, y))
                break

def spawn_pickup(x, y, pickup_type):
    """Spawn health or ammo pickup"""
    pickups.append({"x": x, "y": y, "type": pickup_type, "spin": 0})

def draw_terrain():
    """Draw the ground with texture-like appearance"""
    glColor3f(0.2, 0.4, 0.1)  # Dark green
    
    # Draw grass patches with variation
    for i in range(-WORLD_SIZE, WORLD_SIZE, 20):
        for j in range(-WORLD_SIZE, WORLD_SIZE, 20):
            variation = 0.8 + 0.4 * math.sin(i * 0.1) * math.cos(j * 0.1)
            glColor3f(0.15 * variation, 0.35 * variation, 0.08 * variation)
            glBegin(GL_QUADS)
            glVertex3f(i, j, 0)
            glVertex3f(i+20, j, 0)
            glVertex3f(i+20, j+20, 0)
            glVertex3f(i, j+20, 0)
            glEnd()

def draw_buildings():
    """Draw realistic buildings with doors and windows"""
    for building in buildings:
        x, y = building["x"], building["y"]
        w, d, h = building["width"], building["depth"], building["height"]
        
        # Main building structure
        glBegin(GL_QUADS)
        
        # Front face
        glColor3f(0.6, 0.6, 0.65)
        glVertex3f(x - w/2, y - d/2, 0)
        glVertex3f(x + w/2, y - d/2, 0)
        glVertex3f(x + w/2, y - d/2, h)
        glVertex3f(x - w/2, y - d/2, h)
        
        # Back face
        glColor3f(0.5, 0.5, 0.55)
        glVertex3f(x + w/2, y + d/2, 0)
        glVertex3f(x - w/2, y + d/2, 0)
        glVertex3f(x - w/2, y + d/2, h)
        glVertex3f(x + w/2, y + d/2, h)
        
        # Left face
        glColor3f(0.55, 0.55, 0.6)
        glVertex3f(x - w/2, y + d/2, 0)
        glVertex3f(x - w/2, y - d/2, 0)
        glVertex3f(x - w/2, y - d/2, h)
        glVertex3f(x - w/2, y + d/2, h)
        
        # Right face
        glColor3f(0.45, 0.45, 0.5)
        glVertex3f(x + w/2, y - d/2, 0)
        glVertex3f(x + w/2, y + d/2, 0)
        glVertex3f(x + w/2, y + d/2, h)
        glVertex3f(x + w/2, y - d/2, h)
        
        # Roof
        glColor3f(0.3, 0.1, 0.1)
        glVertex3f(x - w/2, y - d/2, h)
        glVertex3f(x + w/2, y - d/2, h)
        glVertex3f(x + w/2, y + d/2, h)
        glVertex3f(x - w/2, y + d/2, h)
        
        glEnd()
        
        # Draw door on front
        glColor3f(0.4, 0.2, 0.1)
        door_width = 5
        door_height = 10
        glBegin(GL_QUADS)
        glVertex3f(x - door_width/2, y - d/2 - 0.1, 0)
        glVertex3f(x + door_width/2, y - d/2 - 0.1, 0)
        glVertex3f(x + door_width/2, y - d/2 - 0.1, door_height)
        glVertex3f(x - door_width/2, y - d/2 - 0.1, door_height)
        glEnd()
        
        # Draw windows
        glColor3f(0.1, 0.1, 0.2)
        window_size = 3
        for wx in range(int(-w/2 + 5), int(w/2 - 5), 8):
            for wh in range(5, int(h - 5), 8):
                glBegin(GL_QUADS)
                glVertex3f(x + wx, y - d/2 - 0.1, wh)
                glVertex3f(x + wx + window_size, y - d/2 - 0.1, wh)
                glVertex3f(x + wx + window_size, y - d/2 - 0.1, wh + window_size)
                glVertex3f(x + wx, y - d/2 - 0.1, wh + window_size)
                glEnd()

def draw_trees():
    """Draw trees using cylinders and spheres"""
    for tree in trees:
        x, y, height = tree["x"], tree["y"], tree["height"]
        
        # Tree trunk
        glColor3f(0.4, 0.2, 0.1)
        glPushMatrix()
        glTranslatef(x, y, 0)
        quadric = gluNewQuadric()
        gluCylinder(quadric, 1.5, 1, height * 0.7, 12, 12)
        glPopMatrix()
        
        # Tree foliage - multiple spheres for better shape
        glColor3f(0.1, 0.6, 0.1)
        glPushMatrix()
        glTranslatef(x, y, height * 0.6)
        glutSolidSphere(height * 0.3, 16, 16)
        glPopMatrix()
        glPushMatrix()
        glTranslatef(x, y, height * 0.8)
        glutSolidSphere(height * 0.25, 16, 16)
        glPopMatrix()
        glPushMatrix()
        glTranslatef(x, y, height)
        glutSolidSphere(height * 0.2, 16, 16)
        glPopMatrix()

def draw_player():
    """Draw player model with more details (only in third person)"""
    if first_person:
        return
        
    x, y, z = player.pos
    
    # Legs
    glColor3f(0.1, 0.1, 0.4)
    glPushMatrix()
    glTranslatef(x - 1, y, z - 4)
    glScalef(0.8, 0.8, 2)
    glutSolidCube(2)
    glPopMatrix()
    glPushMatrix()
    glTranslatef(x + 1, y, z - 4)
    glScalef(0.8, 0.8, 2)
    glutSolidCube(2)
    glPopMatrix()
    
    # Body
    glColor3f(0.2, 0.3, 0.8)
    glPushMatrix()
    glTranslatef(x, y, z - 1)
    glRotatef(player.angle - 90, 0, 0, 1)
    glScalef(1.5, 0.8, 2)
    glutSolidCube(2)
    glPopMatrix()
    
    # Arms
    glColor3f(0.9, 0.7, 0.6)
    glPushMatrix()
    glTranslatef(x, y, z - 1)
    glRotatef(player.angle - 90, 0, 0, 1)
    glTranslatef(2, 1, 0)
    glScalef(0.5, 0.5, 1.5)
    glutSolidCube(2)
    glPopMatrix()
    glPushMatrix()
    glTranslatef(x, y, z - 1)
    glRotatef(player.angle - 90, 0, 0, 1)
    glTranslatef(2, -1, 0)
    glScalef(0.5, 0.5, 1.5)
    glutSolidCube(2)
    glPopMatrix()
    
    # Head
    glColor3f(0.9, 0.7, 0.6)
    glPushMatrix()
    glTranslatef(x, y, z + 2)
    glutSolidSphere(1.2, 12, 12)
    glPopMatrix()
    
    # Weapon
    glColor3f(0.1, 0.1, 0.1)
    glPushMatrix()
    glTranslatef(x, y, z)
    glRotatef(player.angle - 90, 0, 0, 1)
    glTranslatef(3, 0, 0)
    glScalef(0.3, 0.3, 2)
    glutSolidCube(1)
    glPopMatrix()

def draw_enemies():
    """Draw enemy models with more details"""
    for enemy in enemies:
        if enemy.health <= 0:
            continue
            
        x, y, z = enemy.pos
        is_boss = isinstance(enemy, Boss)
        scale = 1.5 if is_boss else 1.0
        body_color = (0.8, 0.2, 0.2) if not is_boss else (0.5, 0.1, 0.1)
        arm_head_color = (0.7, 0.3, 0.3) if not is_boss else (0.4, 0.1, 0.1)
        
        glPushMatrix()
        glTranslatef(x, y, z)
        glScalef(scale, scale, scale)
        z = 0  # Reset z relative
        
        # Legs
        glColor3f(0.4, 0.1, 0.1)
        glPushMatrix()
        glTranslatef(-1, 0, -4)
        glScalef(0.7, 0.7, 2)
        glutSolidCube(2)
        glPopMatrix()
        glPushMatrix()
        glTranslatef(1, 0, -4)
        glScalef(0.7, 0.7, 2)
        glutSolidCube(2)
        glPopMatrix()
        
        # Body
        glColor3f(*body_color)
        glPushMatrix()
        glTranslatef(0, 0, -1)
        glRotatef(enemy.angle - 90, 0, 0, 1)
        glScalef(1.3, 0.7, 2)
        glutSolidCube(2)
        glPopMatrix()
        
        # Arms
        glColor3f(*arm_head_color)
        glPushMatrix()
        glTranslatef(0, 0, -1)
        glRotatef(enemy.angle - 90, 0, 0, 1)
        glTranslatef(1.5, 1, 0)
        glScalef(0.4, 0.4, 1.2)
        glutSolidCube(2)
        glPopMatrix()
        glPushMatrix()
        glTranslatef(0, 0, -1)
        glRotatef(enemy.angle - 90, 0, 0, 1)
        glTranslatef(1.5, -1, 0)
        glScalef(0.4, 0.4, 1.2)
        glutSolidCube(2)
        glPopMatrix()
        
        # Head
        glColor3f(*arm_head_color)
        glPushMatrix()
        glTranslatef(0, 0, 2)
        glutSolidSphere(1, 10, 10)
        glPopMatrix()
        
        # Weapon
        glColor3f(0.1, 0.1, 0.1)
        glPushMatrix()
        glTranslatef(0, 0, 0)
        glRotatef(enemy.angle - 90, 0, 0, 1)
        glTranslatef(2, 0, 0)
        glScalef(0.2, 0.2, 1.5)
        glutSolidCube(1)
        glPopMatrix()
        
        # Boss extra: horns
        if is_boss:
            glColor3f(0.3, 0.3, 0.3)
            glPushMatrix()
            glTranslatef(-0.8, 0, 3)
            glutSolidCone(0.5, 2, 8, 8)
            glPopMatrix()
            glPushMatrix()
            glTranslatef(0.8, 0, 3)
            glutSolidCone(0.5, 2, 8, 8)
            glPopMatrix()
        
        glPopMatrix()
        
        # Health bar above enemy
        bar_width = 12 if is_boss else 6
        health_ratio = enemy.health / enemy.max_health
        
        glDisable(GL_DEPTH_TEST)
        
        # Background bar
        glColor3f(0.5, 0.5, 0.5)
        glBegin(GL_QUADS)
        glVertex3f(x - bar_width/2, y, z + 5)
        glVertex3f(x + bar_width/2, y, z + 5)
        glVertex3f(x + bar_width/2, y, z + 5.5)
        glVertex3f(x - bar_width/2, y, z + 5.5)
        glEnd()
        
        # Health bar
        glColor3f(1 - health_ratio, health_ratio, 0)
        glBegin(GL_QUADS)
        glVertex3f(x - bar_width/2, y, z + 5)
        glVertex3f(x - bar_width/2 + bar_width * health_ratio, y, z + 5)
        glVertex3f(x - bar_width/2 + bar_width * health_ratio, y, z + 5.5)
        glVertex3f(x - bar_width/2, y, z + 5.5)
        glEnd()
        
        glEnable(GL_DEPTH_TEST)

def draw_bullets():
    """Draw bullets as small spheres with trails"""
    for bullet_list in [bullets, enemy_bullets]:
        for bullet in bullet_list:
            if not bullet.active:
                continue
            if bullet_list == enemy_bullets:
                glColor3f(1, 0.3, 0.3)  # Red enemy bullets
            else:
                glColor3f(1, 1, 0.2)  # Yellow player bullets
                
            glPushMatrix()
            glTranslatef(bullet.pos[0], bullet.pos[1], bullet.pos[2])
            glutSolidSphere(0.3, 6, 6)
            glPopMatrix()
            
            # Simple trail
            glColor4f(1, 1, 0.2, 0.5)
            glEnable(GL_BLEND)
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
            glBegin(GL_LINES)
            trail_dx = math.cos(math.radians(bullet.angle)) * 2
            trail_dy = math.sin(math.radians(bullet.angle)) * 2
            glVertex3f(bullet.pos[0], bullet.pos[1], bullet.pos[2])
            glVertex3f(bullet.pos[0] - trail_dx, bullet.pos[1] - trail_dy, bullet.pos[2])
            glEnd()
            glDisable(GL_BLEND)

def draw_pickups():
    """Draw spinning pickup items"""
    current_time = glutGet(GLUT_ELAPSED_TIME) * 0.01
    
    for pickup in pickups:
        x, y = pickup["x"], pickup["y"]
        pickup_type = pickup["type"]
        
        glPushMatrix()
        glTranslatef(x, y, 3 + math.sin(current_time * 2) * 0.5)
        glRotatef(current_time * 50, 0, 0, 1)
        
        if pickup_type == "health":
            glColor3f(0, 1, 0)  # Green
            glutSolidCube(2)
        elif pickup_type == "ammo":
            glColor3f(0, 0, 1)  # Blue
            glScalef(1.5, 0.5, 0.5)
            glutSolidCube(2)
        
        glPopMatrix()

def draw_muzzle_flash():
    """Draw muzzle flash effect"""
    current_time = glutGet(GLUT_ELAPSED_TIME)
    if current_time - player.last_shot < 100:  # Show for 100ms
        flash_x = player.pos[0] + math.cos(math.radians(player.angle)) * 3
        flash_y = player.pos[1] + math.sin(math.radians(player.angle)) * 3
        flash_z = player.pos[2] - 1
        
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glColor4f(1, 1, 0.5, 0.8)
        glPushMatrix()
        glTranslatef(flash_x, flash_y, flash_z)
        glutSolidSphere(1.5, 8, 8)
        glPopMatrix()
        glDisable(GL_BLEND)

def render_text(x, y, text, font=GLUT_BITMAP_HELVETICA_12):
    glRasterPos2f(x, y)
    for c in text:
        glutBitmapCharacter(font, ord(c))

def draw_hud():
    """Draw heads-up display"""
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, window_width, 0, window_height)
    
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    glDisable(GL_DEPTH_TEST)
    glDisable(GL_LIGHTING)
    
    # Health bar
    health_ratio = player.health / player.max_health
    glColor3f(1 - health_ratio, health_ratio, 0)
    glBegin(GL_QUADS)
    glVertex2f(50, 50)
    glVertex2f(50 + 200 * health_ratio, 50)
    glVertex2f(50 + 200 * health_ratio, 70)
    glVertex2f(50, 70)
    glEnd()
    
    # Health bar border
    glColor3f(1, 1, 1)
    glBegin(GL_LINE_LOOP)
    glVertex2f(50, 50)
    glVertex2f(250, 50)
    glVertex2f(250, 70)
    glVertex2f(50, 70)
    glEnd()
    
    # Stamina bar
    stamina_ratio = player.stamina / player.max_stamina
    glColor3f(0, 0.5 * stamina_ratio + 0.5, 1)
    glBegin(GL_QUADS)
    glVertex2f(50, 30)
    glVertex2f(50 + 200 * stamina_ratio, 30)
    glVertex2f(50 + 200 * stamina_ratio, 50)
    glVertex2f(50, 50)
    glEnd()
    
    # Stamina bar border
    glColor3f(1, 1, 1)
    glBegin(GL_LINE_LOOP)
    glVertex2f(50, 30)
    glVertex2f(250, 30)
    glVertex2f(250, 50)
    glVertex2f(50, 50)
    glEnd()
    
    # Crosshair (only in first person)
    if first_person:
        bob_offset = math.sin(player.crosshair_bob) * 2
        glColor3f(0, 1, 0)
        glLineWidth(2)
        glBegin(GL_LINES)
        # Horizontal line
        glVertex2f(window_width/2 - 10, window_height/2 + bob_offset)
        glVertex2f(window_width/2 + 10, window_height/2 + bob_offset)
        # Vertical line
        glVertex2f(window_width/2, window_height/2 - 10 + bob_offset)
        glVertex2f(window_width/2, window_height/2 + 10 + bob_offset)
        glEnd()
    
    # Weapon info
    glColor3f(1, 1, 1)
    weapon_text = f"Weapon: {player.weapon.upper()}"
    ammo_text = f"Ammo: {player.ammo[player.weapon]}" if not infinite_ammo else "Ammo: Infinite"
    score_text = f"Score: {score}"
    kills_text = f"Kills: {kills}"
    wave_text = f"Wave: {wave}"
    
    # Time indicator
    hour = int(time_of_day) % 24
    if 6 <= hour <= 18:
        time_text = f"Day {hour}:00"
    else:
        time_text = f"Night {hour}:00"
    
    render_text(50, 100, weapon_text)
    render_text(50, 80, ammo_text)
    render_text(window_width - 200, window_height - 50, score_text)
    render_text(window_width - 200, window_height - 70, kills_text)
    render_text(window_width - 200, window_height - 90, wave_text)
    render_text(window_width - 200, window_height - 110, time_text)
    
    if leveling_up:
        glColor3f(1, 1, 0)
        render_text(window_width / 2 - 100, window_height / 2 + 50, "Level Up!", GLUT_BITMAP_HELVETICA_18)
        render_text(window_width / 2 - 150, window_height / 2, "Press 1 for +50 Max Health")
        render_text(window_width / 2 - 150, window_height / 2 - 30, "Press 2 for +0.2 Speed")
    
    if paused:
        glColor3f(1, 1, 1)
        render_text(window_width / 2 - 50, window_height / 2 + 50, "Paused", GLUT_BITMAP_HELVETICA_18)
        render_text(window_width / 2 - 100, window_height / 2 + 20, "P: Resume")
        render_text(window_width / 2 - 100, window_height / 2 - 10, "R: Restart")
        render_text(window_width / 2 - 100, window_height / 2 - 40, "Q: Quit")
    
    if not game_running:
        glColor3f(1, 0, 0)
        render_text(window_width / 2 - 100, window_height / 2, "GAME OVER", GLUT_BITMAP_TIMES_ROMAN_24)
        glColor3f(1, 1, 1)
        render_text(window_width / 2 - 100, window_height / 2 - 50, f"Final Score: {score}", GLUT_BITMAP_HELVETICA_18)
    
    glEnable(GL_LIGHTING)
    glEnable(GL_DEPTH_TEST)
    
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def setup_lighting():
    """Configure OpenGL lighting"""
    clear_color = [0, 0, 0, 1]
    ambient = [0.5, 0.5, 0.5, 1.0]
    diffuse = [1.0, 1.0, 1.0, 1.0]
    
    if 6 <= time_of_day <= 18:
        # Daytime
        clear_color = [0.5, 0.7, 1.0, 1.0]  # Blue sky
        ambient = [0.5, 0.5, 0.5, 1.0]
    else:
        # Nighttime
        clear_color = [0.05, 0.05, 0.1, 1.0]  # Very dark
        if flashlight_on:
            ambient = [0.05, 0.05, 0.05, 1.0]  # Low ambient with flashlight
        else:
            ambient = [0.1, 0.1, 0.1, 1.0]  # Dim without flashlight
    
    glClearColor(*clear_color)
    glLightModelfv(GL_LIGHT_MODEL_AMBIENT, ambient)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, diffuse)
    glLightfv(GL_LIGHT0, GL_POSITION, [0, 0, 1, 0])  # Directional light
    
    # Fog for atmosphere
    glFogfv(GL_FOG_COLOR, clear_color)
    glFogf(GL_FOG_DENSITY, 0.001)
    glFogf(GL_FOG_START, 0)
    glFogf(GL_FOG_END, 400 if flashlight_on else 200)

def setup_flashlight():
    """Setup flashlight as a spotlight"""
    if not flashlight_on or 6 <= time_of_day <= 18:
        glDisable(GL_LIGHT1)
        return
    
    glEnable(GL_LIGHT1)
    spot_pos = [player.pos[0], player.pos[1], player.pos[2] - 1, 1.0]
    spot_dir = [math.cos(math.radians(player.angle)), math.sin(math.radians(player.angle)), 0.0]
    glLightfv(GL_LIGHT1, GL_POSITION, spot_pos)
    glLightfv(GL_LIGHT1, GL_SPOT_DIRECTION, spot_dir)
    glLightf(GL_LIGHT1, GL_SPOT_CUTOFF, 45.0)
    glLightf(GL_LIGHT1, GL_SPOT_EXPONENT, 4.0)
    glLightfv(GL_LIGHT1, GL_DIFFUSE, [0.8, 0.8, 0.8, 1.0])
    glLightfv(GL_LIGHT1, GL_SPECULAR, [0.8, 0.8, 0.8, 1.0])
    glLightf(GL_LIGHT1, GL_CONSTANT_ATTENUATION, 1.0)
    glLightf(GL_LIGHT1, GL_LINEAR_ATTENUATION, 0.01)
    glLightf(GL_LIGHT1, GL_QUADRATIC_ATTENUATION, 0.001)

def setup_camera():
    """Setup camera view"""
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(75, window_width / window_height, 0.1, 500)
    
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    
    setup_flashlight()
    
    eye_z = player.pos[2] + (1 if player.crouching else 2)
    if first_person:
        # First person camera
        look_x = player.pos[0] + math.cos(math.radians(player.angle)) * 10
        look_y = player.pos[1] + math.sin(math.radians(player.angle)) * 10
        gluLookAt(player.pos[0], player.pos[1], eye_z,
                  look_x, look_y, eye_z,
                  0, 0, 1)
    else:
        # Third person camera
        cam_distance = 25
        cam_height = 15
        cam_x = player.pos[0] - math.cos(math.radians(player.angle)) * cam_distance
        cam_y = player.pos[1] - math.sin(math.radians(player.angle)) * cam_distance
        cam_z = player.pos[2] + cam_height
        
        gluLookAt(cam_x, cam_y, cam_z,
                  player.pos[0], player.pos[1], player.pos[2] + 2,
                  0, 0, 1)

def update_game():
    """Main game update loop"""
    global time_of_day, score, kills, wave, game_time, game_running, leveling_up, difficulty_level
    
    if not game_running or leveling_up or paused:
        return
    
    current_time = glutGet(GLUT_ELAPSED_TIME)
    game_time = current_time
    
    # Update time of day
    time_of_day += day_cycle_speed
    if time_of_day >= 24:
        time_of_day = 0
    
    # Handle input
    move_forward = (1 if forward else 0) - (1 if backward else 0)
    move_strafe = (1 if strafe_left else 0) - (1 if strafe_right else 0)
    if not player.dodging:
        player.move(move_forward, move_strafe)
    
    turn_amount = (2 if turn_left else 0) - (2 if turn_right else 0)
    player.angle += turn_amount
    
    if shooting:
        player.shoot()
    
    # Stamina regeneration
    if player.stamina < player.max_stamina:
        player.stamina = min(player.max_stamina, player.stamina + player.stamina_regen)
    
    # Dodge logic
    if player.dodging:
        dx = math.cos(math.radians(player.dodge_direction)) * player.dodge_speed
        dy = math.sin(math.radians(player.dodge_direction)) * player.dodge_speed
        new_x = player.pos[0] + dx
        new_y = player.pos[1] + dy
        if not player.check_collision(new_x, new_y):
            player.pos[0] = new_x
            player.pos[1] = new_y
        player.dodge_timer -= 1
        if player.dodge_timer <= 0:
            player.dodging = False
    
    # Update bullets
    bullets[:] = [b for b in bullets if b.update()]
    enemy_bullets[:] = [b for b in enemy_bullets if b.update()]
    
    # Update enemies
    enemies[:] = [e for e in enemies if e.update()]
    
    # Check player bullet collisions with enemies
    for bullet in bullets[:]:
        for enemy in enemies:
            if enemy.health > 0:
                dx = bullet.pos[0] - enemy.pos[0]
                dy = bullet.pos[1] - enemy.pos[1]
                dz = bullet.pos[2] - enemy.pos[2]
                dist = math.sqrt(dx**2 + dy**2 + dz**2)
                if dist < 3:
                    died = enemy.take_damage(bullet.damage)
                    if died:
                        kills += 1
                        if isinstance(enemy, Boss):
                            score += 500
                            leveling_up = True
                            difficulty_level += 1
                        else:
                            score += 100
                        if random.random() < 0.5:
                            ptype = "health" if random.random() < 0.5 else "ammo"
                            spawn_pickup(enemy.pos[0], enemy.pos[1], ptype)
                        if kills % 10 == 0:
                            spawn_boss()
                    bullet.active = False
                    break
    
    # Check enemy bullet collisions with player
    for bullet in enemy_bullets[:]:
        dx = bullet.pos[0] - player.pos[0]
        dy = bullet.pos[1] - player.pos[1]
        dz = bullet.pos[2] - player.pos[2]
        dist = math.sqrt(dx**2 + dy**2 + dz**2)
        if dist < 4:
            if not god_mode and not player.dodging:
                player.health -= bullet.damage
                if player.health <= 0:
                    game_running = False
            bullet.active = False
    
    # Check pickups
    for pickup in pickups[:]:
        dx = pickup["x"] - player.pos[0]
        dy = pickup["y"] - player.pos[1]
        dist = math.sqrt(dx**2 + dy**2)
        if dist < 5:
            if pickup["type"] == "health":
                player.health = min(player.max_health, player.health + 50)
            elif pickup["type"] == "ammo":
                player.ammo["rifle"] += 30
                player.ammo["shotgun"] += 8
                player.ammo["sniper"] += 5
            pickups.remove(pickup)
    
    # Wave progression
    if len(enemies) == 0:
        wave += 1
        spawn_enemies()
    
    # Gravity and jump
    player.vel_z -= 0.05  # Gravity
    player.pos[2] += player.vel_z
    ground_level = 4 if player.crouching else 8
    if player.pos[2] <= ground_level:
        player.pos[2] = ground_level
        player.vel_z = 0
        player.on_ground = True
    
    # Dampen crosshair bob
    player.crosshair_bob *= 0.9

def reset_game():
    global score, kills, wave, enemies, bullets, enemy_bullets, pickups, game_running, time_of_day, difficulty_level, leveling_up, paused
    score = 0
    kills = 0
    wave = 1
    difficulty_level = 0
    player.pos = [0, 0, 8]
    player.angle = 0
    player.health = 100
    player.max_health = 100
    player.speed = 0.8
    player.stamina = 100
    player.ammo = {"rifle": 120, "shotgun": 24, "sniper": 15}
    player.vel_z = 0
    player.on_ground = True
    player.crouching = False
    player.dodging = False
    enemies = []
    bullets = []
    enemy_bullets = []
    pickups = []
    time_of_day = 12.0
    leveling_up = False
    paused = False
    generate_world()
    spawn_enemies()
    game_running = True

def display():
    setup_lighting()
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    setup_camera()
    draw_terrain()
    draw_buildings()
    draw_trees()
    draw_player()
    draw_enemies()
    draw_bullets()
    draw_pickups()
    draw_muzzle_flash()
    draw_hud()
    glutSwapBuffers()

def keyboard(key, x, y):
    global forward, backward, strafe_left, strafe_right, flashlight_on, first_person, god_mode, infinite_ammo, leveling_up, paused
    if leveling_up:
        if key == b'1':
            player.max_health += 50
            player.health = player.max_health
            leveling_up = False
        elif key == b'2':
            player.speed += 0.2
            leveling_up = False
        return
    if paused:
        if key == b'p' or key == b'P':
            paused = False
        elif key == b'r' or key == b'R':
            reset_game()
        elif key == b'q' or key == b'Q':
            glutLeaveMainLoop()
        return
    if key == b'w' or key == b'W':
        forward = True
    elif key == b's' or key == b'S':
        backward = True
    elif key == b'a' or key == b'A':
        strafe_left = True
    elif key == b'd' or key == b'D':
        strafe_right = True
    elif key == b' ':
        player.dodge()
    elif key == b'1':
        player.weapon = "rifle"
    elif key == b'2':
        player.weapon = "shotgun"
    elif key == b'3':
        player.weapon = "sniper"
    elif key == b'f' or key == b'F':
        flashlight_on = not flashlight_on
    elif key == b'c' or key == b'C':
        first_person = not first_person
    elif key == b'g' or key == b'G':
        god_mode = not god_mode
    elif key == b'i' or key == b'I':
        infinite_ammo = not infinite_ammo
    elif key == b'r' or key == b'R':
        reset_game()
    elif key == b'p' or key == b'P':
        paused = True

def keyboard_up(key, x, y):
    global forward, backward, strafe_left, strafe_right
    if key == b'w' or key == b'W':
        forward = False
    elif key == b's' or key == b'S':
        backward = False
    elif key == b'a' or key == b'A':
        strafe_left = False
    elif key == b'd' or key == b'D':
        strafe_right = False

def special(key, x, y):
    global turn_left, turn_right
    if key == GLUT_KEY_LEFT:
        turn_left = True
    elif key == GLUT_KEY_RIGHT:
        turn_right = True
    elif key == GLUT_KEY_UP:
        player.jump()
    elif key == GLUT_KEY_DOWN:
        player.crouching = True
        player.pos[2] = 4
        player.speed = 0.4

def special_up(key, x, y):
    global turn_left, turn_right
    if key == GLUT_KEY_LEFT:
        turn_left = False
    elif key == GLUT_KEY_RIGHT:
        turn_right = False
    elif key == GLUT_KEY_DOWN:
        player.crouching = False
        player.pos[2] = 8
        player.speed = 0.8

def mouse_click(button, state, x, y):
    global shooting
    if button == GLUT_LEFT_BUTTON:
        if state == GLUT_DOWN:
            shooting = True
        else:
            shooting = False

def mouse_motion(x, y):
    dx = x - window_width // 2
    player.angle -= dx * 0.2  # Inverted mouse control
    glutWarpPointer(window_width // 2, window_height // 2)

def timer(value):
    update_game()
    glutPostRedisplay()
    glutTimerFunc(16, timer, 0)

def init():
    global forward, backward, strafe_left, strafe_right, turn_left, turn_right, shooting, paused
    forward = backward = strafe_left = strafe_right = turn_left = turn_right = shooting = False
    paused = False
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_COLOR_MATERIAL)
    glEnable(GL_FOG)
    glFogi(GL_FOG_MODE, GL_EXP2)
    glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
    glutSetCursor(GLUT_CURSOR_NONE)
    random.seed(42)
    generate_world()
    spawn_enemies()

if __name__ == "__main__":
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(window_width, window_height)
    glutCreateWindow(b"Urban Warfare Shooter")
    init()
    glutDisplayFunc(display)
    glutKeyboardFunc(keyboard)
    glutKeyboardUpFunc(keyboard_up)
    glutSpecialFunc(special)
    glutSpecialUpFunc(special_up)
    glutMouseFunc(mouse_click)
    glutMotionFunc(mouse_motion)
    glutPassiveMotionFunc(mouse_motion)
    glutTimerFunc(0, timer, 0)
    glutMainLoop()