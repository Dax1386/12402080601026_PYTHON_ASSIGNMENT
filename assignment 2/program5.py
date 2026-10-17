"""Q5: Tkinter contact manager backed by MySQL. Requires mysql-connector-python.
Creates Contact table on startup; searches by name/email/phone and supports CRUD.
"""
import re, tkinter as tk
import importlib
from tkinter import ttk, messagebox, simpledialog
try:
    mysql_connector = importlib.import_module("mysql.connector")
    Error = mysql_connector.Error
except ImportError:
    mysql_connector = None
    Error = Exception
EMAIL_RE = re.compile(r"^[A-Za-z0-9._+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")
class ContactManager:
    def __init__(self, root):
        self.root=root; root.title("Contact Manager")
        host=simpledialog.askstring("Database", "MySQL host", initialvalue="localhost")
        user=simpledialog.askstring("Database", "MySQL user")
        password=simpledialog.askstring("Database", "MySQL password", show="*")
        database=simpledialog.askstring("Database", "Database name")
        if mysql_connector is None:
            messagebox.showerror("Missing dependency", "Install mysql-connector-python to use the contact manager.")
            root.destroy(); return
        try:
            self.db=mysql_connector.connect(host=host or "localhost",user=user,password=password,database=database)
            cur=self.db.cursor(); cur.execute("CREATE TABLE IF NOT EXISTS Contact (id INT AUTO_INCREMENT PRIMARY KEY,name VARCHAR(200) NOT NULL,email VARCHAR(254) NOT NULL UNIQUE,phone VARCHAR(40),category VARCHAR(80),notes TEXT, INDEX idx_name(name), INDEX idx_phone(phone)) ENGINE=InnoDB"); self.db.commit(); cur.close()
        except Error as exc: messagebox.showerror("Database error",str(exc)); root.destroy(); return
        self.vars={k:tk.StringVar() for k in ("name","email","phone","category","search")}
        self.search_field=tk.StringVar(value="all")
        menu=tk.Menu(root); actions=tk.Menu(menu,tearoff=False); actions.add_command(label="Clear form",command=self.clear); actions.add_command(label="Exit",command=self.close); menu.add_cascade(label="Contacts",menu=actions); root.config(menu=menu)
        form=ttk.Frame(root,padding=8); form.pack(fill="x")
        for i,(label,key) in enumerate((("Name","name"),("Email","email"),("Phone","phone"))):
            ttk.Label(form,text=label).grid(row=i,column=0,sticky="w"); ttk.Entry(form,textvariable=self.vars[key],width=38).grid(row=i,column=1,sticky="ew")
        ttk.Label(form,text="Category").grid(row=3,column=0,sticky="w"); ttk.Combobox(form,textvariable=self.vars["category"],values=("Personal","Family","Friend","Faculty","Work","Other"),state="normal",width=35).grid(row=3,column=1,sticky="ew")
        ttk.Label(form,text="Notes").grid(row=4,column=0,sticky="nw"); self.notes=tk.Text(form,width=38,height=3); self.notes.grid(row=4,column=1)
        buttons=ttk.Frame(root); buttons.pack(fill="x",padx=8)
        for text,cmd in (("Add",self.add),("Update",self.update),("Delete",self.delete),("Clear",self.clear)): ttk.Button(buttons,text=text,command=cmd).pack(side="left",padx=3)
        search=ttk.Frame(root,padding=8); search.pack(fill="x"); ttk.Entry(search,textvariable=self.vars["search"]).pack(side="left",fill="x",expand=True)
        for label,value in (("All","all"),("Name","name"),("Email","email"),("Phone","phone")): ttk.Radiobutton(search,text=label,value=value,variable=self.search_field).pack(side="left")
        ttk.Button(search,text="Search",command=self.refresh).pack(side="left"); ttk.Button(search,text="Show all",command=lambda:self.refresh(True)).pack(side="left")
        self.tree=ttk.Treeview(root,columns=("id","name","email","phone","category"),show="headings",height=14)
        for col in self.tree["columns"]: self.tree.heading(col,text=col.title()); self.tree.column(col,width=130)
        self.tree.pack(fill="both",expand=True,padx=8,pady=8); self.tree.bind("<<TreeviewSelect>>",self.select)
        root.protocol("WM_DELETE_WINDOW",self.close); self.refresh(True)
    def values(self):
        name=self.vars["name"].get().strip(); email=self.vars["email"].get().strip(); phone=self.vars["phone"].get().strip(); category=self.vars["category"].get().strip(); notes=self.notes.get("1.0","end").strip()
        if not name or not EMAIL_RE.fullmatch(email): raise ValueError("Name is required and email must be valid.")
        return name,email,phone,category,notes
    def add(self):
        try:
            vals=self.values(); cur=self.db.cursor(); cur.execute("INSERT INTO Contact(name,email,phone,category,notes) VALUES(%s,%s,%s,%s,%s)",vals); self.db.commit(); cur.close(); self.refresh(True); self.clear()
        except (ValueError,Error) as e: messagebox.showerror("Cannot add contact",str(e))
    def update(self):
        sel=self.tree.selection()
        if not sel: return messagebox.showinfo("Select", "Select a contact first.")
        try:
            vals=self.values(); ident=self.tree.item(sel[0])["values"][0]; cur=self.db.cursor(); cur.execute("UPDATE Contact SET name=%s,email=%s,phone=%s,category=%s,notes=%s WHERE id=%s",(*vals,ident)); self.db.commit(); cur.close(); self.refresh(True)
        except (ValueError,Error) as e: messagebox.showerror("Cannot update contact",str(e))
    def delete(self):
        sel=self.tree.selection()
        if sel and messagebox.askyesno("Delete", "Delete selected contact?"):
            cur=self.db.cursor(); cur.execute("DELETE FROM Contact WHERE id=%s",(self.tree.item(sel[0])["values"][0],)); self.db.commit(); cur.close(); self.refresh(True); self.clear()
    def refresh(self, all_rows=False):
        for item in self.tree.get_children(): self.tree.delete(item)
        term=self.vars["search"].get().strip()
        cur=self.db.cursor()
        if term and not all_rows:
            fields={"all":("name","email","phone"),"name":("name",),"email":("email",),"phone":("phone",)}[self.search_field.get()]
            where=" OR ".join(f"{field} LIKE %s" for field in fields)
            cur.execute(f"SELECT id,name,email,phone,category FROM Contact WHERE {where} ORDER BY name",tuple(f"%{term}%" for _ in fields))
        else: cur.execute("SELECT id,name,email,phone,category FROM Contact ORDER BY name")
        for row in cur: self.tree.insert("","end",values=row)
        cur.close()
    def select(self,_event):
        sel=self.tree.selection()
        if not sel:return
        ident=self.tree.item(sel[0])["values"][0]; cur=self.db.cursor(); cur.execute("SELECT name,email,phone,category,notes FROM Contact WHERE id=%s",(ident,)); row=cur.fetchone(); cur.close()
        if row:
            for key,value in zip(("name","email","phone","category"),row[:4]): self.vars[key].set(value or "")
            self.notes.delete("1.0","end"); self.notes.insert("1.0",row[4] or "")
    def clear(self):
        for key in ("name","email","phone","category"): self.vars[key].set("")
        self.notes.delete("1.0","end")
    def close(self): self.db.close(); self.root.destroy()
if __name__=="__main__":
    root=tk.Tk(); ContactManager(root); root.mainloop()
