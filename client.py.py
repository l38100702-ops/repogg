import threading
import socket
import customtkinter as ctk


class ChatClient(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Chat Client")
        self.geometry("500x400")

        self.username = "User"
        self.sock = None
        self.font_size = 14

        # ===== GLOBAL STYLE (BLUE) =====
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # ===== LEFT MENU =====
        self.menu_frame = ctk.CTkFrame(self, width=60, fg_color="#1f2a44")
        self.menu_frame.pack(side="left", fill="y")
        self.menu_frame.pack_propagate(False)

        self.menu_button = ctk.CTkButton(
            self.menu_frame, text="▶", width=40,
            command=self.toggle_menu,
            fg_color="#2b6cb0", hover_color="#2c5282"
        )
        self.menu_button.pack(pady=5)

        self.name_entry = ctk.CTkEntry(self.menu_frame, placeholder_text="Name")

        self.save_button = ctk.CTkButton(
            self.menu_frame, text="Save",
            command=self.save_name,
            fg_color="#3182ce"
        )

        # FONT SIZE
        self.size_entry = ctk.CTkEntry(self.menu_frame, placeholder_text="Font size")
        self.size_button = ctk.CTkButton(
            self.menu_frame, text="Apply",
            command=self.set_font_size,
            fg_color="#3182ce"
        )

        self.menu_open = False

        # ===== CHAT =====
        self.chat_frame = ctk.CTkFrame(self, fg_color="#0f172a")
        self.chat_frame.pack(fill="both", expand=True)

        self.chat_box = ctk.CTkScrollableFrame(self.chat_frame, fg_color="#0f172a")
        self.chat_box.pack(fill="both", expand=True, padx=5, pady=5)

        # ===== BOTTOM =====
        self.bottom_frame = ctk.CTkFrame(self, fg_color="#1e3a8a")
        self.bottom_frame.pack(fill="x")

        self.entry = ctk.CTkEntry(self.bottom_frame)
        self.entry.pack(side="left", fill="x", expand=True, padx=5, pady=5)

        self.send_btn = ctk.CTkButton(
            self.bottom_frame, text=">",
            width=40, command=self.send_message,
            fg_color="#2563eb"
        )
        self.send_btn.pack(side="left", padx=5)

        self.bind("<Return>", lambda e: self.send_message())

        self.connect()

    # ===== MENU =====
    def toggle_menu(self):
        if not self.menu_open:
            self.menu_frame.configure(width=200)
            self.menu_button.configure(text="◀")

            self.name_entry.pack(pady=5)
            self.save_button.pack(pady=5)

            self.size_entry.pack(pady=5)
            self.size_button.pack(pady=5)

        else:
            self.menu_frame.configure(width=60)
            self.menu_button.configure(text="▶")

            self.name_entry.pack_forget()
            self.save_button.pack_forget()

            self.size_entry.pack_forget()
            self.size_button.pack_forget()

        self.menu_open = not self.menu_open
        self.menu_frame.update_idletasks()

    def save_name(self):
        name = self.name_entry.get().strip()
        if name:
            self.username = name
            self.add_message(f"[SYSTEM] Name: {name}")

    def set_font_size(self):
        try:
            size = int(self.size_entry.get())
            if 8 <= size <= 40:
                self.font_size = size
                self.add_message(f"[SYSTEM] Font size: {size}")
        except:
            self.add_message("[SYSTEM] Invalid size")

    # ===== CHAT =====
    def add_message(self, text):
        def ui():
            frame = ctk.CTkFrame(self.chat_box, fg_color="#1e293b")
            frame.pack(anchor="w", pady=5, padx=5)

            label = ctk.CTkLabel(
                frame,
                text=text,
                wraplength=350,
                font=("Arial", self.font_size)
            )
            label.pack(padx=5, pady=5)

            try:
                self.chat_box._parent_canvas.yview_moveto(1.0)
            except:
                pass

        self.after(0, ui)

    # ===== NETWORK =====
    def connect(self):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect(("127.0.0.1", 8080))

            threading.Thread(target=self.receive, daemon=True).start()
            self.add_message("[SYSTEM] Connected")

        except Exception as e:
            self.add_message(f"[SYSTEM] No server: {e}")

    def receive(self):
        buffer = ""

        while True:
            try:
                data = self.sock.recv(4096)
                if not data:
                    break

                buffer += data.decode("utf-8", errors="ignore")

                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    self.handle(line.strip())

            except:
                break

    def handle(self, msg):
        parts = msg.split("@", 2)

        if parts[0] == "TEXT" and len(parts) >= 3:
            self.add_message(f"{parts[1]}: {parts[2]}")

    # ===== SEND =====
    def send_message(self):
        text = self.entry.get().strip()
        if not text:
            return

        self.add_message(f"{self.username}: {text}")

        try:
            if self.sock:
                msg = f"TEXT@{self.username}@{text}\n"
                self.sock.sendall(msg.encode())
        except:
            self.add_message("[SYSTEM] Send error")

        self.entry.delete(0, "end")


if __name__ == "__main__":
    app = ChatClient()
    app.mainloop()