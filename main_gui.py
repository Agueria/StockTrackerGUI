import pymongo
import tkinter as tk
from tkinter.ttk import *
from tkinter import ttk as ttk
from tkinter import messagebox
from tkinter import *
from ttkthemes import themed_tk as theme
from tkinter import filedialog as fd
import pandas as pd
from bson.binary import Binary
from PIL import ImageTk, Image
import io
import matplotlib.pyplot as plt

conn_str = "YOUR_CONNECTION_STRING"
myclient = pymongo.MongoClient(conn_str)
mydb = myclient["YOUR_DB_NAME"]
mycol = mydb["YOUR_COLLECTION_NAME"]

image_col = mydb["images"]
logo_data = image_col.find_one()


class MainWindow:
    def __init__(self):
        self.root = theme.ThemedTk(theme="radiance")
        self.pil_img = Image.open(io.BytesIO(logo_data['data']))
        self.all_data_collection = list(mycol.find())
        self.all_data_df = pd.DataFrame(list(mycol.find()))
        self.all_data_df = self.all_data_df.drop(columns=["_id"])
        
        self.custom_name = tk.StringVar()
        self.custom_group = tk.StringVar()
        self.custom_material = tk.StringVar()
        self.custom_quantity = tk.IntVar()
        self.custom_unit = tk.StringVar()
        self.custom_project = tk.StringVar()
        
        self.new_name = tk.StringVar()
        self.new_group = tk.StringVar()
        self.new_material = tk.StringVar()
        self.new_quantity = tk.IntVar()
        self.new_unit = tk.StringVar()
        self.new_project = tk.StringVar()
        
        self.mat_selection_list = []
        self.group_selection_list = []
        self.project_selection_list = []
        
        # configure tkinter visual properties
        self.config_root()
        self.config_all_tree()
        self.config_selected()
        self.config_saver()
        #self.config_addNew_frame()
        self.config_search()
        s = ttk.Style()
        s.configure('.', font=('Candara', 18))
        s.configure('Treeview', rowheight=40)
        #s.configure('.', background='#2d2d2d')
        #s.configure('.', foreground='#ffffff')
        s.configure('.', )

        # run ui visualisation loop
        self.root.mainloop()
        
    def config_root(self):
        self.root.resizable(True, True)
        self.root.title("Stok Kontrol")
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        self.root.geometry("1540x720")
        self.root.grid_rowconfigure(0, weight=0)
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_rowconfigure(5, weight=0)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(2, weight=1)
        self.root.grid_columnconfigure(4, weight=0)

        
    def config_search(self):
        self.search_frame = ttk.Frame(self.root, padding=10)
        self.search_frame.grid(row=0, column=0, sticky="nsew", columnspan=6, rowspan=1)
        self.search_frame.configure(relief="groove", borderwidth=5)
        
        self.search_frame.columnconfigure(0, weight=1)
        
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(self.search_frame, textvariable=self.search_var)
        search_entry.insert(0, "Aramak istediğiniz kelimeyi giriniz..")
        search_entry.grid(row=0, column=0, padx=5, pady=5, columnspan=3, sticky="nsew")
        search_entry.bind("<FocusIn>", lambda e: search_entry.delete('0', 'end'))
        search_entry.bind("<KeyRelease>", lambda e: self.search())
        search_entry.bind("<BackSpace>", lambda e: self.backspace_pressed())
        
        self.filter_btn = ttk.Button(self.search_frame, text="Filtrele", width=10, command=self.filter_popup)
        self.filter_btn.grid(row=0, column=3, padx=5, pady=5, sticky="nsew", columnspan=1)
        
        reset_filter_btn = ttk.Button(self.search_frame, text="Filtreyi Sıfırla", width=10, command=self.reset_filter)
        reset_filter_btn.grid(row=0, column=4, padx=5, pady=5, sticky="nsew", columnspan=1)
        
        search_btn = ttk.Button(self.search_frame, text="Arama", width=10, command=self.search)
        search_btn.grid(row=0, column=5, padx=5, pady=5, sticky="nsew", columnspan=1)

        
    def reset_filter(self):
        self.curselection_indexes = {
            "material": [],
            "group": [],
            "project": []
        }
        self.mat_selection_list = []
        self.group_selection_list = []
        self.project_selection_list = []
        self.liste.delete(*self.liste.get_children())
        self.config_all_tree()

        
    def filter_popup(self):
        popwin = Toplevel(self.root)
        popwin.title("Filtreleme")
        popwin.geometry("600x300")
        popwin.resizable(False, False)
        popwin.grab_set()
            
        group_label = ttk.Label(popwin, text="Grup(lar):")
        group_label.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        group_listbox = Listbox(popwin, selectmode="multiple", exportselection=0, activestyle="dotbox")
        group_listbox.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
        
        for g in sorted(self.all_data_df["group"].unique()):
            group_listbox.insert(END, g)
            group_listbox.itemconfig(END)
        
        material_label = ttk.Label(popwin, text="Malzeme(ler):")
        material_label.grid(row=0, column=2, padx=5, pady=5, sticky="nsew")
        material_listbox = Listbox(popwin, selectmode="multiple", exportselection=0, activestyle="dotbox")
        material_listbox.grid(row=1, column=2, padx=5, pady=5, sticky="nsew")
        
        for mat in sorted(self.all_data_df["material"].unique()):
            material_listbox.insert(END, mat)
            material_listbox.itemconfig(END)
            
        project_label = ttk.Label(popwin, text="Proje:")
        project_label.grid(row=0, column=4, padx=5, pady=5, sticky="nsew")
        project_listbox = Listbox(popwin, selectmode="multiple", exportselection=0, activestyle="dotbox")
        project_listbox.grid(row=1, column=4, padx=5, pady=5, sticky="nsew")
        
        for q in sorted(self.all_data_df["project"].unique()):
            project_listbox.insert(END, q)
            project_listbox.itemconfig(END)
        
        group_yscrollbar = Scrollbar(popwin, orient="vertical", background='#2d2d2d', command=group_listbox.yview)
        group_yscrollbar.grid(row=1, column=1, padx=5, pady=5, sticky="nsew")
        group_listbox.config(yscrollcommand=group_yscrollbar.set)
        
        mat_yscrollbar = Scrollbar(popwin, orient="vertical", background='#2d2d2d', command=material_listbox.yview)
        mat_yscrollbar.grid(row=1, column=3, padx=5, pady=5, sticky="nsew")
        material_listbox.config(yscrollcommand=mat_yscrollbar.set)
        
        project_yscrollbar = Scrollbar(popwin, orient="vertical", background='#2d2d2d', command=project_listbox.yview)
        project_yscrollbar.grid(row=1, column=5, padx=5, pady=5, sticky="nsew")
        project_listbox.config(yscrollcommand=project_yscrollbar.set)
        
        try:
            for i in self.curselection_indexes["material"]:
                material_listbox.selection_set(i)
            for i in self.curselection_indexes["group"]:
                group_listbox.selection_set(i)
            for i in self.curselection_indexes["project"]:
                project_listbox.selection_set(i)
        except:
            pass
        
        def mat_select():
            self.mat_selection_list.clear()
            for i in material_listbox.curselection():
                self.mat_selection_list.append(material_listbox.get(i))
                
        def g_select():
            self.group_selection_list.clear()
            for i in group_listbox.curselection():
                self.group_selection_list.append(group_listbox.get(i))
        
        def p_select():
            self.project_selection_list.clear()
            for i in project_listbox.curselection():
                self.project_selection_list.append(project_listbox.get(i))
                
        material_listbox.bind("<<ListboxSelect>>", lambda x: mat_select())
        group_listbox.bind("<<ListboxSelect>>", lambda x: g_select())
        project_listbox.bind("<<ListboxSelect>>", lambda x: p_select())
        
        self.seleciton_query = {}
        
        def filter():
            self.seleciton_query.clear()
            self.seleciton_query = {
                "material": {"$in": self.mat_selection_list},
                "group": {"$in": self.group_selection_list},
                "project": {"$in": self.project_selection_list}
            }
            
            self.curselection_indexes = {
                "material": material_listbox.curselection(),
                "group": group_listbox.curselection(),
                "project": project_listbox.curselection()
            }
            
            if self.mat_selection_list == []:
                del self.seleciton_query["material"]
            if self.group_selection_list == []:
                del self.seleciton_query["group"]
            if self.project_selection_list == []:
                del self.seleciton_query["project"]
            
            self.liste.delete(*self.liste.get_children())
            querried_data = list(mycol.find(self.seleciton_query))
            for i in querried_data:
                self.liste.insert(parent='', index='end', values=(i["name"], i["group"], i["material"], i["quantity"], i["unit"], i["project"]))
            popwin.destroy()
        
        apply_filter_btn = ttk.Button(popwin, text="Filtrele", command=filter)
        apply_filter_btn.grid(row=2, column=0, padx=5, pady=5, sticky="nsew", columnspan=6)

           
    def config_all_tree(self):
        self.treeFrame = ttk.Frame(self.root)
        self.treeFrame.grid(row=1, column=0, columnspan=6, rowspan=4, sticky="nsew")
        self.treeFrame.columnconfigure(0, weight=1)
        self.treeFrame.rowconfigure(0, weight=1)
        self.liste = ttk.Treeview(self.treeFrame, height=10, show="headings")
        self.liste.bind("<Double-1>", self.selectedItem_fromTree)
        self.liste.grid(row=0, column=0, columnspan=6, rowspan=4, sticky="nsew")
        self.liste["columns"] = ("name", "group", "material", "quantity", 'unit', 'project')
        self.liste.column('#0', minwidth=0, stretch=True)
        self.liste.column('name', minwidth=400, anchor=CENTER, stretch=True)
        self.liste.column('group', anchor=CENTER, minwidth=100, stretch=True)
        self.liste.column('material', anchor=CENTER, minwidth=100, stretch=True)
        self.liste.column('quantity', anchor=CENTER, width=60, stretch=True)
        self.liste.column('unit', anchor=CENTER, width=60, stretch=True)
        self.liste.column('project', anchor=CENTER, minwidth=100, stretch=True)


        self.liste.heading("#0", text="")
        self.liste.heading("name", text="Ürün Adı", command=lambda: self.treeview_sort_column(self.liste, "name", False))
        self.liste.heading("group", text="Ürün Grubu", command=lambda: self.treeview_sort_column(self.liste, "group", False))
        self.liste.heading("material", text="Malzeme", command=lambda: self.treeview_sort_column(self.liste, "material", False))
        self.liste.heading("quantity", text="Miktar", command=lambda: self.treeview_sort_column(self.liste, "quantity", False))
        self.liste.heading("unit", text="Birim", command=lambda: self.treeview_sort_column(self.liste, "unit", False))
        self.liste.heading("project", text="Proje", command=lambda: self.treeview_sort_column(self.liste, "project", False))
        
        custom_style = ttk.Style()
        custom_style.configure("Custom.Treeview", rowheight=30)  # Satır yüksekliğini 30 piksel olarak ayarlayın
        self.liste["style"] = "Custom.Treeview"
        
        try:
            for i in self.all_data_collection:
                self.liste.insert(parent='', index='end', values=(i["name"], i["group"], i["material"], i["quantity"], i["unit"], i["project"]))
        except:
            pass
        
        vsb = tk.Scrollbar(self.treeFrame, orient="vertical", command=self.liste.yview)
        self.liste.configure(yscrollcommand=vsb.set)
        vsb.place(relx=1, rely=0, relheight=1, anchor='ne')

        
    def selectedItem_fromTree(self, event):
        curItem = self.liste.focus()
        item_val_list = list(self.liste.item(curItem).values())[2]
        try:
            self.custom_name.set(item_val_list[0])
            self.custom_group.set(item_val_list[1])
            self.custom_material.set(item_val_list[2])
            self.custom_quantity.set(item_val_list[3])
            self.custom_unit.set(item_val_list[4])
            self.custom_project.set(item_val_list[5])
            self.config_selected()
        except:
            pass
        return item_val_list

        
    def config_selected(self):
        self.selected_frame = ttk.Frame(self.root, padding=20)
        self.selected_frame.grid(row=5, column=0, sticky="nsew", columnspan=2, rowspan=2)
        self.selected_frame.columnconfigure(0, weight=0)
        self.selected_frame.rowconfigure(0, weight=1)
        self.selected_frame.rowconfigure(1, weight=1)
        self.selected_frame.rowconfigure(2, weight=1)
        self.selected_frame.rowconfigure(3, weight=1)
        self.selected_frame.rowconfigure(4, weight=1)
        self.selected_frame.rowconfigure(5, weight=1)
        self.selected_frame.rowconfigure(6, weight=1)
        self.selected_frame.configure(relief="groove", borderwidth=5)
        
        
        slct_lbl = ttk.Label(self.selected_frame, text="Seçili Ürün: ")
        slct_lbl.grid(row=0, column=0, sticky="nswe", columnspan=2, padx=5, pady=5)
        
        custom_name_lbl = ttk.Label(self.selected_frame, text="Ürün Adı: ")
        custom_name_lbl.grid(row=1, column=0, sticky="sew", padx=5, pady=5)
        self.custom_name_entry = ttk.Entry(self.selected_frame, textvariable=self.custom_name)
        self.custom_name_entry.grid(row=1, column=1, sticky="sew", padx=5, pady=5)
        
        custom_group_lbl = ttk.Label(self.selected_frame, text="Ürün Grubu: ")
        custom_group_lbl.grid(row=2, column=0, sticky="sew", padx=5, pady=5)
        self.custom_group_entry = ttk.Entry(self.selected_frame, textvariable=self.custom_group)
        self.custom_group_entry.grid(row=2, column=1, sticky="sew", padx=5, pady=5)
        
        custom_material_lbl = ttk.Label(self.selected_frame, text="Malzeme: ")
        custom_material_lbl.grid(row=3, column=0, sticky="sew", padx=5, pady=5)
        self.custom_material_entry = ttk.Entry(self.selected_frame, textvariable=self.custom_material)
        self.custom_material_entry.grid(row=3, column=1, sticky="sew", padx=5, pady=5)
        
        custom_quantity_lbl = ttk.Label(self.selected_frame, text="Miktar: ")
        custom_quantity_lbl.grid(row=4, column=0, sticky="sew", padx=5, pady=5)
        self.custom_quantity_entry = ttk.Entry(self.selected_frame, textvariable=self.custom_quantity)
        self.custom_quantity_entry.grid(row=4, column=1, sticky="sew", padx=5, pady=5)
        
        custom_unit_lbl = ttk.Label(self.selected_frame, text="Birim: ")
        custom_unit_lbl.grid(row=5, column=0, sticky="sew", padx=5, pady=5)
        self.custom_unit_entry = ttk.Entry(self.selected_frame, textvariable=self.custom_unit)
        self.custom_unit_entry.grid(row=5, column=1, sticky="sew", padx=5, pady=5)
        
        custom_project_lbl = ttk.Label(self.selected_frame, text="Proje: ")
        custom_project_lbl.grid(row=6, column=0, sticky="sew", padx=5, pady=5)
        self.custom_project_entry = ttk.Entry(self.selected_frame, textvariable=self.custom_project)
        self.custom_project_entry.grid(row=6, column=1, sticky="sew", padx=5, pady=5)
        
        delete_btn = ttk.Button(self.selected_frame, text="Sil", command=self.delete_item)
        delete_btn.grid(row=7, column=0, sticky="sew", padx=3, pady=3, columnspan=1)
        
        update_btn = ttk.Button(self.selected_frame, text="Güncelle", command=self.update_item)
        update_btn.grid(row=7, column=1, sticky="sew", padx=3, pady=3, columnspan=1)
        
        self.new_item_frame = ttk.Frame(self.root, padding=20)
        self.new_item_frame.grid(row=5, column=2, sticky="nsew", columnspan=2, rowspan=5)
        self.new_item_frame.columnconfigure(0, weight=0)
        self.new_item_frame.rowconfigure(0, weight=1)
        self.new_item_frame.rowconfigure(1, weight=1)
        self.new_item_frame.rowconfigure(2, weight=1)
        self.new_item_frame.rowconfigure(3, weight=1)
        self.new_item_frame.rowconfigure(4, weight=1)
        self.new_item_frame.rowconfigure(5, weight=1)
        self.new_item_frame.rowconfigure(6, weight=1)
        self.new_item_frame.configure(relief="groove", borderwidth=5)
                
        new_item_lbl = ttk.Label(self.new_item_frame, text="Yeni Ürün: ")
        new_item_lbl.grid(row=0, column=0, sticky="nswe", columnspan=2, padx=5, pady=5)
        
        new_name_lbl = ttk.Label(self.new_item_frame, text="Ürün Adı: ")
        new_name_lbl.grid(row=1, column=0, sticky="sew", padx=5, pady=5)
        self.new_name_entry = ttk.Entry(self.new_item_frame, textvariable=self.new_name)
        self.new_name_entry.grid(row=1, column=1, sticky="sew", padx=5, pady=5)
        
        new_group_lbl = ttk.Label(self.new_item_frame, text="Ürün Grubu: ")
        new_group_lbl.grid(row=2, column=0, sticky="sew", padx=5, pady=5)
        self.new_group_entry = ttk.Entry(self.new_item_frame, textvariable=self.new_group)
        self.new_group_entry.grid(row=2, column=1, sticky="sew", padx=5, pady=5)
        
        new_material_lbl = ttk.Label(self.new_item_frame, text="Malzeme: ")
        new_material_lbl.grid(row=3, column=0, sticky="sew", padx=5, pady=5)
        self.new_material_entry = ttk.Entry(self.new_item_frame, textvariable=self.new_material)
        self.new_material_entry.grid(row=3, column=1, sticky="sew", padx=5, pady=5)
        
        new_quantity_lbl = ttk.Label(self.new_item_frame, text="Miktar: ")
        new_quantity_lbl.grid(row=4, column=0, sticky="sew", padx=5, pady=5)
        self.new_quantity_entry = ttk.Entry(self.new_item_frame, textvariable=self.new_quantity)
        self.new_quantity_entry.grid(row=4, column=1, sticky="sew", padx=5, pady=5)
        
        new_unit_lbl = ttk.Label(self.new_item_frame, text="Birim: ")
        new_unit_lbl.grid(row=5, column=0, sticky="sew", padx=5, pady=5)
        self.new_unit_entry = ttk.Entry(self.new_item_frame, textvariable=self.new_unit)
        self.new_unit_entry.grid(row=5, column=1, sticky="sew", padx=5, pady=5)
        
        new_project_lbl = ttk.Label(self.new_item_frame, text="Proje: ")
        new_project_lbl.grid(row=6, column=0, sticky="sew", padx=5, pady=5)
        self.new_project_entry = ttk.Entry(self.new_item_frame, textvariable=self.new_project)
        self.new_project_entry.grid(row=6, column=1, sticky="sew", padx=5, pady=5)
        
        addNew_btn = ttk.Button(self.new_item_frame, text="Yeni Ürün Ekle", command=self.add_new_item)
        addNew_btn.grid(row=7, column=0, sticky="nsew", padx=2, pady=2, columnspan=2)

        
    def config_saver(self):
        self.save_frame = ttk.Frame(self.root, padding=20)
        self.save_frame.grid(row=5, column=4, sticky="nsew", columnspan=2, rowspan=2)
        self.save_frame.configure(relief="groove", borderwidth=5)
        self.save_frame.rowconfigure(0, weight=1)
        
        self.logo_frame = ttk.Frame(self.save_frame, padding=10)
        self.logo_frame.grid(row=0, column=0, sticky="n", columnspan=2, rowspan=1)
        self.logo_frame.columnconfigure(0, weight=0)
        
        im_width, im_height = self.logo_frame.winfo_width(), self.logo_frame.winfo_height()
        print(im_width, im_height)
        
        image = Image.open(io.BytesIO(logo_data['data']))
        
        image = image.resize((550, 160))
        
        photo = ImageTk.PhotoImage(image)

        label = Label(self.logo_frame, image = photo)
        label.image = photo
        label.grid(row=0)

        
        
        save_btn = ttk.Button(self.save_frame, text="Excel dosyası olarak dışa aktar (.xlsx)", command=self.save_to_file)
        save_btn.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)

        
    def save_to_file(self):
        final_df  = pd.DataFrame(list(mycol.find()))
        final_df = final_df.drop(columns=["_id"])
        file = fd.asksaveasfilename(defaultextension=".xlsx")
        final_df.to_excel(file, index=False)


    def treeview_sort_column(self, treeview: ttk.Treeview, col, reverse: bool):
        """
        to sort the table by column when clicking in column
        """
        try:
            data_list = [
                (int(treeview.set(k, col)), k) for k in treeview.get_children("")
            ]
        except Exception:
            data_list = [(treeview.set(k, col), k) for k in treeview.get_children("")]

        data_list.sort(reverse=reverse)

        # rearrange items in sorted positions
        for index, (val, k) in enumerate(data_list):
            treeview.move(k, "", index)

        bool_str_modificator = {True: "▼", False: "▲"}
        
        if col == "name":
            text_temp = "Ürün Adı " + bool_str_modificator[reverse]
        elif col == "group":
            text_temp = "Ürün Grubu " + bool_str_modificator[reverse]
        elif col == "material":
            text_temp = "Malzeme " + bool_str_modificator[reverse]
        elif col == "quantity":
            text_temp = "Miktar " + bool_str_modificator[reverse]
        elif col == "unit":
            text_temp = "Birim " + bool_str_modificator[reverse]
        elif col == "project":
            text_temp = "Proje " + bool_str_modificator[reverse]
        
        # reverse sort next time
        self.liste.heading("name", text="Ürün Adı", command=lambda: self.treeview_sort_column(self.liste, "name", False))
        self.liste.heading("group", text="Ürün Grubu", command=lambda: self.treeview_sort_column(self.liste, "group", False))
        self.liste.heading("material", text="Malzeme", command=lambda: self.treeview_sort_column(self.liste, "material", False))
        self.liste.heading("quantity", text="Miktar", command=lambda: self.treeview_sort_column(self.liste, "quantity", False))
        self.liste.heading("unit", text="Birim", command=lambda: self.treeview_sort_column(self.liste, "unit", False))
        self.liste.heading("project", text="Proje", command=lambda: self.treeview_sort_column(self.liste, "project", False))
        treeview.heading(col, text=text_temp, command=lambda: self.treeview_sort_column(treeview, col, not reverse))

  
    def search(self):
        self.reset_filter()
        s_query = self.search_var.get()
        selections = []
        container = False
        for child in self.liste.get_children():
            for value in self.liste.item(child)['values']:
                if str(s_query).lower() in str(value).lower():   
                    container = True
                    break
                else:
                    pass
            if not container:
                    self.liste.delete(child)
            container = False

    
    def backspace_pressed(self):
        self.reset_filter()
        s_query = self.search_var.get()[:-1]
        selections = []
        container = False
        for child in self.liste.get_children():
            for value in self.liste.item(child)['values']:
                if str(s_query).lower() in str(value).lower():   
                    container = True
                    break
                else:
                    pass
            if not container:
                    self.liste.delete(child)
            container = False
        print('search completed')

    
    def add_new_item(self):
        new_item = {
            "name": self.new_name.get(),
            "group": self.new_group.get(),
            "material": self.new_material.get(),
            "quantity": self.new_quantity.get(),
            "unit": self.new_unit.get(),
            "project": self.new_project.get()
        }
        self.liste.insert(parent='', index='end', values=(new_item["name"], new_item["group"], new_item["material"], new_item["quantity"], new_item["unit"], new_item["project"]))
        mycol.insert_one(new_item)

    
    def update_item(self):
        curItem = self.liste.focus()
        item_val_list = list(self.liste.item(curItem).values())[2]
        
        self.liste.insert(parent='', index=str(curItem)[1:], values=(self.custom_name.get(), self.custom_group.get(), self.custom_material.get(), self.custom_quantity.get(), self.custom_unit.get(), self.custom_project.get()))
        self.liste.delete(curItem)
        
        up_query = {
            "name": item_val_list[0],
            "group": item_val_list[1],
            "material": item_val_list[2],
            "quantity": item_val_list[3],
            "unit": item_val_list[4],
            "project": item_val_list[5]
        }
    
        mycol.update_one(up_query, {"$set": {
                                                "name": self.custom_name.get(),
                                                "group": self.custom_group.get(),
                                                "material": self.custom_material.get(),
                                                "quantity": self.custom_quantity.get(),
                                                "unit": self.custom_unit.get(),
                                                "project": self.custom_project.get()
                                            }})

    
    def delete_item(self):
        curItem = self.liste.focus()
        item_val_list = list(self.liste.item(curItem).values())[2]
        
        del_query = {
            "name": item_val_list[0],
            "group": item_val_list[1],
            "material": item_val_list[2],
            "quantity": item_val_list[3],
            "unit": item_val_list[4],
            "project": item_val_list[5]
        }
        
        mycol.delete_one(del_query)
        self.liste.delete(curItem)

          
if __name__ == "__main__":
    show = MainWindow()
    