import pygame 
import os
import random
import sys
import csv
import math
from PIL import Image, ImageDraw

import tkinter as tk
from tkinter import filedialog

# === BASIC SETTINGS ===
BLOCKS = 100
GRID_COLS = 10
GRID_ROWS = 10
NUM_SNAKES = 8
NUM_LADDERS = 8
NUM_PLAYERS = 2
NUM_TRIVIA = 25   # or any number you want
import random
#GRID_COLS = 10
#BLOCKS = GRID_COLS * GRID_COLS
MAX_JUMP = 8
MIN_GAP = 3 
#trivia_blocks = []  # Will store block indices with trivia
trivia_blocks = []
import tkinter as tk
from tkinter import filedialog, messagebox
##################################################################3
###############################################################
###############################################################
def process_turn(p, roll):
    old = p['pos']
    dest = old + roll
    if dest > BLOCKS-1:
        return False, "Need exact roll", old, "none"
    effect = block_data[dest]['effect']
    to_block = block_data[dest]['effect_to']
    print(f"Dest block {dest+1} has effect '{effect}' → {to_block}")
    b = block_data[dest]
#####################################################################################################################
###########################################################################################################################
    # trivia
    """
    if dest in trivia_blocks and b['trivia_question']:
        correct = trivia_popup(dest, p)
        trivia_blocks.remove(dest)
        if correct:
            target = (b['effect_to'] - 1) if b['effect_to'] else dest
        else:
            target = max(0, dest - 1)
        p['pos'] = target
        return True, f"{'Correct' if correct else 'Wrong'}! Moved to {target+1}", target, "trivia"
    """
    if dest in trivia_blocks and b['trivia_question']:
        p['trivia_attempts'] += 1          # ⬅ Count attempt
        correct = trivia_popup(dest, p)
        if correct:
            p['trivia_correct'] += 1       # ⬅ Count correct
            target = (b['effect_to'] - 1) if b['effect_to'] else dest
        else:
            target = max(0, dest - 1)
        trivia_blocks.remove(dest)
        p['pos'] = target
        return True, f"{'Correct' if correct else 'Wrong'}! Moved to {target+1}", target, "trivia"

    
###########################################################################################################################
##########################################################################################################################3
    # snake
    if b['effect'] == 'snake' and b['effect_to']:
        target = b['effect_to'] - 1
        p['pos'] = target
        return True, f"Oh no! Snake down to {target+1}", target, "snake"

    # ladder
    if b['effect'] == 'ladder' and b['effect_to']:
        target = b['effect_to'] - 1
        p['pos'] = target
        return True, f"Ladder up to {target+1}", target, "ladder"

    # normal
    target = dest
    p['pos'] = target
    return True, f"Moved to {target+1}", target, "normal"

#######################################################################
####################################################################3
###########################################################################





def animate_move(p, start, end):
    """Animate the token moving from start to end one block at a time."""
    step = 1 if end >= start else -1
    for pos in range(start + step, end + step, step):
        p['pos'] = pos
        # redraw everything here:
        screen.fill((235,240,255))
        draw_board()
        draw_snakes_and_ladders()
        draw_tokens()
        draw_side_panel(hover_block, last_roll)
        pygame.display.flip()
        pygame.time.wait(200)







def get_player_info_gui(n_players=2):
    players_info = []
    root = tk.Tk()
    root.withdraw()  # Hide root window

    for i in range(n_players):
        player_window = tk.Toplevel(root)
        player_window.title(f"Player {i+1} Setup")
        player_window.geometry("440x300")
        player_window.resizable(False, False)
        name_var = tk.StringVar(value=f"Player {i+1}")
        avatar_path = tk.StringVar(value="")

        tk.Label(player_window, text=f"Enter name for Player {i+1}:").pack(pady=10)
        tk.Entry(player_window, textvariable=name_var, width=30).pack()

        def choose_img():
            path = filedialog.askopenfilename(
                title="Select Avatar Image",
                filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.webp")],
            )
            if path:
                avatar_path.set(path)

        img_btn = tk.Button(player_window, text="Choose Avatar Image", command=choose_img)
        img_btn.pack(pady=8)
        img_lbl = tk.Label(player_window, textvariable=avatar_path, wraplength=280, fg="gray")
        img_lbl.pack()

        button_frame = tk.Frame(player_window)
        button_frame.pack(pady=14)

        # If Cancel pressed, exit whole program
        def cancel():
            player_window.destroy()
            root.destroy()
            sys.exit(0)

        def confirm():
            name = name_var.get().strip()
            players_info.append({
                'name': name if name else f"Player {i+1}",
                'avatar_img': avatar_path.get() if avatar_path.get() else None
            })
            player_window.destroy()

        ok_btn = tk.Button(button_frame, text="OK", command=confirm, width=10)
        cancel_btn = tk.Button(button_frame, text="Cancel", command=cancel, width=10)
        ok_btn.pack(side="left", padx=16)
        cancel_btn.pack(side="right", padx=16)

        player_window.grab_set()  # Modal dialog
        player_window.wait_window()

    root.destroy()
    return players_info



pygame.init()
info = pygame.display.Info()

large_panel_font = pygame.font.SysFont("arial", 26, bold=True)
medium_panel_font = pygame.font.SysFont("arial", 20)
turn_font = pygame.font.SysFont("arial", 24, bold=True)


#########################################################

SCREEN_W = min(1400, info.current_w - 40)
SCREEN_H = min(900, info.current_h - 60)
SIDE_PANEL_WIDTH = int(SCREEN_W * 0.28)
BOARD_W = SCREEN_W - SIDE_PANEL_WIDTH
BOARD_H = SCREEN_H
#####################################################





BLOCK_SIZE = min((BOARD_W - 11*2) // GRID_COLS, (BOARD_H - 11*2) // GRID_ROWS)
MARGIN = BLOCK_SIZE // 16 if BLOCK_SIZE >= 32 else 2
WINDOW_WIDTH = GRID_COLS * BLOCK_SIZE + (GRID_COLS + 1) * MARGIN + SIDE_PANEL_WIDTH
WINDOW_HEIGHT = GRID_ROWS * BLOCK_SIZE + (GRID_ROWS + 1) * MARGIN
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Snake & Ladder - Computer Literacy Edition")

def abs_path(*parts):
    return os.path.join(os.path.dirname(__file__), *parts)

def get_block_image(blocknum, size):
    exts = ["jpg", "jpeg", "png", "webp"]
    for ext in exts:
        imgfile = abs_path("images/blocks", f"{blocknum}.{ext}")
        if os.path.exists(imgfile):
            img = pygame.image.load(imgfile)
            return pygame.transform.smoothscale(img, (size, size))
    # Dummy
    img = Image.new("RGB", (size, size), color=(120, 150 + blocknum*2 % 70, 170 + blocknum*4 % 60))
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, size-1, size-1], outline=(50, 80, 120), width=3)
    pygame_img = pygame.image.fromstring(img.tobytes(), img.size, img.mode)
    return pygame_img

def get_dice_image(value, size):
    exts = ["png", "jpg", "jpeg", "webp"]
    for ext in exts:
        fname = abs_path("images/dice", f"dice{value}.{ext}")
        if os.path.exists(fname):
            img = pygame.image.load(fname)
            return pygame.transform.smoothscale(img, (size, size))
    img = pygame.Surface((size, size), pygame.SRCALPHA)
    pygame.draw.rect(img, (255,255,255), (0,0,size,size), border_radius=12)
    dice_font = pygame.font.SysFont("arial", size//2, bold=True)
    t = dice_font.render(str(value), True, (40,40,40))
    r = t.get_rect(center=(size//2, size//2))
    img.blit(t, r)
    return img

def animate_dice_roll(screen, x, y, box_size, final_value, frames=14, delay=34):
    for i in range(frames):
        roll = random.randint(1, 6)
        img = get_dice_image(roll, box_size-12)
        pygame.draw.rect(screen, (200,220,240), (x, y, box_size, box_size), 0, border_radius=24)
        screen.blit(img, (x + 6, y + 6))
        pygame.display.update(pygame.Rect(x, y, box_size, box_size))
        pygame.time.wait(delay)
    img = get_dice_image(final_value, box_size-12)
    pygame.draw.rect(screen, (200,220,240), (x, y, box_size, box_size), 0, border_radius=24)
    screen.blit(img, (x + 6, y + 6))
    pygame.display.update(pygame.Rect(x, y, box_size, box_size))
    pygame.time.wait(130)

def load_trivia_icons(size):
    icons = {}
    folder = abs_path("images/trivia")
    mapping = [
        ("mcq", "mcq.png"),
        ("true_false", "tf.png"),
        ("fill_blank", "fib.png"),
        ("other", "other.png"),
    ]
    for name, fname in mapping:
        path = os.path.join(folder, fname)
        if os.path.exists(path):
            img = pygame.image.load(path)
            icons[name] = pygame.transform.smoothscale(img, (size, size))
        else:
            surf = pygame.Surface((size, size))
            surf.fill((230, 230, 0))
            icons[name] = surf
    return icons

TRIVIA_ICON_SIZE = max(24, BLOCK_SIZE // 2)
trivia_icons = load_trivia_icons(TRIVIA_ICON_SIZE)

def get_trivia_icon(trivia_type):
    t = (trivia_type or "").lower().strip()
    if t in ("multiple_choice", "mcq", "choice", "multiple choice"):
        return trivia_icons.get("mcq", trivia_icons["other"])
    elif t in ("true_false", "true/false", "tf", "true-false", "boolean"):
        return trivia_icons.get("true_false", trivia_icons["other"])
    elif t in ("fill_blank", "fill_in_blank", "fill-in-the-blank", "fib", "fill in the blank"):
        return trivia_icons.get("fill_blank", trivia_icons["other"])
    else:
        return trivia_icons["other"]

def read_block_csv(filename):
    blocks = [{} for _ in range(BLOCKS)]
    
    with open(filename, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)             
        for row in reader:
            idx = int(row['number']) - 1
            blocks[idx] = {
                'number': int(row['number']),
                'title': row.get('title', ''),
                'description': row.get('description', ''),
                'effect': row.get('effect', 'none'),
                'effect_to': int(row['effect_to']) if row.get('effect_to') else None,
                'trivia_type': row.get('trivia_type', 'multiple_choice'),
                'trivia_question': row.get('trivia_question', ''),
                'trivia_choices': [c.strip() for c in row.get('trivia_choices', '').split('|')] if row.get('trivia_choices') else [],
                'trivia_answer': row.get('trivia_answer', ''),
                'bonus': int(row.get('bonus', '0') or 0),
                'penalty': int(row.get('penalty', '0') or 0),
            }
    return blocks

#block_data = read_block_csv('block_data2.csv')
block_data = read_block_csv('data2.csv')
TOTAL_TRIVIA = 50
trivia_blocks = set(random.sample(range(BLOCKS), TOTAL_TRIVIA))
block_images = [get_block_image(i+1, BLOCK_SIZE) for i in range(BLOCKS)]
font = pygame.font.SysFont("arial", max(14, BLOCK_SIZE // 5))
big_font = pygame.font.SysFont("arial", max(18, BLOCK_SIZE // 3), bold=True)
panel_font = pygame.font.SysFont("arial", 18)




############################################
############################################
# Pre-compute the board mapping
board_squares = []
for row in range(GRID_ROWS-1, -1, -1):  # from bottom to top
    if (GRID_ROWS-1 - row) % 2 == 0:
        cols = range(0, GRID_COLS)
    else:
        cols = range(GRID_COLS-1, -1, -1)
    for col in cols:
        board_squares.append((col, row))

# Now define get_block_xy using the precomputed list
def get_block_xy(pos):
    col, row = board_squares[pos]
    x = MARGIN + col * (BLOCK_SIZE + MARGIN)
    y = MARGIN + row * (BLOCK_SIZE + MARGIN)
    return x, y



################################

############################################
def block_at_pixel(x, y):
    for i in range(BLOCKS):
        bx, by = get_block_xy(i)
        if bx <= x < bx + BLOCK_SIZE and by <= y < by + BLOCK_SIZE:
            return i
    return None

PLAYER_COLORS = [(0,90,220), (220,80,60), (0,180,70), (180,0,200)]

# === PLAYER SETUP ===
def get_player_info(n_players=2):
    player_infos = []
    print("=== PLAYER SETUP ===")
    for i in range(n_players):
        name = input(f"Enter name for Player {i+1} (leave blank for 'Player {i+1}'): ").strip()
        if not name:
            name = f"Player {i+1}"
        avatar_img = None
        try:
            use_img = input(f"Do you want to upload an avatar for {name}? (Y/N): ").strip().lower()
        except Exception as e:
            use_img = 'n'
        if use_img == 'y':
            try:
                root = tk.Tk()
                root.withdraw()
                file_path = filedialog.askopenfilename(
                    title=f"Select avatar image for {name}",
                    filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.webp")]
                )
                root.destroy()
                if file_path and os.path.exists(file_path):
                    avatar_img = file_path
            except Exception as e:
                print("Couldn't open file dialog:", e)
                avatar_img = None
        player_infos.append({'name': name, 'avatar_img': avatar_img})
    print("Players ready!\n")
    return player_infos

#player_infos = get_player_info(NUM_PLAYERS)
player_infos = get_player_info_gui(NUM_PLAYERS)
player_imgs = []
for info in player_infos:
    if info['avatar_img'] and os.path.exists(info['avatar_img']):
        img = pygame.image.load(info['avatar_img'])
        player_imgs.append(pygame.transform.smoothscale(img, (int(BLOCK_SIZE * 0.7), int(BLOCK_SIZE * 0.7))))
    else:
        player_imgs.append(None)
players = []
for i, info in enumerate(player_infos):
    players.append({
        'name': info['name'],
        'pos': 0,
        'score': 0,
        'color': PLAYER_COLORS[i % len(PLAYER_COLORS)],
        'avatar': player_imgs[i] if i < len(player_imgs) else None, 
        'trivia_attempts': 0,
        'trivia_correct': 0 
    })
turn = 0

# === SNAKE/LADDER PLACEMENT ===

def row_of_block(idx):
    return idx // GRID_COLS
################################################


################################################


######################################################



def row(pos):
    return pos // GRID_COLS

def segments_overlap(seg1, seg2):
    a1, b1 = sorted(seg1)
    a2, b2 = sorted(seg2)
    return not (b1 + MIN_GAP < a2 or b2 + MIN_GAP < a1)

def generate_pieces(count, is_snake=True, existing_ends=None):
    pieces = []
    ends = set(existing_ends or [])
    used_segments = []

    attempts = 0
    while len(pieces) < count and attempts < count * 1000:
        attempts += 1
        jump = random.randint(1, MAX_JUMP)
        start = random.randrange(0, BLOCKS)
        end = start - jump if is_snake else start + jump

        # 1. Within board
        if not (0 <= end < BLOCKS):
            continue
        # 2. Different row
        if row(start) == row(end):
            continue
        # 3. Correct direction
        if is_snake and start <= end:
            continue
        if not is_snake and end <= start:
            continue
        # 4. End-block uniqueness
        if end in ends:
            continue

        seg = (start, end)
        # 5. No overlapping segments
        if any(segments_overlap(seg, s) for s in used_segments):
            continue

        # Accept
        pieces.append(seg)
        ends.add(end)
        used_segments.append(seg)

    return pieces, ends

def generate_snakes_and_ladders(num_snakes, num_ladders):
    snakes, ends = generate_pieces(num_snakes, is_snake=True, existing_ends=set())
    ladders, ends = generate_pieces(num_ladders, is_snake=False, existing_ends=ends)

    if len(snakes) < num_snakes:
        print(f"⚠️ Only generated {len(snakes)}/{num_snakes} snakes.")
    if len(ladders) < num_ladders:
        print(f"⚠️ Only generated {len(ladders)}/{num_ladders} ladders.")

    return snakes, ladders

"""
import random

GRID_COLS = 10
BLOCKS = GRID_COLS * GRID_COLS
MAX_JUMP = 6
MIN_GAP = 3

def row(pos):
    return pos // GRID_COLS

def segments_overlap(seg1, seg2):
    a1, b1 = sorted(seg1)
    a2, b2 = sorted(seg2)
    return not (b1 + MIN_GAP < a2 or b2 + MIN_GAP < a1)

def generate_pieces(count, is_snake=True):
    pieces = []
    used_segments = []

    attempts = 0
    while len(pieces) < count and attempts < count * 1000:
        attempts += 1
        jump = random.randint(1, MAX_JUMP)
        start = random.randrange(0, BLOCKS)

        end = start - jump if is_snake else start + jump

        # Validate within board
        if not (0 <= end < BLOCKS):
            continue
        # Different row
        if row(start) == row(end):
            continue
        # Correct direction
        if is_snake and start <= end:
            continue
        if not is_snake and end <= start:
            continue

        seg = (start, end)
        # No overlapping segments
        if any(segments_overlap(seg, s) for s in used_segments):
            continue

        pieces.append(seg)
        used_segments.append(seg)

    return pieces

def generate_snakes_and_ladders(num_snakes, num_ladders):
    snakes = generate_pieces(num_snakes, is_snake=True)
    ladders = generate_pieces(num_ladders, is_snake=False)

    # Report if not enough could be placed
    if len(snakes) < num_snakes:
        print(f"⚠️ Only generated {len(snakes)}/{num_snakes} snakes.")
    if len(ladders) < num_ladders:
        print(f"⚠️ Only generated {len(ladders)}/{num_ladders} ladders.")

    return snakes, ladders


"""









#######################End of generate snakes and ladders effect
#######################################################################
######################################################################

#snakes, ladders = generate_snakes_and_ladders(NUM_SNAKES, NUM_LADDERS)

#snakes, ladders = generate_snakes_and_ladders(NUM_SNAKES, NUM_LADDERS, max_jump=4)
"""
print("Snakes:", snakes)
print("Ladders:", ladders)  

for i, b in enumerate(block_data):
    if b['effect'] == 'snake' and (i, b['effect_to'] - 1) not in snakes:
        snakes.append((i, b['effect_to'] - 1))
    if b['effect'] == 'ladder' and (i, b['effect_to'] - 1) not in ladders:
        ladders.append((i, b['effect_to'] - 1))

for head, tail in snakes:
    block_data[head]['effect'] = 'snake'
    block_data[head]['effect_to'] = tail+1
for base, top in ladders:
    block_data[base]['effect'] = 'ladder'
    block_data[base]['effect_to'] = top+1
    """
snakes, ladders = generate_snakes_and_ladders(NUM_SNAKES, NUM_LADDERS)

# Filter out snakes involving the final block
snakes = [(h, t) for (h, t) in snakes if h < BLOCKS - 1 and t < BLOCKS - 1]

# You can optionally ensure uniqueness of tails
tails = [t for _, t in snakes]
assert len(tails) == len(set(tails)), "Duplicate snake tails detected"

for head, tail in snakes:
    print(f"Forced snake at {head}->{tail}")
    block_data[head]['effect'] = 'snake'
    block_data[head]['effect_to'] = tail + 1

for base, top in ladders:
    block_data[base]['effect'] = 'ladder'
    block_data[base]['effect_to'] = top + 1

print("Snakes:", snakes)
print("Ladders:", ladders)
for head, tail in snakes + ladders:
    print(f"Placed {'snake' if (head, tail) in snakes else 'ladder'} at {head}->{tail}")
##############################################
################################################
"""
#########################################
# Remove any snake with a forbidden head/tail
snakes = [(h, t) for (h, t) in snakes if h < BLOCKS - 1 and t < BLOCKS - 1]
# Ensure all tails are unique
tails = [t for (_, t) in snakes]
assert len(tails) == len(set(tails)), "Duplicate snake tails detected"
snakes = [(h, t) for h, t in snakes if t != BLOCKS - 1 and h != BLOCKS - 1]
############################################
print(f"Forced snake at {head}->{tail}")
for head, tail in snakes:
    block_data[head]['effect'] = 'snake'
    block_data[head]['effect_to'] = tail + 1
for base, top in ladders:
    block_data[base]['effect'] = 'ladder'
    block_data[base]['effect_to'] = top + 1   
print("Snakes:", snakes)
print("Ladders:", ladders)
for head, tail in snakes + ladders:
    print(f"Placed { 'snake' if (head, tail) in snakes else 'ladder' } at {head}->{tail}")
###########################################################
"""
###########################################################
used_blocks = set()
for head, tail in snakes:
    used_blocks.add(head); used_blocks.add(tail)
for base, top in ladders:
    used_blocks.add(base); used_blocks.add(top)
    

#NUM_TRIVIA = 5  # adjust as needed
trivia_blocks = set(random.sample(
    [i for i in range(1, BLOCKS-1) if i not in used_blocks],
    min(NUM_TRIVIA, BLOCKS - len(used_blocks) - 2)
))

# Clear trivia in block_data, then assign only to trivia_blocks
for i, b in enumerate(block_data):
    if i not in trivia_blocks:
        b['trivia_question'] = ''
        b['trivia_choices'] = []
        b['trivia_answer'] = ''
        b['bonus'] = 0
        b['penalty'] = 0





# Now place trivia blocks randomly, not on snakes/ladders
def generate_trivia_blocks(blocks, num_trivia, used_blocks):
    available = [i for i in range(1, BLOCKS-1) if i not in used_blocks]
    random.shuffle(available)
    selected = available[:num_trivia]
    return selected

trivia_blocks = generate_trivia_blocks(block_data, NUM_TRIVIA, used_blocks)
# You may want to assign or update trivia questions here as well.

#####################################################3
######################################################
import pygame


def draw_snake_curve(head, tail, color=(40,220,40), animate_block=None, t=0):
    # Head is the START block; tail is the END block
    x_head, y_head = get_block_xy(head)
    x_head += BLOCK_SIZE // 2
    y_head += BLOCK_SIZE // 2
    x_tail, y_tail = get_block_xy(tail)
    x_tail += BLOCK_SIZE // 2
    y_tail += BLOCK_SIZE // 2
    steps = 24
    pts = []
    t_anim = t
    for i in range(steps+1):
        pct = i/steps
        mx = x_head * (1-pct) + x_tail * pct + 28 * math.sin(2 * pct * math.pi + t_anim/28)
        my = y_head * (1-pct) + y_tail * pct + 16 * math.sin(3 * pct * math.pi + t_anim/21)
        pts.append((int(mx), int(my)))
    # Draw body first
    pygame.draw.lines(screen, color, False, pts, 18)
    pygame.draw.lines(screen, (0,120,40), False, pts, 7)
    # Spots
    for i in range(5, steps-2, 6):
        bx, by = pts[i]
        pygame.draw.circle(screen, (170,240,130), (bx+5, by+2), 7, 0)
    # Draw tail (ellipse) at the end
    pygame.draw.ellipse(screen, (60, 180, 80), (pts[-1][0]-13, pts[-1][1]-8, 26, 16))
    pygame.draw.ellipse(screen, (0, 90, 40), (pts[-1][0]-13, pts[-1][1]-8, 26, 16), 2)
    # Draw head/mouth at head block, only animate if player is at this block
    is_anim = animate_block == head
    draw_snake_head(pts[0][0]+11, pts[0][1]+4, animate=is_anim, t=t_anim)

def draw_snake_head(cx, cy, animate=False, t=0):
    # Main head
    pygame.draw.ellipse(screen, (40,220,50), (cx-26, cy-22, 53, 38))
    # Open mouth
    mouth_rect = pygame.Rect(cx+6, cy+7, 26, 16)
    pygame.draw.ellipse(screen, (100,30,30), mouth_rect)
    pygame.draw.arc(screen, (0,0,0), mouth_rect, 0.1, 3.04, 2)
    pygame.draw.arc(screen, (255,160,110), mouth_rect.inflate(-4, -7), 0.4, 2.75, 2)
    # Fangs
    fang_y1 = cy+15
    fang_y2 = fang_y1+8
    fang_xl = cx+12
    fang_xr = cx+25
    pygame.draw.polygon(screen, (255,255,255), [(fang_xl, fang_y1), (fang_xl+3, fang_y2), (fang_xl+6, fang_y1)])
    pygame.draw.polygon(screen, (255,255,255), [(fang_xr, fang_y1), (fang_xr-3, fang_y2), (fang_xr-6, fang_y1)])
    # Eyes
    pygame.draw.circle(screen, (255,255,255), (cx+10, cy-6), 7)
    pygame.draw.circle(screen, (0,0,0), (cx+10, cy-6), 3)
    pygame.draw.circle(screen, (255,255,255), (cx+20, cy), 7)
    pygame.draw.circle(screen, (0,0,0), (cx+20, cy), 3)
    # Eyebrows
    pygame.draw.arc(screen, (60, 90, 40), (cx+7, cy-12, 14, 6), math.pi*0.18, math.pi*0.97, 2)
    pygame.draw.arc(screen, (60, 90, 40), (cx+17, cy-6, 14, 6), math.pi*0.12, math.pi*0.91, 2)
    # Animated tongue
    if animate:
        tongue_base_x = cx+20
        tongue_base_y = cy+15
        tongue_tip_x = tongue_base_x + 18
        tongue_tip_y = tongue_base_y + int(7*math.sin(t/2))
        pygame.draw.line(screen, (255,0,0), (tongue_base_x, tongue_base_y), (tongue_tip_x, tongue_tip_y), 4)
        fork_w = 9
        pygame.draw.line(screen, (255,0,0), (tongue_tip_x, tongue_tip_y), (tongue_tip_x+fork_w, tongue_tip_y-7), 2)
        pygame.draw.line(screen, (255,0,0), (tongue_tip_x, tongue_tip_y), (tongue_tip_x+fork_w, tongue_tip_y+7), 2)
    else:
        pygame.draw.line(screen, (255,0,0), (cx+20, cy+15), (cx+38, cy+15), 4)

def draw_ladder_rungs(start, end, color=(250, 200, 30), t=0):
    # Animated ladder rungs shimmer and wiggle
    x0, y0 = get_block_xy(start)
    x0 += BLOCK_SIZE // 2
    y0 += BLOCK_SIZE // 2
    x1, y1 = get_block_xy(end)
    x1 += BLOCK_SIZE // 2
    y1 += BLOCK_SIZE // 2

    # Wiggly effect for animation
    wiggle_amt = 8 * math.sin(t/17)
    pygame.draw.line(screen, color, (x0-10+wiggle_amt, y0-10), (x1-10+wiggle_amt, y1-10), 7)
    pygame.draw.line(screen, color, (x0+10-wiggle_amt, y0+10), (x1+10-wiggle_amt, y1+10), 7)

    rungs = 6
    for i in range(rungs+1):
        tt = i/rungs
        rx = int(x0*(1-tt) + x1*tt)
        ry = int(y0*(1-tt) + y1*tt)
        # Shimmer between yellow and white
        shimmer = 200 + int(55 * abs(math.sin((t/15) + tt*math.pi*2)))
        rung_color = (shimmer, shimmer, 90)
        pygame.draw.line(screen, rung_color, (rx-10, ry-10), (rx+10, ry+10), 4)


def draw_snakes_and_ladders():
    t = pygame.time.get_ticks() // 22  # slow down!
    # Determine player blocks (for head mouth animation)
    player_blocks = [p['pos'] for p in players]
    for head, tail in snakes:
        animate_block = head if head in player_blocks else None
        draw_snake_curve(head, tail, (40,220,40), animate_block, t)
    for base, top in ladders:
        draw_ladder_rungs(base, top, t=t)





















######################################################
#######################################################



# === MODIFIED: No lock symbol on trivia blocks ===
##############################################################33
#############################################################
def draw_board():
    for i in range(BLOCKS):
        x, y = get_block_xy(i)
        # Draw block background
        screen.blit(block_images[i], (x, y))

        # Block number (with shadow + transparent background)
        num = str(i + 1)
        num_font = pygame.font.SysFont("arial", max(14, BLOCK_SIZE // 6), bold=True)
        numtxt = num_font.render(num, True, (255, 255, 255))
        numtxt_rect = numtxt.get_rect(topleft=(x + 4, y + 3))
        num_bg = pygame.Surface((numtxt_rect.width + 6, numtxt_rect.height + 3), pygame.SRCALPHA)
        num_bg.fill((0, 0, 0, 150))
        screen.blit(num_bg, (x + 2, y + 2))
        shadow = num_font.render(num, True, (0, 0, 0))
        screen.blit(shadow, (x + 6, y + 5))
        screen.blit(numtxt, numtxt_rect)

        # Trivia icon — only if block still has unsolved trivia
        if (i in trivia_blocks) and block_data[i].get('trivia_question'):
            trivia_icon_size = max(16, BLOCK_SIZE // 4)
            qmark_font = pygame.font.SysFont("arial", trivia_icon_size, bold=True)
            qmark = qmark_font.render("?", True, (255, 255, 180))
            qmark_rect = qmark.get_rect()
            qx = x + BLOCK_SIZE - qmark_rect.width - 7
            qy = y + BLOCK_SIZE - qmark_rect.height - 7

            bg_padding = 5
            bg_surf = pygame.Surface(
                (qmark_rect.width + bg_padding*2, qmark_rect.height + bg_padding*2),
                pygame.SRCALPHA
            )
            bg_surf.fill((0, 0, 0, 140))
            screen.blit(bg_surf, (qx - bg_padding, qy - bg_padding))
            screen.blit(qmark, (qx, qy))

#############################################################
#####################################################################
def draw_board2():
    for i in range(BLOCKS):
        x, y = get_block_xy(i)
        # Draw the block image, scaled
        screen.blit(block_images[i], (x, y))
        # --- Number at top left, small font with transparent black background ---
        num = str(i + 1)
        num_font = pygame.font.SysFont("arial", max(14, BLOCK_SIZE // 6), bold=True)  # Smaller font size
        numtxt = num_font.render(num, True, (255, 255, 255))
        numtxt_rect = numtxt.get_rect(topleft=(x + 4, y + 3))  # Padding from left/top
        # Transparent background rectangle (just around number)
        num_bg = pygame.Surface((numtxt_rect.width + 6, numtxt_rect.height + 3), pygame.SRCALPHA)
        num_bg.fill((0, 0, 0, 150))  # Black, 150 alpha
        num_bg_rect = num_bg.get_rect(topleft=(x + 2, y + 2))
        screen.blit(num_bg, num_bg_rect)
        # Draw number with shadow for extra visibility
        shadow = num_font.render(num, True, (0, 0, 0))
        shadow_rect = shadow.get_rect(topleft=(x + 6, y + 5))
        screen.blit(shadow, shadow_rect)
        # Draw white number, top left
        screen.blit(numtxt, numtxt_rect)
        # --- Trivia icon (unchanged) ---
        #if block_data[i].get('trivia_question'):
         #   trivia_type = block_data[i].get('trivia_type','')
          #  icon = get_trivia_icon(trivia_type)
           # qx = x + BLOCK_SIZE//2 - icon.get_width()//2
            #qy = y + BLOCK_SIZE - icon.get_height() - 4
            #screen.blit(icon, (qx, qy))
        # --- Trivia icon: small, at bottom right ---
     # --- Trivia icon: small, at bottom right ---
        #if block_data[i].get('trivia_question'):
            
            
            
        if i in trivia_blocks:
            trivia_icon_size = max(16, BLOCK_SIZE // 4)
            qmark_font = pygame.font.SysFont("arial", trivia_icon_size, bold=True)
            qmark = qmark_font.render("?", True, (255, 255, 180))
            qmark_rect = qmark.get_rect()
            qx = x + BLOCK_SIZE - qmark_rect.width - 7
            qy = y + BLOCK_SIZE - qmark_rect.height - 7
            bg_padding = 5
            bg_surf = pygame.Surface((qmark_rect.width + bg_padding*2,
                                      qmark_rect.height + bg_padding*2),
                                      pygame.SRCALPHA)
            bg_surf.fill((0, 0, 0, 140))
            screen.blit(bg_surf, (qx - bg_padding, qy - bg_padding))
            screen.blit(qmark, (qx, qy))
            # Render the "?" to measure its true size
            






################################################################
def draw_board1():
    for i in range(BLOCKS):
        x, y = get_block_xy(i)
        screen.blit(block_images[i], (x, y))
        ###################################################
        #numtxt = big_font.render(str(i + 1), True, (8, 32, 100))
        #numtxt = big_font.render(str(i + 1), True, (255, 255, 0))
        #screen.blit(numtxt, (x + 6, y + 2))
        ##################
        num = str(i + 1)
        # Draw black shadow
        shadow = big_font.render(num, True, (0,0,0))
        screen.blit(shadow, (x + 8, y + 4))
        # Draw bright yellow or white number on top
        numtxt = big_font.render(num, True, (255, 255, 0))  # Or (255,255,255) for white
        screen.blit(numtxt, (x + 6, y + 2))
        #########################################
        # Trivia icon bottom center
        if block_data[i].get('trivia_question'):
            trivia_type = block_data[i].get('trivia_type','')
            icon = get_trivia_icon(trivia_type)
            qx = x + BLOCK_SIZE//2 - icon.get_width()//2
            qy = y + BLOCK_SIZE - icon.get_height() - 4
            screen.blit(icon, (qx, qy))

def draw_tokens():
    for idx, p in enumerate(players):
        x, y = get_block_xy(p['pos'])
        cx = x + BLOCK_SIZE//2
        cy = y + BLOCK_SIZE//2 + 10
        if p['avatar']:
            img = pygame.transform.smoothscale(p['avatar'], (BLOCK_SIZE//2, BLOCK_SIZE//2))
            rect = img.get_rect(center=(cx, cy))
            screen.blit(img, rect)
        else:
            pygame.draw.circle(screen, p['color'], (int(cx), int(cy)), BLOCK_SIZE//5)
            pygame.draw.circle(screen, (255,255,255), (int(cx), int(cy)), BLOCK_SIZE//5, 2)

# === MODIFIED: Always show current player's block in side panel unless hovering ===
def draw_side_panel(hover_block, last_roll):
    area_x = GRID_COLS * (BLOCK_SIZE + MARGIN) + MARGIN
    pygame.draw.rect(screen, (240,247,255), (area_x, 0, SIDE_PANEL_WIDTH, WINDOW_HEIGHT))
    y = 10
    
    ###############################################
    #############################################
    
    #dice_box_size = BLOCK_SIZE + 36
    #pygame.draw.rect(screen, (200,220,240), (area_x + 24, y + 10, dice_box_size, dice_box_size), 0, border_radius=24)
    #dice_img = get_dice_image(last_roll, dice_box_size-12)
    #screen.blit(dice_img, (area_x + 30, y + 16))
    #y += dice_box_size + 20
    # Center the dice box and image in the side panel
    panel_center_x = area_x + SIDE_PANEL_WIDTH // 2
    dice_box_size = BLOCK_SIZE + 36
    dice_box_x = panel_center_x - (dice_box_size // 2)
    dice_box_y = y + 10
    pygame.draw.rect(screen, (200,220,240), (dice_box_x, dice_box_y, dice_box_size, dice_box_size), 0, border_radius=24)
    dice_img = get_dice_image(last_roll, dice_box_size - 12)
    dice_img_rect = dice_img.get_rect(center=(panel_center_x, dice_box_y + dice_box_size // 2))
    screen.blit(dice_img, dice_img_rect)
    
    y += dice_box_size + 20

    
    ########################################################
    #########################################################
    for idx, p in enumerate(players):
        if p['avatar']:
            img = pygame.transform.smoothscale(p['avatar'], (52, 52))
            screen.blit(img, (area_x+10, y+6))
        else:
            pygame.draw.circle(screen, p['color'], (area_x+32, y+26), 22)
        ptxt = f"{p['name']}: {p['score']} pts"
        color = p['color'] if idx == turn else (80,80,80)
        t = big_font.render(ptxt, True, color)
        screen.blit(t, (area_x+70, y+16))
        y += max(60, 52) + 8
        
    #t2 = font.render(f"Turn: {players[turn]['name']}", True, (30,30,90))
    #screen.blit(t2, (area_x+8, y+8))
    ######################################
#    t2 = turn_font.render(f"Turn: {players[turn]['name']}", True, (30,30,90))
 #   screen.blit(t2, (area_x+8, y+8))
   
    ####################################
    turn_text = f"Turn: {players[turn]['name']}"
    t2 = turn_font.render(turn_text, True, (30,30,90))
    turn_rect = t2.get_rect(center=(area_x + SIDE_PANEL_WIDTH // 2, y + 16))
    screen.blit(t2, turn_rect)
   ############################################################ 
    # Always show block info for player unless hovering!
    block_to_show = hover_block if hover_block is not None else players[turn]['pos']
    b = block_data[block_to_show]
    panel_y = y + 60
    pygame.draw.line(screen, (110,110,130), (area_x+4, panel_y), (area_x+SIDE_PANEL_WIDTH-8, panel_y), 1)
    panel_y += 10
    
    
#    img = get_block_image(b['number'], min(130, SIDE_PANEL_WIDTH-12))
 #   screen.blit(img, (area_x+10, panel_y))
  #  panel_y += img.get_height() + 5
    
    #preview_size = min(180, SIDE_PANEL_WIDTH-16)  # Change 180 to any size you like, or SIDE_PANEL_WIDTH-16 for max fit
    ################################################
    # --- Replace your old code block with this: ---
    preview_size = SIDE_PANEL_WIDTH - 16
    img = get_block_image(b['number'], preview_size)
    img_x = area_x + 10
    img_y = panel_y
    screen.blit(img, (img_x, img_y))
    panel_y += img.get_height() + 10  # More spacing for big text
    
    panel_center_x = img_x + (preview_size // 2)
    
    # Block title (large, centered)
    t3 = large_panel_font.render(f"{b['number']}: {b['title']}", True, (30,30,120))
    title_rect = t3.get_rect(center=(panel_center_x, panel_y + t3.get_height() // 2))
    screen.blit(t3, title_rect)
    panel_y += t3.get_height() + 10
    
    # Block description (medium, centered, line by line)
    if b['description']:
        desc_lines = [b['description'][i:i+28] for i in range(0, len(b['description']), 28)]
        for line in desc_lines:
            t4 = medium_panel_font.render(line, True, (50,50,50))
            line_rect = t4.get_rect(center=(panel_center_x, panel_y + t4.get_height() // 2))
            screen.blit(t4, line_rect)
            panel_y += t4.get_height() + 2
            
    ###########################################################        
            
# --- Effect line (medium, centered) ---
        


    # Only show effect *if* this block still has trivia
    
    if b['trivia_question'] and hover_block in trivia_blocks:
        # Display effect first
        if b['effect'] and b['effect'] != 'none':
            t5 = medium_panel_font.render(f"Effect: {b['effect'].capitalize()}", True, (0,90,200))
            effect_rect = t5.get_rect(center=(panel_center_x, panel_y + t5.get_height() // 2))
            screen.blit(t5, effect_rect)
            panel_y += t5.get_height() + 10
        
        # Then show trivia prompt
        t6 = medium_panel_font.render("Trivia on this block!", True, (200,120,0))
        trivia_rect = t6.get_rect(center=(panel_center_x, panel_y + t6.get_height() // 2))
        screen.blit(t6, trivia_rect)
        panel_y += t6.get_height() + 10

    
"""  

    if b['effect'] and b['effect'] != 'none':
        t5 = medium_panel_font.render(f"Effect: {b['effect'].capitalize()}", True, (0,90,200))
        effect_rect = t5.get_rect(center=(panel_center_x, panel_y + t5.get_height() // 2))
        screen.blit(t5, effect_rect)
        panel_y += t5.get_height() + 10
    
    # --- Trivia line (medium, centered) ---
    #if destination in trivia_blocks:
     #   correct = trivia_popup(destination, p)
      #  trivia_blocks.remove(destination)  # so it won't appear again
        # (Optional) also clear data:
       # bd = block_data[destination]
       # bd['trivia_question'] = ''
    if b['trivia_question']:
        t6 = medium_panel_font.render("Trivia on this block!", True, (200,120,0))
        trivia_rect = t6.get_rect(center=(panel_center_x, panel_y + t6.get_height() // 2))
        screen.blit(t6, trivia_rect)
        panel_y += t6.get_height() + 10
  """      
#########################################################################################
# === ADDED: Show info about destination after trivia ===
def draw_block_info_popup(dest_block_idx, result_type='correct'):
    area_x = GRID_COLS * (BLOCK_SIZE + MARGIN) + MARGIN
    popup_width = SIDE_PANEL_WIDTH - 16
    popup_height = 98
    base_y = WINDOW_HEIGHT - popup_height - 18
    b = block_data[dest_block_idx]
    popup = pygame.Surface((popup_width, popup_height))
    popup.fill((220, 250, 220) if result_type == "correct" else (255, 228, 228))
    pygame.draw.rect(popup, (40, 140, 40) if result_type == "correct" else (180,60,60), (0,0,popup_width,popup_height), 3, border_radius=10)
    heading = f"Destination ({'Correct' if result_type=='correct' else 'Wrong'} Answer):"
    popup.blit(panel_font.render(heading, True, (30,50,120)), (14, 10))
    popup.blit(font.render(f"{b['number']}: {b['title']}", True, (50,50,50)), (18, 35))
    if b['description']:
        lines = [b['description'][i:i+28] for i in range(0, len(b['description']), 28)]
        for k, line in enumerate(lines):
            popup.blit(font.render(line, True, (80,80,80)), (18, 60 + k*18))
    screen.blit(popup, (area_x+8, base_y))

# == Trivia + Feedback popups stay unchanged ==
def trivia_popup(block, player):
    b = block_data[block]
    if not b['trivia_question']:
        return None
    ttype = b.get('trivia_type','multiple_choice').lower()
    width, height = 540, 250 if ttype != "fill_blank" else 180
    popup = pygame.Surface((width, height))
    popup.fill((252, 252, 242))
    pygame.draw.rect(popup, (60,90,200), (0,0,width,height), 2)
    qtxt = panel_font.render(b['trivia_question'], True, (40,40,40))
    popup.blit(qtxt, (20, 18))
    if ttype in ('multiple_choice', 'mcq', 'choice', 'multiple choice'):
        choice_rects = []
        y = 60
        for i, choice in enumerate(b['trivia_choices']):
            choice_rect = pygame.Rect(30, y, width-60, 38)
            pygame.draw.rect(popup, (210,230,250), choice_rect)
            ctxt = font.render(f"{chr(65+i)}) {choice}", True, (40,40,40))
            popup.blit(ctxt, (choice_rect.x+10, choice_rect.y+8))
            choice_rects.append((choice_rect, choice))
            y += 44
        screen.blit(popup, ((WINDOW_WIDTH-width)//2, (WINDOW_HEIGHT-height)//2))
        pygame.display.flip()
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = event.pos
                    rel_x = mx - (WINDOW_WIDTH-width)//2
                    rel_y = my - (WINDOW_HEIGHT-height)//2
                    for i, (rect, choice) in enumerate(choice_rects):
                        if rect.collidepoint(rel_x, rel_y):
                            correct = (choice.strip().lower() == b['trivia_answer'].strip().lower())
                            reward = b['bonus'] if correct else b['penalty']
                            player['score'] += reward
                            feedback_popup(correct, reward, width, height)
                            return correct
                elif event.type == pygame.KEYDOWN:
                    idx = event.key - pygame.K_a
                    if 0 <= idx < len(choice_rects):
                        correct = (b['trivia_choices'][idx].strip().lower() == b['trivia_answer'].strip().lower())
                        reward = b['bonus'] if correct else b['penalty']
                        player['score'] += reward
                        feedback_popup(correct, reward, width, height)
                        return correct
    elif ttype in ('true_false', 'true/false', 'tf', 'true-false', 'boolean'):
        tf_choices = b['trivia_choices'] if b['trivia_choices'] else ['True','False']
        buttons = []
        y = 80
        for i, choice in enumerate(tf_choices):
            btn_rect = pygame.Rect(80 + i*180, y, 120, 46)
            pygame.draw.rect(popup, (210,230,210), btn_rect)
            txt = big_font.render(choice, True, (20,100,40))
            popup.blit(txt, (btn_rect.x+22, btn_rect.y+8))
            buttons.append((btn_rect, choice))
        screen.blit(popup, ((WINDOW_WIDTH-width)//2, (WINDOW_HEIGHT-height)//2))
        pygame.display.flip()
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = event.pos
                    rel_x = mx - (WINDOW_WIDTH-width)//2
                    rel_y = my - (WINDOW_HEIGHT-height)//2
                    for i, (rect, choice) in enumerate(buttons):
                        if rect.collidepoint(rel_x, rel_y):
                            correct = (choice.strip().lower() == b['trivia_answer'].strip().lower())
                            reward = b['bonus'] if correct else b['penalty']
                            player['score'] += reward
                            feedback_popup(correct, reward, width, height)
                            return correct
    elif ttype in ('fill_blank', 'fill_in_blank', 'fill-in-the-blank', 'fib', 'fill in the blank'):
        input_box = pygame.Rect(90, 100, width-180, 38)
        user_input = ""
        active = True
        while active:
            popup.fill((250,250,230))
            pygame.draw.rect(popup, (60,90,200), (0,0,width,height), 2)
            qtxt = panel_font.render(b['trivia_question'], True, (40,40,40))
            popup.blit(qtxt, (20, 18))
            pygame.draw.rect(popup, (230,210,240), input_box)
            txt_surface = font.render(user_input, True, (50,40,70))
            popup.blit(txt_surface, (input_box.x+8, input_box.y+8))
            hint = font.render("(Type and press Enter)", True, (90,90,90))
            popup.blit(hint, (input_box.x, input_box.y+38))
            screen.blit(popup, ((WINDOW_WIDTH-width)//2, (WINDOW_HEIGHT-height)//2))
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        ans = user_input.strip().lower()
                        correct = (ans == b['trivia_answer'].strip().lower())
                        reward = b['bonus'] if correct else b['penalty']
                        player['score'] += reward
                        feedback_popup(correct, reward, width, height)
                        return correct
                    elif event.key == pygame.K_BACKSPACE:
                        user_input = user_input[:-1]
                    elif len(user_input) < 28 and event.unicode.isprintable():
                        user_input += event.unicode
#######################################3
def show_results():
    # Calculate stats
    lines = []
    for p in players:
        lines.append(f"{p['name']} solved {p['trivia_correct']} of {p['trivia_attempts']} trivia")

    # Display loop for results screen
    run = True
    while run:
        screen.fill((30, 30, 40))
        y = WINDOW_HEIGHT // 3
        large = pygame.font.SysFont("arial", 36, bold=True)
        msg = large.render("Game Over!", True, (255, 220, 100))
        screen.blit(msg, (WINDOW_WIDTH//2 - msg.get_width()//2, y - 60))
        font = pygame.font.SysFont("arial", 24)
        for line in lines:
            txt = font.render(line, True, (200, 200, 200))
            screen.blit(txt, (WINDOW_WIDTH//2 - txt.get_width()//2, y))
            y += 40

        hint = font.render("Press SPACE to play again, ESC to quit", True, (180, 180, 180))
        screen.blit(hint, (WINDOW_WIDTH//2 - hint.get_width()//2, y + 50))

        pygame.display.flip()
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_SPACE:
                    run = False
                elif ev.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()
    # Reset game
    for p in players:
        p['pos'] = 0
        p['score'] = 0
        p['trivia_attempts'] = 0
        p['trivia_correct'] = 0




##############################################
def feedback_popup(correct, reward, width, height):
    popup2 = pygame.Surface((width, 80))
    popup2.fill((220, 255, 230) if correct else (255, 230, 230))
    msg = "Correct!" if correct else "Wrong!"
    ftxt = panel_font.render(f"{msg}  ({'+' if reward >=0 else ''}{reward} pts)", True, (30,160,60) if correct else (200,30,30))
    popup2.blit(ftxt, (20, 20))
    screen.blit(popup2, ((WINDOW_WIDTH-width)//2, (WINDOW_HEIGHT+height)//2))
    pygame.display.flip()
    pygame.time.wait(1100)

# === MODIFIED: main game loop for popup destination after trivia ===
player_won = None
last_roll = 1
msg = "Press SPACE or click dice to roll"
clock = pygame.time.Clock()
hover_block = None
popup_result = None  # (block index, 'correct'/'wrong'), or None
area_x = GRID_COLS * (BLOCK_SIZE + MARGIN) + MARGIN
panel_center_x = area_x + SIDE_PANEL_WIDTH // 2
dice_box_size = BLOCK_SIZE + 36
dice_box_x = panel_center_x - (dice_box_size // 2)
dice_box_y = 10 + 10  # If you used y = 10 before (first dice box), else match your 'y'

while True:
    screen.fill((235,240,255))
    draw_board()
    draw_snakes_and_ladders()
    draw_tokens()
    draw_side_panel(hover_block, last_roll)
    if popup_result:
        dest_idx, rtype = popup_result
        draw_block_info_popup(dest_idx, rtype)
    if player_won is not None:
        tmsg = big_font.render(f"{players[player_won]['name']} wins!", True, (200,60,60))
        screen.blit(tmsg, (70, 20))
    else:
        tmsg = font.render(msg, True, (24, 40, 160))
        screen.blit(tmsg, (20, WINDOW_HEIGHT - 35))

    pygame.display.flip()
    clock.tick(30)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit(); sys.exit()
        elif event.type == pygame.MOUSEMOTION:
            hover_block = block_at_pixel(event.pos[0], event.pos[1])
            
            
            
        ##############################################################
        ##############################################################
        
        elif event.type == pygame.KEYDOWN and player_won is not None:
            if event.key == pygame.K_SPACE:
                for p in players: p['pos'] = 0; p['score'] = 0
                turn = 0
                player_won = None
                msg = "Press SPACE to roll dice"
                
        ############################################################
        ############################################################
        
        elif event.type == pygame.KEYDOWN and player_won is None:
            if event.key == pygame.K_SPACE:
                popup_result = None
                roll = random.randint(1, 6)
                old_pos = players[turn]['pos']
        
                moved, msg, target, effect = process_turn(players[turn], roll)
                print(f"After effect: target={target}, effect={effect}")
                last_roll = roll
        
                # DEBUG log:
                print(
                    f"DEBUG | Player {turn+1} | Roll={roll} | "
                    f"From {old_pos} → {target} | Effect={effect} | Moved={moved}"
                )
        
                if moved:
                    animate_move(players[turn], old_pos, target)
                    if target == BLOCKS - 1:
                        player_won = turn
                        show_results()
                    else:
                        turn = (turn + 1) % NUM_PLAYERS
                else:
                    turn = (turn + 1) % NUM_PLAYERS
        
                    turn = (turn + 1) % NUM_PLAYERS

    
        ############################################################
        ############################################################        

                
                ######################################################################
                ######################################################################
            ##
                
               
               

