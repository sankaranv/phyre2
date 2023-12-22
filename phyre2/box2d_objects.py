from Box2D import b2PolygonShape, b2_pi
import math


# Function to create the basket
def create_basket(world, basket_args, name):
    # Unpack basket arguments
    x = basket_args.x
    y = basket_args.y
    scale = basket_args.scale

    # Adjust dimensions based on scale
    width = 1.083 * scale
    height = 1.67 * scale
    theta = 5 * b2_pi / 180
    thickness = 0.075 * scale
    angle_shift = math.cos(theta) * thickness

    # Create the basket body
    basket_body = world.CreateDynamicBody(
        position=(x, y),
        angle=0,
    )

    # Create the bottom rectangle
    bottom_box = basket_body.CreatePolygonFixture(
        box=(width / 2, thickness / 2),
        density=1,
        friction=0.5,
        restitution=0.5,
    )

    # Create the left side rectangle
    left_box = basket_body.CreatePolygonFixture(
        box=(thickness / 2, height / 2),
        density=1,
        friction=0.5,
        restitution=0.5,
    )
    left_box.shape.SetAsBox(
        thickness / 2,
        height / 2,
        (-width / 2 + thickness / 2 - angle_shift, height / 2 + thickness / 2),
        theta,
    )

    # Create the right side rectangle
    right_box = basket_body.CreatePolygonFixture(
        box=(thickness / 2, height / 2),
        density=1,
        friction=0.5,
        restitution=0.5,
    )
    right_box.shape.SetAsBox(
        thickness / 2,
        height / 2,
        (width / 2 - thickness / 2 + angle_shift, height / 2 + thickness / 2),
        -theta,
    )

    basket_body.userData = name
    return basket_body


# Create walls centered around the origin
def create_walls(world, wall_thickness, room_width, room_height):
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


def create_platform(world, platform_args, name):
    # Unpack platform arguments
    x = platform_args.x
    y = platform_args.y
    length = platform_args.length
    width = 0.084
    angle = platform_args.angle * b2_pi / 180

    platform = world.CreateStaticBody(
        position=(x, y),
        angle=angle,
    )

    platform.CreatePolygonFixture(
        box=(length, width),
        density=1,
        friction=0.5,
        restitution=0.5,
    )

    platform.userData = name
    return platform


def create_ball(world, ball_args, name):
    # Unpack ball arguments
    x = ball_args.x
    y = ball_args.y
    radius = ball_args.radius

    circle = world.CreateDynamicBody(
        position=(x, y),
        angle=0,
    )

    circle.CreateCircleFixture(
        radius=radius,
        density=1,
        friction=0.5,
        restitution=0.5,
    )

    circle.userData = name
    return circle