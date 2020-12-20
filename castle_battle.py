import arcade
import images
import math
import random
import time

SPRITE_SCALING = 0.5

SCREEN_WIDTH = 1750
SCREEN_HEIGHT = 1000
SCREEN_TITLE = "CTR Battle Arena"
MUSIC_VOLUME = 0.01
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
        #music
        self.music_list =[]
        self.current_song = 0
        self.music = None
        

        # Sprite lists
        self.wall_list = arcade.SpriteList()
        self.border_list = arcade.SpriteList()
        self.platform_list = arcade.SpriteList()
        self.floor_list = arcade.SpriteList()
        self.player_list = arcade.SpriteList()
        self.actor_list = arcade.SpriteList()
        self.enemy_list = arcade.SpriteList()
        self.background = arcade.load_texture("images/castle_doors.png")
        self.tomb = arcade.load_texture("images/tomb.png")
        arcade.set_background_color = None
        self.setup()
        self.count_1 = 0
        self.count_2 = 0
        self.count_3 = 0
        self.count_4 = 0

        

        # List of physics engines, one per actor; allows for multiple actors
        self.physics_engine = {}

        self.player_sprite = Player(self.actor_list, self.wall_list, self.enemy_list)
        self.enemy_cooldown = 0
        self.enemy_count = 1.0
        self.game_over = False
        self.start_time = self.time_lapsed = time.time()
        self.boss_time = False
        self.fighting_boss = False
        

    def setup(self):    
        for i in list(range(4)) + list(range(8, 30)):
            Wall(self.floor_list, i, 2.9, "images/floor.png")
        Wall(self.platform_list, 5.6, 1.5, "images/floor.png")

        for i in list(range(9)) + list(range(14, 20)) + list(range(22, 30)):
            Wall(self.floor_list, i, 6.15, "images/floor.png")
        Wall(self.platform_list, 10, 4.75, "images/floor.png")

        for i in list(range(5, 14)) + list(range(17, 26)):
            Wall(self.floor_list, i, 9.4, "images/floor.png")
        Wall(self.platform_list, 3, 8, "images/floor.png")

        #Create Border
        for i in range(50):
            Wall(self.border_list, (i -10), -0.5, ":resources:images/tiles/grassMid.png")
            Wall(self.border_list, -5, i, ":resources:images/tiles/grassMid.png")
            Wall(self.border_list, 35, i, ":resources:images/tiles/grassMid.png")
            Wall(self.border_list, (i - 10), 20, ":resources:images/tiles/grassMid.png")
        self.floor_list.extend(self.border_list)
        self.wall_list.extend(self.floor_list) 
        self.wall_list.extend(self.platform_list)

         # List of music
        self.music_list = ["sounds/background_music.mp3"]
        # Array index of what to play
        self.current_song = 0
        # Play the song
        self.play_song()

    def play_song(self):
        """ Play the song. """
        # Stop what is currently playing.
        if self.music:
            self.music.stop()

        self.music = arcade.Sound(self.music_list[self.current_song], streaming=True)
        self.music.play(MUSIC_VOLUME)

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
                else:
                    actor.position = [-100, -100]
                actor.kill()
        
        if self.enemy_cooldown > 0:
            self.enemy_cooldown -= 1
        else:
            self.enemy_cooldown = 500
            self.enemy_count += 0.1
            if self.boss_time == False:
                for _ in range(int(self.enemy_count)):
                    enemy_choice = random.randint(1, 200)
                    if enemy_choice < 50:
                        Orc(self.player_sprite, self.actor_list, self.enemy_list, self.wall_list)
                    elif enemy_choice < 130:
                        Goblin(self.player_sprite, self.actor_list, self.enemy_list, self.wall_list)
                    elif enemy_choice < 180:
                       Skeleton(self.player_sprite, self.actor_list, self.enemy_list, self.wall_list)
                    elif enemy_choice < 190:
                        Cyclops(self.player_sprite, self.actor_list, self.enemy_list, self.floor_list)
                    else:
                        Dragon(self.player_sprite, self.actor_list, self.enemy_list, self.border_list)
                

        if self.boss_time == True and self.fighting_boss == False:
            Wizard(self.player_sprite, self.actor_list, self.enemy_list, self.wall_list)
            self.fighting_boss = True

        if self.fighting_boss == True and Wizard.is_alive == False:
            self.boss_time = False
            self.fighting_boss = False

        position = self.music.get_stream_position()

        if position == 0.0:
            self.play_song()

#50, 130, 180
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

    def on_draw(self):
        """ Render the screen. """
        arcade.start_render()

        # Draw the background texture
        arcade.draw_lrwh_rectangle_textured(0, -SCREEN_WIDTH * .12,
                                            SCREEN_WIDTH, SCREEN_HEIGHT * 1.25,
                                            self.background)
        arcade.draw_rectangle_filled(75, 970, 150, 60, arcade.color.BLACK)

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

        if self.player_sprite.health <= 0:
            tomb_x = int(self.player_sprite.center_x)
            tomb_y = int(self.player_sprite.center_y)
            arcade.draw_lrwh_rectangle_textured(tomb_x - 20, tomb_y - 30, 75, 100, self.tomb)
           
        

        # Put the text on the screen.
        health = int(self.player_sprite.health)
        if self.player_sprite.health <= 0:
            output = f"Health: {0}"
        else:
            output = f"Health: {health}"
        arcade.draw_text(output, 10, 970,
                         arcade.color.RED, 20)
        coins = self.player_sprite.coins
        output = f"Coins: {coins}"
        arcade.draw_text(output, 10, 940, arcade.color.YELLOW, 20)

        end_time = time.time()
        if not self.game_over:
            self.time_lapsed = end_time - self.start_time
        mins = self.time_lapsed // 60
        secs = int(self.time_lapsed % 60)
        hrs = int(mins // 60)
        mins = int(mins % 60)
        output = f"{hrs}:{mins}:{secs}"
        arcade.draw_text(output, 1600, 960, arcade.color.WHITE, 30)

        if self.game_over:
            arcade.draw_text("Game Over", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2,
            arcade.color.BLACK, font_size=50, anchor_x="center")
            arcade.draw_text("Press Enter to reset",
                         SCREEN_WIDTH / 2,
                         SCREEN_HEIGHT / 2-30,
                         arcade.color.BLACK,
                         font_size=20,
                         anchor_x="center")

        position = self.music.get_stream_position()
        length = self.music.get_length()
        
        size = 20
        margin = size * .5

        
class InstructionView(arcade.View):
    """ View to show instructions """

    def on_show(self):
        self.count = 0
        self.background_1 = arcade.load_texture("images/menu_1.png")
        self.background_2 = arcade.load_texture("images/menu_2.png")
        self.background_3 = arcade.load_texture("images/menu_3.png")
        self.player_icon = arcade.load_texture("images/knight.png")
        arcade.set_background_color = None
    
    def on_update(self, delta_time):
        if self.count < 30:
            self.count += 1
        else:
            self.count = 0
    
    def on_draw(self):
        """ Render the screen. """
        arcade.start_render()

        if self.count < 10:
            arcade.draw_lrwh_rectangle_textured(0, SCREEN_WIDTH * .001, SCREEN_WIDTH, SCREEN_HEIGHT * 1, self.background_1)
        elif self.count < 20:
            arcade.draw_lrwh_rectangle_textured(0, SCREEN_WIDTH * .001, SCREEN_WIDTH, SCREEN_HEIGHT * 1, self.background_2)
        else:
            arcade.draw_lrwh_rectangle_textured(0, SCREEN_WIDTH * .001, SCREEN_WIDTH, SCREEN_HEIGHT * 1, self.background_3)
    
        arcade.draw_lrwh_rectangle_textured(1200, 100, 150, 150, self.player_icon)


        arcade.draw_text("Click to Start", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2,
                         arcade.color.WHITE, font_size=50, anchor_x="center")
        arcade.draw_text("Controls: ", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2-75,
                         arcade.color.WHITE, font_size=20, anchor_x="center")
        arcade.draw_text("WASD / Spacebar - Move / Jump", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2-100,
                         arcade.color.WHITE, font_size=20, anchor_x="center")                 
        arcade.draw_text("Left Mouse - Sword", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2-125,
                         arcade.color.WHITE, font_size=20, anchor_x="center")
        arcade.draw_text("Right Mouse - Bow", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2-150,
                         arcade.color.WHITE, font_size=20, anchor_x="center")
        arcade.draw_text("ESC - Upgrade Menu / Pause ", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2-175,
                         arcade.color.WHITE, font_size=20, anchor_x="center")

    def on_mouse_press(self, _x, _y, _button, _modifiers):
        """ If the user presses the mouse button, start the game. """
        self.window.show_view(GameView())

class UpgradeView(arcade.View):
    def __init__(self, game_view):
        super().__init__()
        self.game_view = game_view
        self.boss_time = game_view.boss_time

    def on_show(self):
        arcade.set_background_color(arcade.color.SKY_BLUE)

    def on_draw(self):
        arcade.start_render()

        arcade.draw_text("PAUSED", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2+50,
                         arcade.color.WHITE, font_size=50, anchor_x="center")

        # Show tip to return or reset
        arcade.draw_text("Press Esc. to return",
                         SCREEN_WIDTH / 2,
                         SCREEN_HEIGHT / 2,
                         arcade.color.WHITE,
                         font_size=20,
                         anchor_x="center")
        arcade.draw_text("Press Enter to reset",
                         SCREEN_WIDTH / 2,
                         SCREEN_HEIGHT / 2-30,
                         arcade.color.WHITE,
                         font_size=20,
                         anchor_x="center")
        arcade.draw_text("1: Increase Health by 25  Cost: 20",
                         SCREEN_WIDTH / 2,
                         SCREEN_HEIGHT / 2-60,
                         arcade.color.WHITE,
                         font_size=20,
                         anchor_x="center")
        arcade.draw_text("2: Increase Sword Damage  Cost: 30",
                         SCREEN_WIDTH / 2,
                         SCREEN_HEIGHT / 2-90,
                         arcade.color.WHITE,
                         font_size=20,
                         anchor_x="center")
        arcade.draw_text("3: Increase Bow Damage    Cost: 30",
                         SCREEN_WIDTH / 2,
                         SCREEN_HEIGHT / 2-120,
                         arcade.color.WHITE,
                         font_size=20,
                         anchor_x="center")
        arcade.draw_text("4: Battle the Boss",
                         SCREEN_WIDTH / 2,
                         SCREEN_HEIGHT / 2-150,
                         arcade.color.WHITE,
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
            self.game_view.player_sprite.health += 25
            self.game_view.player_sprite.coins -= 20
        elif key == arcade.key.KEY_2 and self.game_view.player_sprite.coins >= 30:
            self.game_view.count_2 += 1
            self.game_view.player_sprite.damage *= (1 + 1/(2*self.game_view.count_2))
            self.game_view.player_sprite.coins -= 30
        elif key == arcade.key.KEY_3 and self.game_view.player_sprite.coins >= 30:
            self.game_view.count_3 += 1
            self.game_view.player_sprite.damage_arrow *= (1 + 1/(2*self.game_view.count_3))
            self.game_view.player_sprite.coins -= 30
        elif key == arcade.key.KEY_4:
            self.game_view.boss_time = True
        

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
        distance = math.hypot(x_distance, y_distance)
        self.accelerate((source.knockback * x_distance) / distance, (source.knockback * y_distance) / distance)
    
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
        self.health = 100
        self.speed = 5
        self.accel = 0.5
        self.damage = 5
        self.damage_arrow = 2
        self.knockback = 10
        self.walking = False
        self.direction = "L"
        self.weapon = "sword"
        self.hit_cooldown = 0
        self.move_cooldown = 0
        self.texture = self.textures["idle"][self.direction]
        self.arrows = []
        self.coins = 30
        self.show_health = False

    def is_dead(self):
        return self.center_y < -5 * GRID_PIXEL_SIZE

    def on_key_press(self, key):
        if key in [arcade.key.UP, arcade.key.W, arcade.key.SPACE] and self.physics_engine.can_jump():
            self.change_y = JUMP_SPEED
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
        if self.move_cooldown == 0:
            self.move_cooldown = 10
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
        self.arrows.append(Arrow(actor_list, [x_pos, self.center_y + 10], self.direction, self.damage_arrow))
    
    def update(self):
        if (self.left <= LEFT_LIMIT and self.direction == "L"
                or self.right >= RIGHT_LIMIT and self.direction == "R"):
            self.change_x = 0
        if self.hit_cooldown == 0:    
            for enemy in self.enemies:
                if self.collides_with_sprite(enemy):
                    self.take_damage(enemy)
                    self.hit_cooldown = 50
        if self.move_cooldown > 0:
            self.move_cooldown -= 1
        if abs(self.change_x) > 0 and self.physics_engine.can_jump and (not self.walking or abs(self.change_x) > self.speed):
            self.change_x /= FRICTION
        if self.walking and self.direction == "L" and self.change_x > -self.speed:
            self.accelerate(x_accel=-self.accel)
        elif self.walking and self.direction == "R" and self.change_x < self.speed:
            self.accelerate(x_accel=self.accel)
        if self.hit_cooldown > 0:
            self.hit_cooldown -= 1

        for arrow in self.arrows:
            for enemy in self.enemies:
                if arrow.collides_with_sprite(enemy):
                        enemy.take_damage(arrow)
                        arrow.health -= 1


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
    def __init__(self, actor_list, pos, direction, damage):
        super().__init__()
        actor_list.append(self)
        self.physics_engine = arcade.PhysicsEnginePlatformer(self, arcade.SpriteList(), gravity_constant=0)
        self.health = 1
        self.show_health = False
        if direction == "L":
            self.texture = arcade.load_texture("images/arrow.png")
            self.change_x = -5
        else:
            self.change_x = 5
            self.texture = arcade.load_texture("images/arrow.png",
                                        flipped_horizontally=True)
        self.damage = damage
        self.scale = 0.1
        self.position = pos
        self.knockback = 2
    
    def is_alive(self):
        return self.health > 0
    
    def update(self):
        pass

class Blast(arcade.Sprite):
    def __init__(self, actor_list, pos, direction, damage):
        super().__init__()
        actor_list.append(self)
        self.physics_engine = arcade.PhysicsEnginePlatformer(self, arcade.SpriteList(), gravity_constant=0)
        self.health = 1
        self.show_health = False
        if direction == "L":
            self.texture = arcade.load_texture("images/wizard_blast.png")
            self.change_x = -5
        else:
            self.change_x = 5
            self.texture = arcade.load_texture("images/wizard_blast.png",
                                        flipped_horizontally=True)
        self.damage = damage
        self.scale = 0.1
        self.position = pos
        self.knockback = 2
    
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
        self.health = 75
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
        
        if self.physics_engine.can_jump and abs(self.change_x) > self.speed:
            self.change_x /= FRICTION

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
        self.health = 50
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
        
        if self.physics_engine.can_jump and abs(self.change_x) > self.speed:
            self.change_x /= FRICTION
        
        if self.upgrade_cooldown > 0:
            self.upgrade_cooldown -= 1
        else:
            self.upgrade_cooldown = 1000
            self.health *= 1.1
            self.damage *= 1.1

class Skeleton(Enemy):
    def __init__(self, player, actor_list, enemy_list, wall_list):
        super().__init__(player, actor_list, enemy_list, wall_list)
        self.add_texture("images/skeleton.png", "idle")
        self.texture = self.textures["idle"]["R"]
        self.direction = "R"
        self.scale = SPRITE_SCALING/3.25
        self.actor_list = actor_list
        self.position = random.choice(DOORS)
        self.health = 20
        self.speed = 2
        self.accel = 0.3
        self.jump_height = 10
        self.damage = 0
        self.damage_arrow = 3
        self.knockback = 1
        self.value = 10
        self.prey = player
        self.upgrade_cooldown = 1000
        self.shoot_cooldown = 50
        self.arrows = []
        self.walking = True
        
    def update(self):
        if self.center_x < self.prey.center_x and self.change_x < self.speed:
            if self.walking:
                self.change_x += self.accel
            self.texture = self.textures["idle"]["R"]
            self.direction = "R"
        elif self.center_x > self.prey.center_x and self.change_x > -self.speed:
            if self.walking:
                self.change_x -= self.accel
            self.texture = self.textures["idle"]["L"]
            self.direction = "L"
        self.walking = abs(self.center_x - self.prey.center_x) > 400 or abs(self.center_y - self.prey.center_y) > 100

        if (self.bottom + 10 < self.prey.bottom and self.physics_engine.can_jump()
                and abs(self.center_x - self.prey.center_x) < 150):
            self.change_y = self.jump_height
        
        if self.physics_engine.can_jump and abs(self.change_x) > self.speed or not self.walking:
            self.change_x /= FRICTION

        if self.upgrade_cooldown > 0:
            self.upgrade_cooldown -= 1
        else:
            self.upgrade_cooldown = 1000
            self.health *= 1.1
            self.damage_arrow *= 1.1

        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
        else:
            self.shoot_cooldown = 50
            self.fire_bow(self.actor_list)
        
        for arrow in self.arrows:
            if arrow.collides_with_sprite(self.prey):
                self.prey.take_damage(arrow)
                arrow.health -= 1
        

        
    def fire_bow(self, actor_list):
        if self.direction == "L":
            x_pos = self.left - 20
        else:
            x_pos = self.right + 20
        self.arrows.append(Arrow(actor_list, [x_pos, self.center_y + 10], self.direction, self.damage_arrow))

class Dragon(Enemy):
    def __init__(self, player, actor_list, enemy_list, wall_list):
        super().__init__(player, actor_list, enemy_list, wall_list)
        self.physics_engine = arcade.PhysicsEnginePlatformer(self, wall_list, gravity_constant=0)
        self.add_texture("images/dragon.png", "idle")
        self.texture = self.textures["idle"]["R"]
        self.scale = SPRITE_SCALING/1.5

        self.position = random.choice(CRACKS)
        self.health = 150
        self.speed = 5
        self.accel = 0.1
        self.jump_height = 10
        self.prey = player
        self.damage = 5
        self.knockback = 20
        self.value = 50
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
        
class Cyclops(Enemy):
    def __init__(self, player, actor_list, enemy_list, wall_list):
        super().__init__(player, actor_list, enemy_list, wall_list)
        self.add_texture("images/cyclops.png", "idle")
        self.texture = self.textures["idle"]["R"]
        self.scale = SPRITE_SCALING/2

        self.position = random.choice(DOORS)
        self.health = 200
        self.speed = 1.25
        self.accel = 0.3
        self.jump_height = 5
        self.damage = 10
        self.knockback = 10
        self.value = 75
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
        
        if self.physics_engine.can_jump and abs(self.change_x) > self.speed:
            self.change_x /= FRICTION

        if self.upgrade_cooldown > 0:
            self.upgrade_cooldown -= 1
        else:
            self.upgrade_cooldown = 1000
            self.health *= 1.1
            self.damage *= 1.1

class Wizard(Enemy):
    def __init__(self, player, actor_list, enemy_list, wall_list):
        super().__init__(player, actor_list, enemy_list, wall_list)
        self.add_texture("images/wizard.png", "idle")
        self.texture = self.textures["idle"]["R"]
        self.direction = "R"
        self.scale = SPRITE_SCALING/3
        self.actor_list = actor_list
        self.position = random.choice(DOORS)
        self.health = 1000
        self.speed = 2
        self.accel = 0.3
        self.jump_height = 10
        self.damage = 10
        self.damage_arrow = 50
        self.knockback = 10
        self.value = 1000
        self.prey = player
        self.upgrade_cooldown = 1000
        self.shoot_cooldown = 100
        self.arrows = []
        self.walking = True
        
    def update(self):
        if self.center_x < self.prey.center_x and self.change_x < self.speed:
            if self.walking:
                self.change_x += self.accel
            self.texture = self.textures["idle"]["R"]
            self.direction = "R"
        elif self.center_x > self.prey.center_x and self.change_x > -self.speed:
            if self.walking:
                self.change_x -= self.accel
            self.texture = self.textures["idle"]["L"]
            self.direction = "L"
        self.walking = abs(self.center_x - self.prey.center_x) > 400 or abs(self.center_y - self.prey.center_y) > 100

        if (self.bottom + 10 < self.prey.bottom and self.physics_engine.can_jump()
                and abs(self.center_x - self.prey.center_x) < 150):
            self.change_y = self.jump_height
        
        if self.physics_engine.can_jump and abs(self.change_x) > self.speed or not self.walking:
            self.change_x /= FRICTION

        if self.upgrade_cooldown > 0:
            self.upgrade_cooldown -= 1
        else:
            self.upgrade_cooldown = 1000
            self.health *= 1.1
            self.damage_arrow *= 1.1

        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
        else:
            self.shoot_cooldown = 50
            self.fire_bow(self.actor_list)
        
        for arrow in self.arrows:
            if arrow.collides_with_sprite(self.prey):
                self.prey.take_damage(arrow)
                arrow.health -= 1
        

        
    def fire_bow(self, actor_list):
        if self.direction == "L":
            x_pos = self.left - 20
        else:
            x_pos = self.right + 20
        self.arrows.append(Blast(actor_list, [x_pos, self.center_y + 10], self.direction, self.damage_arrow))

def main():
    """ Main method """
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    start_view = InstructionView()
    window.show_view(start_view)
    arcade.run()


main()