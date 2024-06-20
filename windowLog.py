from tkinter import *
def windowlogin():    
    def btn_clicked():
        if entry0.get() == "":
            var.set("Es necesario ingresar un nombre")
        else : 
            textoCaja=entry0.get()
            texto.set(textoCaja)
            window.destroy()
    window = Tk()
    window.title("Login")
    window.geometry("450x680")
    window.configure(bg = "#ffffff")
    var = StringVar()
    texto=StringVar()
    canvas = Canvas(
        window,
        bg = "#ffffff",
        height = 680,
        width = 450,
        bd = 0,
        highlightthickness = 0,
        relief = "ridge")
    canvas.place(x = 0, y = 0)
    background_img = PhotoImage(file = f"inicio.png")
    background = canvas.create_image(
        223.5, 319.0,
        image=background_img)
    entry0_img = PhotoImage(file = f"")
    entry0_bg = canvas.create_image(
        224.0, 200,
        image = entry0_img)
    entry0 = Entry(
        bd = 0,
        bg = "#ffffff",
        highlightthickness = 0)
    entry0.place(
        x = 58.0, y = 330,
        width = 330,
        height = 36)

    label = Label(window, textvariable=var, bg = "#e7e7e7")
   

    img1 = PhotoImage(file = f"iniciar.png")
    b1 = Button(
        image = img1,
        bg = "#e7e7e7",
        borderwidth = 0,
        highlightthickness = 0,
        command = btn_clicked,
        relief = "flat")

    b1.place(
        x = 169, y = 400,
        width = 110,
        height = 41)

    


    window.resizable(False, False)
    window.mainloop()
    
    return texto.get()
