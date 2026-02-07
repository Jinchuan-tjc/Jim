import math
import sys

import pygame


WIDTH = 900
HEIGHT = 600
FPS = 60
GROUND_Y = HEIGHT - 80
MAX_FUEL = 120.0
MAX_TILT_DEG = 65
SAFE_LANDING_SPEED = 120.0
FUEL_PICKUP_AMOUNT = 35.0


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
        self.crashed = False
        self.angle = -90.0

    def update(self, dt, thrusting, rotate_left, rotate_right, wind):
        if self.landed or self.crashed:
            return

        if not self.launched and thrusting:
            self.launched = True

        if rotate_left:
            self.angle -= 110.0 * dt
        if rotate_right:
            self.angle += 110.0 * dt

        self.angle = max(-90.0 - MAX_TILT_DEG, min(-90.0 + MAX_TILT_DEG, self.angle))

        thrust = 0.0
        if thrusting and self.fuel > 0:
            thrust = 280.0
            self.fuel = max(0.0, self.fuel - 36.0 * dt)

        gravity = 220.0
        angle_rad = math.radians(self.angle)
        ax = math.cos(angle_rad) * thrust + wind
        ay = math.sin(angle_rad) * thrust + gravity

        self.vx += ax * dt
        self.vy += ay * dt
        self.x += self.vx * dt
        self.y += self.vy * dt

        if self.x < 20:
            self.x = 20
            self.vx = 0.0
        if self.x > WIDTH - 20:
            self.x = WIDTH - 20
            self.vx = 0.0

        if self.y >= GROUND_Y:
            self.y = GROUND_Y
            if self.launched:
                speed = math.hypot(self.vx, self.vy)
                if speed <= SAFE_LANDING_SPEED:
                    self.landed = True
                else:
                    self.crashed = True
            self.vx = 0.0
            self.vy = 0.0


class FuelPickup:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 12
        self.collected = False

    def collides_with(self, rocket):
        if self.collected:
            return False
        distance = math.hypot(self.x - rocket.x, self.y - (rocket.y - 30))
        return distance <= self.radius + 18


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
        self.message = "Hold UP to thrust, LEFT/RIGHT to steer!"
        self.landing_pad = pygame.Rect(WIDTH * 0.68, GROUND_Y - 10, 160, 12)
        self.pickups = []
        self.score = 0
        self.wind = 0.0
        self.spawn_pickups()

    def spawn_pickups(self):
        self.pickups = [
            FuelPickup(WIDTH * 0.45, GROUND_Y - 220),
            FuelPickup(WIDTH * 0.6, GROUND_Y - 320),
            FuelPickup(WIDTH * 0.75, GROUND_Y - 180),
        ]

    def run(self):
        running = True
        while running:
            dt = self.clock.tick(FPS) / 1000.0
            thrusting = False
            rotate_left = False
            rotate_right = False

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                    self.reset_run()

            keys = pygame.key.get_pressed()
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                thrusting = True
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                rotate_left = True
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                rotate_right = True

            self.wind = math.sin(pygame.time.get_ticks() * 0.0009) * 45.0
            self.rocket.update(dt, thrusting, rotate_left, rotate_right, self.wind)
            altitude = max(0.0, (GROUND_Y - self.rocket.y))
            self.best_altitude = max(self.best_altitude, altitude)

            for pickup in self.pickups:
                if pickup.collides_with(self.rocket):
                    pickup.collected = True
                    self.rocket.fuel = min(MAX_FUEL, self.rocket.fuel + FUEL_PICKUP_AMOUNT)
                    self.score += 50

            if self.rocket.landed:
                on_pad = self.landing_pad.collidepoint(self.rocket.x, GROUND_Y - 5)
                if on_pad:
                    self.score += 200
                    self.message = "Perfect landing! Press R to launch again."
                else:
                    self.message = "Landed safely! Aim for the pad next time."
            if self.rocket.crashed:
                self.message = "Crash! Slow down before landing. Press R to retry."

            self.draw(altitude)

        pygame.quit()
        sys.exit()

    def reset_run(self):
        self.rocket.reset()
        self.message = "Hold UP to thrust, LEFT/RIGHT to steer!"
        self.score = 0
        self.spawn_pickups()

    def draw(self, altitude):
        self.screen.fill((12, 18, 35))
        pygame.draw.rect(self.screen, (40, 120, 70), (0, GROUND_Y, WIDTH, HEIGHT - GROUND_Y))
        pygame.draw.rect(self.screen, (200, 180, 60), self.landing_pad)

        # Rocket body
        rocket_rect = pygame.Rect(0, 0, 30, 60)
        rocket_rect.center = (self.rocket.x, self.rocket.y - 30)
        rocket_surface = pygame.Surface((60, 80), pygame.SRCALPHA)
        body_rect = pygame.Rect(15, 10, 30, 60)
        pygame.draw.rect(rocket_surface, (220, 220, 240), body_rect, border_radius=6)
        pygame.draw.polygon(
            rocket_surface,
            (255, 120, 90),
            [
                (30, 0),
                (15, 18),
                (45, 18),
            ],
        )
        pygame.draw.rect(rocket_surface, (90, 140, 255), (23, 28, 14, 18))

        rotated = pygame.transform.rotate(rocket_surface, -self.rocket.angle - 90)
        rotated_rect = rotated.get_rect(center=rocket_rect.center)
        self.screen.blit(rotated, rotated_rect)

        if (
            self.rocket.launched
            and not self.rocket.landed
            and not self.rocket.crashed
            and self.rocket.fuel > 0
        ):
            flame_height = 20 + 10 * math.sin(pygame.time.get_ticks() * 0.02)
            flame = pygame.Surface((40, 40), pygame.SRCALPHA)
            pygame.draw.polygon(
                flame,
                (255, 170, 20),
                [(20, 40), (10, 10), (30, 10)],
            )
            flame = pygame.transform.rotate(flame, -self.rocket.angle - 90)
            flame_rect = flame.get_rect(center=(rocket_rect.centerx, rocket_rect.bottom + 10))
            self.screen.blit(flame, flame_rect)

        for pickup in self.pickups:
            if not pickup.collected:
                pygame.draw.circle(self.screen, (80, 220, 140), (int(pickup.x), int(pickup.y)), pickup.radius)
                pygame.draw.circle(self.screen, (20, 60, 40), (int(pickup.x), int(pickup.y)), pickup.radius, 2)

        info_text = self.font.render(f"Altitude: {altitude:0.0f} m", True, (230, 230, 230))
        fuel_text = self.font.render(f"Fuel: {self.rocket.fuel:0.0f}%", True, (230, 230, 230))
        best_text = self.font.render(f"Best: {self.best_altitude:0.0f} m", True, (230, 230, 230))
        score_text = self.font.render(f"Score: {self.score}", True, (230, 230, 230))
        wind_text = self.font.render(f"Wind: {self.wind:+.0f}", True, (230, 230, 230))
        self.screen.blit(info_text, (20, 20))
        self.screen.blit(fuel_text, (20, 50))
        self.screen.blit(best_text, (20, 80))
        self.screen.blit(score_text, (20, 110))
        self.screen.blit(wind_text, (20, 140))

        msg_surface = self.large_font.render(self.message, True, (255, 255, 255))
        msg_rect = msg_surface.get_rect(center=(WIDTH / 2, 40))
        self.screen.blit(msg_surface, msg_rect)

        pygame.display.flip()


if __name__ == "__main__":
    Game().run()
