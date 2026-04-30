import tkinter as tk

class ScrollableFrame(tk.Frame):
    """
    Componente personalizado para evitar la repetición del boilerplate
    de tk.Canvas y tk.Scrollbar al crear áreas desplazables.
    """
    def __init__(self, parent, bg_color, height=None, *args, **kwargs):
        super().__init__(parent, bg=bg_color, *args, **kwargs)
        
        # Configurar el canvas
        canvas_kwargs = {'bg': bg_color, 'highlightthickness': 0}
        if height:
            canvas_kwargs['height'] = height

        self.canvas = tk.Canvas(self, **canvas_kwargs)
        self.scrollbar = tk.Scrollbar(self, command=self.canvas.yview)
        
        # Frame interior donde se agregarán los widgets
        self.view = tk.Frame(self.canvas, bg=bg_color)
        
        self.view.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas_window = self.canvas.create_window((0, 0), window=self.view, anchor="nw")
        
        # Ajustar el ancho del frame interior al ancho del canvas
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfigure(self.canvas_window, width=e.width))
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
