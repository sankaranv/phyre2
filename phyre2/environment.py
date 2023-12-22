from phyre2.box2d_objects import *
import os
from phyre2.utils import Ball, Basket, Platform, detect_success
import json
import gymnasium as gym
from Box2D import b2World, b2Vec2
import numpy as np
import pygame
from phyre2.rendering import render_scene


class Level:
    def __init__(self, ppm):
        self.ppm = ppm
        self.objects = {}
        self.bodies = {}
        self.target = None
        self.actions = []
        self.name = "EmptyLevel"

    def load(self, level_name, level_dir="levels"):
        """
        Load a level from a JSON file and create the appropriate Box2D bodies
        :param level_name:
        :param level_dir:
        :return:
        """
        with open(f"{level_dir}/{level_name}.json", "r") as f:
            level = json.load(f)

        self.objects = {}
        for name, obj in level["objects"].items():
            if name == "basket":
                self.objects[name] = Basket(obj["x"], obj["y"], obj["scale"])
            elif "ball" in name:
                self.objects[name] = Ball(
                    obj["x"], obj["y"], obj["radius"], obj["color"]
                )
            elif "platform" in name:
                self.objects[name] = Platform(
                    obj["x"], obj["y"], obj["length"], obj["angle"], obj["color"]
                )
            else:
                raise Exception(f"Object {obj} is not a valid type")
        self.target = level["target"]
        self.actions = level["actions"]
        self.name = level_name

    def save(self, level_name, level_dir="levels"):
        """
        Save the current level to a JSON file
        :param level_name:
        :param level_dir:
        :return:
        """
        level = {"objects": {}, "target": self.target, "actions": self.actions}
        for name, obj in self.objects.items():
            if isinstance(obj, Basket):
                level["objects"][name] = {
                    "x": obj.x,
                    "y": obj.y,
                    "scale": obj.scale,
                }
            elif isinstance(obj, Ball):
                level["objects"][name] = {
                    "x": obj.x,
                    "y": obj.y,
                    "radius": obj.radius,
                    "color": obj.color,
                }
            elif isinstance(obj, Platform):
                level["objects"][name] = {
                    "x": obj.x,
                    "y": obj.y,
                    "length": obj.length,
                    "angle": obj.angle,
                    "color": obj.color,
                }
            else:
                raise Exception(f"Object {obj} is not a valid type")
        if not os.path.exists(level_dir):
            os.makedirs(level_dir)
        with open(f"{level_dir}/{level_name}.json", "w") as f:
            json.dump(level, f, indent=4)

    def load_default_level(self):
        self.objects = {
            "basket": Basket(0, -5, 1),
            "green_ball": Ball(2.67, -1.25, 0.17, "green"),
            "blue_ball": Ball(0, 4.17, 0.417, "blue"),
            "red_ball": Ball(3.34, 2.5, 0.67, "red"),
            "platform_1": Platform(-4.29, -3.25, 2.5, -45),
            "platform_2": Platform(4.458, -2.915, 2.5, -45),
            "platform_3": Platform(-2.416, 2.083, 1.33, 0),
        }
        self.target = "green_ball"
        self.actions = ["red_ball"]
        self.name = "DefaultLevel"

    def is_valid_level(self):
        # TODO: Check for overlapping objects
        if not self.objects:
            print("No objects found in level")
            return False
        elif not self.target:
            print("No target found in level")
            return False
        elif not self.actions:
            print("No action found in level")
            return False
        elif "basket" not in self.objects:
            print("Basket not found in level")
            return False
        elif self.target not in self.objects:
            print(f"Target {self.target} not found in level")
            return False
        else:
            for action in self.actions:
                if action not in self.objects:
                    print(f"Action {action} not found in level")
                    return False

        return True

    def make_level(self, world, screen_width, screen_height):
        self.bodies = {}
        # Create walls on the edges of the screen
        left_wall, right_wall, top_wall, bottom_wall = create_walls(
            world, 0.01, screen_width / self.ppm, screen_height / self.ppm
        )
        self.bodies["left_wall"] = left_wall
        self.bodies["right_wall"] = right_wall
        self.bodies["top_wall"] = top_wall
        self.bodies["bottom_wall"] = bottom_wall

        # Check for each dataclass type and create the appropriate Box2D body
        for name, obj in self.objects.items():
            if isinstance(obj, Basket):
                self.bodies[name] = create_basket(world, obj, name)
            elif isinstance(obj, Ball):
                self.bodies[name] = create_ball(world, obj, name)
            elif isinstance(obj, Platform):
                self.bodies[name] = create_platform(world, obj, name)
            else:
                raise Exception(f"Object {obj} is not a valid type")

    def null_object(self, world, obj_name):
        """
        Null out the object with the given name
        :param world:
        :param obj_name:
        """
        # Make sure the object exists
        if obj_name not in self.objects:
            raise Exception(f"Object {obj_name} not found in level")
        # Make sure not to null the basket or target
        if obj_name == "basket":
            raise Exception(f"Cannot null the basket")
        elif obj_name == self.target:
            raise Exception(f"Cannot null the target object")
        elif obj_name in self.actions:
            raise Exception(f"Cannot null an action object")
        else:
            # Remove the object from the world
            for body in world.bodies:
                if body.userData == obj_name:
                    world.DestroyBody(body)
            # Remove the object from the level
            del self.objects[obj_name]

    def add_object(self, world, obj, name, is_action=False):
        """
        Add an object to the level
        :param world:
        :param obj:
        :param name:
        :param is_action:
        :return:
        """

        # Make sure the object doesn't already exist
        if obj.name in self.objects:
            raise Exception(f"Object {obj.name} already exists in level")
        # Make sure the object is not the basket or target
        if obj.name == "basket":
            raise Exception(f"Cannot add the basket")
        elif obj.name == self.target:
            raise Exception(f"Cannot add the target object")
        else:
            # Add the object to the world
            if isinstance(obj, Basket):
                create_basket(world, obj, name)
            elif isinstance(obj, Ball):
                create_ball(world, obj, name)
            elif isinstance(obj, Platform):
                create_platform(world, obj, name)
            else:
                raise Exception(f"Object {obj} is not a valid type")
            # Add the object to the level
            self.objects[name] = obj
            if is_action:
                self.actions.append(name)


class PhyreEnv(gym.Env):
    def __init__(
        self,
        level,
        screen_size=600,
        ppm=60,
        max_steps=1000,
        fps=60,
        vel_iters=6,
        pos_iters=2,
        render_level=True,
    ):
        super().__init__()

        # Set up world
        self.level = level
        self.world = b2World(gravity=(0, -10), doSleep=True)
        self.screen_size = screen_size
        self.max_steps = max_steps
        self.fps = fps
        self.vel_iters = vel_iters
        self.pos_iters = pos_iters
        self.render_level = render_level

        if self.render_level:
            # Pygame setup
            pygame.init()
            self.screen = pygame.display.set_mode((screen_size, screen_size))
            pygame.display.set_caption(f"PHYRE: {self.level.name}")

        # Set up observation space
        self.observation_space = gym.spaces.Box(
            low=np.array([-screen_size / ppm * 0.5, -screen_size / ppm * 0.5]),
            high=np.array([screen_size / ppm * 0.5, screen_size / ppm * 0.5]),
            dtype=np.float32,
        )

        # The number of actions to take is specified in the level
        num_actions = len(self.level.actions)
        action_space_low = np.tile(
            np.array([-screen_size / ppm * 0.5, -screen_size / ppm * 0.5]),
            (num_actions, 1),
        )
        action_space_high = np.tile(
            np.array([screen_size / ppm * 0.5, screen_size / ppm * 0.5]),
            (num_actions, 1),
        )

        # If there is only one action, then the action space should be just 2D
        if num_actions == 1:
            action_space_low = action_space_low.flatten()
            action_space_high = action_space_high.flatten()

        self.action_space = gym.spaces.Box(
            low=action_space_low,
            high=action_space_high,
            dtype=np.float32,
        )

        self.reset()

    def reset(self):
        # Reset the world
        self.world.ClearForces()
        for body in self.world.bodies:
            self.world.DestroyBody(body)

        # Reset the level
        self.level.make_level(self.world, self.screen_size, self.screen_size)

    def _get_observation(self):
        # TODO - add state information for all objects including collision detections
        return self.level.bodies[self.level.target].position

    def _calculate_reward(self, success):
        # TODO - add reward function
        return 1.0 if success else 0.0

    def step(self, action):
        # Set positions for all action objects
        if len(self.level.actions) == 1:
            action = [action]
        for i, obj_name in enumerate(self.level.actions):
            target_position = action[i]
            target_position = b2Vec2(
                float(target_position[0]), float(target_position[1])
            )
            self.level.bodies[obj_name].position = target_position

        # Run the simulation for a fixed number of steps
        clock = pygame.time.Clock()
        num_steps = 0
        success = False
        done = False
        while not done and num_steps < self.max_steps:
            # Close the window if the user clicks the close button
            if self.render_level:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        done = True

            # Step Box2D simulation
            time_step = 1.0 / self.fps
            self.world.Step(time_step, self.vel_iters, self.pos_iters)
            num_steps += 1

            # Print position of the action ball
            # print(self.level.bodies[self.level.actions[0]].position)

            # Check if the target ball is in the basket
            if detect_success(self.world, self.level):
                print("Success!")
                success = True
                done = True

            # Clear the screen and render the world
            if self.render_level:
                self.render(mode="human")
                clock.tick(60)

        # Calculate reward
        reward = self._calculate_reward(success)

        # Return the observation, reward, done, and info
        obs = self._get_observation()
        info = {}
        return obs, reward, done, info

    def render(self, mode="human"):
        self.screen.fill((255, 255, 255))
        render_scene(self.world, self.level, self.screen)
        pygame.display.flip()

    def close(self):
        # Reset the world
        self.world.ClearForces()
        for body in self.world.bodies:
            self.world.DestroyBody(body)

        # Quit pygame
        if self.render_level:
            pygame.quit()