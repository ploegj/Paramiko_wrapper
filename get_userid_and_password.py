from tkinter import *
from tkinter import ttk
from getpass import getuser

def login_window(str_title='SSH Login'):
    """
    """

    global root
    global login
    
    def enter(*args):
        global login
        try:
            login[0] = Userid.get()
            login[1] = Password.get()
            root.destroy()    # Remove login window
        except ValueError:
            pass

    login = [getuser(), '']       # Get default userid from OS
        
    root = Tk()
    # root.title("SSH Login")
    root.title(str_title)
    # Main window configuration
    main = ttk.Frame(root, padding='3 3 12 12')
    main.grid(column=0, row=0, sticky=(N, W, E, S))
    main.columnconfigure(0, weight=1)
    main.rowconfigure(0, weight=1)

    # Set initial variables
    Userid = StringVar()          # Create StringVar
    Userid.set(login[0])          # Insert default userid into StringVar
    Password = StringVar()        # Create StringVar

    ttk.Label(main, text="Userid        ").grid(column=0, row=1, sticky=(N, W))
    ttk.Label(main, text="Password      ").grid(column=0, row=2, sticky=(W))

    Userid_entry   = ttk.Entry(main, textvariable=Userid, width=12, takefocus=True)
    Userid_entry.grid(column=1, row=1, sticky=(N, E))

    Password_entry = ttk.Entry(main, textvariable=Password, width=12, takefocus=True, show="*")
    Password_entry.grid(column=1, row=2, sticky=(E))

    for child in main.winfo_children(): child.grid_configure(padx=5, pady=5)
    
    root.bind('<Return>', enter)

    root.mainloop()

    return login[0], login[1]
    

if __name__ == '__main__':
    Userid, Password = login_window()
    print("UserID: ", Userid,"Password: ", Password)

