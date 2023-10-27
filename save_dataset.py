from vis_nav_game import Player, Action
import pygame
import cv2
import os
import datetime
import keyboard
import time

i = 0
key_events = []
capturing = False
# setattr(Action, "CAPTURE", 1 << 6)


class KeyboardPlayerPyGame(Player):
    def __init__(self):
        self.fpv = None
        self.last_act = Action.IDLE
        self.screen = None
        self.keymap = None
        super(KeyboardPlayerPyGame, self).__init__()

    def reset(self):
        self.fpv = None
        self.last_act = Action.IDLE
        self.screen = None
        self.key_events = []
        global capturing

        pygame.init()

        self.keymap = {
            pygame.K_LEFT: Action.LEFT,
            pygame.K_RIGHT: Action.RIGHT,
            pygame.K_UP: Action.FORWARD,
            pygame.K_DOWN: Action.BACKWARD,
            pygame.K_SPACE: Action.CHECKIN,
            pygame.K_ESCAPE: Action.QUIT,
        }

    def act(self):
        global key_events, j, capturing
        current_key_events = []
        keys = pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                self.last_act = Action.QUIT
                return Action.QUIT

            if event.type == pygame.KEYDOWN:
                if keyboard.is_pressed("r"):
                    capturing = not capturing
                    print("r is pressed")
                if event.key in self.keymap:
                    self.last_act |= self.keymap[event.key]
                else:
                    self.show_target_images()
            if event.type == pygame.KEYUP:
                if event.key in self.keymap:
                    self.last_act ^= self.keymap[event.key]

        if capturing:
            for key, action in self.keymap.items():
                if keys[key]:
                    if action == Action.FORWARD:
                        current_key_events.append("F")
                    elif action == Action.BACKWARD:
                        current_key_events.append("B")
                    elif action == Action.RIGHT:
                        current_key_events.append("R")
                    elif action == Action.LEFT:
                        current_key_events.append("L")
                    elif action == Action.QUIT:
                        current_key_events.append("Q")

            key_events.append([i, current_key_events])

        return self.last_act

    def show_target_images(self):
        targets = self.get_target_images()
        if targets is None or len(targets) <= 0:
            return
        hor1 = cv2.hconcat(targets[:2])
        hor2 = cv2.hconcat(targets[2:])
        concat_img = cv2.vconcat([hor1, hor2])

        w, h = concat_img.shape[:2]

        color = (0, 0, 0)

        concat_img = cv2.line(concat_img, (int(h / 2), 0), (int(h / 2), w), color, 2)
        concat_img = cv2.line(concat_img, (0, int(w / 2)), (h, int(w / 2)), color, 2)

        w_offset = 25
        h_offset = 10
        font = cv2.FONT_HERSHEY_SIMPLEX
        line = cv2.LINE_AA
        size = 0.75
        stroke = 1

        cv2.putText(
            concat_img,
            "Front View",
            (h_offset, w_offset),
            font,
            size,
            color,
            stroke,
            line,
        )
        cv2.putText(
            concat_img,
            "Right View",
            (int(h / 2) + h_offset, w_offset),
            font,
            size,
            color,
            stroke,
            line,
        )
        cv2.putText(
            concat_img,
            "Back View",
            (h_offset, int(w / 2) + w_offset),
            font,
            size,
            color,
            stroke,
            line,
        )
        cv2.putText(
            concat_img,
            "Left View",
            (int(h / 2) + h_offset, int(w / 2) + w_offset),
            font,
            size,
            color,
            stroke,
            line,
        )

        cv2.imshow(f"KeyboardPlayer:target_images", concat_img)
        cv2.waitKey(1)

    def set_target_images(self, images):
        super(KeyboardPlayerPyGame, self).set_target_images(images)
        self.show_target_images()

    def get_k_matrix(self, images):
        k = super(KeyboardPlayerPyGame, self).get_camera_intrinsic_matrix()
        print(k)

    def see(self, fpv):
        global i
        if fpv is None or len(fpv.shape) < 3:
            return

        if capturing:
            if not os.path.exists("./images"):
                os.mkdir("./images")

        self.fpv = fpv

        if self.screen is None:
            h, w, _ = fpv.shape
            self.screen = pygame.display.set_mode((w, h))

        def convert_opencv_img_to_pygame(opencv_image):
            """
            Convert OpenCV images for Pygame.

            see https://blanktar.jp/blog/2016/01/pygame-draw-opencv-image.html
            """
            opencv_image = opencv_image[:, :, ::-1]  # BGR->RGB
            # (height,width,Number of colors) -> (width, height)
            shape = opencv_image.shape[1::-1]
            pygame_image = pygame.image.frombuffer(opencv_image.tobytes(), shape, "RGB")

            return pygame_image

        pygame.display.set_caption("KeyboardPlayer:fpv")
        rgb = convert_opencv_img_to_pygame(fpv)
        self.screen.blit(rgb, (0, 0))
        pygame.display.update()

        cv2.imshow("fpv", fpv)
        key = cv2.waitKey(1) & 0xFF

        if capturing:
            file_path = f"./images/{i}.jpg"
            cv2.imwrite(file_path, fpv)
            i += 1


if __name__ == "__main__":
    import vis_nav_game

    vis_nav_game.play(the_player=KeyboardPlayerPyGame())
    print(key_events)
