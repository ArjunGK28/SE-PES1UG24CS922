import math
import random
import pygame

GRID_SIZE = 8
TILE_SIZE = 60
GEM_POINTS = 10
BLAST_FLASH_MS = 350
GEM_COLORS = [
    (220, 50, 50),   # Red
    (50, 200, 50),   # Green
    (50, 100, 240),  # Blue
    (240, 200, 40),  # Yellow
    (180, 50, 220),  # Purple
    (240, 130, 40),  # Orange
]


class Gem:
   
    def __init__(self, color, target_row, col):
        self.color = color
        self.target_row = target_row
        self.col = col
        self.current_y = (target_row - 2) * TILE_SIZE
        self.target_y = target_row * TILE_SIZE
        self.fall_speed = 12.0
        self.special = None

    def update(self):
        if self.current_y < self.target_y:
            self.current_y += self.fall_speed
            if self.current_y > self.target_y:
                self.current_y = self.target_y

    def is_animating(self):
        return self.current_y < self.target_y


class Board:

    def __init__(self, offset_x, offset_y, target_score=500, max_moves=20):
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.target_score = target_score
        self.max_moves = max_moves
        self.grid = [[None for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.selected = None
        self.score = 0
        self.moves_remaining = max_moves
        self.last_points = 0
        self.last_combo = 0
        self.blasts = []
        self.hint = None
        self.reset()

    def reset(self):
        self.score = 0
        self.moves_remaining = self.max_moves
        self.last_points = 0
        self.last_combo = 0
        self.blasts = []
        self.hint = None
        self.selected = None
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                color = random.choice(GEM_COLORS)
                gem = Gem(color, r, c)
                gem.current_y = gem.target_y  
                self.grid[r][c] = gem

        self.resolve_matches(spawn_specials=False)

    def is_animating(self):
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                if self.grid[r][c] and self.grid[r][c].is_animating():
                    return True
        return False

    def swap_gems(self, pos1, pos2):
        r1, c1 = pos1
        r2, c2 = pos2

        g1, g2 = self.grid[r1][c1], self.grid[r2][c2]
        self.grid[r1][c1], self.grid[r2][c2] = g2, g1

        if self.grid[r1][c1]:
            self.grid[r1][c1].target_row = r1
            self.grid[r1][c1].target_y = r1 * TILE_SIZE
            self.grid[r1][c1].current_y = r1 * TILE_SIZE

        if self.grid[r2][c2]:
            self.grid[r2][c2].target_row = r2
            self.grid[r2][c2].target_y = r2 * TILE_SIZE
            self.grid[r2][c2].current_y = r2 * TILE_SIZE

    def is_adjacent(self, pos1, pos2):
        r1, c1 = pos1
        r2, c2 = pos2
        return abs(r1 - r2) + abs(c1 - c2) == 1

    def same_color(self, pos1, pos2):
        g1 = self.grid[pos1[0]][pos1[1]]
        g2 = self.grid[pos2[0]][pos2[1]]
        return g1 is not None and g2 is not None and g1.color == g2.color

    def find_runs(self):
        lines = [("row", [(r, c) for c in range(GRID_SIZE)]) for r in range(GRID_SIZE)]
        lines += [("col", [(r, c) for r in range(GRID_SIZE)]) for c in range(GRID_SIZE)]

        runs = []
        for orientation, line in lines:
            start = 0
            for i in range(1, GRID_SIZE + 1):
                if i < GRID_SIZE and self.same_color(line[start], line[i]):
                    continue
                if i - start >= 3:
                    runs.append((orientation, line[start:i]))
                start = i
        return runs

    def find_matches(self):
        matched = set()
        for _, cells in self.find_runs():
            matched.update(cells)
        return matched

    def find_hint(self):
        grid = self.grid
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                for r2, c2 in ((r, c + 1), (r + 1, c)):
                    if r2 < GRID_SIZE and c2 < GRID_SIZE:
                        grid[r][c], grid[r2][c2] = grid[r2][c2], grid[r][c]
                        makes_match = bool(self.find_runs())
                        grid[r][c], grid[r2][c2] = grid[r2][c2], grid[r][c]
                        if makes_match:
                            return (r, c), (r2, c2)
        return None

    def drop_and_refill(self):
        for c in range(GRID_SIZE):
            empty_slots = 0
            for r in range(GRID_SIZE - 1, -1, -1):
                if self.grid[r][c] is None:
                    empty_slots += 1
                elif empty_slots > 0:
                    gem = self.grid[r][c]
                    gem.target_row = r + empty_slots
                    gem.target_y = (r + empty_slots) * TILE_SIZE
                    self.grid[r + empty_slots][c] = gem
                    self.grid[r][c] = None

            for r in range(empty_slots):
                color = random.choice(GEM_COLORS)
                gem = Gem(color, r, c)
                gem.current_y = -((empty_slots - r) * TILE_SIZE)
                self.grid[r][c] = gem

    def detonate_specials(self, cleared):
        pending = [(r, c) for r, c in cleared if self.grid[r][c].special]
        while pending:
            r, c = pending.pop()
            if self.grid[r][c].special == "row":
                line = [(r, i) for i in range(GRID_SIZE)]
                self.blasts.append(("row", r, pygame.time.get_ticks()))
            else:
                line = [(i, c) for i in range(GRID_SIZE)]
                self.blasts.append(("col", c, pygame.time.get_ticks()))

            for pos in line:
                if pos not in cleared:
                    cleared.add(pos)
                    if self.grid[pos[0]][pos[1]].special:
                        pending.append(pos)

    def resolve_matches(self, swapped=(), spawn_specials=True):
        points = 0
        cascades = 0
        while True:
            runs = self.find_runs()
            if not runs:
                break
            cascades += 1

            cleared = set()
            for _, cells in runs:
                cleared.update(cells)
            self.detonate_specials(cleared)
            points += len(cleared) * GEM_POINTS * cascades

            if spawn_specials:
                for orientation, cells in runs:
                    if len(cells) >= 4:
                        r, c = next((pos for pos in cells if pos in swapped), cells[1])
                        self.grid[r][c].special = orientation
                        cleared.discard((r, c))

            for r, c in cleared:
                self.grid[r][c] = None
            self.drop_and_refill()
            swapped = ()
        return points, cascades

    def process_swap(self, pos1, pos2):
        if not self.is_adjacent(pos1, pos2) or self.is_game_over() or self.is_animating():
            return False

        self.swap_gems(pos1, pos2)
        matches = self.find_matches()

        if not matches:
            self.swap_gems(pos1, pos2)
            return False

        self.moves_remaining -= 1
        self.hint = None
        self.last_points, self.last_combo = self.resolve_matches(swapped=(pos1, pos2))
        self.score += self.last_points
        return True

    def is_game_over(self):
        return self.score >= self.target_score or self.moves_remaining <= 0

    def check_result(self):
        if self.score >= self.target_score:
            return "WIN"
        if self.moves_remaining <= 0:
            return "LOSS"
        return None

    def update(self):
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                if self.grid[r][c]:
                    self.grid[r][c].update()

        now = pygame.time.get_ticks()
        self.blasts = [b for b in self.blasts if now - b[2] < BLAST_FLASH_MS]

    def render_special(self, surface, gem, x, y):
        pulse = (math.sin(pygame.time.get_ticks() / 180) + 1) / 2
        glow = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        pygame.draw.rect(
            glow,
            (255, 255, 255, int(110 + 145 * pulse)),
            glow.get_rect(),
            width=5,
            border_radius=12,
        )
        surface.blit(glow, (x, y))

        mid = TILE_SIZE // 2
        if gem.special == "row":
            stripe = pygame.Rect(x + 9, y + mid - 4, TILE_SIZE - 18, 8)
        else:
            stripe = pygame.Rect(x + mid - 4, y + 9, 8, TILE_SIZE - 18)
        pygame.draw.rect(surface, (255, 255, 255), stripe, border_radius=4)

    def render_hint(self, surface):
        pulse = (math.sin(pygame.time.get_ticks() / 300) + 1) / 2
        for r, c in self.hint:
            shimmer = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
            tile_rect = shimmer.get_rect().inflate(-4, -4)
            pygame.draw.rect(
                shimmer, (255, 255, 255, int(30 + 60 * pulse)), tile_rect, border_radius=10
            )
            pygame.draw.rect(
                shimmer,
                (255, 240, 150, int(80 + 175 * pulse)),
                tile_rect,
                width=3,
                border_radius=10,
            )
            surface.blit(
                shimmer, (self.offset_x + c * TILE_SIZE, self.offset_y + r * TILE_SIZE)
            )

    def render_blasts(self, surface):
        now = pygame.time.get_ticks()
        for orientation, index, started in self.blasts:
            fade = 1 - (now - started) / BLAST_FLASH_MS
            if fade <= 0:
                continue
            if orientation == "row":
                rect = pygame.Rect(
                    self.offset_x, self.offset_y + index * TILE_SIZE, GRID_SIZE * TILE_SIZE, TILE_SIZE
                )
            else:
                rect = pygame.Rect(
                    self.offset_x + index * TILE_SIZE, self.offset_y, TILE_SIZE, GRID_SIZE * TILE_SIZE
                )
            flash = pygame.Surface(rect.size, pygame.SRCALPHA)
            flash.fill((255, 255, 255, int(210 * fade)))
            surface.blit(flash, rect.topleft)

    def render(self, surface):
        board_rect = pygame.Rect(
            self.offset_x, self.offset_y, GRID_SIZE * TILE_SIZE, GRID_SIZE * TILE_SIZE
        )
        pygame.draw.rect(surface, (20, 22, 28), board_rect, border_radius=8)
        pygame.draw.rect(surface, (60, 65, 75), board_rect, width=3, border_radius=8)

        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                gem = self.grid[r][c]
                if gem:
                    x = self.offset_x + c * TILE_SIZE
                    y = self.offset_y + gem.current_y
                    tile_rect = pygame.Rect(x + 2, y + 2, TILE_SIZE - 4, TILE_SIZE - 4)

                    pygame.draw.rect(surface, gem.color, tile_rect, border_radius=10)
                    pygame.draw.rect(
                        surface, (255, 255, 255), tile_rect, width=1, border_radius=10
                    )
                    if gem.special:
                        self.render_special(surface, gem, x, int(y))

                if self.selected == (r, c):
                    sel_x = self.offset_x + c * TILE_SIZE
                    sel_y = self.offset_y + r * TILE_SIZE
                    sel_rect = pygame.Rect(sel_x + 2, sel_y + 2, TILE_SIZE - 4, TILE_SIZE - 4)
                    pygame.draw.rect(
                        surface, (255, 255, 255), sel_rect, width=4, border_radius=10
                    )

        if self.hint:
            self.render_hint(surface)
        self.render_blasts(surface)
