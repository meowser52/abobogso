import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import os
import random
from collections import Counter
import time


class JobLoader:
    def __init__(self):
        self.txt_files = [f for f in os.listdir('.') if os.path.isfile(f) and f.endswith('.txt')]

    def load_random_file(self):
        file_name = random.choice(self.txt_files)
        with open(file_name, 'r') as file:
            return list(file.read())


class Statistics:
    def __init__(self):
        self.total_chars = 0
        self.errors = 0
        self.start_time = time.time()  # Add start time
        self.error_counter = Counter()
        self.is_stopped = False  # Add a flag to check if the program is stopped
        self.start_time = None

    def start(self):
        if self.start_time is None:
            self.start_time = time.time()

    def stop(self):
        self.is_stopped = True
        self.stop_time = time.time()  # Remember the time when stopped

    def continue_(self):
        if self.is_stopped:
            self.is_stopped = False
            self.start_time += time.time() - self.stop_time  # Adjust the start time

    def update(self, char, error):
        self.total_chars += 1
        if error:
            self.errors += 1
            self.error_counter[char] += 1

    def most_common_error(self):
        return self.error_counter.most_common(1)[0] if self.error_counter else None

    def keystrokes_per_second(self):
        elapsed_time = time.time() - self.start_time
        return self.total_chars / elapsed_time if elapsed_time > 0 else 0


class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.start_button = None
        self.start_label = None
        self.master = master
        self.pack()
        self.create_widgets()

    def start_typing(self):
        self.master.destroy()
        #        self.start_button.destroy()
        #        self.start_label.destroy()
        app = App()
        app.start()
        app.run()

    def create_widgets(self):
        self.start_label = tk.Label(self, text="Are you ready to start?")
        self.start_label.pack()

        self.start_button = ttk.Button(self, text="Start")
        self.start_button["command"] = self.start_typing
        self.start_button.pack()


class TypingTrainer:
    def __init__(self, char_list, statistics):
        self.char_list = char_list
        self.statistics = statistics
        self.counter = 0

    def check_char(self, char):
        correct = char == self.char_list[self.counter]
        self.statistics.update(char, not correct)
        if correct:
            self.counter += 1
        return correct


class App:
    def __init__(self):
        self.job_loader = JobLoader()
        self.char_list = self.job_loader.load_random_file()
        self.statistics = Statistics()
        self.typing_trainer = TypingTrainer(self.char_list, self.statistics)

        self.root = tk.Tk()

        self.text_widget = tk.Text(self.root, height=30, width=100)
        self.text_widget.insert('1.0', ''.join(self.char_list))
        self.text_widget.pack()

        self.entry = tk.Entry(self.root)
        self.entry.pack()
        self.entry.focus_set()

        self.reload_button = tk.Button(self.root, text="Reload", command=self.reload)
        self.reload_button.pack(side='left')

        self.exit_button = tk.Button(self.root, text="Exit", command=self.root.quit)
        self.exit_button.pack(side='right')

        self.stats_button = tk.Button(self.root, text="Statistics", command=self.show_statistics)
        self.stats_button.pack(side='right')

        self.stop_button = tk.Button(self.root, text="Stop", command=self.stop)
        self.stop_button.pack(side='right')
        self.continue_button = tk.Button(self.root, text="Continue", command=self.continue_)
        self.continue_button.pack(side='right')

        self.root.bind('<Key>', self.key_pressed)

        self.entered_text_window = tk.Toplevel(self.root)
        self.entered_text_widget = tk.Text(self.entered_text_window, height=10, width=50)
        self.entered_text_widget.pack()
        self.text_widget.config(state='disabled')

        self.complete_button = tk.Button(self.root, text="Complete", command=self.complete)
        self.complete_button.pack(side='right')

        self.start_button = tk.Button(self.root, command=self.start)

        self.timer_label = tk.Label(self.root)
        self.timer_label.pack(side='right')

    def start(self):
        self.statistics.start()
        self.update_timer()

    def update_timer(self):
        elapsed_time = time.time() - self.statistics.start_time
        minutes, seconds = divmod(int(elapsed_time), 60)
        self.timer_label.config(text=f'{minutes}:{seconds:02}')
        if not self.statistics.is_stopped:
            self.root.after(1000, self.update_timer)  # Update the timer every second

    def key_pressed(self, event):
        if self.statistics.is_stopped:  # Don't register key presses when stopped
            return
        if event.keysym not in ['Shift_L', 'Shift_R', 'BackSpace']:  # Ignore Shift and Backspace keys
            correct = self.typing_trainer.check_char(event.char)
            if correct:
                print(event.char, end='', flush=True)
                self.entered_text_widget.insert('end', event.char)  # Add entered char to the new window
                self.text_widget.delete('1.0', '1.1')  # Remove the correct char from the original text
                self.text_widget.delete('1.0', tk.END)  # Delete the old text
                self.text_widget.insert('1.0', ''.join(self.char_list[self.statistics.total_chars:]))

    def stop(self):
        self.statistics.stop()

    def continue_(self):
        self.statistics.continue_()

    def reload(self):
        self.char_list = self.job_loader.load_random_file()
        self.statistics = Statistics()
        self.typing_trainer = TypingTrainer(self.char_list, self.statistics)
        self.entry.delete(0, 'end')
        # Update the original text
        self.text_widget.config(state='normal')  # Make the text widget changeable
        self.text_widget.delete('1.0', 'end')
        self.text_widget.insert('1.0', ''.join(self.char_list))
        self.text_widget.config(state='disabled')  # Make the text widget unchangeable again
        # Clear the entered text window
        self.entered_text_widget.delete('1.0', 'end')

    def show_statistics(self):
        messagebox.showinfo("Statistics",
                            f"Total characters: {self.statistics.total_chars}\n"
                            f"Errors: {self.statistics.errors}\n"
                            f"Most common error: {self.statistics.most_common_error()}\n"
                            f"Keystrokes per second: {self.statistics.keystrokes_per_second():.2f}")
        # Add keystrokes per second

    def run(self):
        self.root.mainloop()

    def complete(self):
        # Generate statistics
        stats = {
            "Total Chars": self.statistics.total_chars,
            "Errors": self.statistics.errors,
            "Most Common Error": self.statistics.most_common_error(),
            "Keystrokes per Second": self.statistics.keystrokes_per_second()
        }

        # Write statistics to a text file
        with open('statistics.txt', 'w') as file:
            for key, value in stats.items():
                file.write(f"{key}: {value}\n")

        # Show a message box indicating that the attempt has been completed
        messagebox.showinfo("Complete", "Your attempt has been completed and the statistics have been saved.")


if __name__ == "__main__":
    root = tk.Tk()
    app = Application(master=root)
    app.mainloop()
