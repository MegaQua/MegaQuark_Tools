from functools import partial
import maya.cmds as cmds
import random

# 游戏设置
BOARD_SIZE = 10
SNAKE_COLOR = (1, 0, 0)  # 红色
FOOD_COLOR = (0, 1, 0)  # 绿色
GAME_SPEED = 1

class SnakeGameUI(object):
    def __init__(self):
        self.window_name = 'SnakeGameUI'
        self.board_cells = []
        self.snake = []
        self.food = None
        self.direction = 'right'

    def create_game_board(self):
        cmds.setParent(self.window_name)
        cmds.gridLayout(nc=BOARD_SIZE, cwh=(30, 30))

        for i in range(BOARD_SIZE):
            row_cells = []
            for j in range(BOARD_SIZE):
                cell = cmds.button(label='', bgc=(0, 0, 0))
                row_cells.append(cell)
            self.board_cells.append(row_cells)

    def generate_food(self):
        if self.food:
            cmds.button(self.food, e=True, bgc=(0, 0, 0))

        while True:
            x = random.randint(0, BOARD_SIZE - 1)
            y = random.randint(0, BOARD_SIZE - 1)
            if (x, y) not in self.snake:
                break

        self.food = self.board_cells[x][y]
        cmds.button(self.food, e=True, bgc=FOOD_COLOR)

    def update_snake(self):
        head_x, head_y = self.snake[0]
        if self.direction == 'up':
            new_head = (head_x, head_y + 1)
        elif self.direction == 'down':
            new_head = (head_x, head_y - 1)
        elif self.direction == 'left':
            new_head = (head_x - 1, head_y)
        elif self.direction == 'right':
            new_head = (head_x + 1, head_y)

        if new_head[0] < 0 or new_head[0] >= BOARD_SIZE or new_head[1] < 0 or new_head[1] >= BOARD_SIZE or new_head in self.snake:
            self.game_over()
            return

        self.snake.insert(0, new_head)
        cmds.button(self.board_cells[new_head[0]][new_head[1]], e=True, bgc=SNAKE_COLOR)

        if new_head == (cmds.button(self.food, q=True, ann=True)):
            self.generate_food()
        else:
            tail = self.snake.pop()
            cmds.button(self.board_cells[tail[0]][tail[1]], e=True, bgc=(0, 0, 0))

    def game_over(self):
        cmds.confirmDialog(title='Game Over', message='Game Over!', button='OK', defaultButton='OK')
        cmds.deleteUI(self.window_name)

    def start_game(self, *args):
        self.create_game_board()
        self.snake = [(BOARD_SIZE // 2, BOARD_SIZE // 2)]

        cmds.button(self.board_cells[BOARD_SIZE // 2][BOARD_SIZE // 2], e=True, bgc=SNAKE_COLOR)
        self.generate_food()
        cmds.refresh(suspend=False)
        self.update_snake()

    def on_key_press(self, key):
        if key == "w" and self.direction != "down":
            self.direction = "up"
        elif key == "s" and self.direction != "up":
            self.direction = "down"
        elif key == "a" and self.direction != "right":
            self.direction = "left"
        elif key == "d" and self.direction != "left":
            self.direction = "right"

    def create_ui(self):
        if cmds.window(self.window_name, exists=True):
            cmds.deleteUI(self.window_name)
        window = cmds.window(self.window_name, title='Snake Game', widthHeight=(500, 500))
        cmds.columnLayout(adjustableColumn=True)
        start_button = cmds.button(label='Start Game', c=self.start_game)
        cmds.showWindow(self.window_name)
        cmds.scriptJob(event=["idle", self.update_snake], parent=self.window_name)
        cmds.scriptJob(event=["KeyPress"], parent=self.window_name, runOnce=True, c=partial(self.on_key_press, "<"))

game_ui = SnakeGameUI()
game_ui.create_ui()
