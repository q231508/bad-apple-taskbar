import threading
import time 
import pystray
import tkinter as tk
from tkinter import filedialog, simpledialog
from PIL import Image, ImageSequence, UnidentifiedImageError

running = False
count = 0
frames = []
tray_icon = None

def animate(icon):
    # Handles the animation loop
    # runs on a different thread
    global count, running, frames
    while running and icon.visible:
        icon.icon = frames[count]
        count = (count + 1) % len(frames)
        time.sleep(1 / 48)  # <-- FPS
        
def ask_for_input():
    global user_input

    root = tk.Tk()
    root.withdraw()
    user_input = simpledialog.askstring("Input", "Please enter a value:")
    root.destroy()

    if user_input is not None:
        print(f"User typed: {user_input}")
    else:
        print("User cancelled input")
        
def on_clicked(icon, item):
    # Checks if user chose an action from the menu
    # Complete one of the available actions
    global running
    if str(item) == "Run":
        if not running:
            running = True
            threading.Thread(target=animate, args=(icon,), daemon=True).start()
    elif str(item) == "Stop":
        running = False
    elif str(item) == "Change file":
        running = False
        if not change_file():
            running = True
            
    elif str(item) == "Exit":
        running = False
        icon.stop()

def select_and_processing():
    global frames
    print("Select a file")
    
    root = tk.Tk()
    root.withdraw()
    target_file = filedialog.askopenfilename(title="Select a file") # <-- Pick an image or gif
    root.quit()
    if not target_file:
        print("No file selected")
        return None

    try:
        gif = Image.open(target_file)
    except Exception as e:
        print(f"Error: {e}")
        return None
    except UnidentifiedImageError:
        print("Invalid file selected")
        return
    
    print(f"Processing Frames: 0%", end='\r')
    raw_frames = list(ImageSequence.Iterator(gif)) 
    total = len(raw_frames)
    
    frames = []
    frames_processed = 1
    for frame in ImageSequence.Iterator(gif):
        processed_frame = frame.copy().convert("RGBA").resize((32, 32), Image.LANCZOS)
        frames.append(processed_frame)
        print(f"Processing Frames: {round((frames_processed + 1) / total * 100, 2)}%", end='\r')
        frames_processed += 1
    print(f"Processing Frames: Finished!")
    
    return(frames[0])

 
def change_file():
    global tray_icon, count
    new_icon_image = select_and_processing()
    if new_icon_image:
        count = 0
        tray_icon.icon = new_icon_image
        print("Icon updated with new file")
        return True
    return False
        
def main():
    global tray_icon
    
    icon_image = select_and_processing() # <-- Icon thumbnail is the first frame of the provided file
    if icon_image is None:
        return
    
    tray_icon = pystray.Icon("Animated_icon", icon_image, title="Animated Icon", menu=pystray.Menu(
        pystray.MenuItem("Run", on_clicked),
        pystray.MenuItem("Stop", on_clicked),
        pystray.MenuItem("Change file", on_clicked),
        pystray.MenuItem("Change speed", ask_for_input),
        pystray.MenuItem("Exit", on_clicked)
        
    ))
    
    tray_icon.run()
    
if __name__ == "__main__":
    main()