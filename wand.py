import tkinter as tk
from tkinter import messagebox
import json
import os

# TODO: choose which file to load
FILENAME = "websites.json"


class WebsiteManagerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Website Manager")
        self.geometry("600x400")

        self.websites = []
        self.selected_index = None
        self.new_entry_mode = False  # adding new entry

        # GUI widgets
        self.listbox = tk.Listbox(self)
        self.listbox.pack(side=tk.LEFT, fill=tk.Y)

        btn_frame = tk.Frame(self)
        btn_frame.pack(side=tk.LEFT, fill=tk.Y)

        tk.Button(btn_frame, text="Add", command=self.add_website).pack(fill=tk.X)
        tk.Button(btn_frame, text="Delete", command=self.delete_website).pack(fill=tk.X)
        tk.Button(btn_frame, text="Save File", command=self.save_data).pack(fill=tk.X)
        tk.Button(btn_frame, text="Load File", command=self.load_data).pack(fill=tk.X)

        self.save_entry_btn = tk.Button(btn_frame, text="Save Changes", command=self.save_entry, state='disabled')
        self.save_entry_btn.pack(fill=tk.X)

        details_frame = tk.Frame(self)
        details_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        tk.Label(details_frame, text="Name:").grid(row=0, column=0, sticky="w")
        tk.Label(details_frame, text="URL:").grid(row=1, column=0, sticky="w")
        tk.Label(details_frame, text="Slug:").grid(row=2, column=0, sticky="w")
        tk.Label(details_frame, text="Owner:").grid(row=3, column=0, sticky="w")
        tk.Label(details_frame, text="About:").grid(row=4, column=0, sticky="nw")

        self.name_var = tk.StringVar()
        self.url_var = tk.StringVar()
        self.slug_var = tk.StringVar()
        self.owner_var = tk.StringVar()
        self.about_text = tk.Text(details_frame, height=5, width=40)

        self.name_entry = tk.Entry(details_frame, textvariable=self.name_var)
        self.slug_entry = tk.Entry(details_frame, textvariable=self.slug_var)
        self.url_entry = tk.Entry(details_frame, textvariable=self.url_var)
        self.owner_entry = tk.Entry(details_frame, textvariable=self.owner_var)

        self.name_entry.grid(row=0, column=1, sticky="we", padx=3, pady=2)
        self.url_entry.grid(row=1, column=1, sticky="we", padx=3, pady=2)
        self.slug_entry.grid(row=2, column=1, sticky="we", padx=3, pady=2)
        self.owner_entry.grid(row=3, column=1, sticky="we", padx=3, pady=2)
        self.about_text.grid(row=4, column=1, sticky="we", padx=3, pady=2)

        details_frame.columnconfigure(1, weight=1)

        self.listbox.bind('<<ListboxSelect>>', self.on_select)

        # Monitor changes to activate "Save Changes"
        self.name_var.trace_add('write', self.field_modified)
        self.url_var.trace_add('write', self.field_modified)
        self.slug_var.trace_add('write', self.field_modified)
        self.owner_var.trace_add('write', self.field_modified)
        self.about_text.bind('<<Modified>>', self.field_modified_event)

        self.load_data()

    def load_data(self):
        if os.path.exists(FILENAME):
            with open(FILENAME, 'r', encoding='utf-8') as f:
                self.websites = json.load(f)
        else:
            self.websites = []
        self.update_listbox()
        self.clear_details()

    def save_data(self):
        try:
            with open(FILENAME, 'w', encoding='utf-8') as f:
                json.dump(self.websites, f, indent=4)
            messagebox.showinfo("Save", "JSON saved!")
        except Exception as e:
            messagebox.showerror("Error", f"Could not save: {e}")

    def update_listbox(self):
        self.listbox.delete(0, tk.END)
        for entry in self.websites:
            self.listbox.insert(tk.END, entry.get("name", "Unnamed"))

    def clear_details(self):
        self.selected_index = None
        self.name_var.set("")
        self.url_var.set("")
        self.slug_var.set("")
        self.owner_var.set("")
        self.about_text.delete("1.0", tk.END)
        self.name_entry.config(state="normal")
        self.url_entry.config(state="normal")
        self.slug_entry.config(state="normal")
        self.owner_entry.config(state="normal")
        self.about_text.config(state="normal")
        self.save_entry_btn.config(state='disabled')
        self.new_entry_mode = False

    def display_details(self, entry):
        self.name_var.set(entry.get("name", ""))
        self.url_var.set(entry.get("url", ""))
        self.slug_var.set(entry.get("slug", ""))
        self.owner_var.set(entry.get("owner", ""))
        self.about_text.delete("1.0", tk.END)
        self.about_text.insert(tk.END, entry.get("about", ""))

        self.name_entry.config(state="normal")
        self.url_entry.config(state="normal")
        self.slug_entry.config(state="normal")
        self.owner_entry.config(state="normal")
        self.about_text.config(state="normal")
        self.save_entry_btn.config(state='disabled')

    def on_select(self, event):
        selection = self.listbox.curselection()
        if selection:
            self.selected_index = selection[0]
            entry = self.websites[self.selected_index]
            self.display_details(entry)
            self.new_entry_mode = False
        else:
            self.selected_index = None
            self.clear_details()

    def add_website(self):
        self.clear_details()
        self.new_entry_mode = True
        self.save_entry_btn.config(text="Save New", state="normal")
        self.name_entry.focus_set()

    def save_entry(self):
        data = {
            "name": self.name_var.get(),
            "url": self.url_var.get(),
            "slug": self.slug_var.get(),
            "owner": self.owner_var.get(),
            "about": self.about_text.get("1.0", tk.END).strip()
        }
        if not data["url"]:
            messagebox.showwarning("Input error", "Website must have a URL.")
            return
        if self.new_entry_mode:
            self.websites.append(data)
            self.update_listbox()
            self.listbox.select_set(tk.END)
            self.listbox.event_generate('<<ListboxSelect>>')
        elif self.selected_index is not None:
            self.websites[self.selected_index] = data
            self.update_listbox()
            self.listbox.select_set(self.selected_index)
        self.save_entry_btn.config(state='disabled')
        self.new_entry_mode = False

    def delete_website(self):
        if self.selected_index is None:
            messagebox.showwarning("Delete", "No item selected!")
            return
        if messagebox.askyesno("Delete", "Delete this entry?"):
            del self.websites[self.selected_index]
            self.update_listbox()
            self.clear_details()

    def field_modified(self, *args):
        # Enable Save button if not blank fields and an entry is selected or in new mode
        if self.new_entry_mode or self.selected_index is not None:
            self.save_entry_btn.config(state='normal')

    def field_modified_event(self, event):
        self.about_text.edit_modified(0)
        self.field_modified()


if __name__ == "__main__":
    app = WebsiteManagerApp()
    app.mainloop()
