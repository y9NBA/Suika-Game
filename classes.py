import pygame as pg
import numpy as np
import pymunk as pm

from constants import *


shape_to_particle = dict()


class Particle:
    def __init__(self, pos, n, space, mapper):
        self.n = n % 11
        self.radius = RADII[self.n]
        self.body = pm.Body(body_type=pm.Body.DYNAMIC)
        self.body_position = tuple(pos)
        self.shape = pm.Circle(body=self.body, radius=self.radius)
        self.shape.density = DENSITY
        self.shape.elasticity = ELASTICITY
        self.shape.collision_type = 1
        self.shape.friction = 0.2
        self.has_collided = False
        mapper[self.shape] = self

        space.add(self.body, self.shape)
        self.alive = True

    def draw(self, display):
        if self.alive:
            c1 = np.array(COLORS[self.n])
            c2 = (c1 * 0.8).astype(int)
            pg.draw.circle(display, tuple(c2), self.body_position, self.radius)
            pg.draw.circle(display, tuple(c1), self.body_position, self.radius * 0.9)

    def kill(self, space):
        space.remove(self.body, self.shape)
        self.alive = False

    @property
    def pos(self):
        return np.array(self.body_position)


class PreParticle:
    def __init__(self, x, n):
        self.n = n % 11
        self.radius = RADII[self.n]
        self.x = x

    def draw(self, display):
        c1 = np.array(COLORS[self.n])
        c2 = (c1 * 0.8).astype(int)
        pg.draw.circle(display, tuple(c2), (self.x, PAD[1] // 2), self.radius)
        pg.draw.circle(display, tuple(c1), (self.x, PAD[1] // 2), self.radius * 0.9)

    def set_x(self, x):
        lim = PAD[0] + self.radius + THICKNESS // 2
        self.x = np.clip(x, lim, WIDTH - lim)

    def release(self, space, mapper):
        return Particle((self.x, PAD[1] // 2), self.n, space, mapper)


class Wall:
    thickness = THICKNESS

    def __init__(self, a, b, space):
        self.body = pm.Body(body_type=pm.Body.STATIC)
        self.shape = pm.Segment(self.body, a, b, self.thickness // 2)
        self.shape.friction = 10
        space.add(self.body, self.shape)

    def draw(self, display):
        pg.draw.line(display, W_COLOR, self.shape.a, self.shape.b, self.thickness)


def resolve_collision(p1: Particle, p2: Particle, space, particles, mapper):
    if p1.n == p2.n:
        distance = np.linalg.norm(p1.pos - p2.pos)
        if distance < 2 * p1.radius:
            p1.kill(space)
            p2.kill(space)
            pn = Particle(np.mean([p1.pos, p2.pos], axis=0), p1.n+1, space, mapper)
            for p in particles:
                if p.alive:
                    vector = p.pos - pn.pos
                    distance = np.linalg.norm(vector)
                    if distance < pn.radius + p.radius:
                        impulse = IMPULSE * vector / (distance ** 2)
                        p.body.apply_impulse_at_local_point(tuple(impulse))
            return pn
    return None