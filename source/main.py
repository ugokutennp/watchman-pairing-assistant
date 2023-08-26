import tkinter as tk
import customtkinter as ctk
import re
import subprocess
import time
import threading

class SidebarFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, width=140, corner_radius=0, **kwargs)

        self.sidebar_label_logo = ctk.CTkLabel(self, text="Pairing Assistant", font=ctk.CTkFont(size=20, weight="bold"))
        self.sidebar_label_logo.grid(row=0, column=0, padx=13, pady=(30, 20))
        self.sidebar_button_reload = ctk.CTkButton(self,text="Reload",command=self.sidebar_button_reload_callbacks, border_width=2)
        self.sidebar_button_reload.grid(row=1, column=0, padx=20, pady=10)
        self.sidebar_button_pairall = ctk.CTkButton(self,text="PairAll",command=lambda:self.sidebar_button_callback("pairall"))
        self.sidebar_button_pairall.grid(row=2, column=0, padx=20, pady=10)
        self.sidebar_button_force_pairall = ctk.CTkButton(self,text="ForcePairAll",command=lambda:self.sidebar_button_callback("forcepairall"))
        self.sidebar_button_force_pairall.grid(row=3, column=0, padx=20, pady=10)
        self.sidebar_button_unpairall = ctk.CTkButton(self,text="UnpairAll",command=lambda:self.sidebar_button_callback("unpairall"))
        self.sidebar_button_unpairall.grid(row=4, column=0, padx=20, pady=10)
        self.sidebar_button_unpairall = ctk.CTkButton(self,text="DongleResetAll",command=lambda:self.sidebar_button_callback("dongleresetall"),fg_color="transparent", border_width=2,text_color=("gray10", "#DCE4EE"),)
        self.sidebar_button_unpairall.grid(row=5, column=0, padx=20, pady=10)

        self.sidebar_label_mode = ctk.CTkLabel(self, text="Theme:")
        self.sidebar_label_mode.grid(row=7, column=0, padx=20, pady=(10, 0))
        self.sidebar_optionemenu_mode = ctk.CTkOptionMenu(self, values=["Light", "Dark", "System"],command=self.sidebar_optionemenu_callback)
        self.sidebar_optionemenu_mode.grid(row=8, column=0, padx=20, pady=(10, 20))

        #reset
        self.sidebar_optionemenu_mode.set("System")

    def sidebar_button_reload_callbacks(self):
        app_instance = self.master
        exe_path = app_instance.exe_path_frame.exepath_entry_serial.get()
        output = app_instance.execute_subprocess("serial", exe_path)
        device_serials = app_instance.extract_device_serials(output)
        app_instance.insert_log("Recognized devices : " + ", ".join(device_serials))

        app_instance.scrollable_frame.update_device_frames(device_serials,app_instance)
        app_instance.status_check()
        app_instance.insert_log("Reloaded devices")
        
    def sidebar_button_callback(self, command):
        app_instance = self.master
        exe_path = app_instance.exe_path_frame.exepath_entry_serial.get() 
    
        if command == "pairall":
            self.sidebar_button_pairall.configure(text="Pairing...",state="disabled")
        elif command == "forcepairall":
            self.sidebar_button_force_pairall.configure(text="Pairing...",state="disabled")
        
        threading.Thread(target=lambda: app_instance.execute_subprocess(command, exe_path)).start()
    
        if command == "pairall":
            self.after(5000, lambda: self.sidebar_button_pairall.configure(text="PairAll",state="normal"))
        elif command == "forcepairall":
            self.after(5000, lambda: self.sidebar_button_force_pairall.configure(text="ForcePairAll",state="normal"))

        self.after(5000, app_instance.status_check)
        app_instance.insert_log("Executed command: " + command)

    def sidebar_optionemenu_callback(self, new_appearance_mode: str):
        ctk.set_appearance_mode(new_appearance_mode)

class ScrollableFrame(ctk.CTkScrollableFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.device_frames = []

    def update_device_frames(self, device_serials,app_instance):
        self.clear_device_frames()
        
        for i, serial in enumerate(device_serials):
            self.device_frame = DeviceFrame(self, fg_color=['#cfcfcf', '#333333'], serial=serial,app_instance=app_instance)
            self.device_frame.grid(row=i, column=0, padx=(10, 10), pady=(10, 10), sticky="nsew")
            self.device_frame.grid_columnconfigure(3, weight=1)
            self.device_frames.append(self.device_frame)

    def clear_device_frames(self):
        for frame in self.device_frames:
            frame.grid_forget()
            frame.destroy()
            
        self.device_frames = []

class DeviceFrame(ctk.CTkFrame):
    def __init__(self, master, serial, app_instance, **kwargs):
        super().__init__(master, **kwargs)
        self.app_instance = app_instance

        self.device_label_id = ctk.CTkLabel(self, text="Device ID :")
        self.device_label_id.grid(row=0, column=0, padx=(20, 0), pady=20)
        self.device_label_serial = ctk.CTkLabel(self, text=serial)  # Display serial here
        self.device_label_serial.grid(row=0, column=1, padx=(5, 20), pady=20)

        self.device_label_name = ctk.CTkLabel(self, text=self.app_instance.get_device_name(serial))
        #self.device_label_name.grid(row=0, column=2, padx=20, pady=20)
        self.device_label_name.place(x=210,y=20)

        self.device_button_pair = ctk.CTkButton(self,width=100,command=lambda: self.device_button_callback("pair",serial), text="Pair")
        self.device_button_pair.grid(row=0, column=4, padx=(70, 10), pady=20)
        self.device_button_unpair = ctk.CTkButton(self,width=100,command=lambda: self.device_button_callback("unpair",serial), text="Unpair")
        self.device_button_unpair.grid(row=0, column=5, padx=(10, 10), pady=20)
        self.device_button_reset = ctk.CTkButton(self,width=100, text_color=("gray10", "#DCE4EE"), fg_color="transparent", border_width=2, command=lambda: self.device_button_callback("donglereset",serial), text="DongleReset")
        self.device_button_reset.grid(row=0, column=6, padx=(10, 20), pady=20)

    def device_button_callback(self,command,serial):
        exe_path = self.app_instance.exe_path_frame.exepath_entry_serial.get()

        if command == "pair":
            self.device_button_pair.configure(text="Pairing...",state="disabled")

        threading.Thread(target=lambda: self.app_instance.execute_subprocess_serial(serial, command, exe_path)).start()
        self.app_instance.insert_log("Executed command : " + serial +" "+ command)
        
        if command == "pair":
            self.after(5000, lambda: self.device_button_pair.configure(text="Pair",state="normal"))
        
        self.after(5000, self.app_instance.status_check)

    def button_status_change(self, status):
        if status == "normal":
            self.device_button_pair.configure(state=status, text="Pair")
        elif status == "disabled":
            self.device_button_pair.configure(state=status, text="Paired")

class ExePathFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.exepath_entry_serial = ctk.CTkEntry(self, width=120)
        self.exepath_entry_serial.grid(row=0, column=0, padx=(20, 0), pady=(20, 20), sticky="ew")

        self.exepath_button_browse = ctk.CTkButton(self, command=self.exepath_button_callback, fg_color="transparent", text_color=("gray10", "#DCE4EE"), border_width=2, text="Browse")
        self.exepath_button_browse.grid(row=0, column=1, padx=20, pady=20)

        #reset
        self.exepath_entry_serial.delete(0, tk.END)
        self.exepath_entry_serial.insert(0, r"C:\Program Files (x86)\Steam\steamapps\common\SteamVR\tools\lighthouse\bin\win64\lighthouse_console.exe")

    def exepath_button_callback(self):
        app_instance = self.master
        file_name = app_instance.file_read()

        if file_name is not None:
            self.exepath_entry_serial.delete(0, tk.END)
            self.exepath_entry_serial.insert(0, file_name)
            app_instance.exe_check()
                  
class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")
        self.title("watchman_pairing_assistant")
        self.after(201, lambda :self.iconbitmap(r'resources\icon.ico')) #set icon dir
        self.geometry(f"{940}x{590}")
        
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.exe_path_frame = ExePathFrame(self)
        self.exe_path_frame.grid(row=0, column=1, padx=(20, 20), pady=(10, 0), sticky="nsew")
        self.exe_path_frame.grid_rowconfigure(0, weight=1)
        self.exe_path_frame.grid_columnconfigure(0, weight=1)

        self.sidebar_frame = SidebarFrame(self)
        self.sidebar_frame.grid(row=0, column=0, rowspan=5, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(6, weight=1)

        self.scrollable_frame = ScrollableFrame(self)
        self.scrollable_frame.grid(row=1, column=1, padx=(20, 20), pady=(10, 0), sticky="nsew")
        self.scrollable_frame.grid_columnconfigure(0, weight=1)

        self.textbox_log = ctk.CTkTextbox(self,height= 100)
        self.textbox_log.grid(row=2, column=1, padx=(20, 20), pady=(20, 20), sticky="nsew")

        #reset
        self.insert_log("Welcome to watchman_pairing_assistant ! (v1.3)")
        self.exe_check()
        self.sidebar_frame.sidebar_button_reload_callbacks()
        
    def insert_log(self,log):
        current_time = time.strftime("[%Y-%m-%d %H:%M:%S] ")
        self.textbox_log.insert(tk.END, current_time + log + "\n")
        self.textbox_log.see(tk.END)
        print(current_time + log)

    def execute_subprocess(self, command, exe_path):
        completed_process = subprocess.run([exe_path, command], capture_output=True, text=True)
        return completed_process.stdout
        ##print("Completed Process:", completed_process)

    def execute_subprocess_serial(self, serial, command, exe_path, timeout=5):
        process = subprocess.Popen([exe_path], stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        try:
            process.stdin.write(f"serial {serial}\n")
            process.stdin.flush()
            process.stdin.write(f"{command}\n")
            process.stdin.flush()
            process.communicate(timeout=timeout)

        except subprocess.TimeoutExpired:
            process.kill()
            #self.insert_log(f"Process timed out after {timeout} seconds and was forcibly terminated.")
        finally:
            if process.poll() is None:
                process.wait()

    def status_check(self):
        exe_path = self.exe_path_frame.exepath_entry_serial.get()
        output = self.execute_subprocess("dongleinfo", exe_path)
        #print(output)

        for device_frame in self.scrollable_frame.device_frames:
            serial = device_frame.device_label_serial.cget("text")
            serial_appears_disabled = f"VRC-{serial}" in output

            if serial_appears_disabled:
                self.device_status_change(serial,"disabled")
                self.insert_log("Device connected with "+serial)
            else:
                self.device_status_change(serial,"normal")

    def device_status_change(self, serial, status):
        for device_frame in self.scrollable_frame.device_frames:
            check_serial = device_frame.device_label_serial.cget("text")
            if check_serial == serial:
                device_frame.button_status_change(status)
                break

    def extract_device_serials(self, output):
        lines = [line.strip() for line in output.split('\n') if line.startswith('\t') and not line.lstrip().startswith('LHR-')]
        return lines
    
    def get_device_name(self, serial_number):
        if serial_number.endswith(("LYM", "RYB")):
            return "IndexHMD"
        elif serial_number.endswith(("LYX")):
            return "IndexFW"
        elif re.match(r".*(-[0-9]YX)$", serial_number):
            return "Tundra"
        else:
            return "Dongle"
        
    def exe_check(self):
        exe_path = self.exe_path_frame.exepath_entry_serial.get() 
        output = self.execute_subprocess("serial", exe_path)

        if "lighthouse_console.exe" in output:
            self.insert_log("Successfully recognized lighthouse_console.exe")
        else:
            self.insert_log("Failed to recognize lighthouse_console.exe")

    def file_read(self):
        file_path = tk.filedialog.askopenfilename(filetypes=[("Executable Files", "*.exe")])

        if len(file_path) != 0:
            return file_path
        else:
            return None

if __name__ == "__main__":
    app = App() 
    app.mainloop()
