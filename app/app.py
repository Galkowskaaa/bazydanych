from flask import Flask, render_template, request, redirect, url_for, session
import pyodbc
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'sekretny_klucz'

def connect_to_db():
    return pyodbc.connect(
        'Driver={SQL Server};'
        'Server=DESKTOP-01EETR2\SQLEXPRESS01;'
        'Database=zawody_konne;'
        'Trusted_Connection=yes;'
    )

def is_admin():
    return session.get('rola') == 'Administrator'

@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login_register'))

    with connect_to_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Konkursy")
        konkursy = cursor.fetchall()
        cursor.execute("SELECT * FROM Zawodnicy")
        zawodnicy = cursor.fetchall()
        cursor.execute("SELECT * FROM Konie")
        konie = cursor.fetchall()
        cursor.execute("SELECT * FROM Wyniki")
        wyniki = cursor.fetchall()
        cursor.execute("SELECT * FROM Przejazdy")
        przejazdy = cursor.fetchall()
    return render_template('index.html', konkursy=konkursy, zawodnicy=zawodnicy, konie=konie, wyniki=wyniki, przejazdy=przejazdy, session=session)

@app.route('/login_register', methods=['GET', 'POST'])
def login_register():
    error = None
    if request.method == 'POST':
        form_type = request.form.get('form_type')
        
        if 'email' in request.form and 'password' in request.form and 'imie' not in request.form:
            # Handling login
            email = request.form['email']
            password = request.form['password']
            with connect_to_db() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM Uzytkownicy WHERE Email = ?", (email,))
                user = cursor.fetchone()
            if user and check_password_hash(user[4], password):
                session['user_id'] = user[0]
                session['rola'] = user[5]
                return redirect(url_for('index'))
            else:
                error = 'Invalid email or password'
        elif 'imie' in request.form and 'nazwisko' in request.form and 'email' in request.form and 'haslo' in request.form and 'rola' in request.form and 'pesel' in request.form:
            # Handling registration
            imie = request.form['imie']
            nazwisko = request.form['nazwisko']
            email = request.form['email']
            haslo = generate_password_hash(request.form['haslo'])
            rola = request.form['rola']
            pesel = request.form['pesel']
            with connect_to_db() as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO Uzytkownicy (Imie, Nazwisko, Email, Haslo, Rola, PESEL) VALUES (?, ?, ?, ?, ?, ?)",
                               (imie, nazwisko, email, haslo, rola, pesel))
                conn.commit()
            return redirect(url_for('login_register'))
    return render_template('login_register.html', error=error)

@app.route('/logout', methods=['GET'])
def logout():
    session.clear()
    return redirect(url_for('login_register'))

@app.route('/dodaj_konkurs', methods=['POST'])
def dodaj_konkurs():
    if not is_admin():
        return redirect(url_for('index'))

    nazwa = request.form['nazwa']
    poczatek = request.form['poczatek']
    koniec = request.form['koniec']
    miejsce = request.form['miejsce']
    with connect_to_db() as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Konkursy (NazwaKonkursu, DataRozpoczecia, DataZakonczenia, Miejsce) VALUES (?, ?, ?, ?)",
                       (nazwa, poczatek, koniec, miejsce))
        conn.commit()
    return redirect(url_for('index'))

@app.route('/rejestracja_uczestnictwa', methods=['POST'])
def rejestracja_uczestnictwa():
    if not is_admin():
        return redirect(url_for('index'))

    zawodnik_id = request.form['zawodnik_id']
    konkurs_id = request.form['konkurs_id']
    kon_id = request.form['kon_id']
    start_przejazdu = request.form['start_przejazdu']
    koniec_przejazdu = request.form['koniec_przejazdu']
    czas_przejazdu = request.form['czas_przejazdu']
    with connect_to_db() as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Przejazdy (StartPrzejazdu, KoniecPrzejazdu, CzasPrzejazdu, KonkursID, ZawodnikID, KonID) VALUES (?, ?, ?, ?, ?, ?)",
                       (start_przejazdu, koniec_przejazdu, czas_przejazdu, konkurs_id, zawodnik_id, kon_id))
        conn.commit()
    return redirect(url_for('index'))

@app.route('/zarzadzanie_zawodnikami', methods=['POST'])
def zarzadzanie_zawodnikami():
    if not is_admin():
        return redirect(url_for('index'))

    imie = request.form['imie']
    nazwisko = request.form['nazwisko']
    data_urodzenia = request.form['data_urodzenia']
    kraj_pochodzenia = request.form['kraj_pochodzenia']
    miasto_pochodzenia = request.form['miasto_pochodzenia']
    poziom_umiejetnosci = request.form['poziom_umiejetnosci']
    with connect_to_db() as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Zawodnicy (Imie, Nazwisko, DataUrodzenia, KrajPochodzenia, MiastoPochodzenia, PoziomUmiejetnosci) VALUES (?, ?, ?, ?, ?, ?)",
                       (imie, nazwisko, data_urodzenia, kraj_pochodzenia, miasto_pochodzenia, poziom_umiejetnosci))
        conn.commit()
    return redirect(url_for('index'))

@app.route('/usun_zawodnika', methods=['POST'])
def usun_zawodnika():
    if not is_admin():
        return redirect(url_for('index'))

    zawodnik_id = request.form['zawodnik_id']
    with connect_to_db() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Zawodnicy WHERE ZawodnikID = ?", (zawodnik_id,))
        conn.commit()
    return redirect(url_for('index'))

@app.route('/zarzadzanie_konmi', methods=['POST'])
def zarzadzanie_koniami():
    if not is_admin():
        return redirect(url_for('index'))

    imie = request.form['imie']
    rasa = request.form['rasa']
    wiek = request.form['wiek']
    wlasciciel_id = request.form['wlasciciel_id']
    with connect_to_db() as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Konie (Imie, Rasa, Wiek, WlascicielID) VALUES (?, ?, ?, ?)",
                       (imie, rasa, wiek, wlasciciel_id))
        conn.commit()
    return redirect(url_for('index'))

@app.route('/usun_konia', methods=['POST'])
def usun_konia():
    if not is_admin():
        return redirect(url_for('index'))

    kon_id = request.form['kon_id']
    with connect_to_db() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Konie WHERE KonID = ?", (kon_id,))
        conn.commit()
    return redirect(url_for('index'))

@app.route('/rejestracja_wynikow', methods=['POST'])
def rejestracja_wynikow():
    if not is_admin():
        return redirect(url_for('index'))

    wynik = request.form['wynik']
    ilosc_bledow = request.form['ilosc_bledow']
    data_wyniku = request.form['data_wyniku']
    konkurs_id = request.form['konkurs_id']
    zawodnik_id = request.form['zawodnik_id']
    kon_id = request.form['kon_id']
    with connect_to_db() as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Wyniki (Wynik, IloscBledow, DataWyniku, KonkursID, ZawodnikID, KonID) VALUES (?, ?, ?, ?, ?, ?)",
                       (wynik, ilosc_bledow, data_wyniku, konkurs_id, zawodnik_id, kon_id))
        conn.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
