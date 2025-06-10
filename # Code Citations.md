# Code Citations

## License: MIT
https://github.com/Andrei486/Schedule_Generator/tree/71e09ed436b0794e45fe7f2de7eca9c927006db8/Application.py

```
(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        canvas = tk.Canvas(self)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview
```


## License: unknown
https://github.com/GitOfVitol/openCVProj/tree/37efdb8ed90e2d4d2764a3e356aa7d0f580be3e6/UserPage.py

```
ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.scrollable_frame = tk.Frame(canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all
```


## License: MIT
https://github.com/bawaviki/SaveTube/tree/446978c4bb6449f18854756dd37931a4b65937b1/Savetube/GUI/scrollableframe.py

```
self, orient="vertical", command=canvas.yview)
        self.scrollable_frame = tk.Frame(canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
```


## License: unknown
https://github.com/AndersonSacramento/TEFA/tree/e0794b1d198ae1159582a8a5387584e1d2d03095/src/scrollableframe.py

```
.Frame(canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="
```

