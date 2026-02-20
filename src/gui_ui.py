"""
Illumio Rule Scheduler — Tkinter GUI (Dark Theme, Zero Dependencies)
"""
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import threading
import re
from src.core import truncate, extract_id

# ==========================================
# Color Palette
# ==========================================
BG_DARK   = "#1a1a2e"
BG_PANEL  = "#16213e"
BG_CARD   = "#0f3460"
BG_INPUT  = "#1a1a3e"
FG_TEXT   = "#e0e0e0"
FG_DIM    = "#8899aa"
FG_ACCENT = "#00d2ff"
FG_GREEN  = "#00e676"
FG_RED    = "#ff5252"
FG_GOLD   = "#ffd740"
BTN_BG    = "#0f3460"
BTN_HOVER = "#1a5276"
BTN_ACCENT = "#00b4d8"

class IllumioGUI:
    def __init__(self, root, core_system):
        self.root = root
        self.root.title("Illumio Rule Scheduler")
        self.root.geometry("1100x750")
        self.root.minsize(900, 650)
        self.root.configure(bg=BG_DARK)
        
        self.cfg = core_system['cfg']
        self.db = core_system['db']
        self.pce = core_system['pce']
        self.engine = core_system['engine']
        
        self._setup_styles()
        self._build_ui()
        self.root.after(200, self._initial_load)

    # ==========================
    # Styles
    # ==========================
    def _setup_styles(self):
        s = ttk.Style()
        s.theme_use('clam')

        # Notebook (Tabs)
        s.configure("TNotebook", background=BG_DARK, borderwidth=0)
        s.configure("TNotebook.Tab", background=BG_PANEL, foreground=FG_DIM,
                     padding=[14, 6], font=('Segoe UI', 10, 'bold'))
        s.map("TNotebook.Tab",
               background=[("selected", BG_CARD)],
               foreground=[("selected", FG_ACCENT)])

        # Frames
        s.configure("Dark.TFrame", background=BG_DARK)
        s.configure("Card.TFrame", background=BG_PANEL)

        # Labels
        s.configure("Dark.TLabel", background=BG_DARK, foreground=FG_TEXT, font=('Segoe UI', 10))
        s.configure("Title.TLabel", background=BG_DARK, foreground=FG_ACCENT, font=('Segoe UI', 13, 'bold'))
        s.configure("Card.TLabel", background=BG_PANEL, foreground=FG_TEXT, font=('Segoe UI', 10))

        # Entries
        s.configure("Dark.TEntry", fieldbackground=BG_INPUT, foreground=FG_TEXT, insertcolor=FG_TEXT)

        # Buttons
        s.configure("Accent.TButton", background=BTN_ACCENT, foreground="#ffffff",
                     font=('Segoe UI', 10, 'bold'), padding=[12, 6])
        s.map("Accent.TButton", background=[("active", BTN_HOVER)])
        s.configure("Dark.TButton", background=BTN_BG, foreground=FG_TEXT,
                     font=('Segoe UI', 9), padding=[10, 5])
        s.map("Dark.TButton", background=[("active", BTN_HOVER)])

        # Treeview
        s.configure("Dark.Treeview", background=BG_PANEL, foreground=FG_TEXT,
                     fieldbackground=BG_PANEL, font=('Consolas', 10), rowheight=26, borderwidth=0)
        s.configure("Dark.Treeview.Heading", background=BG_CARD, foreground=FG_ACCENT,
                     font=('Segoe UI', 9, 'bold'), borderwidth=0)
        s.map("Dark.Treeview", background=[("selected", BG_CARD)], foreground=[("selected", FG_GOLD)])

        # Separator
        s.configure("Dark.TSeparator", background=BG_CARD)

        # LabelFrame
        s.configure("Dark.TLabelframe", background=BG_PANEL, foreground=FG_ACCENT)
        s.configure("Dark.TLabelframe.Label", background=BG_PANEL, foreground=FG_ACCENT, font=('Segoe UI', 10, 'bold'))

        # Radiobutton
        s.configure("Dark.TRadiobutton", background=BG_PANEL, foreground=FG_TEXT, font=('Segoe UI', 10))

        # Combobox
        s.configure("Dark.TCombobox", fieldbackground=BG_INPUT, foreground=FG_TEXT, selectbackground=BG_CARD)

    # ==========================
    # Main Layout
    # ==========================
    def _build_ui(self):
        # Header
        hdr = tk.Frame(self.root, bg=BG_DARK, pady=8)
        hdr.pack(fill=tk.X, padx=15)
        tk.Label(hdr, text="🕒 Illumio Rule Scheduler", bg=BG_DARK, fg=FG_ACCENT,
                 font=('Segoe UI', 16, 'bold')).pack(side=tk.LEFT)
        tk.Label(hdr, text="v4.1  •  Zero Dependencies", bg=BG_DARK, fg=FG_DIM,
                 font=('Segoe UI', 9)).pack(side=tk.LEFT, padx=10)

        # Notebook
        self.notebook = ttk.Notebook(self.root, style="TNotebook")
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=12, pady=(0, 5))

        self.tab_browse = ttk.Frame(self.notebook, style="Dark.TFrame")
        self.tab_schedules = ttk.Frame(self.notebook, style="Dark.TFrame")
        self.tab_logs = ttk.Frame(self.notebook, style="Dark.TFrame")
        self.tab_config = ttk.Frame(self.notebook, style="Dark.TFrame")

        self.notebook.add(self.tab_browse, text="  📋 Browse & Add  ")
        self.notebook.add(self.tab_schedules, text="  ⏱ Schedules  ")
        self.notebook.add(self.tab_logs, text="  📜 Logs & Check  ")
        self.notebook.add(self.tab_config, text="  ⚙ Settings  ")

        self._build_browse_tab()
        self._build_schedules_tab()
        self._build_logs_tab()
        self._build_config_tab()

        # Status Bar
        self.status_var = tk.StringVar(value="Ready.")
        st = tk.Label(self.root, textvariable=self.status_var, bg=BG_PANEL, fg=FG_DIM,
                      anchor=tk.W, padx=10, pady=3, font=('Consolas', 9))
        st.pack(side=tk.BOTTOM, fill=tk.X)

    def set_status(self, msg):
        self.status_var.set(msg)
        self.root.update_idletasks()

    # ==========================
    # Tab 1: Browse
    # ==========================
    def _build_browse_tab(self):
        # Search bar
        top = tk.Frame(self.tab_browse, bg=BG_DARK, pady=8)
        top.pack(fill=tk.X, padx=10)

        tk.Label(top, text="Search:", bg=BG_DARK, fg=FG_TEXT, font=('Segoe UI', 10)).pack(side=tk.LEFT, padx=(0, 5))
        self.search_var = tk.StringVar()
        se = tk.Entry(top, textvariable=self.search_var, width=35, bg=BG_INPUT, fg=FG_TEXT,
                      insertbackground=FG_TEXT, font=('Segoe UI', 10), relief=tk.FLAT, bd=2)
        se.pack(side=tk.LEFT, padx=5, ipady=3)
        se.bind('<Return>', lambda e: self.do_search_rulesets())

        ttk.Button(top, text="🔍 Search", command=self.do_search_rulesets, style="Dark.TButton").pack(side=tk.LEFT, padx=3)
        ttk.Button(top, text="↻ All", command=self.refresh_browse, style="Dark.TButton").pack(side=tk.LEFT, padx=3)

        # Paned: Left=RS, Right=Rules
        paned = tk.PanedWindow(self.tab_browse, orient=tk.HORIZONTAL, bg=BG_DARK, sashwidth=4, sashrelief=tk.FLAT)
        paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 8))

        # Left
        left = tk.Frame(paned, bg=BG_DARK)
        paned.add(left, width=330)
        tk.Label(left, text="RuleSets", bg=BG_DARK, fg=FG_DIM, font=('Segoe UI', 9)).pack(anchor=tk.W)

        rs_cols = ("stat", "name", "id", "sch")
        self.tree_rs = ttk.Treeview(left, columns=rs_cols, show="headings", style="Dark.Treeview", selectmode='browse')
        for c, t, w in [("stat","⚡",40),("name","Name",170),("id","ID",55),("sch","📅",35)]:
            self.tree_rs.heading(c, text=t)
            self.tree_rs.column(c, width=w, anchor=tk.CENTER if w < 60 else tk.W)
        self.tree_rs.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        sb = ttk.Scrollbar(left, orient=tk.VERTICAL, command=self.tree_rs.yview)
        self.tree_rs.configure(yscroll=sb.set)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree_rs.bind('<<TreeviewSelect>>', self.on_rs_selected)

        # Right
        right = tk.Frame(paned, bg=BG_DARK)
        paned.add(right)
        
        rh = tk.Frame(right, bg=BG_DARK)
        rh.pack(fill=tk.X, pady=(0, 4))
        self.lbl_rs_detail = tk.Label(rh, text="← Select a RuleSet", bg=BG_DARK, fg=FG_ACCENT, font=('Segoe UI', 10, 'bold'))
        self.lbl_rs_detail.pack(side=tk.LEFT)
        ttk.Button(rh, text="＋ Schedule Selected", command=self.show_schedule_dialog, style="Accent.TButton").pack(side=tk.RIGHT)

        r_cols = ("stat", "id", "desc", "src", "dst", "svc", "sch")
        self.tree_rules = ttk.Treeview(right, columns=r_cols, show="headings", style="Dark.Treeview", selectmode='browse')
        for c, t, w in [("stat","⚡",40),("id","ID",55),("desc","Description",180),("src","Source",120),("dst","Dest",120),("svc","Service",100),("sch","📅",35)]:
            self.tree_rules.heading(c, text=t)
            self.tree_rules.column(c, width=w, anchor=tk.CENTER if w < 60 else tk.W)
        self.tree_rules.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        sb2 = ttk.Scrollbar(right, orient=tk.VERTICAL, command=self.tree_rules.yview)
        self.tree_rules.configure(yscroll=sb2.set)
        sb2.pack(side=tk.RIGHT, fill=tk.Y)

    def do_search_rulesets(self):
        kw = self.search_var.get()
        res = self.pce.search_rulesets(kw) if kw else self.pce.get_all_rulesets()
        self._populate_rs_tree(res)

    def refresh_browse(self):
        self.search_var.set("")
        self.set_status("Loading RuleSets...")
        def fetch():
            res = self.pce.get_all_rulesets(force_refresh=True)
            self.root.after(0, lambda: self._populate_rs_tree(res))
            self.root.after(0, lambda: self.set_status(f"Loaded {len(res)} RuleSets."))
        threading.Thread(target=fetch, daemon=True).start()

    def _populate_rs_tree(self, r_list):
        for i in self.tree_rs.get_children(): self.tree_rs.delete(i)
        if not r_list: return
        for rs in r_list:
            href = rs['href']
            stat = "ON" if rs.get('enabled') else "OFF"
            st = self.db.get_schedule_type(rs)
            sch = "★" if st == 1 else ("●" if st == 2 else "")
            self.tree_rs.insert("", tk.END, iid=href, values=(stat, truncate(rs['name'], 35), extract_id(href), sch))

    def on_rs_selected(self, event):
        sel = self.tree_rs.selection()
        if not sel: return
        rs_href = sel[0]
        self.set_status(f"Loading rules for RuleSet {extract_id(rs_href)}...")
        def fetch():
            rs = self.pce.get_ruleset_by_id(extract_id(rs_href))
            self.root.after(0, lambda: self._populate_rules_tree(rs))
            self.root.after(0, lambda: self.set_status("Rules loaded."))
        threading.Thread(target=fetch, daemon=True).start()

    def _populate_rules_tree(self, rs):
        for i in self.tree_rules.get_children(): self.tree_rules.delete(i)
        if not rs: return
        self.lbl_rs_detail.config(text=f"RuleSet: {truncate(rs['name'], 45)} ({len(rs.get('rules',[]))} rules)")

        # RuleSet row
        rs_href = rs['href']
        sch = "★" if rs_href in self.db.get_all() else ""
        stat = "ON" if rs.get('enabled') else "OFF"
        self.tree_rules.insert("", tk.END, iid=rs_href, values=(stat, extract_id(rs_href), "▶ [ENTIRE RULESET]", "ALL", "ALL", "ALL", sch))

        for r in rs.get('rules', []):
            href = r['href']
            stat = "ON" if r.get('enabled') else "OFF"
            desc = truncate(r.get('description'), 35)
            dest = r.get('destinations', r.get('consumers', []))
            src = truncate(self.pce.resolve_actor_str(dest), 20)
            dst = truncate(self.pce.resolve_actor_str(r.get('providers', [])), 20)
            svc = truncate(self.pce.resolve_service_str(r.get('ingress_services', [])), 18)
            sch = "★" if href in self.db.get_all() else ""
            self.tree_rules.insert("", tk.END, iid=href, values=(stat, extract_id(href), desc, src, dst, svc, sch))

    # ==========================
    # Schedule Dialog (Fixed Layout)
    # ==========================
    def show_schedule_dialog(self):
        sel_rs = self.tree_rs.selection()
        sel_rule = self.tree_rules.selection()
        if not sel_rs or not sel_rule:
            messagebox.showwarning("Warning", "Please select a RuleSet on the left AND a rule (or [ENTIRE RULESET]) on the right panel first.")
            return

        rs_href = sel_rs[0]
        rule_href = sel_rule[0]
        is_rs = (rs_href == rule_href)
        vals = self.tree_rules.item(rule_href, 'values')
        name = vals[2] if "ENTIRE" not in str(vals[2]) else self.tree_rs.item(rs_href, 'values')[1]

        dlg = tk.Toplevel(self.root)
        dlg.title(f"Schedule: {name}")
        dlg.geometry("500x520")
        dlg.configure(bg=BG_DARK)
        dlg.transient(self.root)
        dlg.grab_set()
        dlg.resizable(False, False)

        # Title
        tk.Label(dlg, text=f"📅 Schedule for: {truncate(name, 40)}", bg=BG_DARK, fg=FG_ACCENT,
                 font=('Segoe UI', 12, 'bold')).pack(pady=(15, 10), padx=15, anchor=tk.W)

        # Mode Selection
        mode_var = tk.StringVar(value="recurring")
        mf = tk.Frame(dlg, bg=BG_DARK)
        mf.pack(fill=tk.X, padx=20)
        tk.Radiobutton(mf, text="Recurring Schedule (Weekly)", variable=mode_var, value="recurring",
                       bg=BG_DARK, fg=FG_TEXT, selectcolor=BG_PANEL, font=('Segoe UI', 10), activebackground=BG_DARK, activeforeground=FG_ACCENT).pack(anchor=tk.W, pady=2)
        tk.Radiobutton(mf, text="One-Time Expiration", variable=mode_var, value="one_time",
                       bg=BG_DARK, fg=FG_TEXT, selectcolor=BG_PANEL, font=('Segoe UI', 10), activebackground=BG_DARK, activeforeground=FG_ACCENT).pack(anchor=tk.W, pady=2)

        # Separator
        tk.Frame(dlg, bg=BG_CARD, height=2).pack(fill=tk.X, padx=15, pady=10)

        # Recurring Settings
        rf = tk.LabelFrame(dlg, text=" Recurring Settings ", bg=BG_PANEL, fg=FG_ACCENT, font=('Segoe UI', 10, 'bold'), padx=10, pady=8)
        rf.pack(fill=tk.X, padx=15, pady=5)

        def _row(parent, label, default, row, width=20):
            tk.Label(parent, text=label, bg=BG_PANEL, fg=FG_TEXT, font=('Segoe UI', 9)).grid(row=row, column=0, sticky=tk.W, pady=3)
            v = tk.StringVar(value=default)
            tk.Entry(parent, textvariable=v, width=width, bg=BG_INPUT, fg=FG_TEXT, insertbackground=FG_TEXT, relief=tk.FLAT, bd=2, font=('Segoe UI', 10)).grid(row=row, column=1, sticky=tk.W, padx=8, pady=3)
            return v

        act_var = tk.StringVar(value="allow")
        tk.Label(rf, text="Action:", bg=BG_PANEL, fg=FG_TEXT, font=('Segoe UI', 9)).grid(row=0, column=0, sticky=tk.W, pady=3)
        act_cb = ttk.Combobox(rf, textvariable=act_var, values=["allow", "block"], state="readonly", width=12, style="Dark.TCombobox")
        act_cb.grid(row=0, column=1, sticky=tk.W, padx=8, pady=3)

        days_var = _row(rf, "Days (comma sep):", "Monday,Tuesday,Wednesday,Thursday,Friday", 1, 30)
        start_var = _row(rf, "Start (HH:MM):", "08:00", 2, 8)
        end_var = _row(rf, "End (HH:MM):", "18:00", 3, 8)

        # One-Time Settings
        of = tk.LabelFrame(dlg, text=" One-Time Expiration ", bg=BG_PANEL, fg=FG_ACCENT, font=('Segoe UI', 10, 'bold'), padx=10, pady=8)
        of.pack(fill=tk.X, padx=15, pady=5)

        expire_var = _row(of, "Expire At:", datetime.now().strftime("%Y-%m-%d 23:59"), 0, 22)
        tk.Label(of, text="Format: YYYY-MM-DD HH:MM  (auto-disable & remove schedule)", bg=BG_PANEL, fg=FG_DIM, font=('Segoe UI', 8)).grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=2)

        # Buttons (FIXED: using pack on dlg, not grid)
        bf = tk.Frame(dlg, bg=BG_DARK)
        bf.pack(fill=tk.X, padx=15, pady=15)

        def on_save():
            meta_rs = self.tree_rs.item(rs_href, 'values')[1]
            meta_src, meta_dst, meta_svc = ("All","All","All") if is_rs else (vals[3], vals[4], vals[5])
            db_entry = {"name": name, "is_ruleset": is_rs,
                        "detail_rs": meta_rs, "detail_src": meta_src, "detail_dst": meta_dst, "detail_svc": meta_svc, "detail_name": name}
            try:
                if mode_var.get() == "recurring":
                    days = [d.strip() for d in days_var.get().split(',')]
                    datetime.strptime(start_var.get(), "%H:%M")
                    datetime.strptime(end_var.get(), "%H:%M")
                    db_entry.update({"type": "recurring", "action": act_var.get(), "days": days, "start": start_var.get(), "end": end_var.get()})
                    note_msg = f"[📅 排程: {act_var.get()} {start_var.get()}-{end_var.get()}]"
                else:
                    ex = expire_var.get().replace(" ", "T")
                    datetime.fromisoformat(ex)
                    db_entry.update({"type": "one_time", "action": "allow", "expire_at": ex})
                    note_msg = f"[⏳ 有效期限至 {ex} 止]"
            except ValueError:
                messagebox.showerror("Error", "Invalid Date/Time format.")
                return

            self.set_status("Saving schedule and provisioning...")
            self.db.put(rule_href, db_entry)

            def provision():
                self.pce.update_rule_note(rule_href, note_msg)
                self.root.after(0, lambda: messagebox.showinfo("Success", "Schedule saved and provisioned!"))
                self.root.after(0, dlg.destroy)
                self.root.after(0, self.refresh_schedules)
                self.root.after(0, lambda: self.on_rs_selected(None))
            threading.Thread(target=provision, daemon=True).start()

        tk.Button(bf, text="💾  Save Schedule", command=on_save, bg=BTN_ACCENT, fg="#fff",
                  font=('Segoe UI', 11, 'bold'), relief=tk.FLAT, padx=15, pady=6, cursor="hand2").pack(side=tk.LEFT, padx=(0, 10))
        tk.Button(bf, text="Cancel", command=dlg.destroy, bg=BG_CARD, fg=FG_TEXT,
                  font=('Segoe UI', 10), relief=tk.FLAT, padx=12, pady=5).pack(side=tk.LEFT)

    # ==========================
    # Tab 2: Active Schedules
    # ==========================
    def _build_schedules_tab(self):
        top = tk.Frame(self.tab_schedules, bg=BG_DARK, pady=8)
        top.pack(fill=tk.X, padx=10)
        ttk.Button(top, text="↻ Refresh", command=self.refresh_schedules, style="Dark.TButton").pack(side=tk.LEFT, padx=3)
        ttk.Button(top, text="🗑 Delete Selected", command=self.delete_schedule, style="Dark.TButton").pack(side=tk.LEFT, padx=3)

        cols = ("type", "rs_name", "rule_desc", "action", "timing", "href")
        self.tree_sch = ttk.Treeview(self.tab_schedules, columns=cols, show="headings", style="Dark.Treeview", selectmode='browse')
        for c, t, w in [("type","Type",55),("rs_name","RuleSet",200),("rule_desc","Description",250),("action","Action",80),("timing","Timing / Expires",200),("href","",0)]:
            self.tree_sch.heading(c, text=t)
            self.tree_sch.column(c, width=w, stretch=(w > 0))
        self.tree_sch.column("href", width=0, stretch=False)
        self.tree_sch.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 8))

    def refresh_schedules(self):
        for i in self.tree_sch.get_children(): self.tree_sch.delete(i)
        data = self.db.get_all()
        if not data: return
        for href, c in data.items():
            t_type = "RS" if c.get('is_ruleset') else "Rule"
            rs_name = truncate(c.get('detail_rs', 'Unknown'), 30)
            desc = c.get('detail_name', c['name'])
            if c['type'] == 'recurring':
                act = "ALLOW" if c.get('action') == 'allow' else "BLOCK"
                d_str = "Everyday" if len(c['days']) == 7 else ",".join([d[:3] for d in c['days']])
                timing = f"{d_str} {c['start']}-{c['end']}"
            else:
                act = "EXPIRE"
                timing = c['expire_at'].replace("T", " ")
            self.tree_sch.insert("", tk.END, values=(t_type, rs_name, desc, act, timing, href))

    def delete_schedule(self):
        sel = self.tree_sch.selection()
        if not sel: return
        vals = self.tree_sch.item(sel[0], 'values')
        href = vals[5]
        if messagebox.askyesno("Confirm", f"Remove schedule for ID: {extract_id(href)}?"):
            try: self.pce.update_rule_note(href, "", remove=True)
            except Exception: pass
            self.db.delete(href)
            self.refresh_schedules()

    # ==========================
    # Tab 3: Logs & Check
    # ==========================
    def _build_logs_tab(self):
        top = tk.Frame(self.tab_logs, bg=BG_DARK, pady=8)
        top.pack(fill=tk.X, padx=10)
        ttk.Button(top, text="▶ Run Manual Check", command=self.run_manual_check, style="Accent.TButton").pack(side=tk.LEFT)

        self.log_text = tk.Text(self.tab_logs, bg="#0d1117", fg="#c9d1d9", font=("Consolas", 10),
                                relief=tk.FLAT, bd=0, padx=8, pady=8, state=tk.DISABLED, wrap=tk.WORD)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 8))

    def log_message(self, msg):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, msg + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def run_manual_check(self):
        self.log_message(f"[{datetime.now().strftime('%H:%M:%S')}] Starting policy check...")
        def do_check():
            logs = self.engine.check(silent=True)
            ansi_re = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
            for l in logs:
                clean = ansi_re.sub('', l)
                self.root.after(0, lambda m=clean: self.log_message(m))
            self.root.after(0, lambda: self.log_message("✔ Check complete.\n"))
            self.root.after(0, self.refresh_schedules)
        threading.Thread(target=do_check, daemon=True).start()

    # ==========================
    # Tab 4: Settings
    # ==========================
    def _build_config_tab(self):
        outer = tk.Frame(self.tab_config, bg=BG_DARK)
        outer.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)

        tk.Label(outer, text="⚙  PCE API Configuration", bg=BG_DARK, fg=FG_ACCENT,
                 font=('Segoe UI', 14, 'bold')).pack(anchor=tk.W, pady=(0, 15))

        card = tk.Frame(outer, bg=BG_PANEL, padx=20, pady=15)
        card.pack(fill=tk.X)

        self.cfg_url = tk.StringVar(value=self.cfg.config.get('pce_url', ''))
        self.cfg_org = tk.StringVar(value=self.cfg.config.get('org_id', ''))
        self.cfg_key = tk.StringVar(value=self.cfg.config.get('api_key', ''))
        self.cfg_sec = tk.StringVar(value=self.cfg.config.get('api_secret', ''))

        fields = [("PCE URL", self.cfg_url, False), ("Org ID", self.cfg_org, False),
                  ("API Key", self.cfg_key, False), ("API Secret", self.cfg_sec, True)]

        for i, (label, var, secret) in enumerate(fields):
            tk.Label(card, text=label + ":", bg=BG_PANEL, fg=FG_TEXT, font=('Segoe UI', 10)).grid(row=i, column=0, sticky=tk.W, pady=5)
            tk.Entry(card, textvariable=var, width=50, bg=BG_INPUT, fg=FG_TEXT, insertbackground=FG_TEXT,
                     show="•" if secret else "", font=('Segoe UI', 10), relief=tk.FLAT, bd=2).grid(row=i, column=1, padx=10, pady=5, sticky=tk.W)

        bf = tk.Frame(card, bg=BG_PANEL)
        bf.grid(row=4, column=1, sticky=tk.W, padx=10, pady=15)
        tk.Button(bf, text="💾 Save", command=self.save_config, bg=BTN_ACCENT, fg="#fff",
                  font=('Segoe UI', 10, 'bold'), relief=tk.FLAT, padx=15, pady=5, cursor="hand2").pack(side=tk.LEFT)

    def save_config(self):
        if not all([self.cfg_url.get(), self.cfg_org.get(), self.cfg_key.get(), self.cfg_sec.get()]):
            messagebox.showerror("Error", "All fields are required.")
            return
        self.cfg.save(self.cfg_url.get(), self.cfg_org.get(), self.cfg_key.get(), self.cfg_sec.get())
        messagebox.showinfo("Success", "Configuration saved!")
        self.pce.update_label_cache(silent=True)
        self.refresh_browse()
        self.refresh_schedules()

    # ==========================
    # Init
    # ==========================
    def _initial_load(self):
        if not self.cfg.is_ready():
            messagebox.showinfo("Welcome", "Please configure your PCE API settings first.")
            self.notebook.select(self.tab_config)
        else:
            self.refresh_schedules()
            self.refresh_browse()


def launch_gui(core_system):
    root = tk.Tk()
    IllumioGUI(root, core_system)
    root.mainloop()
