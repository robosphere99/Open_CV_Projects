import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk

class ImageResizerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Resizer App")
        
        # Initializing the image
        self.img = None
        self.imgTk = None
        
        # Set up the GUI
        self.create_widgets()

    def create_widgets(self):
        # Upload Button
        self.upload_button = tk.Button(self.root, text="Upload Image", command=self.upload_image)
        self.upload_button.pack(pady=20)
        
        # Canvas to display the image
        self.canvas = tk.Canvas(self.root, width=500, height=500)
        self.canvas.pack()

        # Resize fields and button
        self.width_label = tk.Label(self.root, text="Width:")
        self.width_label.pack()
        self.width_entry = tk.Entry(self.root)
        self.width_entry.pack()
        
        self.height_label = tk.Label(self.root, text="Height:")
        self.height_label.pack()
        self.height_entry = tk.Entry(self.root)
        self.height_entry.pack()
        
        self.resize_button = tk.Button(self.root, text="Resize Image", command=self.resize_image)
        self.resize_button.pack(pady=10)

        # Save Button
        self.save_button = tk.Button(self.root, text="Save Resized Image", command=self.save_image)
        self.save_button.pack(pady=10)

    def upload_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp;*.gif")])
        if file_path:
            try:
                self.img = Image.open(file_path)
                self.display_image(self.img)
            except Exception as e:
                messagebox.showerror("Error", f"Could not open image: {e}")

    def display_image(self, img):
        # Convert image to Tkinter format and display it
        self.imgTk = ImageTk.PhotoImage(img)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.imgTk)

    def resize_image(self):
        if self.img:
            try:
                # Get new width and height
                new_width = int(self.width_entry.get())
                new_height = int(self.height_entry.get())
                
                # Resize image
                resized_img = self.img.resize((new_width, new_height))
                self.display_image(resized_img)
                self.img = resized_img
            except Exception as e:
                messagebox.showerror("Error", f"Invalid width or height input: {e}")
        else:
            messagebox.showerror("Error", "Please upload an image first.")

    def save_image(self):
        if self.img:
            save_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg")])
            if save_path:
                try:
                    self.img.save(save_path)
                    messagebox.showinfo("Success", "Image saved successfully!")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to save image: {e}")
        else:
            messagebox.showerror("Error", "No image to save.")

# Create the root window
root = tk.Tk()

# Create the app object
app = ImageResizerApp(root)

# Run the GUI main loop
root.mainloop()
