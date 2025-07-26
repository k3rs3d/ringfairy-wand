import tkinter as tk
from tkinter import messagebox
import subprocess
import json
import os

FILENAME = "websites.json" # TODO: allow user to choose which file to load
GENERATOR_BINARY = "./ringfairy"  # path to ringfairy binary

DEFAULT_CONFIG = {
    "output": "",
    "assets": "",
    "templates": "",
    "url": "",
    "name": "",
    "description": "",
    "maintainer": "",
    "website": "",
    "shuffle": False,
    "verbose": False,
    "skip_minification": False,
    "skip_verification": False,
    "dry_run": False,
    "audit": False,
    "audit_retries_max": "",
    "audit_retries_delay": "",
    "client_user_agent": "",
    "client_header": ""
}

class WebsiteManagerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Website Manager")
        self.geometry("600x400")

        self.websites = []
        self.selected_index = None
        self.new_entry_mode = False 
        self.generator_config = dict(DEFAULT_CONFIG)

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

        tk.Button(btn_frame, text="Settings...", command=self.edit_settings).pack(fill=tk.X, pady=(20,0))
        tk.Button(btn_frame, text="Generate Webring", command=self.generate_webring).pack(fill=tk.X)

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

    def edit_settings(self):
        config = self.generator_config
        dialog = tk.Toplevel(self)
        dialog.title("Generator Settings")
        fields = [
            ("Output folder", "output"),
            ("Assets folder", "assets"),
            ("Templates folder", "templates"),
            ("Base URL", "url"),
            ("Webring name", "name"),
            ("Description", "description"),
            ("Maintainer", "maintainer"),
            ("Maintainer website", "website"),
            ("Audit Max Retries", "audit_retries_max"),
            ("Audit Retries Delay (ms)", "audit_retries_delay"),
            ("Client User-Agent", "client_user_agent"),
            ("Client Header", "client_header")
        ]
        entries = {}
        for i, (label, key) in enumerate(fields):
            tk.Label(dialog, text=label+":").grid(row=i, column=0, sticky="e")
            entry = tk.Entry(dialog, width=40)
            entry.insert(0, config.get(key, ""))
            entry.grid(row=i, column=1)
            entries[key] = entry
        i = len(fields)

        # Checkboxes for booleans
        var_shuffle = tk.BooleanVar(value=config.get("shuffle", False))
        var_verbose = tk.BooleanVar(value=config.get("verbose", False))
        var_skip_min = tk.BooleanVar(value=config.get("skip_minification", False))
        var_skip_ver = tk.BooleanVar(value=config.get("skip_verification", False))
        var_dry_run   = tk.BooleanVar(value=config.get("dry_run", False))
        var_audit     = tk.BooleanVar(value=config.get("audit", False))

        tk.Checkbutton(dialog, text="Shuffle", variable=var_shuffle).grid(row=i, column=0, sticky="w")
        tk.Checkbutton(dialog, text="Verbose logging", variable=var_verbose).grid(row=i, column=1, sticky="w")
        i+=1
        tk.Checkbutton(dialog, text="Skip Minification", variable=var_skip_min).grid(row=i, column=0, sticky="w")
        tk.Checkbutton(dialog, text="Skip Verification", variable=var_skip_ver).grid(row=i, column=1, sticky="w")
        i += 1
        tk.Checkbutton(dialog, text="Dry Run (no files)", variable=var_dry_run).grid(row=i, column=0, sticky="w")
        tk.Checkbutton(dialog, text="Audit (scrape and check links)", variable=var_audit).grid(row=i, column=1, sticky="w")
        i += 1

        def save_config():
            for key, entry in entries.items():
                config[key] = entry.get()
            config["shuffle"]           = var_shuffle.get()
            config["verbose"]           = var_verbose.get()
            config["skip_minification"] = var_skip_min.get()
            config["skip_verification"] = var_skip_ver.get()
            config["dry_run"]           = var_dry_run.get()
            config["audit"]             = var_audit.get()
            dialog.destroy()

        tk.Button(dialog, text="Save", command=save_config).grid(row=i, column=0, columnspan=2, pady=10)


    # Call as subprocess
    def generate_webring(self):
        self.save_data() # Save list before generating
        args = [GENERATOR_BINARY]
        c = self.generator_config

        args += ["-l", FILENAME]
        if c.get("output"):   args += ["-o", c["output"]]
        if c.get("assets"):   args += ["-a", c["assets"]]
        if c.get("templates"):args += ["-t", c["templates"]]
        if c.get("url"):      args += ["-u", c["url"]]
        if c.get("name"):     args += ["-n", c["name"]]
        if c.get("description"): args += ["-d", c["description"]]
        if c.get("maintainer"):  args += ["-m", c["maintainer"]]
        if c.get("website"):     args += ["-w", c["website"]]
        if c.get("audit_retries_max"):
            args += ["-M", str(c["audit_retries_max"])]
        if c.get("audit_retries_delay"):
            args += ["-D", str(c["audit_retries_delay"])]
        if c.get("client_user_agent"):
            args += ["-U", str(c["client_user_agent"])]
        if c.get("client_header"):
            args += ["-H", str(c["client_header"])]

        # toggles
        if c.get("shuffle"):            args.append("-s")
        if c.get("verbose"):            args.append("-v")
        if c.get("skip_minification"):  args.append("--skip-minification")
        if c.get("skip_verification"):  args.append("--skip-verification")
        if c.get("dry_run"):            args.append("--dry-run")
        if c.get("audit"):              args.append("-A")

        # run!
        try:
            res = subprocess.run(args, capture_output=True, text=True, check=True)
            output = res.stdout + "\n" + res.stderr
            messagebox.showinfo("Generator output", output if output.strip() else "Generation complete (no output).")
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Generator failed", e.stdout + "\n" + e.stderr)


if __name__ == "__main__":
    app = WebsiteManagerApp()
    app.mainloop()
