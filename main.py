from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, ReferenceListProperty
from kivy.vector import Vector
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle, Ellipse
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen


# Optional: set a fixed window size for testing on desktop
Window.size = (400, 600)

class Paddle(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas:
            Color(0, 1, 0)  # Green
            self.rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self.update_graphics_pos, size=self.update_graphics_pos)

    def update_graphics_pos(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

class Ball(Widget):
    vx = NumericProperty(0)
    vy = NumericProperty(0)
    velocity = ReferenceListProperty(vx, vy)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas:
            Color(1, 0, 0)  # Red
            self.ellipse = Ellipse(pos=self.pos, size=(20, 20))
        self.bind(pos=self.update_graphics_pos)

    def update_graphics_pos(self, *args):
        self.ellipse.pos = self.pos

    def move(self):
        self.pos = Vector(*self.velocity) + self.pos

class Brick(Widget):
    def __init__(self, color=(0, 0, 1), **kwargs):
        super().__init__(**kwargs)
        with self.canvas:
            Color(*color)  # RGB tuple
            self.rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self.update_graphics_pos, size=self.update_graphics_pos)

    def update_graphics_pos(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

class BreakoutGame(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.ball = Ball(size=(20, 20))
        self.ball.velocity = Vector(12, 12)
        self.add_widget(self.ball)

        self.paddle = Paddle(size=(100, 20))
        self.add_widget(self.paddle)

        self.bricks = []
        self.bricks_created = False

        Clock.schedule_interval(self.update, 1/60)
        self.bind(size=self.reset_positions)

    def reset_positions(self, *args):
        # Center ball and paddle
        self.ball.center = self.center
        self.paddle.center_x = self.center_x
        self.paddle.y = 50

        # Create bricks once
        if not self.bricks_created:
            rows = 5
            cols = 6
            padding = 10
            brick_width = (self.width - padding*(cols+1)) / cols
            brick_height = 20
            start_y = self.height - 100

            colors = [
                (1,0,0), (0,1,0), (0,0,1), (1,1,0), (1,0,1)
            ]  # Row colors

            for i in range(rows):
                for j in range(cols):
                    x = padding + j*(brick_width + padding)
                    y = start_y - i*(brick_height + padding)
                    brick = Brick(color=colors[i % len(colors)], size=(brick_width, brick_height), pos=(x, y))
                    self.add_widget(brick)
                    self.bricks.append(brick)

            self.bricks_created = True

    def on_touch_move(self, touch):
        # Slide paddle along x-axis
        self.paddle.center_x = touch.x

    def update(self, dt):
        self.ball.move()

        # Bounce off walls
        if self.ball.x < 0 or self.ball.right > self.width:
            self.ball.vx *= -1
        if self.ball.top > self.height:
            self.ball.vy *= -1

        # Ball falls below screen
        if self.ball.y < 0:
            self.ball.center = self.center
            self.ball.velocity = Vector(12, 12)

        # Bounce off paddle
        if self.ball.collide_widget(self.paddle):
            self.ball.vy *= -1

        # Bounce off bricks
        for brick in self.bricks[:]:
            if self.ball.collide_widget(brick):
                self.ball.vy *= -1
                self.remove_widget(brick)
                self.bricks.remove(brick)

class BreakoutApp(App):
    def build(self):
        return BreakoutGame()

if __name__ == '__main__':
    BreakoutApp().run()