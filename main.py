import math
import sys

import pygame


WIDTH = 900
HEIGHT = 600
FPS = 60
GROUND_Y = HEIGHT - 80
MAX_FUEL = 100.0


class Rocket:
    def __init__(self):
        self.reset()

    def reset(self):
        self.x = WIDTH * 0.2
        self.y = GROUND_Y
        self.vx = 0.0
        self.vy = 0.0
        self.fuel = MAX_FUEL
        self.launched = False
        self.landed = False

    def update(self, dt, thrusting):
        if self.landed:
            return

        if not self.launched and thrusting:
            self.launched = True

        thrust = 0.0
        if thrusting and self.fuel > 0:
            thrust = 240.0
            self.fuel = max(0.0, self.fuel - 30.0 * dt)

        gravity = 220.0
        angle = -math.pi / 2
        ax = math.cos(angle) * thrust
        ay = math.sin(angle) * thrust + gravity

        self.vx += ax * dt
        self.vy += ay * dt
        self.x += self.vx * dt
        self.y += self.vy * dt

        if self.y >= GROUND_Y:
            self.y = GROUND_Y
            self.vx = 0.0
            self.vy = 0.0
            if self.launched:
                self.landed = True


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Rocket Launch Mini-Game")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Segoe UI", 22)
        self.large_font = pygame.font.SysFont("Segoe UI", 36)
        self.rocket = Rocket()
        self.best_altitude = 0.0
        self.message = "Hold SPACE to ignite, release to coast!"

    def run(self):
        running = True
        while running:
            dt = self.clock.tick(FPS) / 1000.0
            thrusting = False

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                    self.rocket.reset()
                    self.message = "Hold SPACE to ignite, release to coast!"

            keys = pygame.key.get_pressed()
            if keys[pygame.K_SPACE]:
                thrusting = True

            self.rocket.update(dt, thrusting)
            altitude = max(0.0, (GROUND_Y - self.rocket.y))
            self.best_altitude = max(self.best_altitude, altitude)

            if self.rocket.landed:
                self.message = "Landed! Press R to launch again."

            self.draw(altitude)

        pygame.quit()
        sys.exit()

    def draw(self, altitude):
        self.screen.fill((12, 18, 35))
        pygame.draw.rect(self.screen, (40, 120, 70), (0, GROUND_Y, WIDTH, HEIGHT - GROUND_Y))

        # Rocket body
        rocket_rect = pygame.Rect(0, 0, 30, 60)
        rocket_rect.center = (self.rocket.x, self.rocket.y - 30)
        pygame.draw.rect(self.screen, (220, 220, 240), rocket_rect, border_radius=6)
        pygame.draw.polygon(
            self.screen,
            (255, 120, 90),
            [
                (rocket_rect.centerx, rocket_rect.top - 18),
                (rocket_rect.left, rocket_rect.top + 5),
                (rocket_rect.right, rocket_rect.top + 5),
            ],
        )
        pygame.draw.rect(self.screen, (90, 140, 255), (rocket_rect.left + 8, rocket_rect.top + 18, 14, 18))

        if self.rocket.launched and not self.rocket.landed and self.rocket.fuel > 0:
            flame_height = 20 + 10 * math.sin(pygame.time.get_ticks() * 0.02)
            pygame.draw.polygon(
                self.screen,
                (255, 170, 20),
                [
                    (rocket_rect.centerx, rocket_rect.bottom + flame_height),
                    (rocket_rect.left + 4, rocket_rect.bottom),
                    (rocket_rect.right - 4, rocket_rect.bottom),
                ],
            )

        info_text = self.font.render(f"Altitude: {altitude:0.0f} m", True, (230, 230, 230))
        fuel_text = self.font.render(f"Fuel: {self.rocket.fuel:0.0f}%", True, (230, 230, 230))
        best_text = self.font.render(f"Best: {self.best_altitude:0.0f} m", True, (230, 230, 230))
        self.screen.blit(info_text, (20, 20))
        self.screen.blit(fuel_text, (20, 50))
        self.screen.blit(best_text, (20, 80))

        msg_surface = self.large_font.render(self.message, True, (255, 255, 255))
        msg_rect = msg_surface.get_rect(center=(WIDTH / 2, 40))
        self.screen.blit(msg_surface, msg_rect)

        pygame.display.flip()


if __name__ == "__main__":
    Game().run()
