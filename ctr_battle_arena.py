import arcade
import images
import math
import random

SPRITE_SCALING = 0.5

SCREEN_WIDTH = 1750
SCREEN_HEIGHT = 1000
SCREEN_TITLE = "CTR Battle Arena"
SPRITE_PIXEL_SIZE = 128
GRID_PIXEL_SIZE = (SPRITE_PIXEL_SIZE * SPRITE_SCALING)
LEFT_LIMIT = 0
RIGHT_LIMIT = SCREEN_WIDTH
DOORS = [[1230, 0],
        [800, 214], [1530, 214],
        [365, 420], [1100, 420],
        [650, 620], [1380, 620]]
CRACKS = [[451, 931], [1296, 931]]

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
        self.border_list = arcade.SpriteList()
        self.player_list = arcade.SpriteList()
        self.actor_list = arcade.SpriteList()
        self.enemy_list = arcade.SpriteList()
        self.background = arcade.load_texture("images/castle_doors.png")
        arcade.set_background_color = None
        self.setup()

        # List of physics engines, one per actor; allows for multiple actors
        self.physics_engine = {}

        self.player_sprite = Player(self.actor_list, self.wall_list, self.enemy_list)
        self.enemy_cooldown = 0
        self.enemy_count = 1.0
        self.game_over = False
        

        #self.coins = 0

    def setup(self):    
        for i in list(range(4)) + list(range(8, 30)):
            Wall(self.wall_list, i, 2.9, "images/floor.png")
        Wall(self.wall_list, 5.6, 1.5, "images/floor.png")

        for i in list(range(9)) + list(range(14, 20)) + list(range(22, 30)):
            Wall(self.wall_list, i, 6.15, "images/floor.png")
        Wall(self.wall_list, 10, 4.75, "images/floor.png")

        for i in list(range(5, 14)) + list(range(17, 26)):
            Wall(self.wall_list, i, 9.4, "images/floor.png")
        Wall(self.wall_list, 3, 8, "images/floor.png")

        #Create Border
        for i in range(50):
            Wall(self.border_list, (i -10), -0.5, ":resources:images/tiles/grassMid.png")
            Wall(self.border_list, -5, i, ":resources:images/tiles/grassMid.png")
            Wall(self.border_list, 35, i, ":resources:images/tiles/grassMid.png")
            Wall(self.border_list, (i - 10), 20, ":resources:images/tiles/grassMid.png")
        self.wall_list.extend(self.border_list) 

    def on_update(self, delta_time):
        # Call update on all sprites
        for engine in self.physics_engine.values():
            engine.update()

        # If the player falls off the platform, game over
        if self.player_sprite.is_dead():
            arcade.close_window()
        
        for actor in self.actor_list:
            actor.update()
            if actor.physics_engine is not None:
                actor.physics_engine.update()
            if not actor.is_alive():
                if actor in self.enemy_list:
                    self.player_sprite.coins += actor.value
                if actor is self.player_sprite:
                    self.game_over = True
                actor.kill()
        
        if self.enemy_cooldown > 0:
            self.enemy_cooldown -= 1
        else:
            self.enemy_cooldown = 500
            self.enemy_count += 0.1
            for _ in range(int(self.enemy_count)):
                enemy_choice = random.randint(1, 100)
                if enemy_choice < 40:
                    Orc(self.player_sprite, self.actor_list, self.enemy_list, self.wall_list)
                elif 40 <= enemy_choice < 95:
                    Goblin(self.player_sprite, self.actor_list, self.enemy_list, self.wall_list)
                else:
                    Dragon(self.player_sprite, self.actor_list, self.enemy_list, self.border_list) 

    def on_key_press(self, key, modifiers):
        self.player_sprite.on_key_press(key)
        if key in [arcade.key.ESCAPE]:
            upgrade_view = UpgradeView(self)
            self.window.show_view(upgrade_view)
        elif key == arcade.key.ENTER and self.game_over is True:  # reset game
            game = GameView()
            self.window.show_view(game)

    def on_key_release(self, key, modifiers):
        self.player_sprite.on_key_release(key)
    
    def on_mouse_press(self, _x, _y, button, _modifiers):
        self.player_sprite.on_mouse_press(self.actor_list, button)
        print(_x, _y)

    def on_draw(self):
        """ Render the screen. """
        arcade.start_render()

        # Draw the background texture
        arcade.draw_lrwh_rectangle_textured(0, -SCREEN_WIDTH * .12,
                                            SCREEN_WIDTH, SCREEN_HEIGHT * 1.25,
                                            self.background)

        # Draw the sprites.
        self.wall_list.draw()
        self.actor_list.draw()

        # Draw health
        for actor in self.actor_list:
            if actor.show_health:        
                actor_health = int(actor.health)
                output = f"{actor_health}"
                x = actor.center_x - 10
                y = actor.center_y + 20
                arcade.draw_text(output, x, y, arcade.color.RED, 14)

        # Put the text on the screen.
        health = int(self.player_sprite.health)
        output = f"Health: {health}"
        arcade.draw_text(output, 10, 970,
                         arcade.color.RED, 20)
        coins = self.player_sprite.coins
        output = f"Coins: {coins}"
        arcade.draw_text(output, 10, 940, arcade.color.YELLOW, 20)

        if self.game_over is True:
            arcade.draw_text("Game Over", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2,
            arcade.color.BLACK, font_size=50, anchor_x="center")
            arcade.draw_text("Press Enter to reset",
                         SCREEN_WIDTH / 2,
                         SCREEN_HEIGHT / 2-30,
                         arcade.color.BLACK,
                         font_size=20,
                         anchor_x="center")
    
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
        arcade.draw_text("1: Increase Health by 50  Cost: 20",
                         SCREEN_WIDTH / 2,
                         SCREEN_HEIGHT / 2-60,
                         arcade.color.BLACK,
                         font_size=20,
                         anchor_x="center")
        arcade.draw_text("2: Increase Sword Damage  Cost: 30",
                         SCREEN_WIDTH / 2,
                         SCREEN_HEIGHT / 2-90,
                         arcade.color.BLACK,
                         font_size=20,
                         anchor_x="center")
        arcade.draw_text("3: Increase Bow Damage    Cost: 30",
                         SCREEN_WIDTH / 2,
                         SCREEN_HEIGHT / 2-120,
                         arcade.color.BLACK,
                         font_size=20,
                         anchor_x="center")
        arcade.draw_text("4: Increase Agility      Cost: 50",
                         SCREEN_WIDTH / 2,
                         SCREEN_HEIGHT / 2-150,
                         arcade.color.BLACK,
                         font_size=20,
                         anchor_x="center")
        health = int(self.game_view.player_sprite.health)
        output = f"Health: {health}"
        arcade.draw_text(output, 10, 970,
                         arcade.color.RED, 20)
        coins = self.game_view.player_sprite.coins
        output = f"Coins: {coins}"
        arcade.draw_text(output, 10, 940, arcade.color.YELLOW, 20)

    def on_key_press(self, key, _modifiers):
        if key == arcade.key.ESCAPE:   # resume game
            self.game_view.player_sprite.walking = False
            self.window.show_view(self.game_view)
        elif key == arcade.key.ENTER:  # reset game
            game = GameView()
            self.window.show_view(game)
        elif key == arcade.key.KEY_1 and self.game_view.player_sprite.coins >= 20:
            self.game_view.player_sprite.health += 50
            self.game_view.player_sprite.coins -= 20
        elif key == arcade.key.KEY_2 and self.game_view.player_sprite.coins >= 20:
            self.count2 = 0
            self.count2 += 1
            self.game_view.player_sprite.damage *= (1 + 1/self.count2)
            self.game_view.player_sprite.coins -= 20
        elif key == arcade.key.KEY_3 and self.game_view.player_sprite.coins >= 20:
            self.count3 = 0
            self.count3 += 1
            self.game_view.player_sprite.damage_arrow *= (1 + 1/(2*self.count3))
            self.game_view.player_sprite.coins -= 20
        elif key == arcade.key.KEY_4 and self.game_view.player_sprite.coins >= 20:
            self.game_view.player_sprite.health += 50
            self.game_view.player_sprite.coins -= 20
        

class Actor(arcade.Sprite):
    """ All dynamic sprites inherit this """
    def __init__(self, actor_list, wall_list):
        super().__init__()
        self.health = None
        self.boundary_left = LEFT_LIMIT
        self.boundary_right = RIGHT_LIMIT
        self.textures = {}
        # Make the sprite drawn and have physics applied
        actor_list.append(self)
        self.physics_engine = arcade.PhysicsEnginePlatformer(self, wall_list, gravity_constant=GRAVITY)
        self.show_health = True
    
    def set_vel(self, x_vel = None, y_vel = None):
        if x_vel is not None:
            self.change_x = x_vel
        if y_vel is not None:
            self.change_y = y_vel

    def is_alive(self):
        return self.health > 0
    
    def add_texture(self, img, name):
        self.textures[name] = {"L": arcade.load_texture(img), "R": arcade.load_texture(img, flipped_horizontally=True)}
    
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
        self.add_texture("images/knight.png", "idle")
        self.add_texture("images/knight_sword.png", "sword")
        self.add_texture("images/knight_bow.png", "bow")
        self.scale = SPRITE_SCALING/4
        self.position = [216, 0]
        self.enemies = enemy_list
        self.health = 10
        self.speed = 5
        self.jump_speed = 20 * SPRITE_SCALING
        self.accel = 0.5
        self.damage = 5
        self.knockback = 10
        self.walking = False
        self.direction = "L"
        self.hit_cooldown = 0
        self.texture = self.textures["idle"][self.direction]
        if self.health <= 0:
            self.texture = arcade.load_texture("images/tomb.png")
        self.coins = 0
        self.arrows = []
        self.show_health = False

    def is_dead(self):
        return self.center_y < -5 * GRID_PIXEL_SIZE

    def on_key_press(self, key):
        if key in [arcade.key.UP, arcade.key.W, arcade.key.SPACE] and self.physics_engine.can_jump():
            self.accelerate(y_accel=self.jump_speed)
        elif key in [arcade.key.LEFT, arcade.key.A]:
            self.walking = True
            self.direction = "L"
            self.texture = self.textures["idle"][self.direction]
        elif key in [arcade.key.RIGHT, arcade.key.D] and self.right < RIGHT_LIMIT:
            self.walking = True
            self.direction = "R"
            self.texture = self.textures["idle"][self.direction]

    def on_key_release(self, key):
        if (key in [arcade.key.LEFT, arcade.key.A] and self.direction == "L"
                or key in [arcade.key.RIGHT, arcade.key.D] and self.direction == "R"):
            self.walking = False
        if key in [arcade.key.UP, arcade.key.W, arcade.key.SPACE] and self.change_y > 0:
            self.change_y *= 0.5

    def on_mouse_press(self, actor_list, button):
        if button == arcade.MOUSE_BUTTON_LEFT:
            self.swing_sword(actor_list)
        if button == arcade.MOUSE_BUTTON_RIGHT:
            self.fire_bow(actor_list)

    def swing_sword(self, actor_list):
        if self.direction == "L":
            x_pos = self.left - 20
        else:
            x_pos = self.right + 20
        self.texture = self.textures["sword"][self.direction]
        swing = Swing(actor_list, [x_pos, self.center_y], self.direction)
        for enemy in self.enemies:
            if swing.collides_with_sprite(enemy):
                    enemy.take_damage(self)
    
    def fire_bow(self, actor_list):
        if self.direction == "L":
            x_pos = self.left - 20
        else:
            x_pos = self.right + 20
        self.texture = self.textures["bow"][self.direction]
        self.arrows.append(Arrow(actor_list, [x_pos, self.center_y + 10], self.direction))
    
    def update(self):
        if (self.left <= LEFT_LIMIT and self.change_x < 0
                or self.right >= RIGHT_LIMIT and self.change_x > 0):
            self.change_x = 0
        if self.hit_cooldown == 0:    
            for enemy in self.enemies:
                if self.collides_with_sprite(enemy):
                    self.take_damage(enemy)
                    self.hit_cooldown = 50
        if abs(self.change_x) > 0 and self.physics_engine.can_jump and (not self.walking or abs(self.change_x) > self.speed):
            self.change_x /= FRICTION
        if self.walking and self.direction == "L" and self.change_x > -self.speed:
            self.accelerate(x_accel=-self.accel)
        elif self.walking and self.direction == "R" and self.change_x < self.speed:
            self.accelerate(x_accel=self.accel)
        if self.hit_cooldown > 0:
            self.hit_cooldown -= 1


class Swing(arcade.Sprite):
    def __init__(self, actor_list, pos, direction):
        super().__init__()
        actor_list.append(self)
        self.health = 10
        self.show_health = False
        self.physics_engine = None
        self.position = pos
        self.scale = 1.5
        if direction == "L":
            self.texture = arcade.load_texture("images/swing.png")
        else:
            self.texture = arcade.load_texture("images/swing.png", 
                                        flipped_horizontally=True)
        
    def is_alive(self):
        return self.health > 0
    
    def update(self):
        self.health -= 1

class Arrow(arcade.Sprite):
    def __init__(self, actor_list, pos, direction):
        super().__init__()
        actor_list.append(self)
        self.physics_engine = arcade.PhysicsEnginePlatformer(self, arcade.SpriteList(), gravity_constant=0)
        self.health = 1
        if direction == "L":
            self.texture = arcade.load_texture("images/arrow.png")
            self.change_x = -10
        else:
            self.change_x = 10
            self.texture = arcade.load_texture("images/arrow.png",
                                        flipped_horizontally=True)
        self.scale = 0.1
        self.position = pos
    
    def is_alive(self):
        return self.health > 0
    
    def update(self):
        pass

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
        self.add_texture("images/orc.png", "idle")
        self.texture = self.textures["idle"]["R"]
        self.scale = SPRITE_SCALING/3.25

        self.position = random.choice(DOORS)
        self.health = 50
        self.speed = 1.5
        self.accel = 0.3
        self.jump_height = 10
        self.damage = 4
        self.knockback = 10
        self.value = 10
        self.prey = player
        self.upgrade_cooldown = 1000
        
    def update(self):
        if self.center_x < self.prey.center_x and self.change_x < self.speed:
            self.change_x += self.accel
            self.texture = self.textures["idle"]["R"]
        elif self.center_x > self.prey.center_x and self.change_x > -self.speed:
            self.change_x -= self.accel
            self.texture = self.textures["idle"]["L"]
        if (self.bottom + 10 < self.prey.bottom and self.physics_engine.can_jump()
                and abs(self.center_x - self.prey.center_x) < 150):
            self.change_y = self.jump_height

        if self.upgrade_cooldown > 0:
            self.upgrade_cooldown -= 1
        else:
            self.upgrade_cooldown = 1000
            self.health *= 1.1
            self.damage *= 1.1

class Goblin(Enemy):
    def __init__(self, player, actor_list, enemy_list, wall_list):
        super().__init__(player, actor_list, enemy_list, wall_list)
        self.add_texture("images/goblin.png", "idle")
        self.texture = self.textures["idle"]["R"]
        self.scale = SPRITE_SCALING/4

        self.position = random.choice(DOORS)
        self.health = 30
        self.speed = 2
        self.accel = 0.2
        self.jump_height = 10
        self.damage = 2
        self.knockback = 10
        self.value = 5
        self.prey = player
        self.upgrade_cooldown = 1000
        
    def update(self):
        if self.center_x < self.prey.center_x and self.change_x < self.speed:
            self.change_x += self.accel
            self.texture = self.textures["idle"]["R"]
        elif self.center_x > self.prey.center_x and self.change_x > -self.speed:
            self.change_x -= self.accel
            self.texture = self.textures["idle"]["L"]
        if (self.bottom + 10 < self.prey.bottom and self.physics_engine.can_jump()
                and abs(self.center_x - self.prey.center_x) < 150):
            self.change_y = self.jump_height
        
        if self.upgrade_cooldown > 0:
            self.upgrade_cooldown -= 1
        else:
            self.upgrade_cooldown = 1000
            self.health *= 1.1
            self.damage *= 1.1

class Dragon(Enemy):
    def __init__(self, player, actor_list, enemy_list, wall_list):
        super().__init__(player, actor_list, enemy_list, wall_list)
        self.physics_engine = arcade.PhysicsEnginePlatformer(self, wall_list, gravity_constant=0)
        self.add_texture("images/dragon.png", "idle")
        self.texture = self.textures["idle"]["R"]
        self.scale = SPRITE_SCALING/1.5

        self.position = random.choice(CRACKS)
        self.health = 30
        self.speed = 5
        self.accel = 0.1
        self.jump_height = 10
        self.prey = player
        self.damage = 5
        self.knockback = 20
        self.value = 20
        self.upgrade_cooldown = 1000

    def update(self):
        if self.center_x < self.prey.center_x and self.change_x < self.speed:
            self.change_x += self.accel
            self.texture = self.textures["idle"]["R"]
        elif self.center_x > self.prey.center_x and self.change_x > -self.speed:
            self.change_x -= self.accel
            self.texture = self.textures["idle"]["L"]

        if self.center_y < self.prey.center_y and self.change_y < self.speed:
            self.change_y += self.accel
        elif self.center_y > self.prey.center_y and self.change_y > -self.speed:
            self.change_y -= self.accel

        if self.upgrade_cooldown > 0:
            self.upgrade_cooldown -= 1
        else:
            self.upgrade_cooldown = 1000
            self.health *= 1.1
            self.damage *= 1.1
        

def main():
    """ Main method """
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    start_view = InstructionView()
    window.show_view(start_view)
    arcade.run()


main()