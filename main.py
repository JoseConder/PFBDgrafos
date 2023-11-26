from interfaz import *

if __name__ == "__main__":
    root = tk.Tk()
    uri = 'bolt://localhost:7687'
    user = 'neo4j'
    password = '12345678'

    crud = CRUD(uri, user, password)
    '''
    crud.delete_all()
    crud.see_all_D()
    crud.see_all_E()
    crud.insert_scott_D()
    crud.insert_scott_E()
    crud.see_all_D()
    crud.see_all_E()
    '''


    app = MainApplication(root, crud)
    root.mainloop()

    

    crud.close()
