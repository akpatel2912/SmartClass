import streamlit as st
from src.UI.base_layout import style_background_dashboard, style_base_layout 
from src.components.header import header_dashboard 
from src.components.footer import footer_dashboard
import numpy as np
from PIL import Image
from src.pipelines.face_pipeline import predict_attendance, get_face_embeddings, train_classifier
from src.pipelines.voice_pipeline import get_voice_embeddings
from src.database.db import get_all_students, create_student, get_student_subjects, get_student_attendance, unenroll_student_to_subject
import time
from src.components.dialogue_enroll import enroll_dialogue
from src.components.subject_card import subject_card


def student_dashboard():
    student_data = st.session_state.student_data
    student_id = student_data["student_id"]
    c1, c2 = st.columns(2,vertical_alignment="center",gap="xxlarge")

    with c1:
        header_dashboard()
    with c2:
        st.markdown(
        f"""
        <h3 class="teacher-welcome">
            Welcome, {student_data['name']}
        </h3>
        """,
        unsafe_allow_html=True)
        if st.button("Logout", type="secondary",key="student_logout_btn",shortcut="control+backspace"):
            st.session_state["is_logged_in"] = False
            del st.session_state.student_data
            st.rerun()


    st.space()

    c1,c2 = st.columns(2)
    with c1:
        st.header("Your Enrolled Subjects")
    with c2:
        if st.button("Enroll in Subject",type="primary",width="stretch"):
            enroll_dialogue()
    
    st.divider()

    with st.spinner('Loading your enrolled subjects..'):
        subjects = get_student_subjects(student_id)
        logs = get_student_attendance(student_id)

    stats_map = {}

    for log in logs:
        sid = log['subject_id']

        if sid not in stats_map:
            stats_map[sid] = {"total":0, "attended": 0}

        stats_map[sid]['total'] +=1

        if log.get('is_present'):
            stats_map[sid]['attended'] += 1


    cols = st.columns(2)
    for i, sub_node in enumerate(subjects):
        sub = sub_node['subjects']
        sid = sub['subject_id']

        stats = stats_map.get(sid,{"total":0, "attended": 0} )

        def make_unenroll_button(s_id, s_name):
            def unenroll_button():
                if st.button("Unenroll from this course", type='tertiary', width='stretch', icon=':material/delete_forever:', key=f"unenroll_{s_id}"):
                    unenroll_student_to_subject(student_id, s_id)
                    st.toast(f"Unenrolled from {s_name} successfully!")
                    st.rerun()
            return unenroll_button

        with cols[i % 2]:

            subject_card(
                name = sub['name'],
                code = sub['subject_code'],
                section = sub['section'],
                stats = [
                    ('📅', 'Total', stats['total']),
                    ('✅', 'Attended', stats['attended']),
                ],
                footer_callback=make_unenroll_button(sid, sub['name'])
            )


    footer_dashboard()
    style_background_dashboard()
    style_base_layout()

# Backward compatibility alias
student_dashbaord = student_dashboard
    

def student_screen():

    style_background_dashboard()
    style_base_layout()

    if "show_registration" not in st.session_state:
        st.session_state.show_registration = False

    c1, c2 = st.columns(2,vertical_alignment="center",gap="xxlarge")
    with c1:
        header_dashboard()
    with c2:
        if st.button("Go back to Home", type="secondary",key="loginbackbtn",shortcut="control+backspace"):
            st.session_state["login_type"] = None
            st.session_state["show_registration"] = False
            st.rerun()

    st.header("Login using FaceID",text_alignment="center")
    st.space()
    st.space()


    show_registration = False
    photo_source = st.camera_input("Position your face in the center \U0001F604")

    if photo_source:
        img = np.array(Image.open(photo_source))

        with st.spinner("Ai is Scanning ..."):
            detected  , all_ids , num_faces = predict_attendance(img)

            if num_faces == 0:
                st.warning("Face not found !")
            elif num_faces > 1 :
                st.warning("Multiple Faces Found !")
            else:
                if detected:
                    student_id = list(detected.keys())[0]
                    all_students = get_all_students()
                    student = next((s for s in all_students if s["student_id"] == student_id),None)

                    if student:
                        st.session_state.is_logged_in = True
                        st.session_state.user_role = "student"
                        st.session_state.student_data = student
                        st.toast(f"Welcome Back {student['name']}")
                        time.sleep(1)
                        st.rerun()
                else:
                    st.info("Face not recognized ! You might be a New Student")
                    st.session_state.show_registration = True

    if st.session_state.show_registration:

        with st.container(border=True):
            st.markdown("<h2 style='color:#17172B;'>Register new Profile</h2>", unsafe_allow_html=True)
            new_name = st.text_input("Enter your name", placeholder='E.g. Hamza Rizvi')

            st.markdown("<h3 style='color:#17172B;'>Optional : Voice Enrollment</h3>", unsafe_allow_html=True)
            
            st.info("Enroll for your voice only attendance")

            audio_data = None

            try:
                audio_data = st.audio_input('Record a short phrase like I am present, My name is Akash.')
            except Exception:
                st.error('Audio Data failed!')

            if st.button('Create Account', type='primary'):
                if not new_name:
                    st.warning('Please enter your name!')
                elif not photo_source:
                    st.warning('Please capture your photo with the camera above to register!')
                else:
                    with st.spinner('Creating profile..'):
                        img = np.array(Image.open(photo_source))
                        encodings = get_face_embeddings(img)
                        if encodings:
                            face_emb = encodings[0].tolist()

                            voice_emb = None
                            if audio_data:
                                voice_emb = get_voice_embeddings(audio_data.read())

                            response_data = create_student(new_name, face_embedding=face_emb, voice_embedding=voice_emb)

                            if response_data:
                                train_classifier()
                                st.session_state.is_logged_in = True
                                st.session_state.user_role = 'student'
                                st.session_state.student_data = response_data[0]
                                st.session_state.show_registration = False
                                st.toast(f'Profile Created! Hi {new_name}!')
                                time.sleep(1)
                                st.rerun()
                        else:
                            st.error('Could not capture your facial features for registration. Please try taking another photo.')





    footer_dashboard()