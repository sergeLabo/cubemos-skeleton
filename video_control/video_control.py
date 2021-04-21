import pyglet

class VideoPlayer:
    """Creates a new window and plays the requested video"""

    def __init__(self, filepath, fullscreen = False):
        self.filepath = filepath
        self.fullscreen = fullscreen
        self.window = pyglet.window.Window()
        self.video = pyglet.media.load(filepath)
        self.player = pyglet.media.Player()

        self.player.queue(self.video)

        @self.window.event
        def on_key_press(symbol, modifiers):
            key = pyglet.window.key
            if symbol == key.SPACE:
                if self.player.playing:
                    self.player.pause()
                    print("PAUSED")
                else:
                    self.player.play()
                    print("PLAYING")

            elif symbol == key.LEFT:
                self.player.seek(-2)
                print("Rewinding by 2 seconds")

        @self.window.event
        def on_draw():
            if (self.player.source.duration - self.player.time) < 0.1:
                # pyglet does not correctly handle EOS, so restart almost at the end
                # #self.player.source.seek(1.0)
                self.player.play()

            else:
                if self.player.playing:
                    self.player.get_texture().blit(0, 0)

        @self.window.event
        def on_close():
            self.player.delete()
            pyglet.app.exit()

        # #self.player.play()
        pyglet.app.run()


if __name__ == '__main__':

    VideoPlayer("2021-04-15 09-27-32.mkv")
