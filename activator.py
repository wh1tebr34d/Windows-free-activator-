#!/usr/bin/env pythonw
import subprocess
import time
import threading
import tkinter as tk
from tkinter import ttk
import ctypes
import sys
import os
import urllib.request

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def request_admin():
    if not is_admin():
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        sys.exit(0)

def is_activated():
    # Check using license state (works on all editions)
    try:
        result = subprocess.run(
            'powershell -Command "(Get-CimInstance -ClassName SoftwareLicensingProduct | Where-Object {$_.PartialProductKey}).LicenseStatus"',
            shell=True, capture_output=True, text=True, timeout=10
        )
        if "1" in result.stdout:
            return True
    except:
        pass
    return False

def press_key(vk_code):
    INPUT_KEYBOARD = 1
    KEYEVENTF_KEYDOWN = 0x0000
    KEYEVENTF_KEYUP = 0x0002
    
    class KEYBDINPUT(ctypes.Structure):
        _fields_ = [("wVk", ctypes.c_ushort), ("wScan", ctypes.c_ushort), 
                   ("dwFlags", ctypes.c_ulong), ("time", ctypes.c_ulong), 
                   ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong))]
    
    class INPUT_UNION(ctypes.Union):
        _fields_ = [("ki", KEYBDINPUT), ("mi", ctypes.c_byte * 40)]
    
    class INPUT(ctypes.Structure):
        _fields_ = [("type", ctypes.c_ulong), ("ui", INPUT_UNION)]
    
    inp = INPUT()
    inp.type = INPUT_KEYBOARD
    inp.ui.ki.wVk = vk_code
    inp.ui.ki.dwFlags = KEYEVENTF_KEYDOWN
    ctypes.windll.user32.SendInput(1, ctypes.byref(inp), ctypes.sizeof(INPUT))
    time.sleep(0.05)
    inp.ui.ki.dwFlags = KEYEVENTF_KEYUP
    ctypes.windll.user32.SendInput(1, ctypes.byref(inp), ctypes.sizeof(INPUT))

def activate():
    try:
        # Download MAS script
        url = "https://raw.githubusercontent.com/massgravel/Microsoft-Activation-Scripts/master/MAS/All-In-One-Version/MAS_AIO.cmd"
        temp_file = os.path.join(os.environ['TEMP'], 'mas.cmd')
        urllib.request.urlretrieve(url, temp_file)
        
        # Run it
        subprocess.Popen([temp_file], shell=True)
        time.sleep(5)
        
        # Send keys: 1 (Activation), 1 (HWID), 0 (Exit)
        press_key(0x31)
        time.sleep(2)
        press_key(0x31)
        time.sleep(15)
        press_key(0x30)
        
        time.sleep(3)
        os.remove(temp_file)
        
        return is_activated()
    except Exception as e:
        return False

def gui():
    request_admin()
    
    root = tk.Tk()
    root.title("Windows Activation")
    root.geometry("500x250")
    root.resizable(False, False)
    root.eval('tk::PlaceWindow . center')
    
    tk.Label(root, text="Windows Activation", font=("Arial", 14, "bold")).pack(pady=10)
    
    status_label = tk.Label(root, text="Checking current activation...", font=("Arial", 10))
    status_label.pack(pady=5)
    
    bar = ttk.Progressbar(root, length=400, mode='indeterminate')
    bar.pack(pady=15)
    
    result_label = tk.Label(root, text="", font=("Arial", 10))
    result_label.pack(pady=10)
    
    def run():
        if is_activated():
            status_label.config(text="Windows is already activated")
            result_label.config(text="No action needed", fg="green")
            root.after(3000, root.destroy)
            return
        
        bar.start(10)
        status_label.config(text="Activating (this may take a minute)...")
        
        success = activate()
        
        bar.stop()
        if success:
            result_label.config(text="Activation successful!", fg="green")
        else:
            result_label.config(text="Activation failed - check internet", fg="red")
        
        root.after(5000, root.destroy)
    
    threading.Thread(target=run).start()
    root.mainloop()

if __name__ == "__main__":
    gui()