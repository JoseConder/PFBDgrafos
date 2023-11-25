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
            employee = record['e']
            department = record['d']
            # Agrega el departamento a las propiedades del empleado
            employee['department'] = department
            return employee
        else:
            return None

    
    def read_all_departments(self):
        with self._driver.session() as session:
            result = session.execute_read(self._read_all_departments)
            return result

    @staticmethod
    def _read_all_departments(tx):
        result = tx.run("MATCH (d:Department) RETURN d")
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



if __name__ == "__main__":
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
    

    crud.close()
