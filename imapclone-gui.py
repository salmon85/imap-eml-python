import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import shlex
import os
import sys

def run_imap_clone():
    # Collect inputs
    host = src_host.get()
    port = src_port.get()
    username = src_user.get()
    password = src_pass.get()
    ssl = src_ssl.get()

    remote_host_ = dst_host.get()
    remote_port_ = dst_port.get()
    remote_user_ = dst_user.get()
    remote_pass_ = dst_pass.get()
    remote_ssl_ = dst_ssl.get()

    if not all([host, username, password, remote_host_, remote_user_, remote_pass_]):
        messagebox.showerror("Missing Info", "Please fill in all required fields.")
        return

    # Locate imapclone.py in bundle or locally
    if getattr(sys, 'frozen', False):
        script_path = os.path.join(sys._MEIPASS, 'imapclone.py')
    else:
        script_path = 'imapclone.py'

    # Build command
    cmd = f"{shlex.quote(sys.executable)} {shlex.quote(script_path)} -s {shlex.quote(host)} -P {shlex.quote(port)} -u {shlex.quote(username)} -p {shlex.quote(password)}"
    if ssl:
        cmd += " --ssl"
    cmd += f" -rs {shlex.quote(remote_host_)} -rP {shlex.quote(remote_port_)} -ru {shlex.quote(remote_user_)} -rp {shlex.quote(remote_pass_)}"
    if remote_ssl_:
        cmd += " --rssl"

    # Run the script
    try:
        subprocess.Popen(shlex.split(cmd))
        messagebox.showinfo("Started", "Cloning started. Check terminal for progress.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to run imapclone.py:\n{e}")

# GUI setup
root = tk.Tk()
root.title("IMAP-to-IMAP Cloner")
root.geometry("600x650")

tk.Label(root, text="Source IMAP Server", font=("Arial", 12, "bold")).pack(pady=5)

tk.Label(root, text="Host:").pack()
src_host = tk.Entry(root, width=60)
src_host.pack()

tk.Label(root, text="Port:").pack()
src_port = tk.Entry(root, width=60)
src_port.insert(0, "143")
src_port.pack()

tk.Label(root, text="Username:").pack()
src_user = tk.Entry(root, width=60)
src_user.pack()

tk.Label(root, text="Password:").pack()
src_pass = tk.Entry(root, width=60, show="*")
src_pass.pack()

src_ssl = tk.BooleanVar()
tk.Checkbutton(root, text="Use SSL", variable=src_ssl).pack()

tk.Label(root, text="Destination IMAP Server", font=("Arial", 12, "bold")).pack(pady=10)

tk.Label(root, text="Host:").pack()
dst_host = tk.Entry(root, width=60)
dst_host.pack()

tk.Label(root, text="Port:").pack()
dst_port = tk.Entry(root, width=60)
dst_port.insert(0, "143")
dst_port.pack()

tk.Label(root, text="Username:").pack()
dst_user = tk.Entry(root, width=60)
dst_user.pack()

tk.Label(root, text="Password:").pack()
dst_pass = tk.Entry(root, width=60, show="*")
dst_pass.pack()

dst_ssl = tk.BooleanVar()
tk.Checkbutton(root, text="Use SSL", variable=dst_ssl).pack()

tk.Button(root, text="Run Clone", command=run_imap_clone, bg="blue", fg="white", height=2).pack(pady=20)

root.mainloop()
