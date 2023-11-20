from flask import Flask, render_template, request, redirect, url_for, jsonify
from datetime import datetime, timedelta
import mysql.connector
import jinja2

app = Flask(__name__)

# MySQL connection configuration goes here...
db = mysql.connector.connect(
    host='127.0.0.1',
    user='root',
    password='myadmin1502',
    database='gatrdb'
)
cursor = db.cursor()

def get_classes():
    # Fetch the list of classes from the 'classes' table
    cursor.execute("SELECT idclasse FROM classes")
    return [row[0] for row in cursor.fetchall()]

def get_subjects():
    # Fetch the list of subjects from the 'matieres' table
    cursor.execute("SELECT idmatiere FROM matieres")
    return [row[0] for row in cursor.fetchall()]

def get_rooms():
    # Fetch the list of rooms from the 'salles' table
    cursor.execute("SELECT idsalle FROM salles")
    return [row[0] for row in cursor.fetchall()]

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
            session_id, professor_id = create_new_session(class_id, subject, start_time, end_time, room)

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
def session_started():
    session_id = request.args.get('session_id')

    # Fetch additional session details based on session_id from the database
    session_details = get_session_details(session_id)

    if session_details:
        # If session details are found, render the template
        return render_template('session_started.html', session_id=session_id, session_details=session_details)
    else:
        # If session is not found, you can handle it appropriately (e.g., redirect to an error page)
        return render_template('session_not_found.html')


def create_new_session(class_id, subject, start_time, end_time, room):
    try:
        # Generate a unique session ID (you may use a better method)
        session_id = f"session_{datetime.now().strftime('%Y%m%d%H%M%S')}"

        # Fetch the professor ID (you need to implement this logic)
        professor_id = 'ES0001'

        # Insert the new session into the 'seances' table
        sql = """INSERT INTO seances 
                 (idseance, idmatiere, idclasse, idenseignant, dateheuredebut, dateheurefin, idsalle,presenceenseignant) 
                 VALUES (%s, %s, %s, %s, %s, %s, %s,%s)"""
        
        values = (session_id, subject, class_id, professor_id, start_time, end_time, room,1)
        cursor.execute(sql, values)

        # Commit the changes to the database
        db.commit()

        return session_id, professor_id
    except Exception as e:
        # Rollback in case of an error
        db.rollback()
        raise e

def get_session_details(session_id):
    # Fetch additional session details based on session_id from the database
    # You may need to adapt this based on your database structure
    # For example, you can fetch the start and end times of the session
    cursor.execute("SELECT idenseignant,idmatiere, dateheuredebut, dateheurefin FROM seances WHERE idseance = %s", (session_id,))
    session_details = cursor.fetchone()
    return {'professor_id': session_details[0], 'subject' : session_details[1],'start_time' :session_details[2], 'end_time': session_details[3]}

# Rest of the code remains the same...

if __name__ == '__main__':
    app.run(debug=True)
