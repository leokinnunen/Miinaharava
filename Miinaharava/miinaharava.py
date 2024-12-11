import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import os
import time
import random
import csv
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
tile_width = 40


def count_csv_rows(file_path):
    try:
        with open(file_path, mode='r', newline='') as file:
            reader = csv.reader(file)
            row_count = sum(1 for row in reader)
        return row_count
    except:
        return 0


def unix_to_finland_time(unix_time):
    utc_dt = datetime.fromtimestamp(int(float(unix_time)), tz=timezone.utc)

    finland_tz = ZoneInfo('Europe/Helsinki')

    finland_dt = utc_dt.astimezone(finland_tz)

    date_str = finland_dt.strftime('%d-%m-%Y')
    time_str = finland_dt.strftime('%H:%M:%S')

    return date_str, time_str


def get_script_directory():
    #Returns the path where this file is
    script_path = os.path.abspath(__file__)
    script_dir = os.path.dirname(script_path)
    return script_dir


#The main class that acts as the window
class Miinaharava(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Miinaharava")
        self.geometry("720x480")
        self.resizable(True, True) 
        self.minsize(160, 0)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.width = 0
        self.height = 0
        # Initialize frames
        self.visible_frame = ""
        self.frames = {}
        for F in (Menu, Game, Dimensions, Stats, Loss, Win):
            page_name = F.__name__
            frame = F(parent=self, controller=self)
            self.frames[page_name] = frame

            # Place all frames in the same location
            frame.grid(row=0, column=0, sticky="nsew")
        
        self.show_frame("Menu")

    def show_frame(self, page_name):
        #Show a frame for the given page name
        frame = self.frames[page_name]
        frame.tkraise()  
        self.visible_frame = page_name
        if page_name == "Loss":
            self.frames[page_name].upon_losing()
        if page_name == "Win":
            self.frames[page_name].upon_winning()
        if page_name == "Stats":
            self.frames[page_name].show_stats()
    
#Menu for the game
class Menu(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.parent = parent
        self.parent.geometry(f"720x480")
        #Dimensions for the frame
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)
        #Button Play new game
        button_play = tk.Button(self,
                           text="Play new game",
                           command=lambda: controller.show_frame("Dimensions"))
        button_play.grid(row=0, column=1, pady=10, sticky="nsew")
        #Button that brings you to stats menu
        button_stats = tk.Button(self,
                           text="Statistics",
                           command=lambda: controller.show_frame("Stats"))      
        button_stats.grid(row=1, column=1, pady=10, sticky="nsew")
        #Button that quits
        button_quit = tk.Button(self,
                           text="Quit",
                           command=self.controller.destroy)      
        button_quit.grid(row=2, column=1, pady=10, sticky="nsew")

class Dimensions(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.parent = parent
        self.parent.geometry(f"720x480")
        # Dimensions for the frame
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)
        self.rowconfigure(3, weight=1)
        self.rowconfigure(4, weight=1)
        self.rowconfigure(5, weight=1)
        self.rowconfigure(6, weight=1)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)
        

        x_label = tk.Label(self, text="Input width of the game in number of tiles(max 40)")
        y_label = tk.Label(self, text="Input height of the game in number of tiles(max 20)")
        mine_label = tk.Label(self, text="Input number of mines")
        self.x_entry = tk.Entry(self, justify='center')
        self.y_entry = tk.Entry(self, justify='center')
        self.mine_entry = tk.Entry(self, justify='center')
        self.x_entry.bind('<Return>', self.focus_next_window)
        self.y_entry.bind('<Return>', self.focus_next_window)
        self.mine_entry.bind('<Return>', self.focus_next_window)

        button_game = tk.Button(self,
                                text="Play",
                                command=self.start_game)

        x_label.grid(row=0, column=1, pady=10, sticky="nsew")
        self.x_entry.grid(row=1, column=1, pady=10, sticky="nsew")
        y_label.grid(row=2, column=1, pady=10, sticky="nsew")
        self.y_entry.grid(row=3, column=1, pady=10, sticky="nsew")
        mine_label.grid(row=4, column=1, pady=10, sticky="nsew")
        self.mine_entry.grid(row=5, column=1, pady=10, sticky="nsew")
        button_game.grid(row=6, column=1, pady=10, sticky="nsew")
    def focus_next_window(self, event): #Siirtää kursorin seuraavaan widgettiin
        event.widget.tk_focusNext().focus()
        return("break")

    def start_game(self):
        try:
            # Get dimensions from entries
            width = int(self.x_entry.get())
            height = int(self.y_entry.get())
            mine_number = int(self.mine_entry.get())
            if width <= 0 or height <= 0:
                raise ValueError("Dimensions must be positive integers.")

            if width > 40 or height > 20:
                self.controller.show_frame("Dimensions")
                return 0
            if mine_number >= width*height-8:
                self.controller.show_frame("Dimensions")
                return 0
            # Set dimensions in the parent
            self.controller.width = width
            self.controller.height = height
            self.controller.mine_number = mine_number
            
            self.parent.geometry(f"{40*self.controller.width}x{40*self.controller.height}")
            # Update the Game frame with new dimensions
            game_frame = self.controller.frames["Game"]
            game_frame.create_buttons(width, height)
            # Show the Game frame
            self.controller.show_frame("Game")
        except ValueError as e:
            messagebox.showerror("Invalid input", str(e))


class Stats(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.parent = parent
        self.parent.geometry(f"720x480")
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)
        self.columnconfigure(3, weight=1)
        self.columnconfigure(4, weight=1)

    def show_stats(self):
        file_path = f"{get_script_directory()}\\statistics.csv"
        #Säädöt scrollbaria varten
        canvas = tk.Canvas(self)
        scrollbar = tk.Scrollbar(self, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=0, column=1, sticky="ns")
        canvas.grid(row=0, column=0, sticky="nsew")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)
        row_count = count_csv_rows(file_path)        
        try:
            with open(file_path, mode='r', newline='', encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile)
                rows = list(reader)
                for i, row in enumerate(rows):
                    stat_labelw = tk.Label(scrollable_frame, text=str(row[0]))
                    stat_labelt = tk.Label(scrollable_frame, text=str(row[1]))
                    stat_labelm = tk.Label(scrollable_frame, text=str(row[2]))
                    stat_labeld = tk.Label(scrollable_frame, text=str(row[3]))
                    stat_labelc = tk.Label(scrollable_frame, text=str(row[4]))
                    stat_labelw.grid(row=i+1, column=0, pady=10, sticky="nsew")
                    stat_labelt.grid(row=i+1, column=1, pady=10, sticky="nsew")
                    stat_labelm.grid(row=i+1, column=2, pady=10, sticky="nsew")
                    stat_labeld.grid(row=i+1, column=3, pady=10, sticky="nsew")
                    stat_labelc.grid(row=i+1, column=4, pady=10, sticky="nsew")
                    if i == row_count-1:
                        break

        except Exception:
            warninglabel = tk.Label(scrollable_frame, text="No Stats yet")
            warninglabel.grid(row=0, column=0, sticky="nsew")
        button_menu = tk.Button(self,
                           text="Menu",
                           command=lambda: self.controller.show_frame("Menu"))
        button_menu.grid(row=0, column=2, pady=10)

# The game
class Game(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.controller.start_time = 0
        self.parent = parent
        self.photo_tile = tk.PhotoImage(file = f"{get_script_directory()}\\sprites\\tile_back.png") 
        self.photo_mine = tk.PhotoImage(file = f"{get_script_directory()}\\sprites\\tile_mine.png")
        self.tile_graphics = []
        self.tile_graphics.append(tk.PhotoImage(file = f"{get_script_directory()}\\sprites\\tile_empty.png"))
        for i in range(1, 9):
            self.tile_graphics.append(tk.PhotoImage(file = f"{get_script_directory()}\\sprites\\tile_{i}.png"))
        self.tile_graphics.append(tk.PhotoImage(file = f"{get_script_directory()}\\sprites\\tile_mine.png"))
        self.tile_graphics.append(tk.PhotoImage(file = f"{get_script_directory()}\\sprites\\tile_flag.png"))
        

    def create_buttons(self, width, height):

        # Clear any existing buttons
        self.mines_scattered = False
        for widget in self.winfo_children():
            widget.destroy()

        # Configure columns and rows
        for i in range(width):
            self.columnconfigure(i, weight=1)
        for i in range(height):
            self.rowconfigure(i, weight=1)
        self.buttons = {}
        # Create buttons
        for i in range(width):
            for j in range(height):
                button = tk.Button(self, image=self.photo_tile)
                button.grid(row=j, column=i, sticky="nsew")
                button.bind("<Button-1>", self.on_left_click)
                button.bind("<Button-3>", self.on_right_click)
                self.buttons[(i, j)] = button

    def scatter_mines(self, init_x, init_y):
        self.mine_coordinates = []
        coordinates = ()
        for mine in range(self.controller.mine_number):
            mine_x = random.randint(0, self.controller.width-1)
            mine_y = random.randint(0, self.controller.height-1)
            coordinates = (mine_x, mine_y)
            #Ensures that there is no duplicate coordinates
            while coordinates in self.mine_coordinates or coordinates == (init_x, init_y) or coordinates in self.tiles_nearby(init_x, init_y):
                mine_x = random.randint(0, self.controller.width-1)
                mine_y = random.randint(0, self.controller.height-1)
                coordinates = (mine_x, mine_y)
            self.mine_coordinates.append(coordinates)
        self.mines_scattered = True
        self.all_coordinates = {}
        for i in range(self.controller.width):
            for j in range(self.controller.height):
                self.all_coordinates[(i, j)] = self.mines_nearby(i, j)
    
        


    def on_right_click(self, event):
        grid_info = event.widget.grid_info()
        x = grid_info['column']
        y = grid_info['row']
        self.buttons[(x, y)].config(image=self.tile_graphics[10])

    def on_left_click(self,event):
        grid_info = event.widget.grid_info()
        x = grid_info['column']
        y = grid_info['row']
        if not self.mines_scattered:
            self.scatter_mines(x, y)
            self.controller.start_time = time.time()
        if (x, y) in self.mine_coordinates:
            
            self.buttons[(x, y)].config(image=self.photo_mine)
            self.after(1000,lambda: self.controller.show_frame("Loss"))            
        else:
            mine_number = self.mines_nearby(x, y)
            if mine_number==0:
                self.find_connected_coordinates((x, y), self.all_coordinates.keys(), False)
            self.buttons[(x, y)].config(image=self.tile_graphics[mine_number])
        if self.check_win():
            self.after(1000,lambda: self.controller.show_frame("Win"))     

    
    def mines_nearby(self, x, y):
        mines = 0
        if (x,y) in self.mine_coordinates:
            return 9
        for i in range (x-1, x+2):
            for j in range(y-1, y+2):
                if (i, j) in self.mine_coordinates and (i,j) != (x,y):
                    mines += 1
        return mines

    def emptys_nearby(self, x, y):
        for i in range (x-1, x+2):
            for j in range(y-1, y+2):
                if self.all_coordinates[(i, j)]==0:
                    self.find_connected_coordinates((i, j), self.all_coordinates.keys(), False)

    def tiles_nearby(self, x, y):
        list_of_nearbys = []
        for i in range (x-1, x+2):
            for j in range(y-1, y+2):
                list_of_nearbys.append((i, j))
        return list_of_nearbys


    def find_connected_coordinates(self, start, coordinates, recurse):
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        #using sets to be more efficient and avoid duplicates
        coordinate_set = set(coordinates)
        waiting = [start]
        visited = set()
        connected = set()

        while waiting:
            current = waiting.pop(0)

            if current in visited:
                continue

            visited.add(current)
            connected.add(current)

            # Check all adjacent coordinates
            for direction in directions:
                neighbor = (current[0] + direction[0], current[1] + direction[1])
                if neighbor in coordinate_set and neighbor not in visited and not self.mines_nearby(neighbor[0], neighbor[1]):
                    waiting.append(neighbor)
                    self.buttons[neighbor].config(image=self.tile_graphics[self.mines_nearby(neighbor[0], neighbor[1])])
        
        #Check the borders to get the numbers
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0), (1, 1), (1, -1), (-1, -1), (-1, 1)]
        for block in connected:
            for direction in directions:
                neighbor = (block[0] + direction[0], block[1] + direction[1])
                if neighbor in coordinate_set and neighbor not in connected:
                    if self.mines_nearby(neighbor[0], neighbor[1]):
                        self.buttons[neighbor].config(image=self.tile_graphics[self.mines_nearby(neighbor[0], neighbor[1])])
                    if not self.mines_nearby(neighbor[0], neighbor[1]) and not recurse:
                        self.buttons[neighbor].config(image=self.tile_graphics[self.mines_nearby(neighbor[0], neighbor[1])])                        
                        self.find_connected_coordinates((neighbor), self.all_coordinates, True)


        return connected
    
    def check_win(self):
        for tile in self.all_coordinates:
            if self.all_coordinates[tile] != 9 and not self.check_turned(self.buttons[tile]):
                return False
        
        return True


    def check_turned(self, button):
        if str(button.cget("image")) != str(self.photo_tile) and str(button.cget("image")) != str(self.photo_mine):
            return True
        else:
            return False

    
class Loss(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)
        self.rowconfigure(3, weight=1)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)
    
    def upon_losing(self):
        loss_label = tk.Label(self, text="You lose!")
        time_label = tk.Label(self, text=f"Your time: {round(time.time()-self.controller.start_time)}s")
        
        button_play = tk.Button(self,
                           text="Play new game",
                           command=lambda: self.controller.show_frame("Dimensions"))
        button_menu = tk.Button(self,
                           text="Menu",
                           command=lambda: self.controller.show_frame("Menu")) 
        loss_label.grid(row=0, column=1, pady=10, sticky="nsew")
        time_label.grid(row=1, column=1, pady=10, sticky="nsew")
        button_play.grid(row=2, column=1, pady=10, sticky="nsew")
        button_menu.grid(row=3, column=1, pady=10, sticky="nsew")
        date, clock = unix_to_finland_time(time.time())
        save_data_csv("Loss", f"{round(time.time()-self.controller.start_time)}s", self.controller.mine_number, date, clock)

class Win(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)
        self.rowconfigure(3, weight=1)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)

    def upon_winning(self):
        win_label = tk.Label(self, text="You win!")
        time_label = tk.Label(self, text=f"Your time: {round(time.time()-self.controller.start_time)}s")
        
        button_play = tk.Button(self,
                           text="Play new game",
                           command=lambda: self.controller.show_frame("Dimensions"))
        button_menu = tk.Button(self,
                           text="Menu",
                           command=lambda: self.controller.show_frame("Menu")) 
        win_label.grid(row=0, column=1, pady=10, sticky="nsew")
        time_label.grid(row=1, column=1, pady=10, sticky="nsew")
        button_play.grid(row=2, column=1, pady=10, sticky="nsew")
        button_menu.grid(row=3, column=1, pady=10, sticky="nsew")
        date, clock = unix_to_finland_time(time.time())
        save_data_csv("Win", f"{round(time.time()-self.controller.start_time)}s", self.controller.mine_number, date, clock)

#Saves data to csv
def save_data_csv(worl, time, mine_number, date, clock):
    file_name = f"{get_script_directory()}/statistics.csv"
    fieldnames = ["Win or loss", "Time", "Mines", "Date", "Clock"]  # List of column names

    file_exists = os.path.isfile(file_name)
    with open(file_name, 'a', encoding='UTF8', newline='') as f_object:
        writer = csv.DictWriter(f_object, fieldnames=fieldnames, delimiter=',')
        if not file_exists:
            writer.writeheader()
        data_row = {
            "Win or loss": worl,
            "Time": time,
            "Mines": mine_number,
            "Date": date,
            "Clock": clock
        }
        writer.writerow(data_row)

if __name__ == "__main__":
    app = Miinaharava()
    app.mainloop()
