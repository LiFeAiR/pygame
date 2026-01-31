class Cell:
    def __init__(self):
        self.is_mine = False
        self.is_open = False
        self.is_flagged = False
        self.adjacent_mines = 0


import random


# Класс Cell, который мы написали выше, должен быть здесь...

class GameBoard:
    def __init__(self, width, height, mines_count):
        self.width = width
        self.height = height
        self.mines_count = mines_count

        self.board = [[Cell() for _ in range(width)] for _ in range(height)]

        # Добавляем эти две строки:
        self._place_mines()
        self._calculate_adjacent_mines()
        self.game_over = False

    def _place_mines(self):
        # Создаем список всех возможных координат (строка, столбец)
        all_coords = [(r, c) for r in range(self.height) for c in range(self.width)]

        # Выбираем из списка случайные уникальные координаты для мин
        mine_coords = random.sample(all_coords, self.mines_count)

        # В ячейках по этим координатам ставим мины
        for r, c in mine_coords:
            self.board[r][c].is_mine = True

    def _calculate_adjacent_mines(self):
        # Проходим по каждой ячейке поля
        for r in range(self.height):
            for c in range(self.width):
                # Если в ячейке уже есть мина, считать ничего не нужно
                if self.board[r][c].is_mine:
                    continue

                mine_count = 0
                # Проверяем всех 8 соседей
                for dr in [-1, 0, 1]:  # Смещение по строке
                    for dc in [-1, 0, 1]:  # Смещение по столбцу
                        # Пропускаем саму текущую ячейку
                        if dr == 0 and dc == 0:
                            continue

                        # Вычисляем координаты соседа
                        nr, nc = r + dr, c + dc

                        # ВАЖНО: Проверяем, что сосед не вышел за границы поля
                        if 0 <= nr < self.height and 0 <= nc < self.width:
                            if self.board[nr][nc].is_mine:
                                mine_count += 1

                # Записываем результат в ячейку
                self.board[r][c].adjacent_mines = mine_count

    def open_cell(self, r, c):
        # Получаем ячейку, по которой кликнули
        cell = self.board[r][c]

        # Нельзя открыть уже открытую ячейку или ячейку с флагом
        if cell.is_open or cell.is_flagged:
            return

        cell.is_open = True

        # Если это была мина - игра окончена
        if cell.is_mine:
            self.game_over = True
            return  # Сразу выходим

        # Магия "Сапёра": если ячейка пустая, открываем соседей
        if cell.adjacent_mines == 0 and not cell.is_mine:
            # Проходим по всем 8 соседям
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    if dr == 0 and dc == 0:
                        continue

                    nr, nc = r + dr, c + dc

                    # Убеждаемся, что сосед в пределах поля
                    if 0 <= nr < self.height and 0 <= nc < self.width:
                        # И рекурсивно вызываем эту же функцию для соседа!
                        self.open_cell(nr, nc)

    def toggle_flag(self, r, c):
        cell = self.board[r][c]
        # Флаг можно ставить только на закрытые ячейки
        if not cell.is_open:
            cell.is_flagged = not cell.is_flagged


import pygame

# --- Константы ---
# Размеры поля в ячейках
BOARD_WIDTH = 15
BOARD_HEIGHT = 15
MINES_COUNT = 2

# Размер одной ячейки в пикселях
CELL_SIZE = 30

# Рассчитываем размер окна в пикселях
SCREEN_WIDTH = BOARD_WIDTH * CELL_SIZE
SCREEN_HEIGHT = BOARD_HEIGHT * CELL_SIZE

# Цвета (в формате RGB)
BG_COLOR = (192, 192, 192)  # Серый
LINE_COLOR = (128, 128, 128)  # Темно-серый

# --- Инициализация Pygame и создание окна ---
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Сапёр")
# Добавляем создание шрифта
font = pygame.font.SysFont('Arial', CELL_SIZE // 2)


def draw_board(board_obj):
    screen.fill(BG_COLOR)

    for r in range(board_obj.height):
        for c in range(board_obj.width):
            cell = board_obj.board[r][c]
            x = c * CELL_SIZE
            y = r * CELL_SIZE
            rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)

            # Рисуем контур ячейки
            pygame.draw.rect(screen, LINE_COLOR, rect, 1)

            # Если ячейка открыта
            if cell.is_open:
                if cell.is_mine:
                    # Рисуем мину (красный круг)
                    pygame.draw.circle(screen, (255, 0, 0), rect.center, CELL_SIZE // 3)
                elif cell.adjacent_mines > 0:
                    # Рисуем цифру
                    text = font.render(str(cell.adjacent_mines), True, (0, 0, 0))
                    text_rect = text.get_rect(center=rect.center)
                    screen.blit(text, text_rect)
            # Если стоит флаг
            elif cell.is_flagged:
                # Рисуем флаг (желтый треугольник)
                pygame.draw.polygon(screen, (255, 255, 0),
                                    [(rect.left + 5, rect.top + 5),
                                     (rect.right - 5, rect.centery),
                                     (rect.left + 5, rect.bottom - 5)])


# --- Создание игрового поля ---
game_board = GameBoard(BOARD_WIDTH, BOARD_HEIGHT, MINES_COUNT)

# --- Главный игровой цикл ---
running = True
i = 0
clock = pygame.time.Clock()
while running:
    # 1. Обработка событий
    for event in pygame.event.get():
        # Если пользователь нажал на "крестик"
        if event.type == pygame.QUIT:
            running = False

        # ДОБАВЛЯЕМ ЭТОТ БЛОК:
        # Если произошло событие "кнопка мыши нажата"
        if event.type == pygame.MOUSEBUTTONDOWN and not game_board.game_over:
            # Получаем координаты клика в пикселях
            mouse_x, mouse_y = pygame.mouse.get_pos()

            # Превращаем пиксели в координаты ячейки
            clicked_col = mouse_x // CELL_SIZE
            clicked_row = mouse_y // CELL_SIZE

            # Если левая кнопка мыши
            if event.button == 1:
                game_board.open_cell(clicked_row, clicked_col)

            # Если правая кнопка мыши
            elif event.button == 3:
                game_board.toggle_flag(clicked_row, clicked_col)

    # 2. Отрисовка
    draw_board(game_board)

    keys = pygame.key.get_pressed()
    if keys[pygame.K_i]:
            i = i + 1
            print(f"Инфо:{i}")

    # Если игра окончена, показываем сообщение
    if game_board.game_over:
        # Полупрозрачный черный фон
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        screen.blit(overlay, (0, 0))

        # Текст
        text = font.render("Вы проиграли!", True, (255, 255, 255))
        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        screen.blit(text, text_rect)

    # 3. Обновление экрана
    pygame.display.flip()

    # limits FPS to 24
    # dt is delta time in seconds since last frame, used for framerate-
    # independent physics.
    dt = clock.tick(24) / 1000

# Корректное завершение работы
pygame.quit()
