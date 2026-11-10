"""Shared bark panels and leaf-green menu rows."""

import pygame

import config


def panel(surface, rect):
    pygame.draw.rect(surface, config.COLORS["brown"], rect)
    pygame.draw.rect(surface, config.COLORS["green"], rect, 3)


def menu_rows(surface, title, rows, font, selected=0):
    """Draw a centered panel. Returns the clickable rect for each row."""
    width = 420
    height = 80 + len(rows) * 56
    rect = pygame.Rect(0, 0, width, height)
    rect.center = (config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2)
    panel(surface, rect)
    title_surface = font.render(title, True, config.COLORS["white"])
    surface.blit(title_surface, title_surface.get_rect(midtop=(rect.centerx, rect.y + 16)))
    hits = []
    for index, label in enumerate(rows):
        row = pygame.Rect(rect.x + 40, rect.y + 64 + index * 56, width - 80, 44)
        color = config.COLORS["green"] if index == selected else config.COLORS["dark_blue"]
        pygame.draw.rect(surface, color, row)
        text = font.render(label, True, config.COLORS["white"])
        surface.blit(text, text.get_rect(center=row.center))
        hits.append(row)
    return hits
