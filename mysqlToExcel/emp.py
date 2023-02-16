import openpyxl
import pymysql
workbook = openpyxl.Workbook()

sheet = workbook.active
sheet.title = 'Employee'
sheet.append(('No', 'Name', 'Job','Salary', 'Subsidy', 'Department'))
conn = pymysql.connect(host = '127.0.0.1', port = 3306, user = 'guest', password = 'Guest.618',database = 'hrs', charset = 'utf8mb4')
try:
    with conn.cursor() as cursor:
        cursor.execute(
            'select eno, ename, job, sal, coalesce(comm, 0), dname \
            from tb_emp join tb_dept on tb_emp.dno = tb_dept.dno'
        )
        row = cursor.fetchone()
        while row:
            sheet.append(row)
            row = cursor.fetchone()
    workbook.save('emp.xlsx')
except pymysql.MySQLError as err:
    print(err)
finally:
    conn.close()
