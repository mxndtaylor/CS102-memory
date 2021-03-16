# Source: http://www.codeskulptor.org/#user48_QXHjhKp4u1_3.py
# implementation of card game - Memory

import simplegui
import random

CARD_DIM = (62, 100)
COLORS = {"cardface1" : "White", "cardface2" : "Black",
          "suit1": "Black", "suit2" : "Red", 
          "cardback1" : "#35478C", "cardback2" : "#7FB2F0", 
          "cardback3" : "#4E7AC7", "board1" : "#489A5F", 
          "board2" : "#347045"}
BG_LINES = {"width" : 10, "gap" : 20, "slope" : (1, 0)}
SPACING = (1.5 * CARD_DIM[0], 1.3 * CARD_DIM[1])
SIZE = 4
BOARD = ((SIZE + 1) * SPACING[0], (SIZE + 1) * SPACING[1])
POSITIONS = [((j + 1) * SPACING[0], (i + 1) * SPACING[1]) 
            for j in range(SIZE) for i in range(SIZE)]
CARDS = "234567890JQKA"
SUITS = "dchs"
# graphic path through a 9 point grid that approximates the suits
SUIT_PATHS = [[0,2,1,3], [4,7,2,5,4,5,0,6,4,6,3,8,4,8,7],
              [1,2,5,4,6,3], [4,7,2,0,3,8,4,8,7]]

# performs first time setup
def init():
    calc_cards()
    new_game()
    
# calculates the graphics a card
def calc_cards():
    global card_polys, back_grids, face_grids
    card_polys = []
    back_grids = []
    face_grids = []
    for pos in POSITIONS:
        left = pos[0] - CARD_DIM[0] / 2
        right = left + CARD_DIM[0]
        top = pos[1] - CARD_DIM[1] / 2
        bot = top + CARD_DIM[1]
        card_polys.append([[left, top], [right, top],
                           [right, bot], [left, bot]])
        
        back_top = pos[0], pos[1] - 12
        back_bot = pos[0], pos[1] + 12
        back_grids.append([back_top, back_bot])
        
        face_pts = [(pos[0] + 10, pos[1] - 20), 
                    (pos[0] + 10, pos[1] + 40),
                    (pos[0] - 5, pos[1] + 10), 
                    (pos[0] + 25, pos[1] + 10)]
        for i in range(len(face_pts)):
            for j in range(i+1, len(face_pts)):
                pt = midpoint(face_pts[i], face_pts[j])
                if pt not in face_pts:
                    face_pts.append(pt)
        
        face_pts.append((pos[0] - 25, pos[1] - 5))
        face_grids.append(face_pts)

# calculates the midpoint of two points
def midpoint(pt1, pt2):
    return ((pt1[0] + pt2[0]) / 2, (pt1[1] + pt2[1]) / 2)

# helper function to initialize globals
def new_game():
    global exposed, turns, state, last_card
    exposed = []
    last_card = None
    state = 0
    update_turns(reset = True)
    shuffle_deck()

# updates the turn counter display
def update_turns(reset = False):
    global turns
    text = label.get_text()
    old_turns = text.split(' ')[-1]
    if reset:
        turns = 0
    else:
        turns += 1
    text = text.replace(old_turns,str(turns))
    label.set_text(text)

# randomizes the deck, and deals a game of memory
def shuffle_deck():
    global cards
    n_vals, n_suits = len(CARDS), len(SUITS)
    deck = range(n_vals * n_suits)
    random.shuffle(deck)
    cards = deck[: SIZE ** 2 / 2]
    cards = [(i % n_vals, i % n_suits) for i in cards]
    cards = cards * 2
    random.shuffle(cards)
    
# helper function draws the back of a card
def draw_back(canvas, idx):
    poly, grid = card_polys[idx], back_grids[idx]
    canvas.draw_polygon(poly, 2, COLORS["cardback2"], 
                            COLORS["cardback1"])
    canvas.draw_circle(grid[0], 18, 3, COLORS["cardback3"])
    canvas.draw_circle(grid[1], 18, 3, COLORS["cardback3"])
    canvas.draw_line(grid[0], grid[1], 3, COLORS["cardback3"])
    
# helper function draws the front of a card
def draw_front(canvas, idx):
    poly, grid = card_polys[idx], face_grids[idx]
    val_idx, suit_idx = cards[idx]
    canvas.draw_polygon(poly, 2, COLORS["cardface2"], COLORS["cardface1"])
    
    suit_color = COLORS["suit2"]
    if suit_idx % 2 == 1:
        suit_color = COLORS["suit1"]
    
    grid_path = SUIT_PATHS[suit_idx]
    poly = [grid[pt] for pt in grid_path]
    canvas.draw_polygon(poly, 1, COLORS["cardface1"], suit_color)
    
    val = CARDS[val_idx]
    if val is '0':
        val = '10'
    shadow_pos = [grid[-1][0] + 1, grid[-1][1] + 1]
    canvas.draw_text(val, shadow_pos, 42, "Silver")
    canvas.draw_text(val, grid[-1], 42, suit_color)

# define event handlers
def mouseclick(pos):
    global state, turns
    for idx in range(SIZE ** 2):
        if idx not in exposed:
            poly = card_polys[idx]
            left, top = poly[0]
            right, bot = poly[2]
            if left <= pos[0] <= right and top <= pos[1] <= bot:
                if state == 2:
                    idx1, idx2 = exposed[-2:]
                    if cards[idx1] != cards[idx2]:
                        exposed.pop()
                        exposed.pop()
                if state == 1:
                    update_turns()
                # 0 -> 1, 1 -> 2, 2 -> 1
                state = (state % 2) + 1
                exposed.append(idx)
                        
# cards are logically 62x100 pixels in size (golden ratio)
def draw(canvas):
    for idx in range(SIZE ** 2):
        if idx in exposed:
            draw_front(canvas, idx)
        else:
            draw_back(canvas, idx)

# create frame and add a button and labels
frame = simplegui.create_frame("Memory", BOARD[0], BOARD[1])
frame.set_canvas_background(COLORS["board1"])
frame.add_button("Deal New Game", new_game, 150)
label = frame.add_label("Turns = 0")

# register event handlers
frame.set_mouseclick_handler(mouseclick)
frame.set_draw_handler(draw)

# get things rolling
init()
frame.start()
