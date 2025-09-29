"""
Forest Survival - Inventory System
Modern inventory UI with drag-and-drop, animations, and item management.
"""

import pygame
import math
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum

import config
from src.core.input_manager import InputManager
from src.core.audio_manager import AudioManager
from src.ui.hud_system import HUDElement


class ItemRarity(Enum):
    """Item rarity levels."""
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"


class ItemType(Enum):
    """Item types."""
    WEAPON = "weapon"
    ARMOR = "armor"
    CONSUMABLE = "consumable"
    MATERIAL = "material"
    KEY_ITEM = "key_item"
    TOOL = "tool"


class Item:
    """Game item with properties and metadata."""
    
    def __init__(self, item_id: str, name: str, item_type: ItemType, 
                 rarity: ItemRarity = ItemRarity.COMMON, stack_size: int = 1):
        self.item_id = item_id
        self.name = name
        self.item_type = item_type
        self.rarity = rarity
        self.stack_size = stack_size
        
        # Properties
        self.description = ""
        self.icon_path = None
        self.weight = 1.0
        self.value = 10
        
        # Weapon/Armor specific
        self.damage = 0
        self.defense = 0
        self.durability = 100
        self.max_durability = 100
        
        # Consumable specific
        self.heal_amount = 0
        self.effect_duration = 0.0
        self.effects: List[str] = []
    
    def get_rarity_color(self) -> Tuple[int, int, int]:
        """Get color based on item rarity."""
        rarity_colors = {
            ItemRarity.COMMON: config.COLORS['gray'],
            ItemRarity.UNCOMMON: config.COLORS['green'],
            ItemRarity.RARE: config.COLORS['blue'],
            ItemRarity.EPIC: config.COLORS['purple'],
            ItemRarity.LEGENDARY: config.COLORS['orange']
        }
        return rarity_colors.get(self.rarity, config.COLORS['white'])
    
    def get_tooltip_text(self) -> List[str]:
        """Get tooltip text lines."""
        lines = [self.name]
        
        if self.description:
            lines.append(self.description)
        
        lines.append("")  # Empty line
        
        if self.item_type == ItemType.WEAPON:
            lines.append(f"Damage: {self.damage}")
            lines.append(f"Durability: {self.durability}/{self.max_durability}")
        elif self.item_type == ItemType.ARMOR:
            lines.append(f"Defense: {self.defense}")
            lines.append(f"Durability: {self.durability}/{self.max_durability}")
        elif self.item_type == ItemType.CONSUMABLE:
            if self.heal_amount > 0:
                lines.append(f"Heals: {self.heal_amount} HP")
            if self.effects:
                lines.append(f"Effects: {', '.join(self.effects)}")
        
        lines.append("")
        lines.append(f"Value: {self.value} gold")
        lines.append(f"Weight: {self.weight} kg")
        lines.append(f"Rarity: {self.rarity.value.title()}")
        
        return lines


class ItemStack:
    """Stack of items in inventory."""
    
    def __init__(self, item: Item, quantity: int = 1):
        self.item = item
        self.quantity = min(quantity, item.stack_size)
    
    def can_add(self, amount: int) -> bool:
        """Check if can add amount to this stack."""
        return self.quantity + amount <= self.item.stack_size
    
    def add(self, amount: int) -> int:
        """Add amount to stack. Returns amount that couldn't be added."""
        can_add = min(amount, self.item.stack_size - self.quantity)
        self.quantity += can_add
        return amount - can_add
    
    def remove(self, amount: int) -> int:
        """Remove amount from stack. Returns amount actually removed."""
        removed = min(amount, self.quantity)
        self.quantity -= removed
        return removed
    
    def split(self, amount: int) -> Optional['ItemStack']:
        """Split stack. Returns new stack with amount, or None if can't split."""
        if amount >= self.quantity or amount <= 0:
            return None
        
        self.quantity -= amount
        return ItemStack(self.item, amount)


class InventorySlot(HUDElement):
    """Individual inventory slot with drag-and-drop support."""
    
    def __init__(self, x: float, y: float, size: float, slot_index: int):
        super().__init__(x, y, size, size)
        self.slot_index = slot_index
        self.item_stack: Optional[ItemStack] = None
        
        # Visual properties
        self.slot_size = size
        self.background_color = config.COLORS['dark_gray']
        self.border_color = config.COLORS['gray']
        self.highlight_color = config.COLORS['cyan']
        self.selected_color = config.COLORS['yellow']
        
        # State
        self.hovered = False
        self.selected = False
        self.being_dragged = False
        self.can_drop = False
        
        # Animation
        self.hover_scale = 1.0
        self.highlight_intensity = 0.0
        self.icon_bounce = 0.0
        
        # Font for quantity display
        self.font = pygame.font.Font(None, 20)
    
    def set_item_stack(self, item_stack: Optional[ItemStack]):
        """Set the item stack in this slot."""
        if item_stack != self.item_stack:
            self.item_stack = item_stack
            if item_stack:
                self.icon_bounce = 0.3  # Bounce animation when item added
    
    def is_empty(self) -> bool:
        """Check if slot is empty."""
        return self.item_stack is None or self.item_stack.quantity <= 0
    
    def _update_animations(self, dt: float):
        """Update slot animations."""
        # Hover scale
        target_scale = 1.1 if self.hovered else 1.0
        scale_speed = 8.0
        
        if self.hover_scale < target_scale:
            self.hover_scale = min(target_scale, self.hover_scale + scale_speed * dt)
        elif self.hover_scale > target_scale:
            self.hover_scale = max(target_scale, self.hover_scale - scale_speed * dt)
        
        # Highlight intensity
        target_highlight = 1.0 if (self.selected or self.can_drop) else 0.0
        highlight_speed = 6.0
        
        if self.highlight_intensity < target_highlight:
            self.highlight_intensity = min(target_highlight, self.highlight_intensity + highlight_speed * dt)
        elif self.highlight_intensity > target_highlight:
            self.highlight_intensity = max(target_highlight, self.highlight_intensity - highlight_speed * dt)
        
        # Icon bounce
        self.icon_bounce = max(0.0, self.icon_bounce - dt * 3)
    
    def update(self, dt: float, mouse_pos: Tuple[int, int]):
        """Update slot state."""
        super().update(dt, 0, 0)  # No screen size dependency
        
        # Check hover
        was_hovered = self.hovered
        self.hovered = self.is_point_inside(mouse_pos)
        
        if self.hovered != was_hovered and self.hovered:
            # Play hover sound
            pass  # Audio manager would be passed from inventory system
    
    def render(self, surface: pygame.Surface):
        """Render the inventory slot."""
        if not self.visible:
            return
        
        # Calculate render position with scale
        scaled_size = self.slot_size * self.hover_scale
        offset = (scaled_size - self.slot_size) / 2
        render_rect = pygame.Rect(self.x - offset, self.y - offset, scaled_size, scaled_size)
        
        # Draw slot background
        bg_color = self.background_color
        if self.can_drop:
            bg_color = self._blend_colors(bg_color, config.COLORS['green'], 0.3)
        elif self.selected:
            bg_color = self._blend_colors(bg_color, self.selected_color, 0.2)
        
        pygame.draw.rect(surface, bg_color, render_rect)
        
        # Draw border
        border_color = self.border_color
        border_width = 2
        
        if self.highlight_intensity > 0:
            highlight_color = self.highlight_color if not self.can_drop else config.COLORS['green']
            border_color = self._blend_colors(border_color, highlight_color, self.highlight_intensity)
            border_width = int(2 + 2 * self.highlight_intensity)
        
        pygame.draw.rect(surface, border_color, render_rect, border_width)
        
        # Draw item if present
        if not self.is_empty():
            self._draw_item(surface, render_rect)
        
        # Draw rarity glow for rare items
        if not self.is_empty() and self.item_stack.item.rarity != ItemRarity.COMMON:
            self._draw_rarity_glow(surface, render_rect)
    
    def _draw_item(self, surface: pygame.Surface, rect: pygame.Rect):
        """Draw the item in the slot."""
        item = self.item_stack.item
        
        # Draw item icon (placeholder rectangle for now)
        icon_color = item.get_rarity_color()
        icon_size = int(rect.width * 0.7)
        icon_offset = (rect.width - icon_size) // 2
        
        # Apply bounce effect
        bounce_offset = int(math.sin(self.icon_bounce * 10) * 3) if self.icon_bounce > 0 else 0
        
        icon_rect = pygame.Rect(rect.x + icon_offset, rect.y + icon_offset + bounce_offset,
                               icon_size, icon_size)
        
        # Draw icon background
        pygame.draw.rect(surface, icon_color, icon_rect)
        pygame.draw.rect(surface, config.COLORS['white'], icon_rect, 2)
        
        # Draw item type symbol (placeholder)
        symbol_font = pygame.font.Font(None, 24)
        symbol_map = {
            ItemType.WEAPON: "⚔",
            ItemType.ARMOR: "🛡",
            ItemType.CONSUMABLE: "🧪",
            ItemType.MATERIAL: "📦",
            ItemType.KEY_ITEM: "🗝",
            ItemType.TOOL: "🔧"
        }
        symbol = symbol_map.get(item.item_type, "?")
        
        symbol_surface = symbol_font.render(symbol, True, config.COLORS['white'])
        symbol_rect = symbol_surface.get_rect(center=icon_rect.center)
        surface.blit(symbol_surface, symbol_rect)
        
        # Draw quantity if stackable and > 1
        if item.stack_size > 1 and self.item_stack.quantity > 1:
            quantity_text = str(self.item_stack.quantity)
            quantity_surface = self.font.render(quantity_text, True, config.COLORS['white'])
            quantity_rect = quantity_surface.get_rect()
            quantity_rect.bottomright = (rect.right - 2, rect.bottom - 2)
            
            # Quantity background
            bg_rect = quantity_rect.inflate(4, 2)
            pygame.draw.rect(surface, config.COLORS['black'], bg_rect)
            
            surface.blit(quantity_surface, quantity_rect)
        
        # Draw durability bar for equipment
        if item.item_type in [ItemType.WEAPON, ItemType.ARMOR] and item.max_durability > 0:
            durability_ratio = item.durability / item.max_durability
            if durability_ratio < 1.0:  # Only show if damaged
                bar_width = icon_size
                bar_height = 3
                bar_x = icon_rect.x
                bar_y = icon_rect.bottom - bar_height - 2
                
                # Background
                bar_bg = pygame.Rect(bar_x, bar_y, bar_width, bar_height)
                pygame.draw.rect(surface, config.COLORS['black'], bar_bg)
                
                # Durability fill
                fill_width = int(bar_width * durability_ratio)
                if fill_width > 0:
                    fill_color = config.COLORS['green']
                    if durability_ratio < 0.3:
                        fill_color = config.COLORS['red']
                    elif durability_ratio < 0.6:
                        fill_color = config.COLORS['orange']
                    
                    fill_rect = pygame.Rect(bar_x, bar_y, fill_width, bar_height)
                    pygame.draw.rect(surface, fill_color, fill_rect)
    
    def _draw_rarity_glow(self, surface: pygame.Surface, rect: pygame.Rect):
        """Draw glow effect for rare items."""
        if self.item_stack.item.rarity == ItemRarity.COMMON:
            return
        
        glow_color = self.item_stack.item.get_rarity_color()
        glow_intensity = 0.3 + 0.2 * math.sin(self.animation_timer * 3)
        glow_size = 4
        
        glow_surface = pygame.Surface((rect.width + glow_size * 2, rect.height + glow_size * 2), pygame.SRCALPHA)
        
        for i in range(glow_size, 0, -1):
            alpha = int(100 * glow_intensity * (1 - i / glow_size))
            if alpha > 0:
                glow_rect = pygame.Rect(glow_size - i, glow_size - i,
                                      rect.width + i * 2, rect.height + i * 2)
                pygame.draw.rect(glow_surface, (*glow_color, alpha), glow_rect, 2)
        
        surface.blit(glow_surface, (rect.x - glow_size, rect.y - glow_size))
    
    def _blend_colors(self, color1: Tuple[int, int, int], color2: Tuple[int, int, int], 
                     progress: float) -> Tuple[int, int, int]:
        """Blend two colors based on progress."""
        r = int(color1[0] + (color2[0] - color1[0]) * progress)
        g = int(color1[1] + (color2[1] - color1[1]) * progress)
        b = int(color1[2] + (color2[2] - color1[2]) * progress)
        return (r, g, b)


class Tooltip(HUDElement):
    """Item tooltip display."""
    
    def __init__(self):
        super().__init__(0, 0, 200, 100)
        self.item: Optional[Item] = None
        self.font = pygame.font.Font(None, 20)
        self.title_font = pygame.font.Font(None, 24)
        
        # Visual properties
        self.background_color = config.COLORS['black']
        self.border_color = config.COLORS['white']
        self.text_color = config.COLORS['white']
        self.title_color = config.COLORS['cyan']
        
        # Animation
        self.appear_timer = 0.0
        self.appear_delay = 0.5
    
    def show(self, item: Item, mouse_pos: Tuple[int, int]):
        """Show tooltip for item at mouse position."""
        self.item = item
        self.appear_timer = 0.0
        self.visible = True
        
        # Calculate tooltip size based on content
        tooltip_lines = item.get_tooltip_text()
        max_width = 0
        
        for line in tooltip_lines:
            if line:  # Skip empty lines for width calculation
                font = self.title_font if line == tooltip_lines[0] else self.font
                text_width = font.size(line)[0]
                max_width = max(max_width, text_width)
        
        self.width = max_width + 20
        self.height = len(tooltip_lines) * 25 + 10
        
        # Position tooltip near mouse but keep on screen
        self.x = mouse_pos[0] + 15
        self.y = mouse_pos[1] + 15
        
        # Adjust if tooltip would go off screen
        if self.x + self.width > config.SCREEN_WIDTH:
            self.x = mouse_pos[0] - self.width - 15
        if self.y + self.height > config.SCREEN_HEIGHT:
            self.y = mouse_pos[1] - self.height - 15
    
    def hide(self):
        """Hide the tooltip."""
        self.visible = False
        self.item = None
        self.appear_timer = 0.0
    
    def _update_animations(self, dt: float):
        """Update tooltip animations."""
        if self.visible:
            self.appear_timer += dt
    
    def render(self, surface: pygame.Surface):
        """Render the tooltip."""
        if not self.visible or not self.item or self.appear_timer < self.appear_delay:
            return
        
        # Calculate fade-in alpha
        fade_progress = min(1.0, (self.appear_timer - self.appear_delay) / 0.2)
        alpha = int(255 * fade_progress)
        
        # Create tooltip surface
        tooltip_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        # Draw background with alpha
        bg_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        bg_surface.fill((*self.background_color, int(220 * fade_progress)))
        tooltip_surface.blit(bg_surface, (0, 0))
        
        # Draw border
        pygame.draw.rect(tooltip_surface, (*self.item.get_rarity_color(), alpha), 
                        pygame.Rect(0, 0, self.width, self.height), 2)
        
        # Draw text
        tooltip_lines = self.item.get_tooltip_text()
        y_offset = 5
        
        for i, line in enumerate(tooltip_lines):
            if not line:  # Empty line
                y_offset += 15
                continue
            
            # Use title font for item name
            font = self.title_font if i == 0 else self.font
            text_color = self.item.get_rarity_color() if i == 0 else self.text_color
            
            text_surface = font.render(line, True, (*text_color, alpha))
            tooltip_surface.blit(text_surface, (10, y_offset))
            y_offset += 25
        
        # Apply overall alpha
        tooltip_surface.set_alpha(alpha)
        surface.blit(tooltip_surface, (self.x, self.y))


class InventorySystem(HUDElement):
    """Main inventory system with grid layout and item management."""
    
    def __init__(self, input_manager: InputManager, audio_manager: AudioManager,
                 rows: int = 6, cols: int = 8):
        # Calculate inventory size
        slot_size = 64
        slot_spacing = 4
        width = cols * (slot_size + slot_spacing) + slot_spacing
        height = rows * (slot_size + slot_spacing) + slot_spacing + 40  # Extra space for title
        
        super().__init__(0, 0, width, height, anchor="center")
        
        self.input_manager = input_manager
        self.audio_manager = audio_manager
        self.rows = rows
        self.cols = cols
        self.slot_size = slot_size
        self.slot_spacing = slot_spacing
        
        # Create inventory slots
        self.slots: List[InventorySlot] = []
        self._create_slots()
        
        # State
        self.is_open = False
        self.selected_slot: Optional[InventorySlot] = None
        self.dragging_stack: Optional[ItemStack] = None
        self.drag_offset = (0, 0)
        
        # UI elements
        self.tooltip = Tooltip()
        self.title_font = pygame.font.Font(None, 32)
        
        # Visual properties
        self.background_color = config.COLORS['dark_blue']
        self.border_color = config.COLORS['cyan']
        self.title_color = config.COLORS['white']
        
        # Animation
        self.open_progress = 0.0
        self.shake_timer = 0.0
        
        # Inventory data
        self.max_weight = 100.0
        self.current_weight = 0.0
        
        print("Inventory system initialized")
    
    def _create_slots(self):
        """Create inventory slot grid."""
        for row in range(self.rows):
            for col in range(self.cols):
                slot_x = col * (self.slot_size + self.slot_spacing) + self.slot_spacing
                slot_y = row * (self.slot_size + self.slot_spacing) + self.slot_spacing + 40
                
                slot_index = row * self.cols + col
                slot = InventorySlot(slot_x, slot_y, self.slot_size, slot_index)
                self.slots.append(slot)
    
    def open_inventory(self):
        """Open the inventory."""
        if not self.is_open:
            self.is_open = True
            self.visible = True
            self.audio_manager.play_sound('click', 0, 0, volume=0.4)
    
    def close_inventory(self):
        """Close the inventory."""
        if self.is_open:
            self.is_open = False
            self.visible = False
            self.tooltip.hide()
            self.selected_slot = None
            self.dragging_stack = None
            self.audio_manager.play_sound('click', 0, 0, volume=0.4)
    
    def toggle_inventory(self):
        """Toggle inventory open/closed."""
        if self.is_open:
            self.close_inventory()
        else:
            self.open_inventory()
    
    def add_item(self, item: Item, quantity: int = 1) -> int:
        """Add item to inventory. Returns quantity that couldn't be added."""
        remaining = quantity
        
        # First, try to add to existing stacks
        if item.stack_size > 1:
            for slot in self.slots:
                if not slot.is_empty() and slot.item_stack.item.item_id == item.item_id:
                    remaining = slot.item_stack.add(remaining)
                    if remaining == 0:
                        break
        
        # Then, try to add to empty slots
        if remaining > 0:
            for slot in self.slots:
                if slot.is_empty():
                    stack_size = min(remaining, item.stack_size)
                    slot.set_item_stack(ItemStack(item, stack_size))
                    remaining -= stack_size
                    if remaining == 0:
                        break
        
        # Update weight
        added = quantity - remaining
        self.current_weight += added * item.weight
        
        # Play sound if something was added
        if added > 0:
            self.audio_manager.play_sound('click', 0, 0, volume=0.3)
            
            # Show notification if inventory is closed
            if not self.is_open:
                # This would be handled by the HUD system
                pass
        
        # Shake if inventory is full
        if remaining > 0:
            self.shake_timer = 0.3
            self.audio_manager.play_sound('error', 0, 0, volume=0.5)
        
        return remaining
    
    def remove_item(self, item_id: str, quantity: int = 1) -> int:
        """Remove item from inventory. Returns quantity actually removed."""
        removed = 0
        
        for slot in self.slots:
            if not slot.is_empty() and slot.item_stack.item.item_id == item_id:
                need_to_remove = min(quantity - removed, slot.item_stack.quantity)
                actual_removed = slot.item_stack.remove(need_to_remove)
                removed += actual_removed
                
                # Update weight
                self.current_weight -= actual_removed * slot.item_stack.item.weight
                
                # Clear slot if empty
                if slot.item_stack.quantity <= 0:
                    slot.set_item_stack(None)
                
                if removed >= quantity:
                    break
        
        return removed
    
    def get_item_count(self, item_id: str) -> int:
        """Get total count of item in inventory."""
        total = 0
        for slot in self.slots:
            if not slot.is_empty() and slot.item_stack.item.item_id == item_id:
                total += slot.item_stack.quantity
        return total
    
    def has_item(self, item_id: str, quantity: int = 1) -> bool:
        """Check if inventory has enough of an item."""
        return self.get_item_count(item_id) >= quantity
    
    def _update_animations(self, dt: float):
        """Update inventory animations."""
        # Open/close animation
        target_progress = 1.0 if self.is_open else 0.0
        progress_speed = 8.0
        
        if self.open_progress < target_progress:
            self.open_progress = min(target_progress, self.open_progress + progress_speed * dt)
        elif self.open_progress > target_progress:
            self.open_progress = max(target_progress, self.open_progress - progress_speed * dt)
        
        # Shake animation
        self.shake_timer = max(0.0, self.shake_timer - dt)
        
        # Update scale based on open progress
        self.scale = 0.5 + 0.5 * self.open_progress
        self.alpha = int(255 * self.open_progress)
    
    def update(self, dt: float, screen_width: int, screen_height: int):
        """Update inventory system."""
        super().update(dt, screen_width, screen_height)
        
        if not self.is_open:
            return
        
        mouse_pos = pygame.mouse.get_pos()
        
        # Update slots
        for slot in self.slots:
            # Adjust slot position based on inventory position
            slot.x = self.x + slot.slot_index % self.cols * (self.slot_size + self.slot_spacing) + self.slot_spacing
            slot.y = self.y + slot.slot_index // self.cols * (self.slot_size + self.slot_spacing) + self.slot_spacing + 40
            slot.update(dt, mouse_pos)
        
        # Update tooltip
        self.tooltip.update(dt, screen_width, screen_height)
        self._update_tooltip(mouse_pos)
    
    def _update_tooltip(self, mouse_pos: Tuple[int, int]):
        """Update tooltip display."""
        # Find hovered slot
        hovered_slot = None
        for slot in self.slots:
            if slot.hovered and not slot.is_empty() and not self.dragging_stack:
                hovered_slot = slot
                break
        
        if hovered_slot:
            self.tooltip.show(hovered_slot.item_stack.item, mouse_pos)
        else:
            self.tooltip.hide()
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle input events."""
        if not self.is_open:
            return False
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE or event.key == pygame.K_i:
                self.close_inventory()
                return True
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                return self._handle_left_click(event.pos)
            elif event.button == 3:  # Right click
                return self._handle_right_click(event.pos)
        
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and self.dragging_stack:
                return self._handle_drag_release(event.pos)
        
        elif event.type == pygame.MOUSEMOTION:
            if self.dragging_stack:
                return True  # Consume event while dragging
        
        return False
    
    def _handle_left_click(self, mouse_pos: Tuple[int, int]) -> bool:
        """Handle left mouse click."""
        clicked_slot = self._get_slot_at_position(mouse_pos)
        
        if clicked_slot:
            if self.dragging_stack:
                # Drop item
                self._drop_item_on_slot(clicked_slot)
            else:
                # Start dragging item
                if not clicked_slot.is_empty():
                    self.dragging_stack = clicked_slot.item_stack
                    clicked_slot.set_item_stack(None)
                    self.drag_offset = (mouse_pos[0] - clicked_slot.x, mouse_pos[1] - clicked_slot.y)
                    self.audio_manager.play_sound('click', 0, 0, volume=0.3)
            
            return True
        
        # Click outside inventory - close if not dragging
        if not self.dragging_stack:
            self.close_inventory()
            return True
        
        return False
    
    def _handle_right_click(self, mouse_pos: Tuple[int, int]) -> bool:
        """Handle right mouse click."""
        clicked_slot = self._get_slot_at_position(mouse_pos)
        
        if clicked_slot and not clicked_slot.is_empty():
            # Use/activate item
            item = clicked_slot.item_stack.item
            
            if item.item_type == ItemType.CONSUMABLE:
                # Use consumable
                self._use_consumable(clicked_slot)
                return True
            elif item.item_type in [ItemType.WEAPON, ItemType.ARMOR]:
                # Equip item
                self._equip_item(clicked_slot)
                return True
        
        return False
    
    def _handle_drag_release(self, mouse_pos: Tuple[int, int]) -> bool:
        """Handle releasing dragged item."""
        if not self.dragging_stack:
            return False
        
        target_slot = self._get_slot_at_position(mouse_pos)
        
        if target_slot:
            self._drop_item_on_slot(target_slot)
        else:
            # Drop outside inventory - return to original position or drop on ground
            # For now, find first empty slot
            empty_slot = self._find_empty_slot()
            if empty_slot:
                empty_slot.set_item_stack(self.dragging_stack)
            else:
                # Drop on ground (would be handled by game world)
                pass
        
        self.dragging_stack = None
        return True
    
    def _get_slot_at_position(self, pos: Tuple[int, int]) -> Optional[InventorySlot]:
        """Get inventory slot at mouse position."""
        for slot in self.slots:
            if slot.is_point_inside(pos):
                return slot
        return None
    
    def _drop_item_on_slot(self, target_slot: InventorySlot):
        """Drop dragged item on target slot."""
        if not self.dragging_stack:
            return
        
        if target_slot.is_empty():
            # Drop on empty slot
            target_slot.set_item_stack(self.dragging_stack)
            self.audio_manager.play_sound('click', 0, 0, volume=0.3)
        elif target_slot.item_stack.item.item_id == self.dragging_stack.item.item_id:
            # Stack with same item
            remaining = target_slot.item_stack.add(self.dragging_stack.quantity)
            if remaining > 0:
                self.dragging_stack.quantity = remaining
                # Find another slot for remainder
                empty_slot = self._find_empty_slot()
                if empty_slot:
                    empty_slot.set_item_stack(self.dragging_stack)
            self.audio_manager.play_sound('click', 0, 0, volume=0.3)
        else:
            # Swap items
            temp_stack = target_slot.item_stack
            target_slot.set_item_stack(self.dragging_stack)
            self.dragging_stack = temp_stack
            self.audio_manager.play_sound('click', 0, 0, volume=0.3)
    
    def _find_empty_slot(self) -> Optional[InventorySlot]:
        """Find first empty inventory slot."""
        for slot in self.slots:
            if slot.is_empty():
                return slot
        return None
    
    def _use_consumable(self, slot: InventorySlot):
        """Use a consumable item."""
        if slot.is_empty() or slot.item_stack.item.item_type != ItemType.CONSUMABLE:
            return
        
        # Apply item effects (would be handled by game systems)
        item = slot.item_stack.item
        
        # Remove one from stack
        slot.item_stack.remove(1)
        if slot.item_stack.quantity <= 0:
            slot.set_item_stack(None)
        
        self.audio_manager.play_sound('heal', 0, 0, volume=0.5)
    
    def _equip_item(self, slot: InventorySlot):
        """Equip an item."""
        if slot.is_empty() or slot.item_stack.item.item_type not in [ItemType.WEAPON, ItemType.ARMOR]:
            return
        
        # Equipment would be handled by equipment system
        self.audio_manager.play_sound('equip', 0, 0, volume=0.4)
    
    def render(self, surface: pygame.Surface):
        """Render the inventory system."""
        if not self.visible or self.open_progress <= 0:
            return
        
        # Calculate shake offset
        shake_x = 0
        shake_y = 0
        if self.shake_timer > 0:
            import random
            shake_amount = self.shake_timer * 10
            shake_x = random.uniform(-shake_amount, shake_amount)
            shake_y = random.uniform(-shake_amount, shake_amount)
        
        # Get render rect with shake
        render_rect = self.get_render_rect()
        render_rect.x += shake_x
        render_rect.y += shake_y
        
        # Create inventory surface
        inv_surface = pygame.Surface((render_rect.width, render_rect.height), pygame.SRCALPHA)
        
        # Draw background
        bg_alpha = int(200 * self.open_progress)
        bg_surface = pygame.Surface((render_rect.width, render_rect.height), pygame.SRCALPHA)
        bg_surface.fill((*self.background_color, bg_alpha))
        inv_surface.blit(bg_surface, (0, 0))
        
        # Draw border
        border_alpha = int(255 * self.open_progress)
        pygame.draw.rect(inv_surface, (*self.border_color, border_alpha), 
                        pygame.Rect(0, 0, render_rect.width, render_rect.height), 3)
        
        # Draw title
        title_alpha = int(255 * self.open_progress)
        title_text = self.title_font.render("INVENTORY", True, (*self.title_color, title_alpha))
        title_rect = title_text.get_rect()
        title_rect.centerx = render_rect.width // 2
        title_rect.y = 10
        inv_surface.blit(title_text, title_rect)
        
        # Draw weight info
        weight_text = f"Weight: {self.current_weight:.1f}/{self.max_weight:.1f} kg"
        weight_font = pygame.font.Font(None, 20)
        weight_color = config.COLORS['red'] if self.current_weight > self.max_weight else config.COLORS['white']
        weight_surface = weight_font.render(weight_text, True, (*weight_color, title_alpha))
        weight_rect = weight_surface.get_rect()
        weight_rect.right = render_rect.width - 10
        weight_rect.y = 10
        inv_surface.blit(weight_surface, weight_rect)
        
        # Apply overall alpha and blit to screen
        inv_surface.set_alpha(int(255 * self.open_progress))
        surface.blit(inv_surface, render_rect.topleft)
        
        # Render slots
        for slot in self.slots:
            if self.open_progress > 0.5:  # Only render slots when mostly open
                slot_surface = pygame.Surface((slot.slot_size, slot.slot_size), pygame.SRCALPHA)
                slot.render(slot_surface)
                slot_surface.set_alpha(int(255 * self.open_progress))
                surface.blit(slot_surface, (slot.x + shake_x, slot.y + shake_y))
        
        # Render dragged item
        if self.dragging_stack:
            self._render_dragged_item(surface)
        
        # Render tooltip
        self.tooltip.render(surface)
    
    def _render_dragged_item(self, surface: pygame.Surface):
        """Render the item being dragged."""
        if not self.dragging_stack:
            return
        
        mouse_pos = pygame.mouse.get_pos()
        item_x = mouse_pos[0] - self.drag_offset[0]
        item_y = mouse_pos[1] - self.drag_offset[1]
        
        # Create dragged item surface
        drag_surface = pygame.Surface((self.slot_size, self.slot_size), pygame.SRCALPHA)
        
        # Create temporary slot for rendering
        temp_slot = InventorySlot(0, 0, self.slot_size, -1)
        temp_slot.set_item_stack(self.dragging_stack)
        temp_slot.render(drag_surface)
        
        # Apply transparency to show it's being dragged
        drag_surface.set_alpha(180)
        surface.blit(drag_surface, (item_x, item_y))