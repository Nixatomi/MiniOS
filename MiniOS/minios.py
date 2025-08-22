import os
import sys
import datetime
import platform
import subprocess
import shutil
import re
import time
import socket
import urllib.request
from urllib.error import URLError
import random

# Import third-party libraries, gracefully handling if they are not installed.
try:
    import psutil
    PSUTIL_INSTALLED = True
except ImportError:
    PSUTIL_INSTALLED = False

try:
    import GPUtil
    GPUTIL_INSTALLED = True
except ImportError:
    GPUTIL_INSTALLED = False
    
try:
    from PIL import Image
    PILLOW_INSTALLED = True
except ImportError:
    PILLOW_INSTALLED = False

# Global variable to store the start time of the program
program_start_time = time.time()

# Global variable to store the current background image path
current_background_path = None

# Global variable to store the server process object for non-blocking execution
server_process = None

def clear_screen():
    """Clears the console screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def show_drivers_help():
    """Displays a list of required packages (drivers)."""
    print("=== MiniOS Drivers Information ==S")
    print("To use all features of MiniOS, you need to install the following packages.")
    print("Open your terminal and run these commands:")
    
    print("\nFor full PC information (CPU, RAM):")
    print("  pip install psutil")
    
    print("\nFor GPU information (NVIDIA only):")
    print("  pip install gputil")

    print("\nFor image display (ASCII art):")
    print("  pip install Pillow")
    
    print("\n")

def get_file_list_lines():
    """Returns a list of strings representing the files and folders."""
    files = os.listdir(os.getcwd())
    file_list_lines = []
    if not files:
        file_list_lines.append("[No files or folders]")
    else:
        for f in files:
            full_path = os.path.join(os.getcwd(), f)
            if os.path.isdir(full_path):
                file_list_lines.append(f"[DIR] {f}")
            else:
                file_list_lines.append(f"[FILE] {f}")
    return file_list_lines

def list_files_and_folders():
    """Prints the list of files and folders to the console."""
    lines = get_file_list_lines()
    for line in lines:
        print(line)

def show_gui_desktop():
    """
    Displays a modern, 'GUI-style' desktop with files and a background.
    Includes error handling to prevent crashes.
    """
    try:
        clear_screen()
        print("================================")
        print("          M i n i O S")
        print("================================\n")
        
        # Get the file list and background ASCII art
        file_list_lines = get_file_list_lines()
        ascii_background_lines = get_ascii_background()
        
        # Determine max line count for consistent display
        max_lines = max(len(file_list_lines), len(ascii_background_lines))
        
        # The image is 66 chars wide, so we pad the file list
        file_list_width = 30
        
        # Print the combined output line by line
        print("           (Apps)")
        print()
        for i in range(max_lines):
            file_line = file_list_lines[i].ljust(file_list_width) if i < len(file_list_lines) else ' ' * file_list_width
            image_line = ascii_background_lines[i] if i < len(ascii_background_lines) else ''
            print(f"  {file_line}  {image_line}")
            
        print("\n" * 2) # Add some space at the bottom
        print("=========================================================================================================================")
        print(" 📂 (folder) | 📝 (create) | 💻 (pcinfo) | ⏰ (time) | 🤖 (ai) | 🎨 (image) | ✍️ (code) | 🖌️ (paint) |")
        print("=========================================================================================================================")
        print("Type a command from the list above or 'help' for all commands.")
        
    except Exception as e:
        print(f"An error occurred while drawing the desktop: {e}")
        print("Trying to reset to a simple layout.")
        print("Please use the 'background' command to change the background again.")
        show_help() # Fallback to a simpler view

def get_ascii_background():
    """
    Generates a solid yellow Christian cross as the ASCII art background.
    Returns the ASCII art as a list of strings.
    """
    WIDTH = 66
    HEIGHT = 20
    ascii_lines = []
    
    # Define the cross dimensions and position
    # Vertical arm
    vertical_x_start = 30
    vertical_x_end = 36
    vertical_y_start = 2
    vertical_y_end = 20
    
    # Horizontal arm
    horizontal_x_start = 22
    horizontal_x_end = 44
    horizontal_y_start = 5
    horizontal_y_end = 8
    
    # ANSI escape code for yellow text
    YELLOW_CHAR = "\033[93m#\033[0m"
    EMPTY_CHAR = " "

    for y in range(HEIGHT):
        line = ""
        for x in range(WIDTH):
            is_on_vertical_arm = (x >= vertical_x_start and x <= vertical_x_end) and \
                                 (y >= vertical_y_start and y <= vertical_y_end)
            
            is_on_horizontal_arm = (x >= horizontal_x_start and x <= horizontal_x_end) and \
                                   (y >= horizontal_y_start and y <= horizontal_y_end)
            
            if is_on_vertical_arm or is_on_horizontal_arm:
                line += YELLOW_CHAR
            else:
                line += EMPTY_CHAR
        ascii_lines.append(line)
        
    return ascii_lines


def set_background(filepath):
    """Sets the current background image path."""
    global current_background_path
    if os.path.exists(filepath):
        current_background_path = filepath
        print(f"Background set to '{filepath}'.")
    else:
        print("Error: File not found.")

def show_boot_screen():
    """
    Displays the boot screen for 4 seconds before moving to the main desktop.
    """
    clear_screen()
    print("================================")
    print("          M i n i O S")
    print("================================\n")
    
    print("\n")
    print("##" + " " * 6 + "W E L C O M E" + " " * 49 + "##")
    print("##" + " " * 66 + "##")
    print("##" + " " * 66 + "##")
    print("##  Welcome to MiniOS!                                      ##")
    print("##  BEFORE USING THIS PROGRAM, PLEASE BE ADVISED THAT IT    ##")
    print("##  CAN DELETE YOUR PERSONAL STUFF. BE CONSCIOUS AND        ##")
    print("##  CAREFUL WHEN USING COMMANDS LIKE 'delete', 'delfolder'  ##")
    print("##  and 'rename'. You have been warned.                     ##")
    ("##" + " " * 66 + "##")
    print("##" + " " * 66 + "##")
    print("#" * 70)
    print("\n")
    
    # Wait for 4 seconds
    time.sleep(4)
    clear_screen()

def show_help():
    """Displays the list of all available commands."""
    print("""
MiniOS Commands:
  help        - Show this message
  list        - List files/folders in current directory
  desktop     - Show fake desktop
  calc        - Open calculator
  create      - Create a new text file
  read        - Read a text file's content
  edit        - Edit an existing text file
  run         - Execute a Python (.py) file
  delete        - Delete a file
  rename      - Rename a file or folder
  delfolder   - Delete a folder and its contents
  todo        - Manage a simple to-do list
  pcinfo      - Display PC hardware (CPU/RAM/GPU) information
  time        - Display the current date and time
  uptime      - Display system uptime
  folder        - Manage a folder (view or create)
  ai          - Chat with a mini AI
  internet    - Connect to a simple server (runs in background)
  kill_server - Stop the running internet server
  convert     - Convert the last fetched webpage to Markdown
  image       - Display an image as ASCII art
  code        - Open a simple code editor
  paint       - Open a text-based drawing app
  cd          - Change the current directory
  background  - Set an image as the desktop background
  drivers     - Displays the required pips to install
  games       - Opens a folder for your games
  terry_davis - Displays information about Terry A. Davis
  special_thanks - Displays special thanks and credits
  ping        - Pings google.com to check internet connectivity
  exit        - Exit MiniOS
""")

def terry_davis_story():
    """Displays information about Terry A. Davis and his legacy."""
    clear_screen()
    print("====================================")
    print("         Terry A. Davis Story      ")
    print("====================================")
    print("\nTerry A. Davis was an American programmer who created the operating system TempleOS.")
    print("His story is a tragic one, marked by a severe mental illness, schizophrenia, which began in his 20s.")
    print("He was a brilliant and highly skilled programmer, but his illness led to bizarre behaviors,")
    print("delusions of divine communication, and struggles that isolated him from the world.")
    print("\nDespite his personal struggles, he dedicated over a decade of his life to building TempleOS")
    print("entirely from scratch, a project he believed was divinely inspired. The OS is a testament")
    print("to his programming genius, featuring a unique 64-bit, non-preemptive multitasking kernel,")
    print("and a programming language called HolyC. It was designed to be a modern-day temple, a tribute to God.")
    print("\nTerry's life and work have become a complex and often misunderstood part of internet lore.")
    print("While some remember him for his eccentric behavior, many in the programming community respect")
    print("his incredible technical ability and the sheer scale of his one-man project.")
    print("\nTerry A. Davis passed away in 2018 at the age of 48.")
    print("\nMay he rest in peace.")
    print("\n====================================")
    
def special_thanks_command():
    """Displays special thanks and credits."""
    print("\nSPECIAL THANKS TO")
    print("xXNixaXx")
    print("CaseMedia")
    print("Google Gemini</3")
    print("version 1.1")
    print("")

def calculator():
    """A simple calculator that can evaluate math expressions."""
    print("=== MiniOS Calculator ===")
    print("You can enter full math expressions, e.g., '2 + 3 * 4'.")
    print("Type 'exit' to return to MiniOS.\n")
    while True:
        expr = input("Calc> ").strip()
        if expr.lower() == "exit":
            break
        try:
            # Safely evaluate a limited set of expressions
            allowed_names = {"abs": abs, "round": round, "pow": pow}
            result = eval(expr, {"__builtins__": None}, allowed_names)
            print("Result:", result)
        except:
            print("Invalid expression. Use numbers and +, -, *, /, **, %, parentheses.")

def code_editor():
    """A simple text editor for writing and saving Python files."""
    print("=== MiniOS Code Editor ===")
    filename = input("Enter filename for your code (e.g., my_program.py): ").strip()
    
    if not filename.endswith('.py'):
        print("Filename must end with '.py'.")
        return

    print(f"Start writing your code for '{filename}'.")
    print("Type 'save()' on a new line to save and exit.")
    
    lines = []
    while True:
        line = input(">>> ").strip()
        if line == 'save()':
            break
        lines.append(line)
        
    code_content = "\n".join(lines)
    
    try:
        with open(filename, "w") as f:
            f.write(code_content)
        print(f"Code saved to '{filename}'.")
    except Exception as e:
        print(f"Error saving file: {e}")

def text_paint():
    """A simple text-based drawing app."""
    # Define canvas dimensions
    WIDTH = 80
    HEIGHT = 20
    
    # Create an empty canvas (a list of lists)
    canvas = [[' ' for _ in range(WIDTH)] for _ in range(HEIGHT)]
    
    def display_canvas():
        """Helper function to print the current state of the canvas."""
        clear_screen()
        print("=== MiniOS Text Paint ===")
        print("--- Canvas ---")
        print("+" + "-" * WIDTH + "+")
        for row in canvas:
            print("|" + "".join(row) + "|")
        print("+" + "-" * WIDTH + "+")
        print("Commands: draw <x> <y> <char>, clear, save <filename>, load <filename>, exit")
        print(f"Canvas size: {WIDTH}x{HEIGHT}")

    def save_canvas(filename):
        """Saves the current canvas to a file."""
        try:
            with open(filename, 'w') as f:
                for row in canvas:
                    f.write("".join(row) + "\n")
            print(f"Canvas saved to '{filename}'.")
        except Exception as e:
            print(f"Error saving file: {e}")

    def load_canvas(filename):
        """Loads a canvas from a file."""
        nonlocal canvas
        try:
            with open(filename, 'r') as f:
                lines = f.readlines()
                new_canvas = []
                for line in lines:
                    new_canvas.append(list(line.strip().ljust(WIDTH)[:WIDTH]))
                
                # Resize if the loaded canvas is smaller
                while len(new_canvas) < HEIGHT:
                    new_canvas.append([' '] * WIDTH)
                
                canvas = new_canvas[:HEIGHT]
            print(f"Canvas loaded from '{filename}'.")
        except FileNotFoundError:
            print(f"Error: File '{filename}' not found.")
        except Exception as e:
            print(f"Error loading file: {e}")

    while True:
        display_canvas()
        command_input = input("Paint> ").strip().split(' ', 3)
        command = command_input[0].lower()

        if command == "exit":
            break
        elif command == "clear":
            canvas = [[' ' for _ in range(WIDTH)] for _ in range(HEIGHT)]
        elif command == "draw":
            try:
                if len(command_input) < 4:
                    print("Usage: draw <x> <y> <char>")
                    continue
                x = int(command_input[1])
                y = int(command_input[2])
                char = command_input[3]
                if 0 <= x < WIDTH and 0 <= y < HEIGHT:
                    canvas[y][x] = char[0] # Use only the first character
                else:
                    print("Coordinates out of bounds.")
            except (ValueError, IndexError):
                print("Invalid coordinates. Please use integers.")
        elif command == "save":
            if len(command_input) > 1:
                save_canvas(command_input[1])
            else:
                print("Usage: save <filename>")
        elif command == "load":
            if len(command_input) > 1:
                load_canvas(command_input[1])
            else:
                print("Usage: load <filename>")
        else:
            print("Unknown command.")

def create_file():
    """Creates a new text file with user-provided content in the current directory."""
    filename = input("Enter filename to create: ").strip()
    if not filename:
        print("No filename entered.")
        return
    
    if os.path.exists(filename):
        print("File already exists.")
        return
    content = input("Enter content for the file (leave empty for blank):\n")
    try:
        with open(filename, "w") as f:
            f.write(content)
        print(f"File '{filename}' created.")
    except Exception as e:
        print("Error creating file:", e)

def read_file():
    """Reads and displays the content of a text file from the current directory."""
    filename = input("Enter filename to read: ").strip()
    if not filename:
        print("No filename entered.")
        return
    
    if not os.path.exists(filename) or os.path.isdir(filename):
        print("File does not exist or is a directory.")
        return
    
    try:
        with open(filename, "r") as f:
            print(f"\n--- Content of '{filename}' ---")
            print(f.read())
            print(f"--- End of file ---")
    except Exception as e:
        print("Error reading file:", e)

def edit_file():
    """Overwrites an existing file with new content in the current directory."""
    filename = input("Enter filename to edit: ").strip()
    if not filename:
        print("No filename entered.")
        return

    if not os.path.exists(filename) or os.path.isdir(filename):
        print("File does not exist or is a directory.")
        return
    
    print(f"Editing '{filename}'. Press Enter to save and exit.")
    new_content = input("Enter new content:\n")
    try:
        with open(filename, "w") as f:
            f.write(new_content)
        print(f"File '{filename}' updated successfully.")
    except Exception as e:
        print("Error writing to file:", e)

def run_file():
    """Executes a Python (.py) file in the current directory."""
    filename = input("Enter filename to run: ").strip()
    if not filename:
        print("No filename entered.")
        return
    if not filename.endswith('.py'):
        print("Can only run Python (.py) files.")
        return

    try:
        print(f"\n--- Running '{filename}' ---")
        # Use subprocess to run the file with the same Python interpreter
        result = subprocess.run([sys.executable, filename], capture_output=True, text=True, check=True)
        print(result.stdout)
        print(f"--- Finished running '{filename}' ---")
    except subprocess.CalledProcessError as e:
        print(f"\nError while running '{filename}':")
        print(e.stderr)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def delete_file():
    """Deletes a file from the current directory."""
    filename = input("Enter filename to delete: ").strip()
    if not filename:
        print("No filename entered.")
        return

    if not os.path.exists(filename) or os.path.isdir(filename):
        print("File does not exist or is a directory.")
        return
    
    try:
        os.remove(filename)
        print(f"File '{filename}' deleted.")
    except Exception as e:
        print("Error deleting file:", e)

def delete_folder():
    """Deletes a folder and all its contents with a confirmation."""
    foldername = input("Enter folder name to delete: ").strip()
    if not foldername:
        print("No folder name entered.")
        return
    
    if not os.path.exists(foldername) or not os.path.isdir(foldername):
        print("Folder does not exist.")
        return
    
    print(f"WARNING: This will permanently delete the folder '{foldername}' and all its contents.")
    confirm = input("Are you sure? (yes/no): ").strip().lower()
    
    if confirm == 'yes':
        try:
            # shutil.rmtree is used for deleting non-empty directories
            shutil.rmtree(foldername)
            print(f"Folder '{foldername}' deleted.")
        except Exception as e:
            print(f"Error deleting folder: {e}")
    else:
        print("Deletion cancelled.")

def rename_item():
    """Renames a file or folder in the current directory."""
    old_name = input("Enter current name of file or folder: ").strip()
    if not old_name:
        print("No name entered.")
        return

    if not os.path.exists(old_name):
        print("File or folder does not exist.")
        return
    
    new_name = input("Enter new name: ").strip()
    if not new_name:
        print("No new name entered.")
        return
    
    try:
        os.rename(old_name, new_name)
        print(f"'{old_name}' renamed to '{new_name}'.")
    except Exception as e:
        print("Error renaming:", e)

def change_directory(path):
    """Changes the current working directory."""
    try:
        os.chdir(path)
        print(f"Changed directory to '{os.getcwd()}'.")
    except FileNotFoundError:
        print("Error: Directory not found.")
    except PermissionError:
        print("Error: Permission denied.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def manage_todo():
    """Manages a simple to-do list stored in a text file."""
    todo_file = "todo.txt"
    if not os.path.exists(todo_file):
        with open(todo_file, "w") as f:
            f.write("")

    while True:
        print("\n=== To-Do List ===")
        try:
            with open(todo_file, "r") as f:
                tasks = [line.strip() for line in f if line.strip()]
        except Exception as e:
            print("Error reading to-do list:", e)
            tasks = []

        if not tasks:
            print("[Empty to-do list]")
        else:
            for i, task in enumerate(tasks):
                print(f"{i+1}. {task}")
        
        print("\nOptions: add <task>, remove <number>, exit")
        command = input("Todo> ").strip().split(' ', 1)
        cmd = command[0].lower()
        
        if cmd == "exit":
            break
        elif cmd == "add" and len(command) > 1:
            with open(todo_file, "a") as f:
                f.write(command[1] + "\n")
            print("Task added.")
        elif cmd == "remove" and len(command) > 1:
            try:
                task_num = int(command[1]) - 1
                if 0 <= task_num < len(tasks):
                    tasks.pop(task_num)
                    with open(todo_file, "w") as f:
                        for task in tasks:
                            f.write(task + "\n")
                    print("Task removed.")
                else:
                    print("Invalid task number.")
            except ValueError:
                print("Invalid number format.")
        else:
            print("Unknown command.")

def show_pc_info():
    """Displays real-time system information (CPU, RAM, GPU, Storage) using psutil, gputil, and shutil."""
    print("=== PC Information (Live Monitor) ===")
    print("Press Ctrl+C to exit.\n")
    try:
        while True:
            clear_screen()
            print("=== PC Information (Live Monitor) ===")
            print("Press Ctrl+C to exit.\n")

            # CPU and System RAM Info
            if PSUTIL_INSTALLED:
                print(f"CPU: {platform.processor()}")
                print(f"  - Physical Cores: {psutil.cpu_count(logical=False)}")
                print(f"  - Threads: {psutil.cpu_count(logical=True)}")
                print(f"  - Usage: {psutil.cpu_percent()}%")
                
                mem = psutil.virtual_memory()
                print("\nSystem RAM:")
                print(f"  - Total: {mem.total / (1024**3):.2f} GB")
                print(f"  - Used: {mem.used / (1024**3):.2f} GB")
                print(f"  - Free: {mem.available / (1024**3):.2f} GB")
                
                process = psutil.Process(os.getpid())
                process_mem = process.memory_info().rss
                print("\nMiniOS Process RAM:")
                print(f"  - Used: {process_mem / (1024**2):.2f} MB")
            else:
                print("System info (CPU/RAM) not available. Please install 'psutil'.")

            # GPU Info
            print("\n--- GPU Information ---")
            if GPUTIL_INSTALLED:
                try:
                    gpus = GPUtil.getGPUs()
                    if gpus:
                        for i, gpu in enumerate(gpus):
                            print(f"  GPU {i + 1}: {gpu.name}")
                            print(f"    - Memory Total: {gpu.memoryTotal} MB")
                            print(f"    - Memory Used: {gpu.memoryUsed} MB")
                            print(f"    - GPU Load: {gpu.load * 100:.2f}%")
                    else:
                        print("  No NVIDIA GPU detected.")
                except Exception:
                    print("  Could not retrieve GPU information. (Is nvidia-smi installed?)")
            else:
                print("  GPU information is only available for NVIDIA cards with the 'GPUtil' library.")
            
            # Disk Storage Info
            print("\n--- Disk Storage ---")
            if PSUTIL_INSTALLED:
                try:
                    partitions = psutil.disk_partitions(all=False)
                    for partition in partitions:
                        mount_point = partition.mountpoint
                        # Get disk usage for the partition
                        total, used, free = shutil.disk_usage(mount_point)
                        total_gb = total / (1024**3)
                        used_gb = used / (1024**3)
                        free_gb = free / (1024**3)
                        
                        print(f"\n  Device: {partition.device}")
                        print(f"  Mount Point: {mount_point}")
                        print(f"  - Free: {free_gb:.2f} GB")
                        print(f"  - Used: {used_gb:.2f} GB")
                        print(f"  - Total: {total_gb:.2f} GB")
                        
                        # Create a simple progress bar
                        bar_length = 20
                        used_percent = (used / total) * 100 if total > 0 else 0
                        filled_len = int(bar_length * used // total) if total > 0 else 0
                        bar = '█' * filled_len + '░' * (bar_length - filled_len)
                        print(f"  [{bar}] {used_percent:.1f}% used")
                        
                except Exception as e:
                    print(f"  Could not retrieve disk information: {e}")
            else:
                print("  Disk information is not available. Please install 'psutil'.")

            print("\n=======================\n")
            time.sleep(2) # Wait for 2 seconds before the next refresh

    except KeyboardInterrupt:
        print("\nLive monitor stopped.")

def show_time():
    """Displays the current date and time."""
    now = datetime.datetime.now()
    print(f"\n{now.strftime('%A, %B %d, %Y')}")
    print(f"{now.strftime('%H:%M:%S')}\n")

def show_uptime():
    """Calculates and displays the system uptime."""
    global program_start_time
    # Calculate the elapsed time in seconds
    elapsed_time_seconds = time.time() - program_start_time
    
    # Convert seconds to a readable format (days, hours, minutes)
    days = int(elapsed_time_seconds // (24 * 3600))
    hours = int((elapsed_time_seconds % (24 * 3600)) // 3600)
    minutes = int((elapsed_time_seconds % 3600) // 60)
    
    # Construct the output string
    uptime_string = ""
    if days > 0:
        uptime_string += f"{days} day{'s' if days > 1 else ''}, "
    if hours > 0:
        uptime_string += f"{hours} hour{'s' if hours > 1 else ''}, "
    
    uptime_string += f"{minutes} minute{'s' if minutes > 1 else ''}"
    
    print(f"\nUptime: {uptime_string}\n")


def folder_command():
    """Allows the user to view or create a folder and interact with it."""
    folder_name = input("Enter folder name: ").strip()
    if not folder_name:
        print("No folder name entered.")
        return

    folder_path = os.path.join(os.getcwd(), folder_name)
    
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print(f"Folder '{folder_name}' created.")
    
    while True:
        try:
            files = os.listdir(folder_path)
        except FileNotFoundError:
            print(f"Error: Folder '{folder_name}' does not exist.")
            break
        
        print(f"\nContents of '{folder_name}':")
        if not files:
            print("[Empty folder]")
        else:
            for f in files:
                print(f"[FILE] {f}")
        print("Options: read <filename>, exit")
        command = input(f"{folder_name}> ").strip().split()
        if not command:
            continue
        cmd = command[0].lower()
        if cmd == "exit":
            break
        elif cmd == "read":
            if len(command) > 1:
                file_path = os.path.join(folder_path, command[1])
                if os.path.exists(file_path):
                    with open(file_path, "r") as f:
                        print("\n" + f.read() + "\n")
                else:
                    print("File does not exist.")
            else:
                print("Specify a filename to read.")
        else:
            print("Unknown command.")

def ai_chat():
    """A simple, rule-based conversational AI feature."""
    print("=== MiniOS AI Chat ===")
    print("Ask me anything! Type 'exit' to return to MiniOS.")
    
    # Simple, hard-coded responses for a mini AI
    responses = {
        "hello": "Hello! How can I help you today?",
        "hi": "Hello! How can I help you today?",
        "how are you": "I am a program, so I'm always running!",
        "what is the time": show_time, # Call the show_time function
        "what is the capital of the us": "The capital of the US is Washington, D.C.",
        "what is the capital of united states": "The capital of the US is Washington, D.C.",
        "who are you": "I am MiniOS, a simple command-line operating system written in Python.",
        "what is your name": "My name is MiniOS.",
    }

    while True:
        prompt = input("You> ").strip().lower()
        if prompt == 'exit':
            break

        response_found = False
        for key, value in responses.items():
            if key in prompt:
                if callable(value):
                    value() # Call the function
                else:
                    print(f"AI> {value}")
                response_found = True
                break

        if not response_found:
            print("AI> I'm sorry, I don't understand that question. Try asking about the time, my name, or the capital of the US.")

def html_to_markdown():
    """
    Converts the raw HTML from the last web fetch into a more readable Markdown format.
    This is a simplified converter for educational purposes.
    """
    try:
        with open("last_web_content.txt", "r", encoding="utf-8") as f:
            html_content = f.read()
    except FileNotFoundError:
        print("Error: No web content has been fetched yet. Please use the 'fetch' command first.")
        return
    except Exception as e:
        print(f"Error reading file: {e}")
        return

    # A simple approach to converting HTML tags to Markdown
    # This will not handle all cases but works for a basic demonstration.
    markdown_content = html_content

    # Replace headings with Markdown heading syntax
    markdown_content = re.sub(r'<h1[^>]*>(.*?)</h1>', r'# \1\n', markdown_content, flags=re.DOTALL)
    markdown_content = re.sub(r'<h2[^>]*>(.*?)</h2>', r'## \1\n', markdown_content, flags=re.DOTALL)
    markdown_content = re.sub(r'<h3[^>]*>(.*?)</h3>', r'### \1\n', markdown_content, flags=re.DOTALL)

    # Replace bold and strong tags with Markdown bold syntax
    markdown_content = re.sub(r'<b>(.*?)</b>', r'**\1**', markdown_content, flags=re.DOTALL)
    markdown_content = re.sub(r'<strong>(.*?)</strong>', r'**\1**', markdown_content, flags=re.DOTALL)

    # Replace italic and em tags with Markdown italic syntax
    markdown_content = re.sub(r'<i>(.*?)</i>', r'*\1*', markdown_content, flags=re.DOTALL)
    markdown_content = re.sub(r'<em>(.*?)</i>', r'*\1*', markdown_content, flags=re.DOTALL)

    # Replace paragraphs with newlines
    markdown_content = re.sub(r'<p[^>]*>(.*?)</p>', r'\1\n\n', markdown_content, flags=re.DOTALL)

    # A simple regex to remove all remaining HTML tags
    clean_content = re.sub(r'<[^>]+>', '', markdown_content)

    # Clean up extra newlines and leading/trailing whitespace
    clean_content = re.sub(r'\n\n+', '\n\n', clean_content)
    clean_content = clean_content.strip()

    print("=== Converted to Markdown ===")
    print(clean_content[:2000] + "...")
    print("\n--- End of conversion ---")

def image_to_ascii(filepath):
    """
    Converts an image file to ASCII art and prints it to the console with color.
    This function requires the 'Pillow' library.
    """
    # Character list for converting brightness to ASCII characters
    ASCII_CHARS = '@%#*+=-:. '
    
    if not PILLOW_INSTALLED:
        print("Image display requires the 'Pillow' library.")
        print("Please run 'pip install Pillow' to use this feature.")
        return
    
    if not os.path.exists(filepath):
        print(f"Error: The file '{filepath}' was not found.")
        return

    try:
        # Open the image without converting to grayscale
        image = Image.open(filepath)
        
        # Resize the image to fit the terminal window
        width, height = image.size
        aspect_ratio = height / width
        new_width = 80 # a reasonable width for a terminal
        # The 0.5 factor is to compensate for the height of terminal characters
        new_height = int(new_width * aspect_ratio * 0.5) 
        resized_image = image.resize((new_width, new_height))
        
        for y in range(new_height):
            for x in range(new_width):
                # Get the pixel's RGB values
                try:
                    r, g, b = resized_image.getpixel((x, y))[:3]
                except ValueError:
                    # Handle paletted images or images with a different mode
                    # by converting them to RGB first.
                    rgb_image = resized_image.convert('RGB')
                    r, g, b = rgb_image.getpixel((x, y))[:3]
                
                # Calculate brightness to select the ASCII character
                brightness = int(0.299 * r + 0.587 * g + 0.114 * b)
                char_index = int(brightness * (len(ASCII_CHARS) - 1) / 255)
                char = ASCII_CHARS[char_index]
                
                # Print the character with a 24-bit ANSI color code
                print(f"\033[38;2;{r};{g};{b}m{char}\033[0m", end="")
            print() # Print a newline at the end of each row
            
    except Exception as e:
        print(f"An error occurred while processing the image: {e}")

def display_important_pips():
    """
    Displays a heading labeled "IMPORTANT" and lists the required pip packages.
    """
    print("\n====================================")
    print("           PIP Drivers              ")
    print("====================================\n")

    # Display the main label, centered
    label = "IMPORTANT"
    print(f"[{label.center(32)}]\n")
    
    # Print the list of required packages
    print("To use all features of MiniOS, you need to install the following packages:")
    print("  - psutil (for CPU and RAM information)")
    print("  - gputil (for GPU information, NVIDIA only)")
    print("  - Pillow (for image display as ASCII art)")
    
    print("\n====================================")
    print("All required packages are installed.")
    print("====================================\n")

def games_command():
    """
    Creates and manages a 'games' folder where users can store and run their own games.
    """
    games_folder_name = "games"
    games_folder_path = os.path.join(os.getcwd(), games_folder_name)

    if not os.path.exists(games_folder_path):
        os.makedirs(games_folder_path)
        print(f"Games folder created at '{games_folder_path}'.")
    
    while True:
        try:
            files = os.listdir(games_folder_path)
        except FileNotFoundError:
            print(f"Error: Games folder does not exist.")
            break
        
        print(f"\nContents of '{games_folder_name}':")
        if not files:
            print("[Empty games folder. Add your .py games here!]")
        else:
            for f in files:
                full_path = os.path.join(games_folder_path, f)
                if os.path.isdir(full_path):
                    print(f"[DIR] {f}")
                else:
                    print(f"[FILE] {f}")
        
        print("\nOptions: run <filename.py>, exit")
        command = input(f"{games_folder_name}> ").strip().split()
        if not command:
            continue
        cmd = command[0].lower()
        
        if cmd == "exit":
            break
        elif cmd == "run":
            if len(command) > 1:
                filename = command[1]
                if not filename.endswith('.py'):
                    print("Can only run Python (.py) files.")
                    continue
                
                file_path = os.path.join(games_folder_path, filename)
                if os.path.exists(file_path):
                    try:
                        print(f"\n--- Running '{filename}' ---")
                        subprocess.run([sys.executable, file_path], check=True)
                        print(f"--- Finished running '{filename}' ---")
                    except subprocess.CalledProcessError as e:
                        print(f"\nError while running '{filename}':")
                        print(e.stderr)
                    except Exception as e:
                        print(f"An unexpected error occurred: {e}")
                else:
                    print("File does not exist.")
            else:
                print("Specify a filename to run.")
        else:
            print("Unknown command.")

def run_internet_server():
    """
    Runs the internet server script in a non-blocking process.
    """
    global server_process
    server_file = "minios_web_server.py" # Use the new web server file
    if not os.path.exists(server_file):
        print(f"Error: '{server_file}' not found. Please create it first.")
        return
    
    if server_process and server_process.poll() is None:
        print("Server is already running.")
        return

    print("Starting web server in the background...")
    try:
        # Use Popen to run the process non-blocking
        server_process = subprocess.Popen([sys.executable, server_file])
        print("Server started. You can continue using MiniOS.")
        print("Go to http://localhost:8000 to view the chat application.")
        print("Use 'kill_server' to stop the server when you are done.")
    except Exception as e:
        print(f"An unexpected error occurred while starting the server: {e}")

def kill_internet_server():
    """
    Terminates the running internet server process.
    """
    global server_process
    if server_process and server_process.poll() is None:
        print("Stopping server...")
        try:
            # Terminate the process
            server_process.terminate()
            server_process.wait(timeout=5)  # Wait for a few seconds for it to close
            if server_process.poll() is None:
                # If it's still running, try to kill it more forcefully
                server_process.kill()
            print("Server stopped.")
        except Exception as e:
            print(f"An error occurred while stopping the server: {e}")
        finally:
            server_process = None
    else:
        print("No server is currently running.")
        
def ping_google():
    """Pings google.com to test internet connectivity."""
    print("Pinging google.com to check connectivity...")
    # Determine the correct ping command based on the OS
    if platform.system() == "Windows":
        command = ["ping", "-n", "4", "google.com"]
    else: # Linux and macOS
        command = ["ping", "-c", "4", "google.com"]
    
    try:
        # Run the command and capture its output
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        print("Success! Connection to google.com is working.")
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print("Error: Could not reach google.com.")
        print("Check your internet connection.")
        print(e.stderr)
    except FileNotFoundError:
        print("Error: The 'ping' command was not found on your system.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def main():
    """The main loop of the MiniOS program."""
    global program_start_time
    clear_screen()
    
    # Check for a 'minios_data' folder and create it if it doesn't exist
    if not os.path.exists('minios_data'):
        os.makedirs('minios_data')
    os.chdir('minios_data')
    
    show_boot_screen()
    show_gui_desktop()

    # NEW: A dictionary to map commands to functions
    apps = {
        "desktop": show_gui_desktop,
        "list": list_files_and_folders,
        "clear": clear_screen,
        "help": show_help,
        "calc": calculator,
        "code": code_editor,
        "paint": text_paint,
        "create": create_file,
        "read": read_file,
        "edit": edit_file,
        "run": run_file,
        "delete": delete_file,
        "rename": rename_item,
        "delfolder": delete_folder,
        "todo": manage_todo,
        "pcinfo": show_pc_info,
        "time": show_time,
        "uptime": show_uptime,
        "folder": folder_command,
        "ai": ai_chat,
        "internet": run_internet_server,
        "kill_server": kill_internet_server,
        "convert": html_to_markdown,
        "image": image_to_ascii,
        "code": code_editor,
        "paint": text_paint,
        "cd": change_directory,
        "background": set_background,
        "drivers": display_important_pips,
        "games": games_command,
        "terry_davis": terry_davis_story,
        "special_thanks": special_thanks_command,
        "ping": ping_google,
        "exit": sys.exit,
    }

    while True:
        try:
            current_dir = os.getcwd()
            command_input = input(f"MiniOS [{current_dir}]> ").strip().split(' ', 1)
            command = command_input[0]
            arg = command_input[1] if len(command_input) > 1 else None

            # Look up the command in the apps dictionary
            if command in apps:
                # The 'image', 'cd', and 'background' commands need an argument
                if command in ["image", "cd", "background"] and arg:
                    apps[command](arg)
                # The 'create' and 'read' commands are handled slightly differently
                # to get user input within their functions, so we call them without args here.
                elif command in ["create", "read", "edit", "run", "delete", "rename", "delfolder"]:
                    apps[command]()
                # All other apps can be called directly
                elif command not in ["image", "cd", "background", "create", "read", "edit", "run", "delete", "rename", "delfolder"]:
                    apps[command]()
                else:
                    print(f"Please provide a filename for '{command}'. Example: {command} myimage.jpg")
            elif command == "":
                continue
            else:
                print("Unknown command. Type 'help'.")
        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    # This line is crucial! It tells Python to run the main() function
    # only when the script is executed directly as a file.
    main()
