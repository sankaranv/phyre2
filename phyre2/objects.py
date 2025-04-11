from dataclasses import dataclass
from typing import Tuple
from Box2D import b2PolygonShape, b2World, b2_pi
import math


@dataclass
class PhyreObject:
    x: float
    y: float
    angle: float = 0.0  # in degrees
    color: str = "black"
    dynamic: bool = True
    restitution: float = 0.5
    friction: float = 0.5


@dataclass
class Ball(PhyreObject):
    radius: float = 0.5


@dataclass
class Platform(PhyreObject):
    length: float = 2.0
    thickness: float = 0.2


@dataclass
class Basket(PhyreObject):
    scale: float = 1.0


def create_basket(world: b2World, basket: Basket, name: str):

    angle_rad = basket.angle * b2_pi / 180
    width = 1.083 * basket.scale
    height = 1.67 * basket.scale
    theta = 5 * b2_pi / 180
    # Use square root scaling for more natural thickness progression
    base_thickness = 0.05
    thickness = base_thickness + 0.1 * math.sqrt(basket.scale)
    angle_shift = math.cos(theta) * thickness

    body = (
        world.CreateDynamicBody(
            position=(basket.x, basket.y), angle=angle_rad, bullet=True
        )
        if basket.dynamic
        else world.CreateStaticBody(position=(basket.x, basket.y), angle=0, bullet=True)
    )

    # Bottom fixture - positioned at the base of the basket
    body.CreatePolygonFixture(
        box=(width / 2, thickness / 2),
        density=1,
        friction=basket.friction,
        restitution=basket.restitution,
    ).shape.SetAsBox(width / 2, thickness / 2, (0, 0), 0)

    # Left side fixture - properly aligned with bottom
    body.CreatePolygonFixture(
        box=(thickness / 2, height / 2),
        density=1,
        friction=basket.friction,
        restitution=basket.restitution,
    ).shape.SetAsBox(
        thickness / 2,
        height / 2 + thickness / 2,
        (-width / 2 + thickness / 2 - angle_shift, height / 2),
        theta,
    )

    # Right side fixture - properly aligned with bottom
    body.CreatePolygonFixture(
        box=(thickness / 2, height / 2),
        density=1,
        friction=basket.friction,
        restitution=basket.restitution,
    ).shape.SetAsBox(
        thickness / 2,
        height / 2 + thickness / 2,
        (width / 2 - thickness / 2 + angle_shift, height / 2),
        -theta,
    )

    # Add a sensor fixture at the bottom to detect when balls are inside
    # This fixture is invisible and not rendered
    body.CreatePolygonFixture(
        box=(width / 2 - thickness / 2, height / 2 - thickness / 2),
        density=0,
        friction=0,
        restitution=0,
        isSensor=True,
    ).shape.SetAsBox(
        width / 2 - thickness / 2, height / 2 - thickness / 2, (0, height / 2), 0
    )

    body.userData = name
    return body


def create_walls(
    world: b2World, wall_thickness: float, room_width: float, room_height: float
):

    left_wall = world.CreateStaticBody(
        position=(-room_width / 2 + wall_thickness / 2, 0),
        shapes=b2PolygonShape(box=(wall_thickness, room_height)),
    )
    right_wall = world.CreateStaticBody(
        position=(room_width / 2 - wall_thickness / 2, 0),
        shapes=b2PolygonShape(box=(wall_thickness, room_height)),
    )
    top_wall = world.CreateStaticBody(
        position=(0, room_height / 2 - wall_thickness / 2),
        shapes=b2PolygonShape(box=(room_width, wall_thickness)),
    )
    bottom_wall = world.CreateStaticBody(
        position=(0, -room_height / 2 + wall_thickness / 2),
        shapes=b2PolygonShape(box=(room_width, wall_thickness)),
    )

    left_wall.userData = "left_wall"
    right_wall.userData = "right_wall"
    top_wall.userData = "top_wall"
    bottom_wall.userData = "bottom_wall"
    return left_wall, right_wall, top_wall, bottom_wall


def create_ball(world: b2World, ball: Ball, name: str):

    body = (
        world.CreateDynamicBody(
            position=(ball.x, ball.y),
            angle=0,
            fixedRotation=False,
            bullet=True,
        )
        if ball.dynamic
        else world.CreateStaticBody(
            position=(ball.x, ball.y), angle=0, fixedRotation=False, bullet=True
        )
    )
    body.CreateCircleFixture(
        radius=ball.radius,
        density=1,
        friction=ball.friction,
        restitution=ball.restitution,
    )
    body.userData = name
    return body


def create_platform(world: b2World, platform: Platform, name: str):

    angle = platform.angle * b2_pi / 180
    body = (
        world.CreateDynamicBody(
            position=(platform.x, platform.y),
            angle=angle,
            bullet=True,
        )
        if platform.dynamic
        else world.CreateStaticBody(
            position=(platform.x, platform.y), angle=angle, bullet=True
        )
    )
    body.CreatePolygonFixture(
        box=(platform.length / 2, platform.thickness / 2),
        density=1,
        friction=platform.friction,
        restitution=platform.restitution,
    )
    body.userData = name
    return body
