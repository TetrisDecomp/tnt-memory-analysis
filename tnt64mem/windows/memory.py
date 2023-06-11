import tkinter as tk
from tkinter import ttk
import time

BOARD_POINTERS = 0x8011FBD0
BOARD_BUFFER_SIZE = 3200

BASE_ADDR = 0x80000000
RAM_SIZE = 4 * 1024 * 1024  # 4 MiB

def hexdump(addr, bytes_):
    lines = []
    hex_str = bytes_.hex()
    for i in range(0, len(hex_str), 32):
        row = hex_str[i : i + 32]
        words = []
        for j in range(0, 32, 8):
            word = row[j : j + 8]
            words.append(word)
        line = f'{addr:08X}: {" ".join(words)}'
        lines.append(line)
        addr += 16
    return lines

def init_text(tk_text, base_addr, bytes_len):
    bytes_ = bytes(bytes_len)
    lines = hexdump(base_addr, bytes_)

    save_state = tk_text['state']
    tk_text['state'] = 'normal'
    tk_text.replace('1.0', 'end', '\n'.join(lines))
    tk_text['state'] = save_state

def update_text(tk_text, base_addr, bytes_len, procmem):
    yview = tk_text.yview()
    #print(yview)
    start = int(yview[0] * bytes_len) & ~15
    end = int(yview[1] * bytes_len) + 15 & ~15
    addr = base_addr + start
    bytes_ = procmem.dump(addr, end - start)

    if len(bytes_) > 0:
        save_state = tk_text['state']
        tk_text['state'] = 'normal'

        lines = hexdump(addr, bytes_)
        start_line = (start >> 4) + 1
        end_line = start_line + len(lines)
        tk_text.replace(f'{start_line}.0', f'{end_line}.0-1c', '\n'.join(lines))
        #print(f'{start_line}.0', f'{end_line}.0-1c')

        tk_text['state'] = save_state

class Memory:
    def __init__(self, root, procmem):
        self.root = root
        self.procmem = procmem

        self.root.title('Memory')
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        self.t = tk.Text(self.root, width=45, height=20, wrap="none", padx=10, pady=10)
        ys = ttk.Scrollbar(self.root, orient='vertical', command=self.t.yview)
        self.t['yscrollcommand'] = ys.set
        self.t.grid(column=0, row=0, sticky='nwes')
        ys.grid(column=1, row=0, sticky='ns')
        self.t['state'] = 'disabled'

        #init_text(self.t, 0, BOARD_BUFFER_SIZE)
        init_text(self.t, 0, RAM_SIZE)

        # For FPS stat
        self.frame_count = 0
        self.last_time = time.time()

        self.root.after_idle(self.update)

    def update(self):
        # Update every 16 ms (target 60 FPS)
        self.root.after(16, self.update)

        # For FPS stat
        current_time = time.time()
        self.frame_count += 1
        if (current_time - self.last_time) > 1:  # 1 second
            #print('FPS:', self.frame_count / (current_time - self.last_time))
            self.frame_count = 0
            self.last_time = current_time

        #update_text(self.t, self.procmem.deref(self.procmem.deref(BOARD_POINTERS)), BOARD_BUFFER_SIZE, self.procmem)
        update_text(self.t, BASE_ADDR, RAM_SIZE, self.procmem)
