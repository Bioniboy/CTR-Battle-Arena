import arcade
import images
import math

SPRITE_SCALING = 0.5

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 600
SCREEN_TITLE = "CTR Battle Arena"
SPRITE_PIXEL_SIZE = 128
GRID_PIXEL_SIZE = (SPRITE_PIXEL_SIZE * SPRITE_SCALING)
LEFT_LIMIT = 0
RIGHT_LIMIT = 1000

# Physics
MOVEMENT_SPEED = 10 * SPRITE_SCALING
JUMP_SPEED = 20 * SPRITE_SCALING
GRAVITY = .9 * SPRITE_SCALING
FRICTION = 1.1

class MyGame(arcade.Window):
    """ Main application class. """

    def __init__(self, width, height, title):
        super().__init__(width, height, title)

        # Sprite lists
        self.wall_list = arcade.SpriteList()
        self.player_list = arcade.SpriteList()
        self.actor_list = arcade.SpriteList()
        self.enemy_list = arcade.SpriteList()

        # List of physics engines, one per actor; allows for multiple actors
        self.physics_engine = {}

        self.player_sprite = Player(self.actor_list, self.wall_list, self.enemy_list)
        Goblin(self.player_sprite, self.actor_list, self.enemy_list, self.wall_list)

        for i in range(18):
            Wall(self.wall_list, i, 0.5, ":resources:images/tiles/grassMid.png")      

        arcade.set_background_color(arcade.color.SKY_BLUE)

    def on_update(self, delta_time):
        # Call update on all sprites
        for engine in self.physics_engine.values():
            engine.update()

        # If the player falls off the platform, game over
        if self.player_sprite.is_dead():
            arcade.close_window()
        
        for actor in self.actor_list:
            actor.update()
            actor.physics_engine.update()
            if not actor.is_alive():
                actor.kill()

    def on_key_press(self, key, modifiers):
        self.player_sprite.on_key_press(key)

    def on_key_release(self, key, modifiers):
        self.player_sprite.on_key_release(key)

    def on_draw(self):
        """ Render the screen. """
        arcade.start_render()

        # Draw the sprites.
        self.wall_list.draw()
        self.actor_list.draw()

        # Put the text on the screen.
        health = self.player_sprite.health
        output = f"Health: {health}"
        arcade.draw_text(output, 10, 20,
                         arcade.color.WHITE, 14)


class Actor(arcade.Sprite):
    """ All dynamic sprites inherit this """
    def __init__(self, actor_list, wall_list):
        super().__init__()
        self.health = None

        # Make the sprite drawn and have physics applied
        actor_list.append(self)
        self.physics_engine = arcade.PhysicsEnginePlatformer(self, wall_list, gravity_constant=GRAVITY)
    
    def set_vel(self, x_vel = None, y_vel = None):
        if x_vel is not None:
            self.change_x = x_vel
        if y_vel is not None:
            self.change_y = y_vel

    def is_alive(self):
        return self.health > 0
    
    def take_damage(self, source):
        self.health -= source.damage
        x_distance = self.center_x - source.center_x
        y_distance = self.center_y - source.center_y
        angle = math.atan(x_distance/y_distance)
        self.change_x = math.sin(angle) * source.knockback
        self.change_y = math.cos(angle) * source.knockback

class Player(Actor):
    """ Sprite for the player """
    def __init__(self, actor_list, wall_list, enemy_list):
        super().__init__(actor_list, wall_list)
        self.textures.append(arcade.load_texture("images/knight-sword.png"))
        self.textures.append(arcade.load_texture("images/knight-sword.png",
                                      flipped_horizontally=True))
        self.texture = self.textures[0]
        self.scale = SPRITE_SCALING/5
        self.position = [(RIGHT_LIMIT + LEFT_LIMIT)/2, 4 * GRID_PIXEL_SIZE]
        self.enemies = enemy_list
        self.health = 100
        self.speed = 5
        self.accel = 0.5
        self.walking = ""
        self.hit_cooldown = 0

    def is_dead(self):
        return self.center_y < -5 * GRID_PIXEL_SIZE

    def on_key_press(self, key):
        if key in [arcade.key.UP, arcade.key.W, arcade.key.SPACE] and self.physics_engine.can_jump():
            self.change_y = JUMP_SPEED
        elif key in [arcade.key.LEFT, arcade.key.A]:
            self.walking = "L"
            self.change_x = -MOVEMENT_SPEED
            self.texture = self.textures[1]
        elif key in [arcade.key.RIGHT, arcade.key.D] and self.right < RIGHT_LIMIT:
            self.walking = "R"
            self.change_x = MOVEMENT_SPEED
            self.texture = self.textures[0]

    def on_key_release(self, key):
        if (key in [arcade.key.LEFT, arcade.key.A] and self.walking == "L"
                or key in [arcade.key.RIGHT, arcade.key.D] and self.walking == "R"):
            self.walking = ""
        if key in [arcade.key.UP, arcade.key.W, arcade.key.SPACE] and self.change_y > 0:
            self.change_y *= 0.5
    
    def update(self):
        if (self.left <= LEFT_LIMIT and self.walking == "L"
                or self.right >= RIGHT_LIMIT and self.walking == "R"):
            self.change_x = 0
        if self.hit_cooldown == 0:    
            for enemy in self.enemies:
                if self.collides_with_sprite(enemy):
                    self.take_damage(enemy)
                    self.hit_cooldown = 50
        if abs(self.change_x) > 0 and self.physics_engine.can_jump and self.walking == "":
            self.change_x /= FRICTION
        if self.walking == "L" and self.left > LEFT_LIMIT and self.change_x > -self.speed:
            self.change_x -= self.accel
        elif self.walking == "R" and self.right < RIGHT_LIMIT and self.change_x < self.speed:
            self.change_x += self.accel
        if self.hit_cooldown > 0:
            self.hit_cooldown -= 1
            


class Wall(arcade.Sprite):
    """ Static sprite for stationary walls """
    def __init__(self, wall_list, x_pos, y_pos, img):
        super().__init__(img, SPRITE_SCALING)
        self.position = [x_pos * GRID_PIXEL_SIZE, y_pos * GRID_PIXEL_SIZE]
        wall_list.append(self)

class Enemy(Actor):
    def __init__(self, player, actor_list, enemy_list, wall_list):
        super().__init__(actor_list, wall_list)
        self.prey = player
        enemy_list.append(self)

class Goblin(Enemy):
    def __init__(self, player, actor_list, enemy_list, wall_list):
        super().__init__(player, actor_list, enemy_list, wall_list)
        self.textures.append(arcade.load_texture(":resources:images/enemies/wormGreen.png"))
        self.textures.append(arcade.load_texture(":resources:images/enemies/wormGreen.png",
                                      flipped_horizontally=True))
        self.texture = self.textures[0]
        self.scale = SPRITE_SCALING
        self.position = [0, 4 * GRID_PIXEL_SIZE]
        self.health = 100
        self.speed = 2
        self.accel = 0.1
        self.jump_height = 10
        self.damage = 1
        self.knockback = 10
        
    
    def update(self):
        if self.center_x < self.prey.center_x and self.change_x < self.speed:
            self.change_x += self.accel
            self.texture = self.textures[1]
        elif self.center_x > self.prey.center_x and self.change_x > -self.speed:
            self.change_x -= self.accel
            self.texture = self.textures[0]
        if (self.bottom + 10 < self.prey.bottom and self.physics_engine.can_jump()
                and abs(self.center_x - self.prey.center_x) < 150):
            self.change_y = self.jump_height
            

def main():
    """ Main method """
    window = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    arcade.run()


main()