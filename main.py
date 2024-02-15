import sys

import pygame as pg
import numpy as np
import pymunk as pm

from classes import *
from constants import *


pg.init()
rng = np.random.default_rng()

display = pg.display.set_mode((WIDTH, HEIGHT))
pg.display.set_caption("Suika-Galaxy")
clock = pg.time.Clock()
pg.font.init()
score_font = pg.font.SysFont("Arial", 32)
over_font = pg.font.SysFont("Arial", 72)

space = pm.Space()
space.gravity = (0, GRAVITY)
space.damping = DAMPING
space.collision_bias = BIAS


pad = 20
left = Wall(A, B, space)
bottom = Wall(B, C, space)
right = Wall(C, D, space)
walls = [left, bottom, right]

particles = []

handler = space.add_collision_handler(1, 1)


def collide(arbiter, space, data):
    sh1, sh2 = arbiter.shapes
    _mapper = data["mapper"]
    pa1, pa2 = _mapper[sh1], _mapper[sh2]
    cond = bool(pa1.n != pa2.n)
    pa1.has_collided, pa2.has_collided = cond, cond
    if not cond:
        pn = resolve_collision(pa1, pa2, space, data["particles"], _mapper)
        data["particles"].append(pn)
        data["score"] += POINTS[pa1.n]
    return cond


handler.begin = collide
handler.data["mapper"] = shape_to_particle
handler.data["particles"] = particles
handler.data["score"] = 0


def loop():

    wait_for_next = 0
    next_particle = PreParticle(WIDTH // 2, rng.integers(0, 5))
    game_over = False

    while not game_over:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            elif event.type == pg.KEYDOWN:
                if event.key in [pg.K_RETURN, pg.K_SPACE]:
                    particles.append(next_particle.release(space, shape_to_particle))
                    wait_for_next = NEXT_DELAY
                elif event.key in [pg.K_q, pg.K_ESCAPE]:
                    pg.quit()
                    sys.exit()
            elif event.type == pg.MOUSEBUTTONDOWN and wait_for_next == 0:
                particles.append(next_particle.release(space, shape_to_particle))
                wait_for_next = NEXT_DELAY

        next_particle.set_x(pg.mouse.get_pos()[0])

        if wait_for_next > 1:
            wait_for_next -= 1
        elif wait_for_next == 1:
            next_particle = PreParticle(next_particle.x, rng.integers(0, 5))
            wait_for_next -= 1

        display.fill(BG_COLOR)
        if wait_for_next == 0:
            next_particle.draw(display)
        for w in walls:
            w.draw(display)
        for p in particles:
            p.draw(display)
            if p.pos[1] < PAD[1] and p.has_collided:
                label = over_font.render("Game Over!", 1, (0, 0, 0))
                display.blit(label, PAD)
                game_over = True
        label = score_font.render(f"Score: {handler.data['score']}", 1, (0, 0, 0))
        display.blit(label, (10, 10))

        space.step(1 / FPS)
        pg.display.update()
        clock.tick(FPS)

    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            elif event.type == pg.KEYDOWN:
                if event.key in [pg.K_RETURN, pg.K_SPACE, pg.K_q, pg.K_ESCAPE]:
                    pg.quit()
                    sys.exit()


if __name__ == '__main__':
    loop()
