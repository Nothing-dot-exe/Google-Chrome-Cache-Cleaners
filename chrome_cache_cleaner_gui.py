import os
import glob
import threading
import time
import subprocess
import tkinter as tk
from tkinter import scrolledtext
from tkinter import messagebox

class ChromeCacheCleanerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Chrome Cache Cleaner")
        self.root.geometry("650x450")
        self.root.configure(bg="#f0f0f0")
        
        # UI Elements Setup
        self.title_label = tk.Label(root, text="Google Chrome Cache Cleaner", font=("Helvetica", 16, "bold"), bg="#f0f0f0")
        self.title_label.pack(pady=10)
        
        # Info Label
        self.info_label = tk.Label(root, text="Clicking the button will forcibly close Chrome and clear your cache files.", font=("Helvetica", 10), bg="#f0f0f0", fg="#555")
        self.info_label.pack(pady=0)

        # Log Area
        self.log_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=75, height=18, font=("Consolas", 9), bg="#1e1e1e", fg="#00ff00")
        self.log_area.pack(pady=10, padx=15, fill=tk.BOTH, expand=True)
        self.log_area.config(state=tk.DISABLED)
        
        # Clear Button
        self.clear_btn = tk.Button(root, text="Clear Cache Now", font=("Helvetica", 12, "bold"), bg="#d9534f", fg="white", activebackground="#c9302c", activeforeground="white", cursor="hand2", command=self.start_cleaning)
        self.clear_btn.pack(pady=15)
        
        self.log("Application started. Ready to clean Chrome cache.")
        self.log("WARNING: Please save all your work in Chrome before clearing.")
        
    def log(self, message):
        """Append a message to the text log."""
        self.log_area.config(state=tk.NORMAL)
        self.log_area.insert(tk.END, message + "\n")
        self.log_area.see(tk.END)
        self.log_area.config(state=tk.DISABLED)
        self.root.update_idletasks()
        
    def start_cleaning(self):
        """Start the cleanup process in a separate thread so GUI doesn't freeze."""
        self.clear_btn.config(state=tk.DISABLED, text="Cleaning...")
        self.log("\n==========================================")
        self.log("Starting cleanup process...")
        threading.Thread(target=self.clean_cache, daemon=True).start()
        
    def close_chrome(self):
        """Close Google Chrome using Windows taskkill."""
        self.log("Checking for running Google Chrome processes...")
        try:
            # Use startupinfo to hide the command prompt window that might pop up
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            
            # Check if Chrome is running
            output = subprocess.check_output('tasklist /FI "IMAGENAME eq chrome.exe"', startupinfo=startupinfo).decode('utf-8', errors='ignore')
            
            if "chrome.exe" in output.lower():
                self.log("Google Chrome is running. Forcibly closing...")
                subprocess.run(['taskkill', '/F', '/IM', 'chrome.exe'], startupinfo=startupinfo, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                self.log("Closed Google Chrome.")
                time.sleep(2) # Give it time to release file locking
            else:
                self.log("Google Chrome is not running.")
        except Exception as e:
            self.log(f"Error while checking/closing Chrome: {str(e)}")

    def delete_directory_contents(self, dir_path):
        """Recursively delete all files in a directory and log each one."""
        if not os.path.exists(dir_path):
            return 0
            
        deleted_count = 0
        for root_dir, dirs, files in os.walk(dir_path, topdown=False):
            # Delete files first
            for name in files:
                file_path = os.path.join(root_dir, name)
                try:
                    os.remove(file_path)
                    self.log(f"Deleted file: {file_path}")
                    deleted_count += 1
                except Exception as e:
                    pass # Ignore locked files or errors silently
                    
            # Delete empty directories
            for name in dirs:
                dir_path_iter = os.path.join(root_dir, name)
                try:
                    os.rmdir(dir_path_iter)
                    self.log(f"Deleted folder: {dir_path_iter}")
                except Exception:
                    pass
                    
        return deleted_count

    def clean_cache(self):
        """Main cleaning logic."""
        try:
            self.close_chrome()
            
            local_app_data = os.environ.get('LOCALAPPDATA')
            if not local_app_data:
                self.log("Error: Could not find LOCALAPPDATA environment variable on your system.")
                return
                
            user_data_path = os.path.join(local_app_data, "Google", "Chrome", "User Data")
            
            if not os.path.exists(user_data_path):
                self.log(f"Error: Chrome User Data not found. Is Chrome installed?")
                self.log(f"Checked path: {user_data_path}")
                return

            self.log(f"Found Chrome Data directory: {user_data_path}")
            
            # Basic standard cache folders
            cache_targets = [
                os.path.join(user_data_path, "Default", "Cache"),
                os.path.join(user_data_path, "Default", "Code Cache"),
                os.path.join(user_data_path, "Default", "GPUCache"),
                os.path.join(user_data_path, "ShaderCache"),
                os.path.join(user_data_path, "GrShaderCache"),
                os.path.join(user_data_path, "System Profile", "Cache")
            ]
            
            # Find all additional profiles (e.g. Profile 1, Profile 2)
            profile_dirs = glob.glob(os.path.join(user_data_path, "Profile *"))
            for profile_dir in profile_dirs:
                cache_targets.extend([
                    os.path.join(profile_dir, "Cache"),
                    os.path.join(profile_dir, "Code Cache"),
                    os.path.join(profile_dir, "GPUCache")
                ])
                
            total_deleted = 0
            
            # Delete cache files from targeted directories
            for target in cache_targets:
                if os.path.exists(target):
                    self.log(f"\nScanning directory: {target}")
                    count = self.delete_directory_contents(target)
                    total_deleted += count
                    if count == 0:
                        self.log("-> Already empty or files are completely locked.")
            
            self.log("\n==========================================")
            self.log(f"Cleanup complete! Total files/folders deleted: {total_deleted}")
            self.log("==========================================")
            
            # Show a success popup
            messagebox.showinfo("Cleanup Complete", f"Successfully cleared Chrome cache!\n\nDeleted {total_deleted} items.")
        
        except Exception as e:
            self.log(f"\nAn error occurred during cleanup: {str(e)}")
            messagebox.showerror("Error", f"An error occurred:\n{str(e)}")
            
        finally:
            # Re-enable the button
            self.clear_btn.config(state=tk.NORMAL, text="Clear Cache Now")

if __name__ == "__main__":
    root = tk.Tk()
    
    # Configure grid weights to handle resizing
    root.columnconfigure(0, weight=1)
    root.rowconfigure(1, weight=1)
    
    app = ChromeCacheCleanerApp(root)
    
    # Try to set a window icon (optional)
    try:
        root.iconbitmap(default='')
    except Exception:
        pass
        
    root.mainloop()
