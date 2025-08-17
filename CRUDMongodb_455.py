import tkinter as tk
from tkinter import messagebox
from pymongo import MongoClient

# ----------------- MongoDB Connection -----------------
client = MongoClient("mongodb://localhost:27017/")
db = client["gym_database"]
collection = db["members"]

# ----------------- Colors & Styles -----------------
BG_COLOR = "#2c3e50"
FG_COLOR = "#ecf0f1"
BTN_COLOR = "#27ae60"
BTN_HOVER = "#219150"
ENTRY_BG = "#34495e"
FONT = ("Segoe UI", 10)

# ----------------- Functions -----------------
def create_member():
    member = get_form_data()
    if not all(member.values()):
        messagebox.showerror("Error", "All fields are required.")
        return
    if collection.find_one({"member_id": member["member_id"]}):
        messagebox.showerror("Error", "Member with this ID already exists.")
        return
    try:
        member["age"] = int(member["age"])
    except ValueError:
        messagebox.showerror("Error", "Age must be a number.")
        return

    collection.insert_one(member)
    messagebox.showinfo("Success", "Member added successfully!")
    clear_entries()
    read_members()

def read_members():
    listbox.delete(0, tk.END)
    for member in collection.find():
        member_id = member.get("member_id", "N/A")
        name = member.get("name", "N/A")
        age = member.get("age", "N/A")
        contact = member.get("contact", "N/A")
        membership = member.get("membership", "N/A")  # FIXED

        listbox.insert(
            tk.END,
            f"{member_id} | {name} | Age: {age} | Contact: {contact} | {membership}"
        )

def update_member():
    member_id = entry_id.get()
    if not member_id:
        messagebox.showerror("Error", "Member ID is required for update.")
        return

    updated = get_form_data()
    try:
        updated["age"] = int(updated["age"])
    except ValueError:
        messagebox.showerror("Error", "Age must be a number.")
        return

    result = collection.update_one({"member_id": member_id}, {"$set": updated})
    if result.modified_count > 0:
        messagebox.showinfo("Success", "Member updated successfully!")
    else:
        messagebox.showwarning("Warning", "No changes made or Member not found.")
    clear_entries()
    read_members()

def delete_member():
    member_id = entry_id.get()
    if not member_id:
        messagebox.showerror("Error", "Member ID is required for deletion.")
        return
    result = collection.delete_one({"member_id": member_id})
    if result.deleted_count > 0:
        messagebox.showinfo("Success", "Member deleted successfully!")
    else:
        messagebox.showwarning("Warning", "Member not found.")
    clear_entries()
    read_members()

def clear_entries():
    for entry in (entry_id, entry_name, entry_age, entry_contact):
        entry.delete(0, tk.END)
    membership_var.set("1 Month")  # Reset dropdown

def get_form_data():
    return {
        "member_id": entry_id.get().strip(),
        "name": entry_name.get().strip(),
        "age": entry_age.get().strip(),
        "contact": entry_contact.get().strip(),
        "membership": membership_var.get().strip()
    }

def on_listbox_select(event):
    selection = listbox.curselection()
    if selection:
        index = selection[0]
        data = listbox.get(index).split(" | ")
        clear_entries()
        entry_id.insert(0, data[0])
        entry_name.insert(0, data[1])
        entry_age.insert(0, data[2].replace("Age: ", ""))
        entry_contact.insert(0, data[3].replace("Contact: ", ""))
        membership_var.set(data[4])

# ----------------- UI Setup -----------------
root = tk.Tk()
root.title("Gym Membership Management")
root.geometry("700x600")
root.config(bg=BG_COLOR)

# Top label
top_label = tk.Label(root, text="Gym Membership Management", bg=BG_COLOR, fg=FG_COLOR, font=("Segoe UI", 14, "bold"))
top_label.pack(anchor="center", pady=10)

# Form Frame
form_frame = tk.Frame(root, bg=BG_COLOR)
form_frame.pack(anchor="w", padx=20)

def create_label_entry(text):
    label = tk.Label(form_frame, text=text, bg=BG_COLOR, fg=FG_COLOR, font=FONT)
    label.pack(anchor="w")
    entry = tk.Entry(form_frame, bg=ENTRY_BG, fg=FG_COLOR, insertbackground="white", font=FONT, width=30)
    entry.pack(anchor="w", pady=4, ipady=3, ipadx=5)
    return entry

entry_id = create_label_entry("Member ID")
entry_name = create_label_entry("Member Name")
entry_age = create_label_entry("Age")
entry_contact = create_label_entry("Contact")

# Dropdown for Membership Type
label = tk.Label(form_frame, text="Membership Type", bg=BG_COLOR, fg=FG_COLOR, font=FONT)
label.pack(anchor="w")
membership_var = tk.StringVar(value="1 Month")
membership_options = ["1 Month", "3 Months", "6 Months", "1 Year"]
membership_menu = tk.OptionMenu(form_frame, membership_var, *membership_options)
membership_menu.config(bg=ENTRY_BG, fg=FG_COLOR, width=28)
membership_menu.pack(anchor="w", pady=4)

# Button Frame
btn_frame = tk.Frame(root, bg=BG_COLOR)
btn_frame.pack(anchor="w", padx=20, pady=10)

def create_button(text, command, color=BTN_COLOR):
    btn = tk.Button(btn_frame, text=text, command=command, bg=color, fg="white",
                    activebackground=BTN_HOVER, font=FONT, width=12)
    btn.pack(side=tk.LEFT, padx=5)
    return btn

create_button("Add", create_member)
create_button("View", read_members)
create_button("Update", update_member)
create_button("Delete", delete_member)
create_button("Clear", clear_entries, "#e74c3c")

# Listbox
listbox = tk.Listbox(root, width=90, height=15, bg=ENTRY_BG, fg=FG_COLOR,
                     font=FONT, selectbackground="#5555aa")
listbox.pack(padx=20, pady=10)
listbox.bind("<<ListboxSelect>>", on_listbox_select)

# Initial Load
read_members()

root.mainloop()
