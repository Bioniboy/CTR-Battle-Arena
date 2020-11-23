import arcade
import images
import math

SPRITE_SCALING = 0.5

SCREEN_WIDTH = 1750
SCREEN_HEIGHT = 1000
SCREEN_TITLE = "CTR Battle Arena"
SPRITE_PIXEL_SIZE = 128
GRID_PIXEL_SIZE = (SPRITE_PIXEL_SIZE * SPRITE_SCALING)
LEFT_LIMIT = 0
RIGHT_LIMIT = SCREEN_WIDTH

# Physics
MOVEMENT_SPEED = 10 * SPRITE_SCALING
JUMP_SPEED = 20 * SPRITE_SCALING
GRAVITY = .75 * SPRITE_SCALING
FRICTION = 1.1


class GameView(arcade.View):
    """ Main application class. """

    def __init__(self):
        super().__init__()

        # Sprite lists
        self.wall_list = arcade.SpriteList()
        self.player_list = arcade.SpriteList()
        self.actor_list = arcade.SpriteList()
        self.enemy_list = arcade.SpriteList()

        # List of physics engines, one per actor; allows for multiple actors
        self.physics_engine = {}

        self.player_sprite = Player(self.actor_list, self.wall_list, self.enemy_list)
        Orc(self.player_sprite, self.actor_list, self.enemy_list, self.wall_list)
        Dragon(self.player_sprite, self.actor_list, self.enemy_list, self.wall_list)


        for i in range(30):
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
        if key in [arcade.key.ESCAPE]:
            upgrade_view = UpgradeView(self)
            self.window.show_view(upgrade_view)

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

class InstructionView(arcade.View):
    """ View to show instructions """

    def on_show(self):
        """ This is run once when we switch to this view """
        arcade.set_background_color(arcade.csscolor.DARK_SLATE_BLUE)

        # Reset the viewport, necessary if we have a scrolling game and we need
        # to reset the viewport back to the start so we can see what we draw.
        arcade.set_viewport(0, SCREEN_WIDTH - 1, 0, SCREEN_HEIGHT - 1)

    def on_draw(self):
        """ Draw this view """
        arcade.start_render()
        arcade.draw_text("Instructions Screen", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2,
                         arcade.color.WHITE, font_size=50, anchor_x="center")
        arcade.draw_text("Click to advance", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2-75,
                         arcade.color.WHITE, font_size=20, anchor_x="center")

    def on_mouse_press(self, _x, _y, _button, _modifiers):
        """ If the user presses the mouse button, start the game. """
        self.window.show_view(GameView())

class UpgradeView(arcade.View):
    def __init__(self, game_view):
        super().__init__()
        self.game_view = game_view

    def on_show(self):
        arcade.set_background_color(arcade.color.SKY_BLUE)

    def on_draw(self):
        arcade.start_render()

        # Draw player, for effect, on pause screen.
        # The previous View (GameView) was passed in
        # and saved in self.game_view.
        player_sprite = self.game_view.player_sprite
        player_sprite.draw()

        # draw an orange filter over him
        arcade.draw_lrtb_rectangle_filled(left=player_sprite.left,
                                          right=player_sprite.right,
                                          top=player_sprite.top,
                                          bottom=player_sprite.bottom,
                                          color=arcade.color.SKY_BLUE + (200,))

        arcade.draw_text("PAUSED", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2+50,
                         arcade.color.BLACK, font_size=50, anchor_x="center")

        # Show tip to return or reset
        arcade.draw_text("Press Esc. to return",
                         SCREEN_WIDTH / 2,
                         SCREEN_HEIGHT / 2,
                         arcade.color.BLACK,
                         font_size=20,
                         anchor_x="center")
        arcade.draw_text("Press Enter to reset",
                         SCREEN_WIDTH / 2,
                         SCREEN_HEIGHT / 2-30,
                         arcade.color.BLACK,
                         font_size=20,
                         anchor_x="center")

    def on_key_press(self, key, _modifiers):
        if key == arcade.key.ESCAPE:   # resume game
            self.window.show_view(self.game_view)
        elif key == arcade.key.ENTER:  # reset game
            game = GameView()
            self.window.show_view(game)

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
        self.accelerate(math.sin(angle) * source.knockback, math.sin(angle) * source.knockback)
    
    def accelerate(self, x_accel=None, y_accel=None):
        if (x_accel is not None and (self.left > LEFT_LIMIT and x_accel < 0
                or self.right < RIGHT_LIMIT and x_accel > 0)):
            self.change_x += x_accel
        if y_accel is not None:
            self.change_y += y_accel

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
        self.jump_speed = 20 * SPRITE_SCALING
        self.accel = 0.5
        self.walking = ""
        self.hit_cooldown = 0

    def is_dead(self):
        return self.center_y < -5 * GRID_PIXEL_SIZE

    def on_key_press(self, key):
        if key in [arcade.key.UP, arcade.key.W, arcade.key.SPACE] and self.physics_engine.can_jump():
            self.accelerate(y_accel=self.jump_speed)
        elif key in [arcade.key.LEFT, arcade.key.A]:
            self.walking = "L"
            self.texture = self.textures[0]
        elif key in [arcade.key.RIGHT, arcade.key.D] and self.right < RIGHT_LIMIT:
            self.walking = "R"
            self.texture = self.textures[1]

    def on_key_release(self, key):
        if (key in [arcade.key.LEFT, arcade.key.A] and self.walking == "L"
                or key in [arcade.key.RIGHT, arcade.key.D] and self.walking == "R"):
            self.walking = ""
        if key in [arcade.key.UP, arcade.key.W, arcade.key.SPACE] and self.change_y > 0:
            self.change_y *= 0.5
    
    def update(self):
        if (self.left <= LEFT_LIMIT and self.change_x < 0
                or self.right >= RIGHT_LIMIT and self.change_x > 0):
            self.change_x = 0
        if self.hit_cooldown == 0:    
            for enemy in self.enemies:
                if self.collides_with_sprite(enemy):
                    self.take_damage(enemy)
                    self.hit_cooldown = 50
        if abs(self.change_x) > 0 and self.physics_engine.can_jump and (self.walking == "" or abs(self.change_x) > self.speed):
            self.change_x /= FRICTION
        if self.walking == "L" and self.change_x > -self.speed:
            self.accelerate(x_accel=-self.accel)
        elif self.walking == "R" and self.change_x < self.speed:
            self.accelerate(x_accel=self.accel)
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

class Orc(Enemy):
    def __init__(self, player, actor_list, enemy_list, wall_list):
        super().__init__(player, actor_list, enemy_list, wall_list)
        self.textures.append(arcade.load_texture("images/orc.png"))
        self.textures.append(arcade.load_texture("images/orc.png",
                                      flipped_horizontally=True))
        self.texture = self.textures[0]
        self.scale = SPRITE_SCALING/5

        self.position = [0, 4 * GRID_PIXEL_SIZE]
        self.health = 100
        self.speed = 2
        self.accel = 0.1
        self.jump_height = 10
        self.damage = 1
        self.knockback = 10
        self.prey = player
        
    
    def update(self):
        if self.center_x < self.prey.center_x and self.change_x < self.speed:
            self.change_x += self.accel
            self.texture = self.textures[0]
        elif self.center_x > self.prey.center_x and self.change_x > -self.speed:
            self.change_x -= self.accel
            self.texture = self.textures[1]
        if (self.bottom + 10 < self.prey.bottom and self.physics_engine.can_jump()
                and abs(self.center_x - self.prey.center_x) < 150):
            self.change_y = self.jump_height

class Dragon(Enemy):
    def __init__(self, player, actor_list, enemy_list, wall_list):
        super().__init__(player, actor_list, enemy_list, wall_list)
        self.physics_engine = arcade.PhysicsEnginePlatformer(self, wall_list, gravity_constant=0)
        self.textures.append(arcade.load_texture("images/dragon.png"))
        self.textures.append(arcade.load_texture("images/dragon.png",
                                      flipped_horizontally=True))
        self.texture = self.textures[0]
        self.scale = SPRITE_SCALING/1.5

        self.position = [0, 4 * GRID_PIXEL_SIZE]
        self.health = 100
        self.speed = 5
        self.accel = 0.1
        self.jump_height = 10
        self.prey = player
        self.damage = 5
        self.knockback = 20

    def update(self):
        if self.center_x < self.prey.center_x and self.change_x < self.speed:
            self.change_x += self.accel
            self.texture = self.textures[1]
        elif self.center_x > self.prey.center_x and self.change_x > -self.speed:
            self.change_x -= self.accel
            self.texture = self.textures[0]

        if self.center_y < self.prey.center_y and self.change_y < self.speed:
            self.change_y += self.accel
        elif self.center_y > self.prey.center_y and self.change_y > -self.speed:
            self.change_y -= self.accel
        

def main():
    """ Main method """
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    start_view = InstructionView()
    window.show_view(start_view)
    arcade.run()


main()