import pygame
import pygame.gfxdraw
import numpy as np
import time
from colorsysx import hsv_to_rgb

pygame.init()

# Set up the drawing window
W, H = 2000, 2000
screen = pygame.display.set_mode((H, W))
pygame.display.set_caption("Heart beat")

pygame.mixer.init()

# Load the music
pygame.mixer.music.load("heart-beat.mp3")

def draw_circle(screen, x, y, r, color):
    pygame.gfxdraw.filled_circle(screen, x, y, r, color)

def rand(a0, a1):
    return np.random.rand() * (a1 - a0) + a0

size_steps = 100
a = np.linspace(13, 13, size_steps)
b = np.linspace(-5, -3.3, size_steps)
c = np.linspace(-2, -2.4, size_steps)
d = np.linspace(-1, -0.16, size_steps)
scalex = np.linspace(1, 1.18, size_steps) * 10
scaley = np.linspace(1, 1.36, size_steps) * 10

class PersistentParticle():
    def __init__(self, t, size, color, off_s):
        self.t = t
        self.off_s = off_s
        self.size = size
        self.color = color

    def draw(self, screen: pygame.Surface, i):
        x, y = self.get_pos(i)
        draw_circle(screen, x, y, self.size, self.color)

    def get_pos(self, i):
        t = self.t

        x_pos = 16 * np.sin(t) ** 3
        x_pos *= (scalex[i] + self.off_s)

        y_pos = a[i] * np.cos(t) + b[i] * np.cos(2 * t) + c[i] * np.cos(3 * t) + d[i] * np.cos(4 * t)
        y_pos *= (scaley[i] + self.off_s)

        return int(x_pos + W / 2), int(-y_pos + H / 2)

class GlitterParticle():
    def __init__(self, t, size, color, off_x, off_y, off_s, phi):
        self.t = t
        self.off_x = off_x
        self.off_y = off_y
        self.off_s = off_s
        self.size = size
        self.color = color
        self.phi = phi

    def get_pos(self, i):
        t = self.t

        x_pos = 16 * np.sin(t) ** 3
        x_pos += self.off_x
        x_pos *= (scalex[i] + self.off_s)

        y_pos = a[i] * np.cos(t) + b[i] * np.cos(2 * t) + c[i] * np.cos(3 * t) + d[i] * np.cos(4 * t)
        y_pos += self.off_y
        y_pos *= (scaley[i] + self.off_s)

        return int(x_pos + W / 2), int(-y_pos + H / 2)

    def draw(self, screen: pygame.Surface, i):
        x, y = self.get_pos(i)
        alpha = int(128 * np.cos(self.phi + i / 5) + 127)
        color = (self.color[0], self.color[1], self.color[2], alpha)
        draw_circle(screen, x, y, self.size, color)

class LightParticle():
    def __init__(self, start_pos, end_pos, size, color):
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.size = size
        self.color = color
        self.current_pos = start_pos

    def update(self, progress):
        self.current_pos = (
            int(self.start_pos[0] + (self.end_pos[0] - self.start_pos[0]) * progress),
            int(self.start_pos[1] + (self.end_pos[1] - self.start_pos[1]) * progress)
        )

    def draw(self, screen: pygame.Surface):
        draw_circle(screen, self.current_pos[0], self.current_pos[1], self.size, self.color)

persistent_particles = []
glitter_particles = []
light_particles = []
heart_colors = []

# Create persistent particles
for repeat in range(1):
    for t in np.concatenate((np.linspace(0.18, 3.14 - 0.18, 1000), np.linspace(3.14 + 0.18, 2 * 3.1415 - 0.18, 1000)), axis=0):
        off_s = -np.random.exponential(1.8)
        size = int(rand(1.5, 2.5))

        red, green, blue = hsv_to_rgb(0.95, rand(0.2, 0.7), 1)
        alpha = np.random.rand() * 255
        color = (int(red * 255), int(green * 255), int(blue * 255), int(alpha))

        particle = PersistentParticle(t, size, color, off_s)
        persistent_particles.append(particle)
        heart_colors.append(color)

# Create glitter particles
for repeat in range(1):
    for t in np.concatenate((np.linspace(0.2, 3.14 - 0.2, 1000), np.linspace(3.14 + 0.2, 2 * 3.1415 - 0.2, 1000)), axis=0):
        off_x = np.random.randn() * 2
        off_y = np.random.randn() * 2
        off_s = np.random.randn() * 1.5 - 1.8
        size = int(rand(1.5, 2.5))

        red, green, blue = hsv_to_rgb(0.95, rand(0.5, 0.8), 1)
        color = (int(red * 255), int(green * 255), int(blue * 255))

        phi = rand(0, 2 * 3.14)

        particle = GlitterParticle(t, size, color, off_x, off_y, off_s, phi)
        glitter_particles.append(particle)
        heart_colors.append((int(red * 255), int(green * 255), int(blue * 255), 255))  # Ensure alpha is 255 for glitter particles

# Create light particles
for _ in range(500):
    start_pos = (np.random.randint(0, W), np.random.randint(0, H))
    end_pos = (W // 2, H // 2)
    size = int(rand(1, 3))

    color = heart_colors[np.random.randint(len(heart_colors))]

    particle = LightParticle(start_pos, end_pos, size, color)
    light_particles.append(particle)


bloom_indices = np.linspace(0, size_steps - 1, 28)
shrink_indices = np.linspace(size_steps - 1, 0, 20)
indices = np.concatenate((bloom_indices, shrink_indices), axis=0)
indices = np.uint8(indices)

frame = 0

# Initial delay of 3 seconds
time.sleep(3)
pygame.mixer.music.play(-1)
# Light particles effect for 0.5 seconds
start_time = pygame.time.get_ticks()
light_effect_duration = 500  # milliseconds

while pygame.time.get_ticks() - start_time < light_effect_duration:
    screen.fill((0, 0, 0))
    progress = (pygame.time.get_ticks() - start_time) / light_effect_duration
    for p in light_particles:
        p.update(progress)
        p.draw(screen)

    pygame.display.flip()



# Run until the user asks to quit
running = True
while running:
    # Did the user click the window close button?
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Fill the background with black
    screen.fill((0, 0, 0))

    # Draw
    index = indices[frame % len(indices)]
    for p in persistent_particles:
        p.draw(screen, index)

    for p in glitter_particles:
        p.draw(screen, size_steps - 1 - index)

    frame += 1

    # Flip the display
    pygame.display.flip()

# Done! Time to quit.
pygame.quit()