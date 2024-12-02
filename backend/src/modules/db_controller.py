from neo4j import GraphDatabase

class AttendanceSystem:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.faces = []
        self.face_names = []

    def close(self):
        self.driver.close()

    def close(self):
        self.driver.close()

    def load_faces_from_db(self):
        with self.driver.session() as session:
            result = session.run("MATCH (s:Student) RETURN s.face_data, s.first_name, s.last_name")
            for record in result:
                face_data = np.frombuffer(record['s.face_data'], dtype=np.uint8)
                face_encoding = face_recognition.face_encodings(face_data)
                if face_encoding:
                    self.faces.append(face_encoding[0])
                    full_name = f"{record['s.first_name']} {record['s.last_name']}"
                    self.face_names.append(full_name)

    def compare_faces(self, unknown_face_encoding):
        match_results = face_recognition.compare_faces(self.faces, unknown_face_encoding)
        identified_faces = [self.face_names[i] for i, match in enumerate(match_results) if match]
        return identified_faces

    def add_teacher(self, first_name, last_name, email, password_hash):
        with self.driver.session() as session:
            session.run(
                "CREATE (t:Teacher {first_name: $first_name, last_name: $last_name, email: $email, password_hash: $password_hash})",
                first_name=first_name, last_name=last_name, email=email, password_hash=password_hash
            )

    def add_student(self, first_name, last_name, email, face_data):
        with self.driver.session() as session:
            session.run(
                "CREATE (s:Student {first_name: $first_name, last_name: $last_name, email: $email, face_data: $face_data})",
                first_name=first_name, last_name=last_name, email=email, face_data=face_data
            )

    def add_class(self, address, class_name):
        with self.driver.session() as session:
            session.run(
                "CREATE (c:Class {address: $address, class_name: $class_name})",
                address=address, class_name=class_name
            )

    def add_lesson(self, date, time, class_name):
        with self.driver.session() as session:
            session.run(
                "MATCH (c:Class {class_name: $class_name}) "
                "CREATE (l:Lesson {date: $date, time: $time})-[:HAPPENS_IN]->(c)",
                date=date, time=time, class_name=class_name
            )

    def add_attendance(self, student_email, lesson_date, lesson_time):
        with self.driver.session() as session:
            session.run(
                "MATCH (s:Student {email: $student_email}), (l:Lesson {date: $lesson_date, time: $lesson_time}) "
                "CREATE (s)-[:ATTENDED]->(l)",
                student_email=student_email, lesson_date=lesson_date, lesson_time=lesson_time
            )

    def get_teachers(self):
        with self.driver.session() as session:
            result = session.run("MATCH (t:Teacher) RETURN t")
            return [record['t'] for record in result]

    def get_students(self):
        with self.driver.session() as session:
            result = session.run("MATCH (s:Student) RETURN s")
            return [record['s'] for record in result]

    def get_classes(self):
        with self.driver.session() as session:
            result = session.run("MATCH (c:Class) RETURN c")
            return [record['c'] for record in result]

    def get_lessons(self):
        with self.driver.session() as session:
            result = session.run("MATCH (l:Lesson) RETURN l")
            return [record['l'] for record in result]

    def get_student_attendance(self, student_email):
        with self.driver.session() as session:
            result = session.run(
                "MATCH (s:Student {email: $student_email})-[:ATTENDED]->(l:Lesson) RETURN l",
                student_email=student_email
            )
            return [record['l'] for record in result]

    def get_teacher_classes(self, teacher_email):
        with self.driver.session() as session:
            result = session.run(
                "MATCH (t:Teacher {email: $teacher_email})-[r:TEACHING_IN]->(c:Class) RETURN c",
                teacher_email=teacher_email
            )
            return [record['c'] for record in result]

    def delete_teacher(self, email):
        with self.driver.session() as session:
            session.run("MATCH (t:Teacher {email: $email}) DELETE t", email=email)

    def delete_student(self, email):
        with self.driver.session() as session:
            session.run("MATCH (s:Student {email: $email}) DELETE s", email=email)

    def delete_class(self, class_name):
        with self.driver.session() as session:
            session.run("MATCH (c:Class {class_name: $class_name}) DELETE c", class_name=class_name)

    def delete_attendance(self, student_email, lesson_date, lesson_time):
        with self.driver.session() as session:
            session.run(
                "MATCH (s:Student {email: $student_email})-[a:ATTENDED]->(l:Lesson {date: $lesson_date, time: $lesson_time}) "
                "DELETE a",
                student_email=student_email, lesson_date=lesson_date, lesson_time=lesson_time
            )

    def update_teacher(self, email, first_name=None, last_name=None, password_hash=None):
        with self.driver.session() as session:
            if first_name:
                session.run("MATCH (t:Teacher {email: $email}) SET t.first_name = $first_name", email=email, first_name=first_name)
            if last_name:
                session.run("MATCH (t:Teacher {email: $email}) SET t.last_name = $last_name", email=email, last_name=last_name)
            if password_hash:
                session.run("MATCH (t:Teacher {email: $email}) SET t.password_hash = $password_hash", email=email, password_hash=password_hash)

    def update_student(self, email, first_name=None, last_name=None, face_data=None):
        with self.driver.session() as session:
            if first_name:
                session.run("MATCH (s:Student {email: $email}) SET s.first_name = $first_name", email=email, first_name=first_name)
            if last_name:
                session.run("MATCH (s:Student {email: $email}) SET s.last_name = $last_name", email=email, last_name=last_name)
            if face_data:
                session.run("MATCH (s:Student {email: $email}) SET s.face_data = $face_data", email=email, face_data=face_data)

    def update_class(self, class_name, address=None):
        with self.driver.session() as session:
            if address:
                session.run("MATCH (c:Class {class_name: $class_name}) SET c.address = $address", class_name=class_name, address=address)

    def update_lesson(self, lesson_date, lesson_time, new_date=None, new_time=None):
        with self.driver.session() as session:
            if new_date:
                session.run("MATCH (l:Lesson {date: $lesson_date, time: $lesson_time}) SET l.date = $new_date", lesson_date=lesson_date, lesson_time=lesson_time, new_date=new_date)
            if new_time:
                session.run("MATCH (l:Lesson {date: $lesson_date, time: $lesson_time}) SET l.time = $new_time", lesson_date=lesson_date, lesson_time=lesson_time, new_time=new_time)

    def get_attendance_for_lesson(self, lesson_date, lesson_time):
        with self.driver.session() as session:
            result = session.run(
                "MATCH (l:Lesson {date: $lesson_date, time: $lesson_time})<-[:ATTENDED]-(s:Student) "
                "RETURN s",
                lesson_date=lesson_date, lesson_time=lesson_time
            )
            return [record['s'] for record in result]