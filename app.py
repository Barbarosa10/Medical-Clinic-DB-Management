from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
import cx_Oracle
from datetime import datetime
dialect = 'oracle'
sql_driver = 'cx_oracle'
username = 'bd053'
password = 'bd053'
host = 'bd-dc.cs.tuiasi.ro'
port = 1539
service = 'orcl'
# engine_path = dialect + '+' + sql_driver + '://' + username + ':' + password + '@' + host + ':' + str(port) + '/?service_name=' + service
# db = create_engine(engine_path)
# con = db.connect()
app = Flask(__name__)
# app.config.from_object('app.instance.config.DevelopmentConfig')
# app.config['SQLALCHEMY_DATABASE_URI'] = engine_path
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# oracle://bd053/bd053@bd-dc.cs.tuiasi.ro:1539/orcl

dsn = cx_Oracle.makedsn(host, port, service_name=service)
connection = cx_Oracle.connect(user=username, password=password, dsn=dsn,
                               encoding="UTF-8")

# db = SQLAlchemy(app)

# class Comment(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     lastName = db.Column(db.String(20))
#     firstName = db.Column(db.String(20))

#     def __repr__(self):
#         return '<Task %r>' % self.id

# with app.app_context():
#     db.engine.execute('desc employees')
# with app.app_context():
#     db.create_all()


@app.route('/')
@app.route('/doctors')
def doctors():
    #doctors
    doctors = []
    cur = connection.cursor()
    cur2 = connection.cursor()
    cur.execute('select * from doctor')

    for result in cur:
        doctor = {}
        doctor['doctor_id'] = result[0]
        doctor['first_name'] = result[1]
        doctor['last_name'] = result[2]
        if (result[3] == '1'):
            doctor['gender'] = 'M'
        elif (result[3] == '0'):
            doctor['gender'] = 'F'
        doctor['phone_number'] = result[4]

        cur2.execute(
            'select fieldArea from department where department_id='+str(result[5]))
        for res in cur2:
            doctor['department_name'] = res[0].upper()
        doctors.append(doctor)

    cur.close()
    cur2.close()

    departments = []
    cur = connection.cursor()
    cur.execute('select department_id, fieldArea from department')
    for result in cur:
        department = {}
        department['department_id'] = result[0]
        department['department_name'] = result[1]
        departments.append(department)
    cur.close()
    
    #workSchedule
    workSchedules = []
    cur = connection.cursor()
    cur2 = connection.cursor()
    cur.execute('select * from workSchedule')

    for result in cur:
        workSchedule = {}
        workSchedule['workSchedule_id'] = result[0]
        workSchedule['day'] = result[1]
        workSchedule['start_time'] = datetime.strptime(str(result[2]), '%Y-%m-%d %H:%M:%S').strftime('%H:%M')
        workSchedule['end_time'] = datetime.strptime(str(result[3]), '%Y-%m-%d %H:%M:%S').strftime('%H:%M')

        cur2.execute(
            'select last_name, first_name from doctor where doctor_id='+str(result[4]))
        for res in cur2:
            workSchedule['last_name'] = res[0]
            workSchedule['first_name'] = res[1]
        workSchedules.append(workSchedule)

    cur.close()
    cur2.close()

    return render_template('doctors.html', doctors=doctors, departments=departments, workSchedules=workSchedules)


@app.route('/getDoctor', methods=['post'])
def getDoctor():
    cur = connection.cursor()
    doc = request.form['doctor_id']
    cur.execute('select * from doctor where doctor_id=' + str(doc))
    res = cur.fetchone()
    doctor_id = res[0]
    first_name = res[1]
    last_name = res[2]
    gender = res[3]
    phone_number = res[4]
    department_id = res[5]
    cur.close()

    department_name = ""
    cur = connection.cursor()
    cur.execute('select fieldArea from department where department_id=' + str(department_id))
    for res in cur:
        department_name = res[0].lower()
    cur.close()

    departments = []
    cur = connection.cursor()
    cur.execute('select department_id, fieldArea from department')
    for result in cur:
        department = {}
        department['department_id'] = result[0]
        department['department_name'] = result[1].lower()
        departments.append(department)
    cur.close()

    return render_template('editDoctors.html', doctor_id=doctor_id, last_name=last_name, first_name=first_name, gender=gender, phone_number=phone_number, departments=departments, department_name=department_name)

@app.route('/getWorkSchedule', methods=['post'])
def getWorkSchedule():
    cur = connection.cursor()
    cur2 = connection.cursor()
    workSch = request.form['workSchedule_id']
    cur.execute('select * from workSchedule where workSchedule_id=' + str(workSch))
    res = cur.fetchone()
    workSchedule_id = res[0]
    day = res[1] 
    start_time_h = datetime.strptime(str(res[2]), '%Y-%m-%d %H:%M:%S').strftime('%H')
    start_time_m = datetime.strptime(str(res[2]), '%Y-%m-%d %H:%M:%S').strftime('%M')
    
    end_time_h = datetime.strptime(str(res[3]), '%Y-%m-%d %H:%M:%S').strftime('%H')
    end_time_m = datetime.strptime(str(res[3]), '%Y-%m-%d %H:%M:%S').strftime('%M')
    
    cur2.execute('select last_name, first_name from doctor where doctor_id='+str(res[4]))
    for res in cur2:
        last_name = res[0]
        first_name = res[1]

    cur.close()
    cur2.close()


    return render_template('editWorkSchedule.html', workSchedule_id=workSchedule_id, last_name=last_name, first_name=first_name,
     day=day, start_time_h=start_time_h, start_time_m=start_time_m, end_time_h=end_time_h, end_time_m=end_time_m)

@app.route('/editDoctor', methods=['post'])
def saveDoctor():
    cur = connection.cursor()
    doctor_id = request.form['doctor_id']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    if (request.form['gender'] == 'male'):
        gender = '1'
    elif (request.form['gender'] == 'female'):
        gender = '0'
    phone_number = request.form['phone_number']
    
    department_id =  request.form['department_name']
    cur.close()
    query = 'UPDATE doctor SET first_name=:1, last_name=:2, gender=:3, phone_number=:4, department_id=:5 where doctor_id=:6'
    
    cur = connection.cursor()
    cur.execute(query, [first_name, last_name, gender, phone_number, department_id, doctor_id])
    cur.execute('commit')
    cur.close()
    return redirect("/doctors")

@app.route('/editWorkSchedule', methods=['post'])
def saveWorkSchedule():
    cur = connection.cursor()
    workSchedule_id = request.form['workSchedule_id']
    day = request.form['day'].upper()
    start_time_h = request.form['start_time_h']
    start_time_m = request.form['start_time_m']
    end_time_h = request.form['end_time_h']
    end_time_m = request.form['end_time_m']
    
    start_time = datetime.strptime(start_time_h + ":" + start_time_m, "%H:%M")
    end_time = datetime.strptime(end_time_h + ":" + end_time_m, "%H:%M")
    cur.close()
    query = 'UPDATE workSchedule SET day=:1, start_time=:2, end_time=:3 where workSchedule_id=:4'
    cur = connection.cursor()
    cur.execute(query, [day, start_time, end_time, workSchedule_id])
    cur.execute('commit')
    cur.close()
    return redirect("/doctors")

@app.route('/deleteDoctor', methods=['post'])
def deleteDoctor():
    doctor = request.form['doctor_id']
    cur = connection.cursor()
    cur.execute('delete from doctor where doctor_id=' + doctor)
    cur.execute('commit')
    return redirect('/doctors')

@app.route('/deleteWorkSchedule', methods=['post'])
def deleteWorkSchedule():
    doctor = request.form['workSchedule_id']
    cur = connection.cursor()
    cur.execute('delete from workSchedule where workSchedule_id=' + doctor)
    cur.execute('commit')
    return redirect('/doctors')    

@app.route('/addDoctor', methods=['POST'])
def addDoctor():
    error = None
    cur = connection.cursor()
    values = []
    values.append("'" + request.form['first_name'] + "'")
    values.append("'" + request.form['last_name'] + "'")

    if (request.form['gender'] == 'male'):
        values.append("'1'")
    elif (request.form['gender'] == 'female'):
        values.append("'0'")
    values.append("'" + request.form['phone_number'] + "'")
    values.append("'" + request.form['department_name'] + "'")

    fields = ['first_name', 'last_name',
              'gender', 'phone_number', 'department_id']
    query = 'INSERT INTO %s (%s) VALUES (%s)' % (
        'doctor', ', '.join(fields), ', '.join(values))

    cur.execute(query)
    cur.execute('commit')
    return redirect('/doctors')

@app.route('/addWorkSchedule', methods=['POST'])
def addWorkSchedule():
    error = None
    cur = connection.cursor()
    last_name = request.form['last_name']
    first_name = request.form['first_name']

    start_time_h = request.form['start_time_h']
    start_time_m = request.form['start_time_m']
    end_time_h = request.form['end_time_h']
    end_time_m = request.form['end_time_m']
    
    start_time = datetime.strptime(start_time_h + ":" + start_time_m, "%H:%M")
    end_time = datetime.strptime(end_time_h + ":" + end_time_m, "%H:%M")
    
    query = 'INSERT INTO workSchedule (day, start_time, end_time, doctor_id) select {}, TO_DATE({}, \'yyyy-mm-dd hh24:mi\'),'\
        ' TO_DATE({}, \'yyyy-mm-dd hh24:mi\'), doctor_id from doctor where last_name={} and first_name={}'\
        .format("'" + request.form['day'].upper() + "'", "'" + start_time.strftime("%Y-%m-%d %H:%M") + "'", "'" + end_time.strftime("%Y-%m-%d %H:%M") + "'", "'" + last_name + "'", "'" + first_name + "'")
    print(query)
    cur.execute(query)
    cur.execute('commit')
    cur.close()
    return redirect('/doctors')

@app.route('/patients')
def patients():
    patients = []
    cur = connection.cursor()
    cur.execute('select * from patient')
    for result in cur:
        patient = {}
        patient['patient_id'] = result[0]
        patient['first_name'] = result[1]
        patient['last_name'] = result[2]
        patient['birth_date'] = datetime.strptime(
            str(result[3]), '%Y-%m-%d %H:%M:%S').strftime('%d.%m.%Y')

        if (result[4] == '1'):
            patient['gender'] = 'M'
        elif (result[4] == '0'):
            patient['gender'] = 'F'
        patient['blood_type'] = result[5]
        patient['phone_number'] = result[6]
        patient['cnp'] = result[7]
        patients.append(patient)
    cur.close()
    return render_template('patients.html', patients=patients)

@app.route('/getPatient', methods=['post'])
def getPatient():
    cur = connection.cursor()
    pat = request.form['patient_id']
    cur.execute('select * from patient where patient_id=' + str(pat))
    res = cur.fetchone()
    patient_id = res[0]
    first_name = res[1]
    last_name = res[2]
    birth_date = datetime.strptime(str(res[3]), '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d')
    print("BIRTH_DATE: " + birth_date)
    gender = res[4]
    blood_type = res[5]
    phone_number = res[6]
    cnp = res[7]
    cur.close()

    return render_template('editPatients.html', patient_id=patient_id, last_name=last_name, first_name=first_name, gender=gender, birth_date=birth_date, blood_type=blood_type, phone_number=phone_number, cnp=cnp)

@app.route('/editPatient', methods=['post'])
def savePatient():
    cur = connection.cursor()
    patient_id = request.form['patient_id']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    birth_date = datetime.strptime(str(request.form['birth_date']), '%Y-%m-%d').strftime('%d-%b-%Y')
    print("BIRTH DATE: " + birth_date)
    blood_type = request.form['blood_type']
    if (request.form['gender'] == 'male'):
        gender = '1'
    elif (request.form['gender'] == 'female'):
        gender = '0'
    phone_number = request.form['phone_number']
    cnp = request.form['cnp']
    print("CNP: " + cnp)
    cur.close()

    query = 'UPDATE patient SET first_name=:1, last_name=:2, gender=:3, phone_number=:4, birth_date=:5, blood_type=:6, cnp=:7 where patient_id=:8'
    
    cur = connection.cursor()
    cur.execute(query, [first_name, last_name, gender, phone_number, birth_date, blood_type, cnp, patient_id])
    cur.execute('commit')
    cur.close()
    return redirect("/patients")


@app.route('/deletePatient', methods=['post'])
def deletePatient():
    patient = request.form['patient_id']
    cur = connection.cursor()
    cur.execute('delete from patient where patient_id=' + patient)
    cur.execute('commit')
    return redirect('/patients')


@app.route('/addPatient', methods=['POST'])
def addPatient():
    error = None
    cur = connection.cursor()
    values = []
    values.append("'" + request.form['first_name'] + "'")
    values.append("'" + request.form['last_name'] + "'")
    values.append("'" + datetime.strptime(str(request.form['birth_date']), '%Y-%m-%d').strftime('%d-%b-%Y') + "'")
    print("GENDER:    " + request.form['gender'])
    if (request.form['gender'] == 'male'):
        values.append("'1'")
    elif (request.form['gender'] == 'female'):
        values.append("'0'")
    values.append("'" + request.form['blood_type'] + "'")
    values.append("'" + request.form['phone_number'] + "'")
    values.append("'" + request.form['cnp'] + "'")

    fields = ['first_name', 'last_name', 'birth_date',
              'gender', 'blood_type', 'phone_number', 'cnp']
    query = 'INSERT INTO %s (%s) VALUES (%s)' % (
        'patient', ', '.join(fields), ', '.join(values))

    cur.execute(query)
    cur.execute('commit')
    return redirect('/patients')

@app.route('/services')
def services():
    services = []
    cur = connection.cursor()
    cur.execute('select * from service')
    for result in cur:
        service = {}
        service['service_id'] = result[0]
        service['name'] = result[1]
        service['price'] = result[2]

        services.append(service)
    cur.close()
    return render_template('services.html', services=services)

@app.route('/getService', methods=['post'])
def getService():
    cur = connection.cursor()
    ser = request.form['service_id']
    cur.execute('select * from service where service_id=' + str(ser))
    res = cur.fetchone()
    service_id = res[0]
    name = res[1]
    price = res[2]
    cur.close()

    return render_template('editServices.html', service_id=service_id, name=name, price=price)

@app.route('/editService', methods=['post'])
def saveService():
    cur = connection.cursor()
    service_id = request.form['service_id']
    name = request.form['name']
    price = request.form['price']
    cur.close()
    query = 'UPDATE service SET name=:1, price=:2 where service_id=:3'
    
    cur = connection.cursor()
    cur.execute(query, [name, price, service_id])
    cur.execute('commit')
    cur.close()
    return redirect("/services")

@app.route('/addService', methods=['POST'])
def addService():
    error = None
    cur = connection.cursor()
    values = []
    values.append("'" + request.form['name'] + "'")
    values.append("'" + request.form['price'] + "'")
    
    fields = ['name', 'price']
    query = 'INSERT INTO %s (%s) VALUES (%s)' % (
        'service', ', '.join(fields), ', '.join(values))

    cur.execute(query)
    cur.execute('commit')
    return redirect('/services')

@app.route('/deleteService', methods=['post'])
def deleteService():
    service = request.form['service_id']
    cur = connection.cursor()
    cur.execute('delete from service where service_id=' + service)
    cur.execute('commit')
    return redirect('/services')

@app.route('/workSchedule')
def workSchedule():
    cur = connection.cursor()
    cur2 = connection.curso()
    cur.execute('select * from workSchedule')
    workSchedules = []
    for result in cur:
        workSchedule = {}
        workSchedule['workSchedule_id'] = result[0]
        workSchedule['day'] = result[1]
        workSchedule['start_time'] = result[2]
        workSchedule['end_time'] = result[3]

        cur2.execute('select last_name, first_name from doctor where doctor_id=' + str(result[4]))
        for res in cur2:
            workSchedule['doctor_name'] = res[0] + " " + res[1]
        workSchedules.append(workSchedule)
    cur.close()
    cur2.close()

    doctors = []
    cur = connection.cursor()
    cur.execute('select doctor_id, last_name, first_name from doctor')
    for result in cur:
        doctor = {}
        doctor['doctor_id'] = result[0]
        doctor['last_name'] = result[1]
        doctor['first_name'] = result[2]
        doctors.append(doctor)

    return render_template('workSchedule.html', workSchedules=workSchedules, doctors=doctors)

@app.route('/departments')
def departments():
    departments = []
    cur = connection.cursor()
    cur.execute('select * from department')
    for result in cur:
        department = {}
        department['department_id'] = result[0]
        department['fieldArea'] = result[1]
        departments.append(department)
    cur.close()
    return render_template('departments.html', departments=departments)

@app.route('/getDepartment', methods=['post'])
def getDepartment():
    cur = connection.cursor()
    dep = request.form['department_id']
    cur.execute('select * from department where department_id=' + str(dep))
    res = cur.fetchone()
    department_id = res[0]
    fieldArea = res[1]
    cur.close()

    return render_template('editDepartments.html', department_id=department_id, fieldArea=fieldArea)

@app.route('/editDepartment', methods=['post'])
def saveDepartment():
    cur = connection.cursor()
    department_id = request.form['department_id']
    fieldArea = request.form['fieldArea']
    cur.close()
    query = 'UPDATE department SET fieldArea=:1 where department_id=:2'
    
    cur = connection.cursor()
    cur.execute(query, [fieldArea, department_id])
    cur.execute('commit')
    cur.close()
    return redirect("/departments")

@app.route('/addDepartment', methods=['POST'])
def addDepartment():
    error = None
    cur = connection.cursor()
    values = []
    values.append("'" + request.form['fieldArea'] + "'")
    
    fields = ['fieldArea']
    query = 'INSERT INTO %s (%s) VALUES (%s)' % (
        'department', ', '.join(fields), ', '.join(values))

    cur.execute(query)
    cur.execute('commit')
    return redirect('/departments')

@app.route('/deleteDepartment', methods=['post'])
def deleteDepartment():
    department = request.form['department_id']
    cur = connection.cursor()
    cur.execute('delete from department where department_id=' + department)
    cur.execute('commit')
    return redirect('/departments')

@app.route('/appointments')
def appointments():
    #appointments
    appointments = []
    cur = connection.cursor()
    cur2 = connection.cursor()
    cur3 = connection.cursor()
    cur4 = connection.cursor()
    cur.execute('select * from appointment')

    for result in cur:
        appointment = {}
        appointment['appointment_id'] = result[0]
        appointment['start_time'] = datetime.strptime(str(result[1]), '%Y-%m-%d %H:%M:%S').strftime('%d.%m.%Y, %H:%M')
        appointment['end_time'] = datetime.strptime(str(result[2]), '%Y-%m-%d %H:%M:%S').strftime('%d.%m.%Y, %H:%M')
        patient_id = result[3]
        service_id = result[4]
        doctor_id = result[5]


        cur2.execute(
            'select last_name, first_name, cnp from patient where patient_id='+str(patient_id))
        for res in cur2:
            appointment['last_namePatient'] = res[0]
            appointment['first_namePatient'] = res[1]
            appointment['cnp'] = res[2]

        cur3.execute('select last_name, first_name from doctor where doctor_id=' + str(doctor_id))
        for result in cur3:
            appointment['last_nameDoctor'] = result[0]
            appointment['first_nameDoctor'] = result[1]
        
        cur4.execute('select name from service where service_id=' + str(service_id))
        for result in cur4:
            appointment['service'] = result[0].upper()

        appointments.append(appointment)

    cur.close()
    cur2.close()
    cur3.close()
    cur4.close()
    
    #bill
    bills = []
    cur = connection.cursor()
    cur2 = connection.cursor()
    cur3 = connection.cursor()
    cur4 = connection.cursor()
    cur.execute('select * from bill')

    for result in cur:
        bill = {}
        bill['bill_id'] = result[0]
        bill['price'] = result[1]
        appointment_id = result[2]

        cur2.execute('select patient_id, service_id, start_time from appointment where appointment_id=' + str(appointment_id))
        for result in cur2:
            patient_id = result[0]
            service_id = result[1]
            bill['date'] = datetime.strptime(str(result[2]), '%Y-%m-%d %H:%M:%S').strftime('%d.%m.%Y, %H:%M')

        cur3.execute('select last_name, first_name, cnp from patient where patient_id='+str(patient_id))
        for res in cur3:
            bill['last_name'] = res[0]
            bill['first_name'] = res[1]
            bill['cnp'] = res[2]

        cur4.execute('select name, price from service where service_id=' + str(service_id))
        for res in cur4:
            bill['service'] = res[0].upper()
            bill['price'] = str(res[1]) + ' RON'
        bills.append(bill)

    cur.close()
    cur2.close()
    cur3.close()
    cur4.close()

    services = []
    cur = connection.cursor()
    cur.execute('select service_id, name from service')
    for result in cur:
        service = {}
        service['service_id'] = result[0]
        service['service_name'] = result[1]
        services.append(service)
    cur.close()



    return render_template('appointments.html', appointments=appointments, bills=bills, services=services)

@app.route('/getAppointment', methods=['post'])
def getAppointment():
    cur = connection.cursor()
    appo = request.form['appointment_id']
    cur.execute('select * from appointment where appointment_id=' + str(appo))
    res = cur.fetchone()
    appointment_id = res[0]
    start_date = datetime.strptime(str(res[1]), '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d')
    end_date = datetime.strptime(str(res[2]), '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d')
    start_time_h = datetime.strptime(str(res[1]), '%Y-%m-%d %H:%M:%S').strftime('%H')
    start_time_m = datetime.strptime(str(res[1]), '%Y-%m-%d %H:%M:%S').strftime('%M')
    end_time_h = datetime.strptime(str(res[2]), '%Y-%m-%d %H:%M:%S').strftime('%H')
    end_time_m = datetime.strptime(str(res[2]), '%Y-%m-%d %H:%M:%S').strftime('%M')
    patient_id = res[3]
    service_id = res[4]
    doctor_id = res[5]
    cur.close()

    cur = connection.cursor()
    cur.execute('select last_name, first_name, cnp from patient where patient_id=' + str(patient_id))
    for res in cur:
        patient_last_name = res[0]
        patient_first_name = res[1]
        cnp = res[2]
    cur.close()
    
    cur = connection.cursor()
    cur.execute('select name from service where service_id=' + str(service_id))
    for res in cur:
        service = res[0]
    cur.close()

    cur = connection.cursor()
    cur.execute('select last_name, first_name from doctor where doctor_id=' + str(doctor_id))
    for res in cur:
        doctor_last_name = res[0]
        doctor_first_name = res[1]
    cur.close()

    services = []
    cur = connection.cursor()
    cur.execute('select service_id, name from service')
    for result in cur:
        service = {}
        service['service_id'] = result[0]
        service['service_name'] = result[1]
        services.append(service)
    cur.close()

    return render_template('editAppointments.html', appointment_id=appointment_id, patient_last_name=patient_last_name, 
    patient_first_name=patient_first_name, doctor_last_name=doctor_last_name, doctor_first_name=doctor_first_name, services=services,
     cnp=cnp, start_date=start_date, end_date=end_date, start_time_h=start_time_h, start_time_m=start_time_m, end_time_h=end_time_h, end_time_m=end_time_m)

@app.route('/editAppointment', methods=['post'])
def saveAppointment():
    cur = connection.cursor()
    appointment_id = request.form['appointment_id']
    patient_last_name = request.form['patient_last_name']
    patient_first_name = request.form['patient_first_name']
    cnp = request.form['cnp']
    doctor_last_name = request.form['doctor_last_name']
    doctor_first_name = request.form['doctor_first_name']
    service_name = request.form['service_name']

    start_date = request.form['start_date']
    start_time_h = request.form['start_time_h']
    start_time_m = request.form['start_time_m']
    end_date = request.form['end_date']
    end_time_h = request.form['end_time_h']
    end_time_m = request.form['end_time_m']

    start_date = str(start_date) + ", " + start_time_h + ":" + start_time_m
    end_date = str(end_date) + ", " + end_time_h + ":" + end_time_m
    start_date = datetime.strptime(start_date, '%Y-%m-%d, %H:%M').strftime('%d.%m.%Y %H:%M')
    end_date = datetime.strptime(end_date, '%Y-%m-%d, %H:%M').strftime('%d.%m.%Y %H:%M')

    print(start_date)
    print(end_date)

    cur.close()
    cur = connection.cursor()
    cur.execute('select doctor_id from doctor where last_name={} and first_name={}'.format("'"+doctor_last_name+"'", "'"+doctor_first_name+"'"))
    for res in cur:
        doctor_id = res[0]
    cur.close()
    query = 'UPDATE appointment SET service_id ={}, doctor_id={}, '\
        'start_time=to_date({}, \'dd.mm.yyyy hh24:mi\'), end_time=to_date({}, \'dd.mm.yyyy hh24:mi\') where appointment_id={} and '\
        'TO_DATE({}, \'dd.mm.yyyy hh24:mi\') >= to_date({}, \'dd.mm.yyyy hh24:mi\') and '\
        'exists (select \'x\' from workSchedule w where w.doctor_id={} and lower(to_char(TO_DATE({}, \'dd.mm.yyyy hh24:mi\'), \'fmday\')) like lower(w.day) '\
        'and to_char(TO_DATE({}, \'dd.mm.yyyy hh24:mi\'), \'hh24:mi\') >= to_char(w.start_time, \'hh24:mi\')  and to_char(TO_DATE({}, \'dd.mm.yyyy hh24:mi\'), \'hh24:mi\')<= to_char(w.end_time, \'hh24:mi\')) '\
        'and not exists ( select \'x\' from appointment a where TO_DATE({}, \'dd.mm.yyyy hh24:mi\')=a.start_time and TO_DATE({}, \'dd.mm.yyyy hh24:mi\') = a.end_time and a.doctor_id={}) '\
            .format(str(service_name), (doctor_id), "'"+start_date+"'", "'"+end_date+"'", str(appointment_id),"'"+end_date+"'","'"+start_date+"'", str(doctor_id), "'"+start_date+"'",
            "'"+start_date+"'", "'"+end_date+"'", "'"+start_date+"'", "'"+end_date+"'", str(doctor_id))

    print(query)
    cur = connection.cursor()
    cur.execute(query)
    cur.execute('commit')
    cur.close()
    return redirect("/appointments")

@app.route('/addAppointment', methods=['POST'])
def addAppointment():
    error = None
    cur = connection.cursor()
    cur2 = connection.cursor()
    cur3 = connection.cursor()
    patient_last_name = request.form['last_namePatient']
    patient_first_name = request.form['first_namePatient']

    cnp = request.form['cnp']
    doctor_last_name = request.form['last_nameDoctor']
    doctor_first_name = request.form['first_nameDoctor']
    service_name = request.form['service_name']

    start_date = request.form['start_date']
    start_time_h = request.form['start_time_h']
    start_time_m = request.form['start_time_m']
    end_date = request.form['end_date']
    end_time_h = request.form['end_time_h']
    end_time_m = request.form['end_time_m']
    
    start_date = str(start_date) + ", " + start_time_h + ":" + start_time_m
    end_date = str(end_date) + ", " + end_time_h + ":" + end_time_m
    start_date = datetime.strptime(start_date, '%Y-%m-%d, %H:%M').strftime('%d.%m.%Y %H:%M')
    end_date = datetime.strptime(end_date, '%Y-%m-%d, %H:%M').strftime('%d.%m.%Y %H:%M')

    cur2.execute('select patient_id from patient where cnp=' + str(cnp))
    for res in cur2:
        patient_id = res[0]

    cur3.execute('select doctor_id from doctor where last_name={} and first_name={}'.format("'"+doctor_last_name+"'", "'"+doctor_first_name+"'"))
    for res in cur3:
        doctor_id = res[0]
    
    query = 'INSERT INTO appointment (start_time, end_time, patient_id, service_id, doctor_id) select TO_DATE({}, \'dd.mm.yyyy hh24:mi\'), '\
        'TO_DATE({}, \'dd.mm.yyyy hh24:mi\'), p.patient_id, s.service_id, d.doctor_id from patient p, doctor d, service s where p.patient_id={} and s.service_id={} and d.doctor_id={} '\
        'and TO_DATE({}, \'dd.mm.yyyy hh24:mi\') > to_date({}, \'dd.mm.yyyy hh24:mi\') '\
        'and exists (select \'x\' from workSchedule w where w.doctor_id={} and lower(to_char(TO_DATE({}, \'dd.mm.yyyy hh24:mi\'), \'fmday\')) like lower(w.day) '\
        'and to_char(TO_DATE({}, \'dd.mm.yyyy hh24:mi\'), \'hh24:mi\') >= to_char(w.start_time, \'hh24:mi\') and to_char(TO_DATE({}, \'dd.mm.yyyy hh24:mi\'), \'hh24:mi\') <= to_char(w.end_time, \'hh24:mi\')) '\
        'and not exists ( select \'x\' from appointment a where TO_DATE({}, \'dd.mm.yyyy hh24:mi\')=a.start_time and TO_DATE({}, \'dd.mm.yyyy hh24:mi\') = a.end_time and a.doctor_id={})'\
            .format("'" + start_date + "'", "'" + end_date + "'", str(patient_id), str(service_name),str(doctor_id),"'"+end_date+"'", "'"+start_date+"'", str(doctor_id), "'"+start_date+"'",
             "'"+start_date+"'", "'"+end_date+"'", "'"+start_date+"'", "'"+end_date+"'", str(doctor_id))
    print(query)
    cur.execute(query)
    cur.execute('commit')
    cur.close()
    return redirect('/appointments')

@app.route('/deleteAppointment', methods=['post'])
def deleteAppointment():
    appointment = request.form['appointment_id']
    cur = connection.cursor()
    cur.execute('delete from appointment where appointment_id=' + appointment)
    cur.execute('commit')
    return redirect('/appointments')

@app.route('/addBill', methods=['POST'])
def addBill():
    error = None
    cur = connection.cursor()
    last_name = request.form['last_name']
    first_name = request.form['first_name']
    cnp = request.form['bill_cnp']
    service_name = request.form['bill_service_name']
    bill_date = request.form['bill_date']
    bill_time_h = request.form['bill_time_h']
    bill_time_m = request.form['bill_time_m']
    cur.close()
    bill_date = str(bill_date) + ", " + bill_time_h + ":" + bill_time_m
    bill_date = datetime.strptime(bill_date, '%Y-%m-%d, %H:%M').strftime('%d.%m.%Y %H:%M')

    cur = connection.cursor()

    query = 'insert into bill (appointment_id, total) SELECT a.appointment_id, s.price  FROM   appointment a, patient p, service s  where a.patient_id = p.patient_id and a.service_id = s.service_id '\
        'and p.cnp={} and s.service_id = {} and a.start_time= TO_DATE({}, \'dd.mm.yyyy hh24:mi\') and a.appointment_id not in (select appointment_id from bill) '\
        .format("'"+str(cnp)+"'", str(service_name), "'"+bill_date+"'")
    print(query)
    cur.execute(query)
    cur.execute('commit')
    cur.close()
    return redirect('/appointments')

@app.route('/deleteBill', methods=['post'])
def deleteBill():
    bill = request.form['bill_id']
    cur = connection.cursor()
    cur.execute('delete from bill where bill_id=' + bill)
    cur.execute('commit')
    return redirect('/appointments')

if __name__ == "__main__":
    app.run(host='localhost', port=8000, debug=True)
