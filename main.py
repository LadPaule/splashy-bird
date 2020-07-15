from random import randint

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.properties import ObjectProperty, NumericProperty
from kivy.uix.image import Image
from kivy.uix.widget import Widget

from pipe import Pipe

class Background(Widget):
    cloud_texture = ObjectProperty(None)
    ground_texture = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # create textures
        self.cloud_texture = Image(source = "cloud.png").texture
        self.cloud_texture.wrap = "repeat"
        self.cloud_texture.uvsize = (Window.width / self.cloud_texture.width, - 1)

        self.ground_texture = Image(source = "ground.png").texture
        self.ground_texture.wrap = "repeat"
        self.ground_texture.uvsize = (Window.width / self.ground_texture.width, - 1)

    def scroll_textures(self, time_passed):
        # update the initial and final velocties of the textures.
        self.cloud_texture.uvpos = ((self.cloud_texture.uvpos[0] - time_passed / 2.) % Window.width , self.cloud_texture.uvpos[1])
        self.ground_texture.uvpos = ((self.ground_texture.uvpos[0] - time_passed / 2.) % Window.width , self.ground_texture.uvpos[1])
        #redraw the texture
        texture = self.property('cloud_texture')
        texture.dispatch(self)

        texture2 = self.property('ground_texture')
        texture2.dispatch(self)

class Bird(Image):
    velocity = NumericProperty(0)
    def on_touch_down(self, touch):
        self.source = "bird1.png"
        self.velocity = 150
        super().on_touch_move(touch)

    def on_touch_up(self, touch):
        self.source = "bird2.png"
        super().on_touch_move(touch) 

class Flappy(App):
    pipes = []
    gravity = 250
    was_colliding = False

    def start_game(self):
        self.was_colliding = False
        self.pipes = []
        self.root.ids.score.text = "0"
        self.frames = Clock.schedule_interval(self.next_frame, 1/60.)
        #create pipes
        number_of_pipes = 5
        distance_between_the_pipes = Window.width / 3
        for i in range(number_of_pipes):
            pipe = Pipe()
            pipe.pipe_center = randint(119 + 100, self.root.height - 100)
            pipe.size_hint = (None, None)
            pipe.pos = (Window.width + i*distance_between_the_pipes, 119)
            pipe.size = (66, self.root.height - 119)
            self.pipes.append(pipe)
            self.root.add_widget(pipe)

    def move_bird(self, time_passed):
        bird = self.root.ids.bird
        bird.y = bird.y + bird.velocity * time_passed
        bird.velocity = bird.velocity - self.gravity * time_passed
        self.check_collision()

    def check_collision(self):
        bird = self.root.ids.bird
        is_colliding = False
        # check for individual pipe collision
        for pipe in self.pipes:
            if pipe.collide_widget(bird):
                is_colliding = True
                #check if the bird is between the gap
                if (bird.y < (pipe.pipe_center - pipe.GAP_SIZE/2.0)) or (bird.top > (pipe.pipe_center + pipe.GAP_SIZE /2.0)):
                    self.game_over()
        #keeping the bird in the window            
        if (bird.y < 114) or (bird.y > Window.height + 5):
            self.game_over() 
        if self.was_colliding and not is_colliding:
            self.root.ids.score.text = str(int(self.root.ids.score.text)+1)
        self.was_colliding = is_colliding

    def game_over(self):
        self.root.ids.bird.pos = (20, (self.root.height - 119) / 2.0)
        for pipe in self.pipes:
            self.root.remove_widget(pipe)
        self.frames.cancel()
        self.root.ids.score.text = "FAILED!"

    def next_frame(self, time_passed):
        self.move_bird(time_passed)
        self.move_pipes(time_passed)
        self.root.ids.background.scroll_textures(time_passed)

    def move_pipes(self, time_passed):
        for pipe in self.pipes:
            pipe.x -= time_passed * 100        
        # check positioning
        number_of_pipes = 5
        distance_between_the_pipes = Window.width / (number_of_pipes - 1)
        pipe_xs = list(map(lambda pipe: pipe.x, self.pipes))
        right_most_x = max(pipe_xs)
        if right_most_x <= Window.width - distance_between_the_pipes:
            left_most_pipe = self.pipes[pipe_xs.index(min(pipe_xs))]
            left_most_pipe.x = Window.width
Flappy().run()
