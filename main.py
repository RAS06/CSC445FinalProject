import tkinter as tk
from tkinter import ttk, messagebox
import random
import time
import threading
from enum import Enum, auto


class SortState(Enum):
    UNSORTED = "#808080"  # Gray
    COMPARING = "#FFD700"  # Yellow
    SWAPPING = "#FF4444"  # Red
    SORTED = "#00AA00"  # Green


class SortingVisualizer:
    def __init__(self, root):
        self.root = root
        self.root.title("Sorting Algorithm Visualizer")
        self.root.geometry("1000x700")
        self.root.configure(bg="#1e1e2e")

        # Data and state
        self.array = []
        self.array_size = 50
        self.min_val = 5
        self.max_val = 100
        self.sorting = False
        self.speed = 0.05  # seconds delay
        self.swap_count = 0
        self.comparison_count = 0
        self.start_time = 0

        # Canvas dimensions
        self.canvas_width = 950
        self.canvas_height = 400

        self.setup_ui()
        self.generate_array()

    def setup_ui(self):
        # Main container with padding
        main_frame = tk.Frame(self.root, bg="#1e1e2e")
        main_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Title
        title = tk.Label(
            main_frame,
            text="Sorting Algorithm Visualizer",
            font=("Segoe UI", 20, "bold"),
            bg="#1e1e2e",
            fg="#cdd6f4"
        )
        title.pack(pady=(0, 10))

        # Control Panel
        control_frame = tk.LabelFrame(
            main_frame,
            text="Controls",
            font=("Segoe UI", 11, "bold"),
            bg="#313244",
            fg="#cdd6f4",
            bd=2,
            relief=tk.GROOVE
        )
        control_frame.pack(fill=tk.X, pady=5)

        # Left side controls
        left_controls = tk.Frame(control_frame, bg="#313244")
        left_controls.pack(side=tk.LEFT, padx=10, pady=10)

        # Array Size
        tk.Label(left_controls, text="Array Size:", bg="#313244", fg="#cdd6f4", font=("Segoe UI", 10)).grid(row=0,
                                                                                                            column=0,
                                                                                                            sticky="w")
        self.size_scale = tk.Scale(
            left_controls,
            from_=10, to=100,
            orient=tk.HORIZONTAL,
            length=150,
            bg="#313244",
            fg="#cdd6f4",
            highlightthickness=0,
            command=self.on_size_change
        )
        self.size_scale.set(self.array_size)
        self.size_scale.grid(row=0, column=1, padx=5)

        # Min Value
        tk.Label(left_controls, text="Min Value:", bg="#313244", fg="#cdd6f4", font=("Segoe UI", 10)).grid(row=1,
                                                                                                           column=0,
                                                                                                           sticky="w")
        self.min_entry = tk.Spinbox(left_controls, from_=1, to=50, width=8, font=("Segoe UI", 10))
        self.min_entry.delete(0, tk.END)
        self.min_entry.insert(0, str(self.min_val))
        self.min_entry.grid(row=1, column=1, padx=5, pady=2)

        # Max Value
        tk.Label(left_controls, text="Max Value:", bg="#313244", fg="#cdd6f4", font=("Segoe UI", 10)).grid(row=2,
                                                                                                           column=0,
                                                                                                           sticky="w")
        self.max_entry = tk.Spinbox(left_controls, from_=50, to=200, width=8, font=("Segoe UI", 10))
        self.max_entry.delete(0, tk.END)
        self.max_entry.insert(0, str(self.max_val))
        self.max_entry.grid(row=2, column=1, padx=5, pady=2)

        # Middle controls
        mid_controls = tk.Frame(control_frame, bg="#313244")
        mid_controls.pack(side=tk.LEFT, padx=20, pady=10)

        # Algorithm Selection
        tk.Label(mid_controls, text="Algorithm:", bg="#313244", fg="#cdd6f4", font=("Segoe UI", 10, "bold")).grid(row=0,
                                                                                                                  column=0,
                                                                                                                  sticky="w")
        self.algo_var = tk.StringVar(value="Bubble Sort")
        self.algo_menu = ttk.Combobox(
            mid_controls,
            textvariable=self.algo_var,
            values=["Bubble Sort", "Merge Sort", "Quick Sort", "Heap Sort"],
            state="readonly",
            width=15,
            font=("Segoe UI", 10)
        )
        self.algo_menu.grid(row=0, column=1, padx=5, pady=2)

        # Speed Control
        tk.Label(mid_controls, text="Speed:", bg="#313244", fg="#cdd6f4", font=("Segoe UI", 10)).grid(row=1, column=0,
                                                                                                      sticky="w")
        self.speed_scale = tk.Scale(
            mid_controls,
            from_=0.001, to=0.5,
            resolution=0.001,
            orient=tk.HORIZONTAL,
            length=150,
            bg="#313244",
            fg="#cdd6f4",
            highlightthickness=0
        )
        self.speed_scale.set(self.speed)
        self.speed_scale.grid(row=1, column=1, padx=5)

        # Buttons
        btn_frame = tk.Frame(control_frame, bg="#313244")
        btn_frame.pack(side=tk.RIGHT, padx=10, pady=10)

        self.generate_btn = tk.Button(
            btn_frame,
            text="🎲 Generate New Array",
            command=self.generate_array,
            bg="#89b4fa",
            fg="#1e1e2e",
            font=("Segoe UI", 10, "bold"),
            width=18,
            relief=tk.FLAT,
            cursor="hand2"
        )
        self.generate_btn.pack(pady=2)

        self.start_btn = tk.Button(
            btn_frame,
            text="▶ Start Sorting",
            command=self.start_sorting,
            bg="#a6e3a1",
            fg="#1e1e2e",
            font=("Segoe UI", 10, "bold"),
            width=18,
            relief=tk.FLAT,
            cursor="hand2"
        )
        self.start_btn.pack(pady=2)

        self.stop_btn = tk.Button(
            btn_frame,
            text="⏹ Stop",
            command=self.stop_sorting,
            bg="#f38ba8",
            fg="#1e1e2e",
            font=("Segoe UI", 10, "bold"),
            width=18,
            relief=tk.FLAT,
            cursor="hand2",
            state=tk.DISABLED
        )
        self.stop_btn.pack(pady=2)

        # Stats Frame
        stats_frame = tk.LabelFrame(
            main_frame,
            text="Statistics",
            font=("Segoe UI", 11, "bold"),
            bg="#313244",
            fg="#cdd6f4",
            bd=2,
            relief=tk.GROOVE
        )
        stats_frame.pack(fill=tk.X, pady=5)

        self.time_label = tk.Label(
            stats_frame,
            text="⏱ Time: 0.000s",
            bg="#313244",
            fg="#89b4fa",
            font=("Segoe UI", 11, "bold"),
            width=20
        )
        self.time_label.pack(side=tk.LEFT, padx=20, pady=5)

        self.comparison_label = tk.Label(
            stats_frame,
            text="🔍 Comparisons: 0",
            bg="#313244",
            fg="#f9e2af",
            font=("Segoe UI", 11, "bold"),
            width=20
        )
        self.comparison_label.pack(side=tk.LEFT, padx=20, pady=5)

        self.swap_label = tk.Label(
            stats_frame,
            text="🔄 Swaps: 0",
            bg="#313244",
            fg="#f38ba8",
            font=("Segoe UI", 11, "bold"),
            width=20
        )
        self.swap_label.pack(side=tk.LEFT, padx=20, pady=5)

        # Legend
        legend_frame = tk.Frame(stats_frame, bg="#313244")
        legend_frame.pack(side=tk.RIGHT, padx=20)

        legends = [
            ("Unsorted", SortState.UNSORTED.value),
            ("Comparing", SortState.COMPARING.value),
            ("Swapping", SortState.SWAPPING.value),
            ("Sorted", SortState.SORTED.value)
        ]

        for text, color in legends:
            lbl = tk.Label(
                legend_frame,
                text="■",
                fg=color,
                bg="#313244",
                font=("Segoe UI", 12)
            )
            lbl.pack(side=tk.LEFT, padx=(10, 0))
            txt = tk.Label(
                legend_frame,
                text=text,
                bg="#313244",
                fg="#cdd6f4",
                font=("Segoe UI", 9)
            )
            txt.pack(side=tk.LEFT, padx=(0, 10))

        # Canvas for visualization
        canvas_frame = tk.Frame(main_frame, bg="#45475a", bd=2, relief=tk.SUNKEN)
        canvas_frame.pack(pady=10, fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(
            canvas_frame,
            width=self.canvas_width,
            height=self.canvas_height,
            bg="#1e1e2e",
            highlightthickness=0
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Status bar
        self.status_label = tk.Label(
            main_frame,
            text="Ready",
            bg="#313244",
            fg="#a6e3a1",
            font=("Segoe UI", 10),
            anchor=tk.W
        )
        self.status_label.pack(fill=tk.X, pady=(5, 0))

    def on_size_change(self, value):
        if not self.sorting:
            self.array_size = int(value)
            self.generate_array()

    def generate_array(self):
        if self.sorting:
            return

        try:
            min_val = int(self.min_entry.get())
            max_val = int(self.max_entry.get())

            if min_val >= max_val:
                messagebox.showerror("Error", "Min value must be less than max value!")
                return

            self.min_val = min_val
            self.max_val = max_val

        except ValueError:
            messagebox.showerror("Error", "Please enter valid integer values!")
            return

        self.array = [random.randint(self.min_val, self.max_val) for _ in range(self.array_size)]
        self.reset_stats()
        self.draw_array()
        self.status_label.config(text=f"Generated new array with {self.array_size} elements", fg="#a6e3a1")

    def reset_stats(self):
        self.swap_count = 0
        self.comparison_count = 0
        self.start_time = 0
        self.update_stats()

    def update_stats(self):
        elapsed = time.time() - self.start_time if self.sorting else 0
        if self.sorting and self.start_time > 0:
            elapsed = time.time() - self.start_time

        self.time_label.config(text=f"⏱ Time: {elapsed:.3f}s")
        self.comparison_label.config(text=f"🔍 Comparisons: {self.comparison_count}")
        self.swap_label.config(text=f"🔄 Swaps: {self.swap_count}")

    def draw_array(self, color_array=None):
        self.canvas.delete("all")

        if not self.array:
            return

        bar_width = self.canvas_width / len(self.array)
        max_height = max(self.array) if self.array else 1
        height_scale = (self.canvas_height - 20) / max_height

        for i, val in enumerate(self.array):
            x0 = i * bar_width + 1
            x1 = (i + 1) * bar_width - 1
            y0 = self.canvas_height
            y1 = self.canvas_height - (val * height_scale)

            color = color_array[i] if color_array else SortState.UNSORTED.value

            self.canvas.create_rectangle(
                x0, y0, x1, y1,
                fill=color,
                outline=""
            )

            # Draw value on top for smaller arrays
            if len(self.array) <= 30:
                self.canvas.create_text(
                    (x0 + x1) / 2, y1 - 10,
                    text=str(val),
                    fill="white",
                    font=("Segoe UI", 8)
                )

        self.root.update_idletasks()

    def get_delay(self):
        return self.speed_scale.get()

    def sleep(self):
        time.sleep(self.get_delay())
        self.update_stats()

    def start_sorting(self):
        if self.sorting:
            return

        if not self.array:
            messagebox.showwarning("Warning", "Please generate an array first!")
            return

        self.sorting = True
        self.starting = True
        self.start_time = time.time()
        self.reset_stats()

        # Update UI state
        self.generate_btn.config(state=tk.DISABLED)
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.algo_menu.config(state=tk.DISABLED)
        self.size_scale.config(state=tk.DISABLED)

        algorithm = self.algo_var.get()
        self.status_label.config(text=f"Running {algorithm}...", fg="#f9e2af")

        # Run sorting in separate thread to keep UI responsive
        sort_thread = threading.Thread(target=self.run_algorithm, args=(algorithm,))
        sort_thread.daemon = True
        sort_thread.start()

    def run_algorithm(self, algorithm):
        try:
            if algorithm == "Bubble Sort":
                self.bubble_sort()
            elif algorithm == "Merge Sort":
                self.merge_sort(0, len(self.array) - 1)
                self.finalize_sort()
            elif algorithm == "Quick Sort":
                self.quick_sort(0, len(self.array) - 1)
                self.finalize_sort()
            elif algorithm == "Heap Sort":
                self.heap_sort()

            if self.sorting:  # If not stopped
                self.status_label.config(text="Sorting completed!", fg="#a6e3a1")
        except Exception as e:
            if self.sorting:
                self.status_label.config(text=f"Error: {str(e)}", fg="#f38ba8")
        finally:
            self.sorting = False
            self.starting = False
            self.root.after(0, self.reset_ui_state)

    def reset_ui_state(self):
        self.generate_btn.config(state=tk.NORMAL)
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.algo_menu.config(state="readonly")
        self.size_scale.config(state=tk.NORMAL)
        self.update_stats()

    def stop_sorting(self):
        self.sorting = False
        self.status_label.config(text="Sorting stopped by user", fg="#f38ba8")

    def finalize_sort(self):
        """Mark all elements as sorted with animation"""
        colors = [SortState.SORTED.value for _ in self.array]
        self.draw_array(colors)
        self.sleep()

    # ==================== BUBBLE SORT ====================
    def bubble_sort(self):
        n = len(self.array)
        for i in range(n):
            swapped = False
            for j in range(0, n - i - 1):
                if not self.sorting:
                    return

                self.comparison_count += 1

                # Visualize comparison
                colors = [SortState.UNSORTED.value] * n
                for k in range(n - i, n):
                    colors[k] = SortState.SORTED.value
                colors[j] = SortState.COMPARING.value
                colors[j + 1] = SortState.COMPARING.value
                self.draw_array(colors)
                self.sleep()

                if self.array[j] > self.array[j + 1]:
                    # Visualize swap
                    colors[j] = SortState.SWAPPING.value
                    colors[j + 1] = SortState.SWAPPING.value
                    self.draw_array(colors)
                    self.sleep()

                    self.array[j], self.array[j + 1] = self.array[j + 1], self.array[j]
                    self.swap_count += 1
                    swapped = True

                    self.draw_array(colors)
                    self.sleep()

            # Mark last element as sorted
            colors = [SortState.UNSORTED.value] * n
            for k in range(n - i - 1, n):
                colors[k] = SortState.SORTED.value
            self.draw_array(colors)

            if not swapped:
                break

        self.finalize_sort()

    # ==================== MERGE SORT ====================
    def merge_sort(self, left, right):
        if not self.sorting:
            return

        if left < right:
            mid = (left + right) // 2

            self.merge_sort(left, mid)
            self.merge_sort(mid + 1, right)
            self.merge(left, mid, right)

    def merge(self, left, mid, right):
        if not self.sorting:
            return

        left_arr = self.array[left:mid + 1]
        right_arr = self.array[mid + 1:right + 1]

        i = j = 0
        k = left

        while i < len(left_arr) and j < len(right_arr):
            if not self.sorting:
                return

            self.comparison_count += 1

            # Visualize comparison
            colors = [SortState.UNSORTED.value] * len(self.array)
            colors[left + i] = SortState.COMPARING.value
            colors[mid + 1 + j] = SortState.COMPARING.value
            self.draw_array(colors)
            self.sleep()

            if left_arr[i] <= right_arr[j]:
                self.array[k] = left_arr[i]
                i += 1
            else:
                self.array[k] = right_arr[j]
                j += 1
                self.swap_count += 1

            # Visualize placement
            colors[k] = SortState.SWAPPING.value
            self.draw_array(colors)
            self.sleep()

            k += 1

        while i < len(left_arr):
            if not self.sorting:
                return
            self.array[k] = left_arr[i]
            i += 1
            k += 1
            self.swap_count += 1

            colors = [SortState.UNSORTED.value] * len(self.array)
            colors[k - 1] = SortState.SWAPPING.value
            self.draw_array(colors)
            self.sleep()

        while j < len(right_arr):
            if not self.sorting:
                return
            self.array[k] = right_arr[j]
            j += 1
            k += 1
            self.swap_count += 1

            colors = [SortState.UNSORTED.value] * len(self.array)
            colors[k - 1] = SortState.SWAPPING.value
            self.draw_array(colors)
            self.sleep()

    # ==================== QUICK SORT ====================
    def quick_sort(self, low, high):
        if not self.sorting:
            return

        if low < high:
            pi = self.partition(low, high)
            self.quick_sort(low, pi - 1)
            self.quick_sort(pi + 1, high)

    def partition(self, low, high):
        if not self.sorting:
            return low

        pivot = self.array[high]
        i = low - 1

        for j in range(low, high):
            if not self.sorting:
                return low

            self.comparison_count += 1

            # Visualize comparison with pivot
            colors = [SortState.UNSORTED.value] * len(self.array)
            colors[high] = "#89b4fa"  # Pivot color (blue)
            colors[j] = SortState.COMPARING.value
            if i >= low:
                colors[i] = "#cba6f7"  # Partition index (purple)
            self.draw_array(colors)
            self.sleep()

            if self.array[j] <= pivot:
                i += 1
                if i != j:
                    # Visualize swap
                    colors[i] = SortState.SWAPPING.value
                    colors[j] = SortState.SWAPPING.value
                    self.draw_array(colors)
                    self.sleep()

                    self.array[i], self.array[j] = self.array[j], self.array[i]
                    self.swap_count += 1

                    self.draw_array(colors)
                    self.sleep()

        # Place pivot in correct position
        colors = [SortState.UNSORTED.value] * len(self.array)
        colors[i + 1] = SortState.SWAPPING.value
        colors[high] = SortState.SWAPPING.value
        self.draw_array(colors)
        self.sleep()

        self.array[i + 1], self.array[high] = self.array[high], self.array[i + 1]
        self.swap_count += 1

        colors[i + 1] = SortState.SORTED.value
        self.draw_array(colors)
        self.sleep()

        return i + 1

    # ==================== HEAP SORT ====================
    def heap_sort(self):
        n = len(self.array)

        # Build max heap
        for i in range(n // 2 - 1, -1, -1):
            if not self.sorting:
                return
            self.heapify(n, i)

        # Extract elements from heap
        for i in range(n - 1, 0, -1):
            if not self.sorting:
                return

            # Visualize swap of root with last element
            colors = [SortState.UNSORTED.value] * n
            colors[0] = SortState.SWAPPING.value
            colors[i] = SortState.SWAPPING.value
            for k in range(i + 1, n):
                colors[k] = SortState.SORTED.value
            self.draw_array(colors)
            self.sleep()

            self.array[0], self.array[i] = self.array[i], self.array[0]
            self.swap_count += 1

            colors[0] = SortState.SORTED.value
            colors[i] = SortState.SORTED.value
            self.draw_array(colors)
            self.sleep()

            self.heapify(i, 0)

        self.finalize_sort()

    def heapify(self, n, i):
        if not self.sorting:
            return

        largest = i
        left = 2 * i + 1
        right = 2 * i + 2

        # Visualize current node
        colors = [SortState.UNSORTED.value] * len(self.array)
        colors[i] = "#cba6f7"  # Current node (purple)
        if left < n:
            colors[left] = SortState.COMPARING.value
        if right < n:
            colors[right] = SortState.COMPARING.value
        for k in range(n, len(self.array)):
            colors[k] = SortState.SORTED.value
        self.draw_array(colors)
        self.sleep()

        if left < n:
            self.comparison_count += 1
            if self.array[left] > self.array[largest]:
                largest = left

        if right < n:
            self.comparison_count += 1
            if self.array[right] > self.array[largest]:
                largest = right

        if largest != i:
            # Visualize swap
            colors[i] = SortState.SWAPPING.value
            colors[largest] = SortState.SWAPPING.value
            self.draw_array(colors)
            self.sleep()

            self.array[i], self.array[largest] = self.array[largest], self.array[i]
            self.swap_count += 1

            self.draw_array(colors)
            self.sleep()

            self.heapify(n, largest)


def main():
    root = tk.Tk()
    app = SortingVisualizer(root)
    root.mainloop()


if __name__ == "__main__":
    main()