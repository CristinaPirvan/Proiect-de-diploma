from flask import Flask, render_template, request, redirect, url_for, session, flash
import cx_Oracle

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a strong secret key

# Oracle database connection setup
dsn = cx_Oracle.makedsn("localhost", 1521, service_name="XE")
connection = cx_Oracle.connect(user="hr", password="hr", dsn=dsn)

@app.route('/')
def home():
    return render_template('Cristina.html')

@app.route('/locatii')
def locatii():
    return render_template('Locatii.html')

@app.route('/despre_noi')
def despre_noi():
    cursor = connection.cursor()
    cursor.execute("""
        SELECT denumire, tip_eveniment, data_ev, locatia, interval_orar, descriere 
        FROM Evenimente
    """)
    evenimente = cursor.fetchall()

    return render_template('Despre_Noi.html', evenimente=evenimente)


@app.route('/login', methods=['POST'])
def login():
    id_copil = request.form['id_copil']
    parola = request.form['parola']

    cursor = connection.cursor()
    cursor.execute("SELECT * FROM Copii WHERE id_copil = :id_copil", [id_copil])
    user = cursor.fetchone()

    if user and user[6] == parola:  # Assuming parola is in the 7th column (index 6)
        session['id_copil'] = user[0]
        session['nume'] = user[1]
        session['prenume'] = user[2]
        return redirect(url_for('welcome'))
    else:
        flash('Invalid ID Copil or Parola.', 'danger')
        return redirect(url_for('home'))


@app.route('/welcome')
def welcome():
    if 'id_copil' in session:
        id_copil = session['id_copil']
        
        # Fetching copil details
        cursor = connection.cursor()
        cursor.execute("""
            SELECT c.id_copil, c.nume, c.prenume, c.data_inscrierii_la_gradinita, c.data_nasterii, 
                   cl.denumire, cl.sala, cl.an_scolar, cl.id_gradi, cl.id_grupa, c.email
            FROM Copii c
            JOIN Clase cl ON c.id_clase = cl.id_clase
            WHERE c.id_copil = :id_copil
        """, [id_copil])
        copil = cursor.fetchone()

        # Fetching imputerniciti
        cursor.execute("""
            SELECT i.nume, i.prenume, ci.statut_apartinator 
            FROM Imputerniciti i
            JOIN copii_imputernicitilor ci ON i.id_apart = ci.id_apart
            WHERE ci.id_copil = :id_copil
        """, [id_copil])
        imputerniciti = cursor.fetchall()

        # Fetching aptitudini
        cursor.execute("""
            SELECT a.denumire, a.descriere 
            FROM aptitudini a
            JOIN copii_aptitudini ca ON a.id_aptit = ca.id_aptit
            WHERE ca.id_copil = :id_copil
        """, [id_copil])
        aptitudini = cursor.fetchall()

        # Fetching absente
        cursor.execute("""
            SELECT data_absen, data_revenirii, motiv 
            FROM Evidenta_absente 
            WHERE id_copil = :id_copil
        """, [id_copil])
        absente = cursor.fetchall()

        return render_template('welcome.html', 
                               id_copil=copil[0], nume=copil[1], prenume=copil[2],
                               data_inscrierii_la_gradinita=copil[3], data_nasterii=copil[4], 
                               denumire_clase=copil[5], sala_clase=copil[6], an_scolar_clase=copil[7], 
                               id_gradi=copil[8], id_grupa=copil[9], email=copil[10],
                               imputerniciti=imputerniciti, aptitudini=aptitudini,
                               absente=absente)
    else:
        return redirect(url_for('home'))




@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
