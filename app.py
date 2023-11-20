from flask import Flask, render_template, request, redirect, url_for, jsonify
from datetime import datetime
import mysql.connector

app = Flask(__name__)

# MySQL connection configuration goes here...
db = mysql.connector.connect(
    host='127.0.0.1',
    user='root',
    password='myadmin1502',
    database='gatrdb'
)
cursor = db.cursor()

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
            session_id = create_new_session(class_id, subject, start_time, end_time, room)

            return jsonify({'status': 'success', 'session_id': session_id})
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)})

    # Fetch the list of classes, subjects, and rooms from the database
    classes = get_classes()
    subjects = get_subjects()
    rooms = get_rooms()

    return render_template('start_session.html', classes=classes, subjects=subjects, rooms=rooms)

def create_new_session(class_id, subject, start_time, end_time, room):
    try:
        # Generate a unique session ID (you may use a better method)
        session_id = f"session_{datetime.now().strftime('%Y%m%d%H%M%S')}"

        # Insert the new session into the 'seances' table
        sql = """INSERT INTO seances 
                 (idseance, idmatiere, idclasse, idenseignant, dateheuredebut, dateheurefin, idsalle,presenceenseignant) 
                 VALUES (%s, %s, %s, %s, %s, %s, %s,%s)"""
        
        values = (session_id, subject, class_id, 'ES0001', start_time, end_time, room,1)
        cursor.execute(sql, values)

        # Commit the changes to the database
        db.commit()

        return session_id
    except Exception as e:
        # Rollback in case of an error
        db.rollback()
        raise e

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

if __name__ == '__main__':
    app.run(debug=True)
