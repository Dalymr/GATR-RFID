from flask import Flask, render_template, request, redirect, url_for, jsonify
from datetime import datetime, timedelta
import mysql.connector
import jinja2
from Crypto.Cipher import AES
from binascii import unhexlify
from array import array

app = Flask(__name__)

# MySQL connection configuration goes here...
db = mysql.connector.connect(
    host='127.0.0.1',
    user='root',
    password='myadmin1502',
    database='gatrdb'
)
cursor = db.cursor()

# professor uid decryption from rfid
def decrypt_id(encrypted_id, key):
    cipher = AES.new(key, AES.MODE_ECB)
    decrypted_id = cipher.decrypt(encrypted_id)
    return decrypted_id.encode('utf-8')

# get all classes id
def get_classes():
    # Fetch the list of classes from the 'classes' table
    cursor.execute("SELECT idclasse FROM classes")
    return [row[0] for row in cursor.fetchall()]


# get all subjects id
def get_subjects():
    # Fetch the list of subjects from the 'matieres' table
    cursor.execute("SELECT idmatiere FROM matieres")
    return [row[0] for row in cursor.fetchall()]


# get all rooms id
def get_rooms():
    # Fetch the list of rooms from the 'salles' table
    cursor.execute("SELECT idsalle FROM salles")
    return [row[0] for row in cursor.fetchall()]




#create a session in sql
def create_new_session(session_info):
    try:

        # Insert the new session into the 'seancesetablis' table
        sql = """INSERT INTO seancesetablis 
                 (idseance,idenseignant, idclasse, idmatiere ,idsalle,presenceenseignat) 
                 VALUES (%s, %s, %s, %s, %s, %s)"""
        
        values = (session_info[0], session_info[3], session_info[2], session_info[1], session_info[6],1)
        cursor.execute(sql, values)

        # Commit the changes to the database
        db.commit()

        return session_info[0], session_info[3]
    except Exception as e:
        # Rollback in case of an error
        db.rollback()
        raise e




#starting session by web
@app.route('/start_session', methods=['GET', 'POST'])
def start_session():
    if request.method == 'POST':
        try:
            class_id = request.form['class']
            subject = request.form['subject']
            start_time = request.form['start_time']
            end_time = request.form['end_time']
            room = request.form['room']

            # Format the date-time strings into Python datetime objects
            start_time = datetime.strptime(start_time, '%Y-%m-%dT%H:%M')
            end_time = datetime.strptime(end_time, '%Y-%m-%dT%H:%M')

            # Insert the session details into the database
            session_id = create_new_session(professor_id, class_id, subject, start_time, end_time, room)

            # Fetch additional session details based on session_id from the database
            # You may need to adapt this based on your database structure
            # For example, you can fetch the start and end times of the session
            session_details = get_session_details(session_id)

            # Redirect to the session_started route with session data
            return redirect(url_for('session_started', session_id=session_id, professor_id=professor_id, session_details=session_details))
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)})

    # Fetch the list of classes, subjects, and rooms from the database
    classes = get_classes()
    subjects = get_subjects()
    rooms = get_rooms()

    return render_template('start_session.html', classes=classes, subjects=subjects, rooms=rooms)




#starting session by rfid scan
def start_professor_session(uid,salleid):
    try:
            
        current_timestamp = datetime.now()
        print(current_timestamp)

        # Allow a 15-minute grace period for early or late scans
        grace_period = timedelta(minutes=10)
        print(grace_period)

        # Calculate the time range for the query
        start_time_range = (current_timestamp - grace_period).strftime('%Y-%m-%d %H:%M:%S')
        end_time_range = (current_timestamp + grace_period).strftime('%Y-%m-%d %H:%M:%S')
        print(start_time_range)

        # Check if there's an active session for the professor within the grace period
        cursor.execute(
            "SELECT * FROM seances WHERE idenseignant = %s AND (dateheuredebut BETWEEN %s AND %s)",
            (uid, start_time_range, end_time_range)
        )

        # Fetch the session information
        session_info = cursor.fetchone()
        print(session_info)
        # Check if a session exists
        if session_info:
            # Active session found
                try:
                    create_new_session(session_info)
                    print('Session created successfully.')
                    print('Session started for professor:', session_info['idenseignant'])
                except Exception as e:
                    print('Error creating session:', e)
                return True
        else:
            # No active session
            print('No active session found for professor:', uid)
            return False
    except Exception as e:
        print('Error checking for active professor session:', e)
        return False
    
    
@app.route('/get_rfid_data', methods=['POST'])
def get_rfid_data():
    try:
        if request.method == 'POST':
            try:
                json_data = request.get_json()
            except Exception as json_error:
                print(json_error)
                return jsonify({'error': 'Failed to parse JSON data'})

            try:
                idsalle = json_data['idsalle']
            except KeyError:
                return jsonify({'error': 'Missing required field: idsalle'})

            try:
                professor_id = json_data['cardID']
            except KeyError:
                return jsonify({'error': 'Missing required field: cardID'})

            try:
                start_professor_session(professor_id, idsalle)
            except Exception as session_error:
                print(session_error)
                return jsonify({'error': 'Failed to start professor session'})

            return '', 200  # Return success
        else:
            return jsonify({'message': 'Invalid request method'})
    except Exception as e:
        print(e)
        return jsonify({'errorbruh': str(e)})




#display running session details
def get_session_details(session_id):
    try:
        # Fetch the necessary details from the 'seances' table based on session_id
        cursor.execute("""
            SELECT idenseignant, idmatiere, dateheuredebut, dateheurefin 
            FROM seances 
            WHERE idseance = %s
        """, (session_id,))
        result = cursor.fetchone()

        if result:
            professor_id = result[0]
            matiere_id = result[1]
            start_time = result[2]
            end_time = result[3]

            # You may fetch additional details based on your needs

            return {
                'professor_id': professor_id,
                'matiere_id': matiere_id,
                'start_time': start_time,
                'end_time': end_time,
                # Add more details as needed
            }
        else:
            return None  # Session not found

    except Exception as e:
        # Handle exceptions as needed
        return None
    
    
@app.route('/session_started')
def get_session_details(session_id):
    # Fetch additional session details based on session_id from the database
    # You may need to adapt this based on your database structure
    # For example, you can fetch the start and end times of the session
    cursor.execute("SELECT idenseignant,idmatiere, dateheuredebut, dateheurefin FROM seances WHERE idseance = %s", (session_id,))
    session_details = cursor.fetchone()
    return {'professor_id': session_details[0], 'subject' : session_details[1],'start_time' :session_details[2], 'end_time': session_details[3]}

# Rest of the code remains the same...

if __name__ == '__main__':
    key = b'whatkeymamamia??'
    app.run(debug=True)
    
