import dlib
import numpy as np
import face_recognition_models
from sklearn.svm import SVC
import streamlit as st

from src.database.db import get_all_students


@st.cache_resource
def load_dlib_models():
    detector = dlib.get_frontal_face_detector()

    sp = dlib.shape_predictor(
        face_recognition_models.pose_predictor_model_location()
    )

    facerec = dlib.face_recognition_model_v1(
        face_recognition_models.face_recognition_model_location()
    )
    return detector,sp,facerec

def get_face_embeddings(image_np):
    detector , sp , facerec = load_dlib_models()
    faces = detector(image_np , 1)

    encodings = []

    for face in faces:
        shape = sp(image_np,face)
        face_descriptor = facerec.compute_face_descriptor(image_np,shape,1)

        encodings.append(np.array(face_descriptor))
    return encodings

def get_trained_model():
    X = []
    y = []

    students_db = get_all_students()

    if not students_db:
        return None

    for student in students_db:
        embedding = student.get("face_embedding")
        sid = student.get("student_id")

        if embedding and sid is not None:
            X.append(np.array(embedding))
            y.append(sid)

    # No face embeddings available
    if len(X) == 0:
        return None

    clf = None
    # SVC needs at least 2 different classes
    if len(set(y)) >= 2:
        clf = SVC(
            kernel="linear",
            probability=True,
            class_weight="balanced"
        )
        try:
            clf.fit(X, y)
        except ValueError as e:
            print("Model training failed:", e)
            clf = None

    return {
        "clf": clf,
        "X": X,
        "y": y
    }

def train_classifier():
    st.cache_resource.clear()

    model_data = get_trained_model()

    return model_data is not None

def predict_attendance(class_image_np):

    encodings = get_face_embeddings(class_image_np)

    detected_student = {}

    model_data = get_trained_model()

    if not model_data:
        return detected_student, [], len(encodings)

    clf = model_data.get("clf")
    X_train = model_data["X"]
    y_train = model_data["y"]

    all_students = sorted(list(set(y_train)))
    resemblance_threshold = 0.6

    for encoding in encodings:
        matched = False
        if clf is not None:
            try:
                predicted_id = int(clf.predict([encoding])[0])
                student_embedding = X_train[y_train.index(predicted_id)]
                best_match_score = np.linalg.norm(
                    student_embedding - encoding
                )
                if best_match_score <= resemblance_threshold:
                    detected_student[predicted_id] = True
                    matched = True
            except Exception:
                matched = False

        if not matched:
            # Distance-based matching fallback (works for single student and catches edge cases)
            best_sid = None
            min_dist = float("inf")
            for stored_emb, sid in zip(X_train, y_train):
                dist = np.linalg.norm(stored_emb - encoding)
                if dist < min_dist:
                    min_dist = dist
                    best_sid = sid
            if best_sid is not None and min_dist <= resemblance_threshold:
                detected_student[best_sid] = True

    return detected_student, all_students, len(encodings)