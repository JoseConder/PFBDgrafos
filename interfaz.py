import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from crud import CRUD

class MainApplication:
    def __init__(self, master, crud):
        self.master = master
        self.crud = crud

        self.tab_control = ttk.Notebook(master)

        self.department_tab = ttk.Frame(self.tab_control)
        self.employee_tab = ttk.Frame(self.tab_control)

        self.tab_control.add(self.department_tab, text='Departamentos')
        self.tab_control.add(self.employee_tab, text='Empleados')

        self.tab_control.pack(expand=1, fill="both")

        DepartmentTab(self.department_tab, crud)
        EmployeeTab(self.employee_tab, crud) # Asumiendo que creaste una clase para la pestaña de empleados


class DepartmentTab:
    def __init__(self, master, crud):
        self.master = master
        self.crud = crud

        self.tree = ttk.Treeview(master, columns=('Dept No', 'DName', 'Location'), show='headings')
        self.tree.heading('Dept No', text='Dept No')
        self.tree.heading('DName', text='DName')
        self.tree.heading('Location', text='Location')
        self.tree.pack(fill=tk.BOTH, expand=True)

        self.refresh_button = tk.Button(master, text="Refrescar Lista", command=self.refresh_departments)
        self.refresh_button.pack()


        self.add_button = tk.Button(master, text="Agregar Departamento", command=self.add_department)
        self.add_button.pack()

        self.update_button = tk.Button(master, text="Actualizar Departamento", command=self.update_department)
        self.update_button.pack()

        self.delete_button = tk.Button(master, text="Eliminar Departamento", command=self.delete_department)
        self.delete_button.pack()

        self.refresh_departments()

    def refresh_departments(self):
        for i in self.tree.get_children():
            self.tree.delete(i)

        departments = self.crud.read_all_departments()
        for department in departments:
            self.tree.insert('', tk.END, values=(department['dept_no'], department['dname'], department['loc']))

    def add_department(self):
        AddDepartmentPopup(self.master, self.crud, self.refresh_departments)
        pass

    def update_department(self):
        selected_item = self.tree.selection()
        if selected_item:
            dept_no = self.tree.item(selected_item[0])['values'][0]
            UpdateDepartmentPopup(self.master, self.crud, dept_no, self.refresh_departments)
        else:
            messagebox.showinfo("Seleccionar", "Por favor, selecciona un departamento primero.")

    def delete_department(self):
        selected_item = self.tree.selection()
        if selected_item:
            dept_no = self.tree.item(selected_item[0])['values'][0]
            if self.crud.department_has_employees(dept_no):
                messagebox.showwarning("Eliminar Departamento", "No se puede eliminar un departamento que tiene empleados.")
            else:
                if messagebox.askyesno("Eliminar Departamento", "¿Estás seguro de que quieres eliminar este departamento?"):
                    self.crud.delete_department(dept_no)
                    self.refresh_departments()
                    messagebox.showinfo("Eliminar Departamento", "Departamento eliminado con éxito.")
        else:
            messagebox.showinfo("Seleccionar", "Por favor, selecciona un departamento primero.")



class UpdateDepartmentPopup:
    def __init__(self, master, crud, dept_no, refresh_callback):
        self.top = tk.Toplevel(master)
        self.crud = crud
        self.dept_no = dept_no
        self.refresh_callback = refresh_callback

        self.top.title("Actualizar Departamento")

        tk.Label(self.top, text="Nombre del Departamento:").pack()
        self.dname_entry = tk.Entry(self.top)
        self.dname_entry.pack()

        tk.Label(self.top, text="Ubicación:").pack()
        self.loc_entry = tk.Entry(self.top)
        self.loc_entry.pack()

        update_button = tk.Button(self.top, text="Actualizar", command=self.update_department)
        update_button.pack()

        # Rellena los campos con los datos actuales del departamento
        self.populate_fields()

    def populate_fields(self):
        department = self.crud.read_department(self.dept_no)
        if department:
            self.dname_entry.insert(0, department['dname'])
            self.loc_entry.insert(0, department['loc'])

    def update_department(self):
        new_dname = self.dname_entry.get()
        new_loc = self.loc_entry.get()
        self.crud.update_department(self.dept_no, new_dname, new_loc)
        self.refresh_callback()  # Actualiza la lista en la interfaz principal
        self.top.destroy()

class AddDepartmentPopup:
    def __init__(self, master, crud, refresh_callback):
        self.top = tk.Toplevel(master)
        self.crud = crud
        self.refresh_callback = refresh_callback

        self.top.title("Agregar Departamento")

        tk.Label(self.top, text="ID del Departamento:").pack()
        self.deptno_entry = tk.Entry(self.top)
        self.deptno_entry.pack()

        tk.Label(self.top, text="Nombre del Departamento:").pack()
        self.dname_entry = tk.Entry(self.top)
        self.dname_entry.pack()

        tk.Label(self.top, text="Ubicación:").pack()
        self.loc_entry = tk.Entry(self.top)
        self.loc_entry.pack()

        add_button = tk.Button(self.top, text="Agregar", command=self.add_department)
        add_button.pack()

    def add_department(self):
        dept_no_str = self.deptno_entry.get()
        dname = self.dname_entry.get()
        loc = self.loc_entry.get()

        try:
            # Convierte DEPTNO de cadena a entero
            dept_no = int(dept_no_str)

            if dname and loc:
                self.crud.create_department(dept_no, dname, loc)
                self.refresh_callback()  # Actualiza la lista en la interfaz principal
                self.top.destroy()
            else:
                messagebox.showwarning("Advertencia", "Todos los campos son obligatorios.")
        except ValueError:
            # Maneja el caso en que DEPTNO no es un número
            messagebox.showwarning("Advertencia", "ID del Departamento debe ser un número.")



class EmployeeTab:
    def __init__(self, master, crud):
        self.master = master
        self.crud = crud

        self.tree = ttk.Treeview(master, columns=('Emp No', 'EName', 'Job', 'Mgr', 'Hire Date', 'Sal', 'Comm', 'Dept No'), show='headings')
        self.tree.heading('Emp No', text='Emp No')
        self.tree.heading('EName', text='EName')
        self.tree.heading('Job', text='Job')
        self.tree.heading('Mgr', text='Mgr')
        self.tree.heading('Hire Date', text='Hire Date')
        self.tree.heading('Sal', text='Sal')
        self.tree.heading('Comm', text='Comm')
        self.tree.heading('Dept No', text='Dept No')
        self.tree.pack(fill=tk.BOTH, expand=True)

        self.tree.column('Emp No', width=70)
        self.tree.column('EName', width=100)
        self.tree.column('Job', width=100)
        self.tree.column('Mgr', width=70)
        self.tree.column('Hire Date', width=100)
        self.tree.column('Sal', width=70)
        self.tree.column('Comm', width=70)
        self.tree.column('Dept No', width=70)

        self.refresh_button = tk.Button(master, text="Refrescar Lista", command=self.refresh_employees)
        self.refresh_button.pack()

        self.add_button = tk.Button(master, text="Agregar Empleado", command=self.add_employee)
        self.add_button.pack()

        self.update_button = tk.Button(master, text="Actualizar Empleado", command=self.update_employee)
        self.update_button.pack()

        self.delete_button = tk.Button(master, text="Eliminar Empleado", command=self.delete_employee)
        self.delete_button.pack()

        self.refresh_employees()


        # Agregar botones para CRUD aquí
    def add_employee(self):
        AddEmployeePopup(self.master, self.crud, self.refresh_employees)
    def delete_employee(self):
        selected_item = self.tree.selection()
        if selected_item:
            emp_no = self.tree.item(selected_item[0])['values'][0]
            if messagebox.askyesno("Eliminar Empleado", f"¿Estás seguro de que deseas eliminar al empleado con ID {emp_no}?"):
                self.crud.delete_employee(emp_no)
                self.refresh_employees()
        else:
            messagebox.showwarning("Advertencia", "Por favor, selecciona un empleado primero.")
    
    def update_employee(self):
        selected_item = self.tree.selection()
        if selected_item:
            emp_no = self.tree.item(selected_item[0])['values'][0]
            UpdateEmployeePopup(self.master, self.crud, emp_no, self.refresh_employees)
        else:
            messagebox.showwarning("Advertencia", "Por favor, selecciona un empleado primero.")


    def refresh_employees(self):
        for i in self.tree.get_children():
            self.tree.delete(i)

        employees = self.crud.read_all_employees()
        for employee in employees:
            self.tree.insert('', tk.END, values=(employee['emp_no'], employee['ename'], employee['job'], employee['mgr'], employee['hire_date'], employee['sal'], employee['comm'], employee['dept_no']))


class AddEmployeePopup:
    def __init__(self, master, crud, refresh_callback):
        self.top = tk.Toplevel(master)
        self.crud = crud
        self.refresh_callback = refresh_callback

        self.top.title("Agregar Empleado")

        # ID del Empleado
        tk.Label(self.top, text="ID del Empleado:").pack()
        self.empno_entry = tk.Entry(self.top)
        self.empno_entry.pack()

        # Nombre
        tk.Label(self.top, text="Nombre:").pack()
        self.ename_entry = tk.Entry(self.top)
        self.ename_entry.pack()

        # Puesto de Trabajo
        tk.Label(self.top, text="Puesto de Trabajo:").pack()
        self.job_entry = tk.Entry(self.top)
        self.job_entry.pack()

        # Manager
        tk.Label(self.top, text="ID del Manager:").pack()
        self.mgr_entry = tk.Entry(self.top)
        self.mgr_entry.pack()

        # Fecha de Contratación
        tk.Label(self.top, text="Fecha de Contratación (dd/mm/yyyy):").pack()
        self.hiredate_entry = tk.Entry(self.top)
        self.hiredate_entry.pack()

        # Salario
        tk.Label(self.top, text="Salario:").pack()
        self.sal_entry = tk.Entry(self.top)
        self.sal_entry.pack()

        # Comisión
        tk.Label(self.top, text="Comisión:").pack()
        self.comm_entry = tk.Entry(self.top)
        self.comm_entry.pack()

        # Número de Departamento
        tk.Label(self.top, text="Número de Departamento:").pack()
        self.deptno_entry = tk.Entry(self.top)
        self.deptno_entry.pack()

        # Botón para agregar empleado
        add_button = tk.Button(self.top, text="Agregar", command=self.add_employee)
        add_button.pack()

    def add_employee(self):
        try:
            emp_no = int(self.empno_entry.get())
            ename = self.ename_entry.get()
            job = self.job_entry.get()
            mgr = int(self.mgr_entry.get()) if self.mgr_entry.get() else None
            hire_date = datetime.strptime(self.hiredate_entry.get(), "%d/%m/%Y")
            sal = float(self.sal_entry.get())
            comm = float(self.comm_entry.get()) if self.comm_entry.get() else None
            dept_no = int(self.deptno_entry.get())

            # Verifica si el departamento existe antes de realizar la acción
            result = self.crud._driver.session().run("MATCH (d:Department {dept_no: $dept_no}) RETURN COUNT(d) AS deptCount", dept_no=dept_no)
            dept_count = result.single()['deptCount']

            if dept_count == 0:
                # El departamento no existe, se deniega la acción
                messagebox.showerror("Error", f"No se puede agregar el empleado porque el departamento {dept_no} no existe.")
            else:
                # Llamada al CRUD para agregar empleado
                self.crud.create_employee(emp_no, ename, job, mgr, hire_date, sal, comm, dept_no)
                self.refresh_callback()  # Actualiza la lista en la interfaz principal
                self.top.destroy()
        except ValueError as e:
            messagebox.showerror("Error", f"Error al agregar empleado: {e}")


class UpdateEmployeePopup:
    def __init__(self, master, crud, emp_no, refresh_callback):
        self.top = tk.Toplevel(master)
        self.crud = crud
        self.emp_no = emp_no
        self.refresh_callback = refresh_callback

        self.top.title("Actualizar Empleado")

        employee = self.crud.read_employee(emp_no)
        if not employee:
            messagebox.showerror("Error", "Empleado no encontrado.")
            self.top.destroy()
            return

        # Guardar los valores actuales que no se van a cambiar
        self.current_ename = employee['ename']
        self.current_hire_date = employee['hire_date']

        # Puesto de Trabajo
        tk.Label(self.top, text="Puesto de Trabajo:").pack()
        self.job_entry = tk.Entry(self.top)
        self.job_entry.insert(0, employee['job'])
        self.job_entry.pack()

        # Manager
        tk.Label(self.top, text="ID del Manager:").pack()
        self.mgr_entry = tk.Entry(self.top)
        self.mgr_entry.insert(0, employee['mgr'] if employee['mgr'] else "")
        self.mgr_entry.pack()

        # Salario
        tk.Label(self.top, text="Salario:").pack()
        self.sal_entry = tk.Entry(self.top)
        self.sal_entry.insert(0, employee['sal'])
        self.sal_entry.pack()

        # Comisión
        tk.Label(self.top, text="Comisión:").pack()
        self.comm_entry = tk.Entry(self.top)
        self.comm_entry.insert(0, employee['comm'] if employee['comm'] else "")
        self.comm_entry.pack()

        # Número de Departamento
        tk.Label(self.top, text="Número de Departamento:").pack()
        self.deptno_entry = tk.Entry(self.top)
        self.deptno_entry.insert(0, employee['dept_no'])
        self.deptno_entry.pack()

        # Botón para actualizar empleado
        update_button = tk.Button(self.top, text="Actualizar", command=self.update_employee)
        update_button.pack()

    def update_employee(self):
        try:
            # Utiliza los valores actuales para los campos que no se pueden cambiar
            ename = self.current_ename
            hire_date = self.current_hire_date

            # Obtén los valores actualizados de los campos que sí pueden cambiar
            job = self.job_entry.get()
            mgr = int(self.mgr_entry.get()) if self.mgr_entry.get() else None
            sal = float(self.sal_entry.get())
            comm = float(self.comm_entry.get()) if self.comm_entry.get() else None
            dept_no = int(self.deptno_entry.get())

            # Verifica si el departamento existe antes de realizar la acción
            result = self.crud._driver.session().run("MATCH (d:Department {dept_no: $dept_no}) RETURN COUNT(d) AS deptCount", dept_no=dept_no)
            dept_count = result.single()['deptCount']

            if dept_count == 0:
                # El departamento no existe, se deniega la acción
                messagebox.showerror("Error", f"No se puede actualizar el empleado porque el departamento {dept_no} no existe.")
            else:
                # Llamada al CRUD para actualizar
                self.crud.update_employee(self.emp_no, ename, job, mgr, hire_date, sal, comm, dept_no)
                self.refresh_callback()
                self.top.destroy()
        except ValueError as e:
            messagebox.showerror("Error", f"Error al actualizar empleado: {e}")
