from neo4j import GraphDatabase
from datetime import datetime

class CRUD:

#CONNECT

    def __init__(self, uri, user, password):
        self._driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self._driver.close()

#CREATE

    def create_department(self, dept_no, dname, loc):
        with self._driver.session() as session:
            session.execute_write(self._create_department, dept_no, dname, loc)

    @staticmethod
    def _create_department(tx, dept_no, dname, loc):
        tx.run("CREATE (d:Department {dept_no: $dept_no, dname: $dname, loc: $loc})", dept_no=dept_no, dname=dname, loc=loc)

    def create_employee(self, emp_no, ename, job, mgr, hire_date, sal, comm, dept_no):
        with self._driver.session() as session:
            session.execute_write(self._create_employee, emp_no, ename, job, mgr, hire_date, sal, comm, dept_no)

    @staticmethod
    def _create_employee(tx, emp_no, ename, job, mgr, hire_date, sal, comm, dept_no):
        # Verifica si el departamento existe antes de crear el empleado
        tx.run("""
            MERGE (d:Department {dept_no: $dept_no})
        """, dept_no=dept_no)

        # Crea el empleado y establece la relación con el departamento existente
        tx.run("""
            MATCH (d:Department {dept_no: $dept_no})
            CREATE (e:Employee {
                emp_no: $emp_no, 
                ename: $ename, 
                job: $job, 
                mgr: $mgr, 
                hire_date: $hire_date, 
                sal: $sal, 
                comm: $comm, 
                dept_no: $dept_no
            })
            MERGE (e)-[:WORKS_IN]->(d)
        """, emp_no=emp_no, ename=ename, job=job, mgr=mgr, hire_date=hire_date, sal=sal, comm=comm, dept_no=dept_no)


#READ

    def read_department(self, dept_no):
        with self._driver.session() as session:
            result = session.execute_read(self._read_department, dept_no)
            return result

    @staticmethod
    def _read_department(tx, dept_no):
        result = tx.run("MATCH (d:Department {dept_no: $dept_no}) RETURN d", dept_no=dept_no)
        record = result.single()
        if record:
            return record['d']
        else:
            return None

    def read_employee(self, emp_no):
        with self._driver.session() as session:
            result = session.execute_read(self._read_employee, emp_no)
            return result

    @staticmethod
    def _read_employee(tx, emp_no):
        result = tx.run("""
            MATCH (e:Employee {emp_no: $emp_no})-[:WORKS_IN]->(d:Department)
            RETURN e, d
        """, emp_no=emp_no)
        record = result.single()
        if record:
            employee_node = record['e']
            department_node = record['d']

            # Crear un nuevo diccionario con la información del empleado y su departamento
            employee = {
                'emp_no': employee_node['emp_no'],
                'ename': employee_node['ename'],
                'job': employee_node['job'],
                'mgr': employee_node['mgr'],
                'hire_date': employee_node['hire_date'].strftime('%Y-%m-%d') if employee_node.get('hire_date') else None,
                'sal': employee_node['sal'],
                'comm': employee_node['comm'],
                'dept_no': department_node['dept_no'],
                'department_name': department_node['dname']
            }
            return employee
        else:
            return None

    
    def read_all_departments(self):
        with self._driver.session() as session:
            result = session.execute_read(self._read_all_departments)
            return result

    @staticmethod
    def _read_all_departments(tx):
        result = tx.run("MATCH (d:Department) RETURN d ORDER BY d.dept_no")
        return [record['d'] for record in result]

    def read_all_employees(self):
        with self._driver.session() as session:
            result = session.execute_read(self._read_all_employees)
            return result

    @staticmethod
    def _read_all_employees(tx):
        result = tx.run("MATCH (e:Employee) RETURN e")
        return [record['e'] for record in result]

#UPDATE
    def update_department(self, dept_no, new_dname, new_loc):
        with self._driver.session() as session:
            session.execute_write(self._update_department, dept_no, new_dname, new_loc)

    @staticmethod
    def _update_department(tx, dept_no, new_dname, new_loc):
        tx.run("MATCH (d:Department {dept_no: $dept_no}) SET d.dname = $new_dname, d.loc = $new_loc", dept_no=dept_no, new_dname=new_dname, new_loc=new_loc)

    def update_employee(self, emp_no, new_ename, new_job, new_mgr, new_hire_date, new_sal, new_comm, new_dept_no):
        with self._driver.session() as session:
            session.execute_write(self._update_employee, emp_no, new_ename, new_job, new_mgr, new_hire_date, new_sal, new_comm, new_dept_no)

    @staticmethod
    def _update_employee(tx, emp_no, new_ename, new_job, new_mgr, new_hire_date, new_sal, new_comm, new_dept_no):
        tx.run("MATCH (e:Employee {emp_no: $emp_no}) SET e.ename = $new_ename, e.job = $new_job, e.mgr = $new_mgr, e.hire_date = $new_hire_date, e.sal = $new_sal, e.comm = $new_comm, e.dept_no = $new_dept_no", emp_no=emp_no, new_ename=new_ename, new_job=new_job, new_mgr=new_mgr, new_hire_date=new_hire_date, new_sal=new_sal, new_comm=new_comm, new_dept_no=new_dept_no)

#DELETE
    def delete_department(self, dept_no):
        with self._driver.session() as session:
            session.execute_write(self._delete_department, dept_no)

    @staticmethod
    def _delete_department(tx, dept_no):
        tx.run("MATCH (d:Department {dept_no: $dept_no}) DETACH DELETE d", dept_no=dept_no)

    def delete_employee(self, emp_no):
        with self._driver.session() as session:
            session.execute_write(self._delete_employee, emp_no)

    @staticmethod
    def _delete_employee(tx, emp_no):
        tx.run("MATCH (e:Employee {emp_no: $emp_no}) DETACH DELETE e", emp_no=emp_no)


    def department_has_employees(self, dept_no):
        with self._driver.session() as session:
            result = session.execute_read(self._department_has_employees, dept_no)
            return result

    @staticmethod
    def _department_has_employees(tx, dept_no):
        result = tx.run("""
            MATCH (e:Employee {dept_no: $dept_no})
            RETURN COUNT(e) > 0 AS hasEmployees
        """, dept_no=dept_no)
        return result.single()[0]

#ALL

    def delete_all(self):
            query = """
            MATCH (n)
            DETACH DELETE n
            """
            with self._driver.session() as session:
                session.run(query)
            print("Todos los nodos han sido borrados.")	

    def see_all_D(self):
        all_departments = crud.read_all_departments()
        print("\nTodos los departamentos:")
        for department in all_departments:
            print("Department ID:", department.element_id)
            print("Properties:")
            for key, value in department.items():
                print(f"  {key}: {value}")
            print()

    def see_all_E(self):
        all_employees = crud.read_all_employees()
        print("\nTodos los empleados:")
        for employee in all_employees:
            print("Employee ID:", employee.element_id)
            print("Properties:")
            for key, value in employee.items():
                print(f"  {key}: {value}")
            print()

#SCOTT

    def insert_scott_D(self):
        crud.create_department(10, 'ACCOUNTING', 'NEW YORK')
        crud.create_department(20, 'RESEARCH', 'DALLAS')
        crud.create_department(30, 'SALES', 'CHICAGO')
        crud.create_department(40, 'OPERATIONS', 'BOSTON')  

    def insert_scott_E(self):
        crud.create_employee(7369, 'SMITH', 'CLERK', 7902, datetime(1980, 12, 17), 800, None, 20)
        crud.create_employee(7499, 'ALLEN', 'SALESMAN', 7698, datetime(1981, 2, 20), 1600, 300, 30)
        crud.create_employee(7521, 'WARD', 'SALESMAN', 7698, datetime(1981, 2, 22), 1250, 500, 30)
        crud.create_employee(7566, 'JONES', 'MANAGER', 7839, datetime(1981, 4, 2), 2975, None, 20)
        crud.create_employee(7654, 'MARTIN', 'SALESMAN', 7698, datetime(1981, 9, 28), 1250, 1400, 30)
        crud.create_employee(7698, 'BLAKE', 'MANAGER', 7839, datetime(1981, 5, 1), 2850, None, 30)
        crud.create_employee(7782, 'CLARK', 'MANAGER', 7839, datetime(1981, 6, 9), 2450, None, 10)
        crud.create_employee(7788, 'SCOTT', 'ANALYST', 7566, datetime(1987, 7, 13), 3000, None, 20)
        crud.create_employee(7839, 'KING', 'PRESIDENT', None, datetime(1981, 11, 17), 5000, None, 10)
        crud.create_employee(7844, 'TURNER', 'SALESMAN', 7698, datetime(1981, 9, 8), 1500, 0, 30)
        crud.create_employee(7876, 'ADAMS', 'CLERK', 7788, datetime(1987, 7, 13), 1100, None, 20)
        crud.create_employee(7900, 'JAMES', 'CLERK', 7698, datetime(1981, 12, 3), 950, None, 30)
        crud.create_employee(7902, 'FORD', 'ANALYST', 7566, datetime(1981, 12, 3), 3000, None, 20)
        crud.create_employee(7934, 'MILLER', 'CLERK', 7782, datetime(1982, 1, 23), 1300, None, 10)








import tkinter as tk
from tkinter import ttk
from tkinter import messagebox


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

            # Valida que los campos requeridos no estén vacíos
            if not all([emp_no, ename, job, hire_date, sal, dept_no]):
                raise ValueError("Todos los campos, excepto Manager y Comisión, son obligatorios.")

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

            # Llamada al CRUD para actualizar
            self.crud.update_employee(self.emp_no, ename, job, mgr, hire_date, sal, comm, dept_no)
            self.refresh_callback()
            self.top.destroy()
        except ValueError as e:
            messagebox.showerror("Error", f"Error al actualizar empleado: {e}")





if __name__ == "__main__":
    root = tk.Tk()
    uri = 'bolt://localhost:7687'
    user = 'neo4j'
    password = '12345678'

    crud = CRUD(uri, user, password)
    crud.delete_all()
    crud.see_all_D()
    crud.see_all_E()
    crud.insert_scott_D()
    crud.insert_scott_E()
    crud.see_all_D()
    crud.see_all_E()
    


    app = MainApplication(root, crud)
    root.mainloop()

    

    crud.close()
