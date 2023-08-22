import tkinter as tk
import customtkinter
import os
import subprocess
import time
import threading


customtkinter.set_appearance_mode("System")
customtkinter.set_default_color_theme("blue")

class SidebarFrame(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, width=140, corner_radius=0, **kwargs)

        self.logo_label = customtkinter.CTkLabel(self, text="Pairing Assistant", font=customtkinter.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=13, pady=(30, 20))
        self.sidebar_button_reload = customtkinter.CTkButton(self,text="Reload",command=self.reload_devices, text_color=("gray10", "#DCE4EE"), fg_color="transparent", border_width=2,)
        self.sidebar_button_reload.grid(row=1, column=0, padx=20, pady=10)
        self.sidebar_button_pairall = customtkinter.CTkButton(self,text="PairAll",command=lambda:self.sidebar_botton_select_callback("pairall"))
        self.sidebar_button_pairall.grid(row=2, column=0, padx=20, pady=10)
        self.sidebar_button_force_pairall = customtkinter.CTkButton(self,text="ForcePairAll",command=lambda:self.sidebar_botton_select_callback("forcepairall"))
        self.sidebar_button_force_pairall.grid(row=3, column=0, padx=20, pady=10)
        self.sidebar_button_unpairall = customtkinter.CTkButton(self,text="UnpairAll",command=lambda:self.sidebar_botton_select_callback("unpairall"))
        self.sidebar_button_unpairall.grid(row=4, column=0, padx=20, pady=10)

        self.appearance_mode_label = customtkinter.CTkLabel(self, text="Theme:")
        self.appearance_mode_label.grid(row=6, column=0, padx=20, pady=(10, 0))
        self.appearance_mode_optionemenu = customtkinter.CTkOptionMenu(self, values=["Light", "Dark", "System"],command=self.change_appearance_mode_event)
        self.appearance_mode_optionemenu.grid(row=7, column=0, padx=20, pady=(10, 20))

        #reset
        self.appearance_mode_optionemenu.set("System")

    def reload_devices(self):
        app_instance = self.master
        exe_path = app_instance.exe_path_frame.textbox.get()
        output = app_instance.execute_subprocess("serial", exe_path)
        device_serials = self.extract_device_serials(output)
        
        app_instance.scrollable_frame.update_device_frames(device_serials,app_instance)
        app_instance.insert_log("Reloaded devices")

    @staticmethod
    def extract_device_serials(output):
        lines = [line.strip() for line in output.split('\n') if line.startswith('\t') and not line.lstrip().startswith('LHR-')]

        return lines

    def sidebar_botton_select_callback(self,command):
        
        app_instance = self.master  # Get the instance of the App class
        exe_path = app_instance.exe_path_frame.textbox.get() 
        app_instance.execute_subprocess(command, exe_path)
        app_instance.insert_log("Executed command : " + command)

    def change_appearance_mode_event(self, new_appearance_mode: str):
        customtkinter.set_appearance_mode(new_appearance_mode)

class ScrollableFrame(customtkinter.CTkScrollableFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.device_frames = []

    def clear_device_frames(self):
        for frame in self.device_frames:
            frame.grid_forget()
            frame.destroy()
        self.device_frames = []

    def update_device_frames(self, device_serials,app_instance):
        self.clear_device_frames()
        for i, serial in enumerate(device_serials):
            self.device_frame = DeviceFrame(self, fg_color=['#cfcfcf', '#333333'], serial=serial,app_instance=app_instance)
            self.device_frame.grid(row=i, column=0, padx=(10, 10), pady=(10, 10), sticky="nsew")
            self.device_frame.grid_columnconfigure(3, weight=1)
            self.device_frames.append(self.device_frame)

class DeviceFrame(customtkinter.CTkFrame):
    def __init__(self, master, serial, app_instance, **kwargs):
        super().__init__(master, **kwargs)

        self.app_instance = app_instance

        device_name = self.get_device_name(serial)
        self.Device_label = customtkinter.CTkLabel(self, text="Device ID:")
        self.Device_label.grid(row=0, column=0, padx=(20, 0), pady=20)
        self.Device_serial_label = customtkinter.CTkLabel(self, text=serial)  # Display the serial here
        self.Device_serial_label.grid(row=0, column=1, padx=(5, 20), pady=20)

        self.Device_name_label = customtkinter.CTkLabel(self, text=device_name)
        #self.Device_name_label.grid(row=0, column=2, padx=20, pady=20)
        self.Device_name_label.place(x=210,y=20)

        self.button_select = customtkinter.CTkButton(self,command=lambda: self.device_button_callback("pair",serial), text="Pair")
        self.button_select.grid(row=0, column=4, padx=(20, 10), pady=20)
        self.button_select = customtkinter.CTkButton(self,command=lambda: self.device_button_callback("unpair",serial), text="Unpair")
        self.button_select.grid(row=0, column=5, padx=(10, 20), pady=20)


    def get_device_name(self, serial_number):
        if serial_number.endswith(("LYM", "RYB")):
            return "Headset"
        else:
            return "Dongle"
        
    def device_button_callback(self,command,serial):
        exe_path = self.app_instance.exe_path_frame.textbox.get()
        self.app_instance.execute_subprocess_serial(serial, command, exe_path)
        self.app_instance.insert_log("Executed command : serial " + serial +" "+ command)
        time.sleep(1)

class ExePathFrame(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.textbox = customtkinter.CTkEntry(self, width=120)
        self.textbox.grid(row=0, column=0, padx=(20, 0), pady=(20, 20), sticky="ew")

        self.button_select = customtkinter.CTkButton(self, command=self.path_button_select_callback, fg_color="transparent", text_color=("gray10", "#DCE4EE"), border_width=2, text="Browse")
        self.button_select.grid(row=0, column=1, padx=20, pady=20)

        #reset
        self.textbox.delete(0, tk.END)
        self.textbox.insert(0, r"C:\Program Files (x86)\Steam\steamapps\common\SteamVR\tools\lighthouse\bin\win64\lighthouse_console.exe")

    def path_button_select_callback(self):
        file_name = self.file_read()

        if file_name is not None:
            self.textbox.delete(0, tk.END)
            self.textbox.insert(0, file_name)
            self.exe_check()

    @staticmethod
    def file_read():
        current_dir = os.path.abspath(os.path.dirname(__file__))
        file_path = tk.filedialog.askopenfilename(filetypes=[("Executable Files", "*.exe")], initialdir=current_dir)

        if len(file_path) != 0:
            return file_path
        else:
            return None

    def exe_check(self):

        app_instance = self.master
        exe_path = app_instance.exe_path_frame.textbox.get() 
        output = app_instance.execute_subprocess("serial", exe_path)
        if "lighthouse_console.exe" in output:
            app_instance.insert_log("Successfully recognized lighthouse_console.exe")
            
        else:
            app_instance.insert_log("Failed to recognize lighthouse_console.exe")
                  
class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.title("watchman_pairing_assistant")
        self.after(201, lambda :self.iconbitmap(r'C:\Users\marim\Desktop\pairing_assistant\UI_test\icon.ico')) #set icon dir
        self.geometry(f"{940}x{590}")
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.exe_path_frame = ExePathFrame(self)
        self.exe_path_frame.grid(row=0, column=1, padx=(20, 20), pady=(10, 0), sticky="nsew")
        self.exe_path_frame.grid_rowconfigure(0, weight=1)
        self.exe_path_frame.grid_columnconfigure(0, weight=1)

        self.sidebar_frame = SidebarFrame(self)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(5, weight=1)

        self.scrollable_frame = ScrollableFrame(self)
        self.scrollable_frame.grid(row=1, column=1, padx=(20, 20), pady=(10, 0), sticky="nsew")
        self.scrollable_frame.grid_columnconfigure(0, weight=1)

        self.log_textbox = customtkinter.CTkTextbox(self,height= 100)
        self.log_textbox.grid(row=2, column=1, padx=(20, 20), pady=(20, 20), sticky="nsew")

        #reset
        self.insert_log("Welcome to watchman_pairing_assistant ! (v1.0)")
        self.exe_path_frame.exe_check()
        self.sidebar_frame.reload_devices()
        
    
    def insert_log(self,log):
        current_time = time.strftime("[%Y-%m-%d %H:%M:%S] ")
        self.log_textbox.insert(tk.END, current_time + log + "\n")
        self.log_textbox.see(tk.END)
        print(current_time + log)

    def execute_subprocess(self, command, exe_path):
        completed_process = subprocess.run([exe_path, command], capture_output=True, text=True)
        ##print("Completed Process:", completed_process)
        return completed_process.stdout
    
    def execute_subprocess_serial(self, serial, command, exe_path, timeout=10):
        def run_subprocess():
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

        thread = threading.Thread(target=run_subprocess)
        thread.start()

if __name__ == "__main__":
    app = App() 
    app.mainloop()
