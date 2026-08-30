from random import randint

import pygame

# Константы для размеров поля и сетки:
SCREEN_WIDTH: int = 640
SCREEN_HEIGHT: int = 480
GRID_SIZE: int = 20
GRID_WIDTH: int = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT: int = SCREEN_HEIGHT // GRID_SIZE

# Направления движения:
UP: tuple[int, int] = (0, -1)
DOWN: tuple[int, int] = (0, 1)
LEFT: tuple[int, int] = (-1, 0)
RIGHT: tuple[int, int] = (1, 0)

# Цвета игры:
BOARD_BACKGROUND_COLOR: tuple[int, int, int] = (0, 0, 0)
BORDER_COLOR: tuple[int, int, int] = (93, 216, 228)
APPLE_COLOR: tuple[int, int, int] = (255, 0, 0)
SNAKE_COLOR: tuple[int, int, int] = (0, 255, 0)

# Скорость движения змейки:
SPEED: int = 20

# Настройка игрового окна:
screen: pygame.Surface = pygame.display.set_mode(
    (SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32
)
pygame.display.set_caption('Змейка')
clock: pygame.time.Clock = pygame.time.Clock()


class GameObject:
    """Базовый класс для игровых объектов."""

    def __init__(
        self,
        body_color: tuple[int, int, int] | None = None
    ) -> None:
        """Инициализирует базовые атрибуты игрового объекта."""
        self.position: tuple[int, int] = (
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT // 2
        )
        self.body_color: tuple[int, int, int] | None = body_color

    def draw_cell(
        self,
        position: tuple[int, int] | None = None,
        color: tuple[int, int, int] | None = None
    ) -> None:
        """Отрисовывает одну ячейку сетки игрового поля."""
        pos = position if position is not None else self.position
        cell_color = color if color is not None else self.body_color
        rect = pygame.Rect(pos, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, cell_color, rect)
        if cell_color != BOARD_BACKGROUND_COLOR:
            pygame.draw.rect(screen, BORDER_COLOR, rect, 1)

    def draw(self) -> None:
        """Отрисовывает объект на игровом поле."""
        raise NotImplementedError(
            'Метод draw должен быть переопределен в дочернем классе.'
        )


class Apple(GameObject):
    """Класс, представляющий яблоко на игровом поле."""

    def __init__(
        self,
        occupied_positions: list[tuple[int, int]] | None = None,
        body_color: tuple[int, int, int] = APPLE_COLOR
    ) -> None:
        """Инициализирует яблоко и задает его случайную позицию."""
        super().__init__(body_color)
        self.randomize_position(occupied_positions or [])

    def randomize_position(
        self,
        occupied_positions: list[tuple[int, int]] | None = None
    ) -> None:
        """Устанавливает случайное положение яблока на игровом поле."""
        occupied = occupied_positions or []
        while True:
            new_pos = (
                randint(0, GRID_WIDTH - 1) * GRID_SIZE,
                randint(0, GRID_HEIGHT - 1) * GRID_SIZE,
            )
            if new_pos not in occupied:
                self.position = new_pos
                break

    def draw(self) -> None:
        """Отрисовывает яблоко на игровой поверхности."""
        self.draw_cell()


class Snake(GameObject):
    """Класс, представляющий змейку и управляющий ее состоянием."""

    def __init__(
        self,
        body_color: tuple[int, int, int] = SNAKE_COLOR
    ) -> None:
        """Инициализирует начальное состояние змейки."""
        super().__init__(body_color)
        self.length: int = 1
        self.positions: list[tuple[int, int]] = []
        self.direction: tuple[int, int] = RIGHT
        self.next_direction: tuple[int, int] | None = None
        self.last: tuple[int, int] | None = None
        self.reset()

    def get_head_position(self) -> tuple[int, int]:
        """Возвращает позицию головы змейки."""
        return self.positions[0]

    def reset(self) -> None:
        """Сбрасывает змейку в исходное состояние."""
        self.length = 1
        self.positions = [(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)]
        self.direction = RIGHT
        self.next_direction = None
        self.last = None

    def update_direction(self) -> None:
        """Обновляет направление движения змейки."""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def move(self) -> None:
        """Обновляет позицию змейки, перемещая её на одну клетку."""
        head_x, head_y = self.get_head_position()
        dx, dy = self.direction
        new_x = (head_x + dx * GRID_SIZE) % SCREEN_WIDTH
        new_y = (head_y + dy * GRID_SIZE) % SCREEN_HEIGHT
        new_head = (new_x, new_y)

        self.positions.insert(0, new_head)
        if len(self.positions) > self.length:
            self.last = self.positions.pop()
        else:
            self.last = None

    def draw(self) -> None:
        """Отрисовывает змейку на игровом поле."""
        for position in self.positions[:-1]:
            self.draw_cell(position)

        self.draw_cell(self.get_head_position())

        if self.last:
            self.draw_cell(self.last, BOARD_BACKGROUND_COLOR)


def handle_keys(game_object: Snake) -> None:
    """Обрабатывает нажатия клавиш для смены направления движения."""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and game_object.direction != DOWN:
                game_object.next_direction = UP
            elif event.key == pygame.K_DOWN and game_object.direction != UP:
                game_object.next_direction = DOWN
            elif event.key == pygame.K_LEFT and game_object.direction != RIGHT:
                game_object.next_direction = LEFT
            elif event.key == pygame.K_RIGHT and game_object.direction != LEFT:
                game_object.next_direction = RIGHT


def main() -> None:
    """Основной цикл игры Змейка."""
    pygame.init()
    snake = Snake()
    apple = Apple(snake.positions)
    screen.fill(BOARD_BACKGROUND_COLOR)

    while True:
        clock.tick(SPEED)
        handle_keys(snake)
        snake.update_direction()
        snake.move()

        if snake.get_head_position() == apple.position:
            snake.length += 1
            apple.randomize_position(snake.positions)
        elif snake.get_head_position() in snake.positions[2:]:
            snake.reset()
            screen.fill(BOARD_BACKGROUND_COLOR)
            apple.randomize_position(snake.positions)

        apple.draw()
        snake.draw()
        pygame.display.update()


if __name__ == '__main__':
    main()
