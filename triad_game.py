import pygame
import random
import sys

# Инициализация Pygame
pygame.init()

# Константы
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 600
GRID_SIZE = 8
CELL_SIZE = 60
GRID_OFFSET_X = (SCREEN_WIDTH - GRID_SIZE * CELL_SIZE) // 2
GRID_OFFSET_Y = (SCREEN_HEIGHT - GRID_SIZE * CELL_SIZE) // 2

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (255, 0, 255)
CYAN = (0, 255, 255)
ORANGE = (255, 165, 0)
PINK = (255, 192, 203)
BROWN = (165, 42, 42)
TEAL = (0, 128, 128)
LIME = (0, 255, 0)
PURPLE_DARK = (128, 0, 128)

GRAY = (200, 200, 200)

# Уровни с прогрессией 1.45, начиная с 600
LEVELS = [(1, 600), (2, 870), (3, 1262), (4, 1829), (5, 2654), (6, 3848), (7, 5581), (8, 8092), (9, 11733), (10, 17008)]

# Цвета камней
STONE_COLORS = [RED, GREEN, BLUE, YELLOW, PURPLE, PURPLE_DARK, CYAN, ORANGE, PINK, BROWN, TEAL, LIME]
STONE_COLORS_DICT = {RED: "RED", GREEN: "GREEN", BLUE: "BLUE", YELLOW: "YELLOW", PURPLE: "PURPLE", CYAN: "CYAN",
                     ORANGE: "ORANGE", PINK: "PINK", BROWN: "BROWN", TEAL: "TEAL", LIME: "LIME",
                     PURPLE_DARK: "PURPLE_DARK"}


class Popup:
    def __init__(self, message, buttons):
        self.message = message
        self.buttons = buttons  # Список кортежей (название, действие)
        self.width = 400
        self.height = 200
        self.x = (SCREEN_WIDTH - self.width) // 2
        self.y = (SCREEN_HEIGHT - self.height) // 2
        self.font = pygame.font.Font(None, 36)
        self.button_font = pygame.font.Font(None, 20)

    def draw(self, screen):
        # Рисуем фон окна
        pygame.draw.rect(screen, WHITE, (self.x, self.y, self.width, self.height))
        pygame.draw.rect(screen, BLACK, (self.x, self.y, self.width, self.height), 3)

        # Рисуем текст сообщения
        message_text = self.font.render(self.message, True, BLACK)
        screen.blit(message_text, (self.x + 20, self.y + 20))

        # Рисуем кнопки
        button_width = 140
        button_height = 40
        spacing = 20
        total_buttons_width = len(self.buttons) * button_width + (len(self.buttons) - 1) * spacing

        start_x = self.x + (self.width - total_buttons_width) // 2

        for i, (button_text, _) in enumerate(self.buttons):
            button_x = start_x + i * (button_width + spacing)
            pygame.draw.rect(screen, GRAY, (button_x, self.y + self.height - 60, button_width, button_height))
            pygame.draw.rect(screen, BLACK, (button_x, self.y + self.height - 60, button_width, button_height), 2)

            text = self.button_font.render(button_text, True, BLACK)
            text_rect = text.get_rect(center=(button_x + button_width // 2, self.y + self.height - 40))
            screen.blit(text, text_rect)

    def clean(self, screen):
        screen.fill(WHITE)

    def handle_click(self, vent):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        # Проверяем клик по кнопкам
        button_width = 140
        button_height = 40
        spacing = 20
        total_buttons_width = len(self.buttons) * button_width + (len(self.buttons) - 1) * spacing

        start_x = self.x + (self.width - total_buttons_width) // 2
        y = self.y + self.height - 60

        for i, (_, action) in enumerate(self.buttons):
            button_x = start_x + i * (button_width + spacing)
            if (button_x <= mouse_x <= button_x + button_width and
                    y <= mouse_y <= y + button_height):
                return action
        return None


class Stone:
    def __init__(self, color, row, col):
        self.color = color
        self.row = row
        self.col = col
        self.x = GRID_OFFSET_X + col * CELL_SIZE + CELL_SIZE // 2
        self.y = GRID_OFFSET_Y + row * CELL_SIZE + CELL_SIZE // 2
        self.selected = False

    def update_position(self):
        """Обновляет позицию камня на основе текущих координат row и col"""
        self.x = GRID_OFFSET_X + self.col * CELL_SIZE + CELL_SIZE // 2
        self.y = GRID_OFFSET_Y + self.row * CELL_SIZE + CELL_SIZE // 2

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (self.x, self.y), CELL_SIZE // 2 - 5)
        if self.selected:
            pygame.draw.circle(screen, WHITE, (self.x, self.y), CELL_SIZE // 2 - 5, 3)


class GameBoard:
    def __init__(self):
        self.grid = [[None for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.level = 1
        self.score = 0
        self.moves = 0
        self.colors = []
        self.initialize_board()

    def initialize_board(self):
        self.colors = STONE_COLORS[:(self.level + 3)]
        print(f"initialize_board: {self.colors}")
        """Инициализация игрового поля случайными камнями"""
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                color = random.choice(self.colors)
                self.grid[row][col] = Stone(color, row, col)

        # Убедиться, что нет начальных совпадений
        while self.has_matches():
            self.clear_matches()
            self.fill_empty_spaces()

    def draw(self, screen):
        """Отрисовка игрового поля"""
        # Рисуем сетку
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                x = GRID_OFFSET_X + col * CELL_SIZE
                y = GRID_OFFSET_Y + row * CELL_SIZE
                pygame.draw.rect(screen, BLACK, (x, y, CELL_SIZE, CELL_SIZE), 1)

        # Рисуем камни
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                if self.grid[row][col]:
                    self.grid[row][col].draw(screen)

    def has_matches(self):
        """Проверяет наличие совпадений на доске"""
        # Проверяем горизонтальные совпадения
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE - 2):
                if (self.grid[row][col] and
                        self.grid[row][col + 1] and
                        self.grid[row][col + 2] and
                        self.grid[row][col].color == self.grid[row][col + 1].color == self.grid[row][col + 2].color):
                    return True

        # Проверяем вертикальные совпадения
        for row in range(GRID_SIZE - 2):
            for col in range(GRID_SIZE):
                if (self.grid[row][col] and
                        self.grid[row + 1][col] and
                        self.grid[row + 2][col] and
                        self.grid[row][col].color == self.grid[row + 1][col].color == self.grid[row + 2][col].color):
                    return True

        return False

    def find_matches(self):
        """Находит все совпадения на доске"""
        matched_stones = set()

        # Проверяем горизонтальные совпадения
        for row in range(GRID_SIZE):
            count = 1
            current_color = self.grid[row][0].color if self.grid[row][0] else None

            for col in range(1, GRID_SIZE):
                if (self.grid[row][col] and
                        self.grid[row][col].color == current_color):
                    count += 1
                else:
                    if count >= 3:
                        for c in range(col - count, col):
                            matched_stones.add((row, c))
                    count = 1
                    current_color = self.grid[row][col].color if self.grid[row][col] else None

            # Проверяем последнюю группу
            if count >= 3:
                for c in range(GRID_SIZE - count, GRID_SIZE):
                    matched_stones.add((row, c))

        # Проверяем вертикальные совпадения
        for col in range(GRID_SIZE):
            count = 1
            current_color = self.grid[0][col].color if self.grid[0][col] else None

            for row in range(1, GRID_SIZE):
                if (self.grid[row][col] and
                        self.grid[row][col].color == current_color):
                    count += 1
                else:
                    if count >= 3:
                        for r in range(row - count, row):
                            matched_stones.add((r, col))
                    count = 1
                    current_color = self.grid[row][col].color if self.grid[row][col] else None

            # Проверяем последнюю группу
            if count >= 3:
                for r in range(GRID_SIZE - count, GRID_SIZE):
                    matched_stones.add((r, col))

        return matched_stones

    def clear_matches(self):
        """Удаляет совпавшие камни"""
        matched_stones = self.find_matches()

        # Удаляем совпавшие камни
        for row, col in matched_stones:
            self.grid[row][col] = None

        # Обновляем счет
        self.score += len(matched_stones) * 10

        return len(matched_stones) > 0

    def fill_empty_spaces(self):
        """Заполняет пустые пространства новыми камнями"""
        # Сдвигаем камни вниз
        for col in range(GRID_SIZE):
            # Собираем камни из столбца (снизу вверх)
            stones = []
            for row in range(GRID_SIZE - 1, -1, -1):
                if self.grid[row][col]:
                    stones.append(self.grid[row][col])

            # Смещаем камни вниз (заполняем пустоты)
            stone_index = 0
            for row in range(GRID_SIZE - 1, -1, -1):
                if stone_index < len(stones):
                    # Помещаем камень из списка
                    self.grid[row][col] = stones[stone_index]
                    self.grid[row][col].row = row
                    self.grid[row][col].update_position()
                    stone_index += 1
                else:
                    # Заполняем пустоты новыми камнями
                    self.grid[row][col] = Stone(random.choice(self.colors), row, col)

    def swap_stones(self, row1, col1, row2, col2):
        """Меняет два камня местами"""
        # Сохраняем временные ссылки на камни
        stone1 = self.grid[row1][col1]
        stone2 = self.grid[row2][col2]

        # Меняем камни местами в сетке
        self.grid[row1][col1] = stone2
        self.grid[row2][col2] = stone1

        # Обновляем координаты камней
        if stone1:
            stone1.row = row2
            stone1.col = col2
            stone1.update_position()

        if stone2:
            stone2.row = row1
            stone2.col = col1
            stone2.update_position()

        # Вывод информации о_SWAP
        if stone1 and stone2:
            col_before = STONE_COLORS_DICT[stone1.color]
            col_after = STONE_COLORS_DICT[stone2.color]
            print(
                f'Swap stones: Col: {col1}, Row: {row1}, Color: {col_before} with Col: {col2}, Row: {row2}, Color: {col_after}')

    def is_valid_move(self, row1, col1, row2, col2):
        """Проверяет, является ли обмен камнями допустимым"""
        # Проверяем, являются ли камни соседними
        if abs(row1 - row2) + abs(col1 - col2) != 1:
            return False

        # Меняем камни местами
        self.swap_stones(row1, col1, row2, col2)

        # Проверяем, есть ли совпадения после обмена
        has_match = self.has_matches()

        # Возвращаем камни на место
        self.swap_stones(row1, col1, row2, col2)

        return has_match


def main():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Три в ряд")
    clock = pygame.time.Clock()

    game_board = GameBoard()
    popup = None  # Всплывающее окно

    selected_stone = None

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()

                # Проверяем, попал ли клик по игровому полю
                if (GRID_OFFSET_X <= mouse_x <= GRID_OFFSET_X + GRID_SIZE * CELL_SIZE and
                        GRID_OFFSET_Y <= mouse_y <= GRID_OFFSET_Y + GRID_SIZE * CELL_SIZE):

                    # Преобразуем координаты мыши в индексы сетки
                    col = (mouse_x - GRID_OFFSET_X) // CELL_SIZE
                    row = (mouse_y - GRID_OFFSET_Y) // CELL_SIZE

                    print(f'User clicked on Col: {col}, Row: {row}')

                    # Если камень уже выбран, пытаемся его переместить
                    if selected_stone:
                        selected_row, selected_col = selected_stone.row, selected_stone.col
                        print(f'User selected stone on Col: {col}, Row: {row}')

                        # Проверяем, является ли новый камень соседним с выбранным
                        if (abs(selected_row - row) + abs(selected_col - col)) == 1:
                            # Проверяем, допустим ли обмен
                            if game_board.is_valid_move(selected_row, selected_col, row, col):
                                print(f'Valid move selected stone on Col: {col}, Row: {row}')
                                # Меняем местами камни
                                game_board.swap_stones(selected_row, selected_col, row, col)

                                # Удаляем совпадения и заполняем пустоты
                                while game_board.clear_matches():
                                    game_board.fill_empty_spaces()

                                # Увеличиваем счетчик ходов
                                game_board.moves += 1
                            else:
                                # Если обмен недопустим, просто сбрасываем выбор
                                pass

                        # col_before = STONE_COLORS_DICT[game_board.grid[row][col].color]
                        # col_after = STONE_COLORS_DICT[game_board.grid[selected_row][selected_col].color]
                        # print(f'Now (after swap stones) Col: {col}, Row: {row}, Color: {col_before} with Col: {selected_col}, Row: {selected_row}, Color: {col_after}')
                        # Сбрасываем выбор
                        selected_stone.selected = False
                        selected_stone = None
                    else:
                        # Выбираем камень
                        if game_board.grid[row][col]:
                            selected_stone = game_board.grid[row][col]
                            selected_stone.selected = True
                # Проверяем клик по всплывающему окну
                if popup:
                    action = popup.handle_click(event)
                    if action == "restart":
                        print(f'User clicked on {action}')
                        # Перезапуск игры
                        game_board = GameBoard()
                        popup = None
                        # Явная очистка экрана после перезапуска
                        screen.fill(WHITE)
                    elif action == "close":
                        # Закрытие игры
                        running = False

        # Отрисовка
        screen.fill(WHITE)
        game_board.draw(screen)

        # Отображение счета и количества ходов
        font = pygame.font.Font(None, 36)
        level_text = font.render(f"Уровень: {game_board.level}", True, BLACK)
        score_text = font.render(f"Счет: {game_board.score}", True, BLACK)
        moves_text = font.render(f"Ходы: {game_board.moves}", True, BLACK)
        screen.blit(level_text, (10, 10))
        screen.blit(score_text, (150, 10))
        screen.blit(moves_text, (280, 10))

        # Отображение инструкции
        instruction_font = pygame.font.Font(None, 24)
        instruction_text = instruction_font.render("Выберите камень и щелкните по соседнему", True, BLACK)
        screen.blit(instruction_text, (10, SCREEN_HEIGHT - 30))

        # Отображение сообщения о победе
        if game_board.score >= LEVELS[game_board.level - 1][
            1]:  # Условие победы - набрать нужное количество очков для уровня
            # win_font = pygame.font.Font(None, 48)
            # win_text = win_font.render("ПОБЕДА!", True, RED)
            # # (SCREEN_WIDTH // 2 - 60, SCREEN_HEIGHT // 2)
            # screen.blit(win_text, (280, 5))

            # Проверяем, не достигли ли мы максимального уровня
            if game_board.level < len(LEVELS):
                game_board.level += 1
                game_board.initialize_board()
                game_board.draw(screen)
            else:
                # Достигнут максимальный уровень - победа
                popup = Popup("Поздравляем! Вы выиграли!", [("Закрыть", "close"), ("Сыграть заново", "restart")])

        # Отрисовка всплывающего окна - только если popup существует
        if popup:
            popup.draw(screen)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
