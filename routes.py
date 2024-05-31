from datetime import datetime
import io
from flask import Response, render_template, redirect, send_from_directory, url_for, request, flash, jsonify, make_response, abort
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import csv
from io import StringIO
from fpdf import FPDF
from models import StudyPlan, db, User, StudySession, Achievement
from forms import LoginForm, RegistrationForm, StudyPlanForm, StudySessionForm, AchievementForm
import os

def init_routes(app):
    @app.route('/')
    def home():
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
        return render_template('index.html')

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        form = RegistrationForm()
        if form.validate_on_submit():
            hashed_password = generate_password_hash(form.password.data, method='pbkdf2:sha256')
            new_user = User(username=form.username.data, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            flash('Konto zostało utworzone!', 'success')
            return redirect(url_for('login'))
        return render_template('register.html', form=form)

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        form = LoginForm()
        if form.validate_on_submit():
            user = User.query.filter_by(username=form.username.data).first()
            if user and check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember.data)
                return redirect(url_for('dashboard'))
            flash('Nieudane logowanie. Sprawdź nazwę użytkownika i hasło', 'danger')
        return render_template('login.html', form=form)

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        flash('Zostałeś wylogowany.', 'success')
        return redirect(url_for('login'))
    
    @app.route('/dashboard')
    @login_required
    def dashboard():
        study_sessions = StudySession.query.filter_by(user_id=current_user.id).all()
        achievements = Achievement.query.filter_by(user_id=current_user.id).all()
        study_form = StudySessionForm()
        achievement_form = AchievementForm()
        plan_form = StudyPlanForm()
        study_plans = StudyPlan.query.filter_by(user_id=current_user.id).all()
        return render_template('dashboard.html', name=current_user.username, study_form=study_form, achievement_form=achievement_form, plan_form=plan_form, study_sessions=study_sessions, achievements=achievements, study_plans=study_plans)

    @app.route('/add_session', methods=['POST'])
    @login_required
    def add_session():
        form = StudySessionForm()
        if form.validate_on_submit():
            new_session = StudySession(
                subject=form.subject.data,
                duration=form.duration.data,
                date=form.session_date.data,
                user_id=current_user.id
            )
            db.session.add(new_session)
            db.session.commit()
            flash('Sesja nauki została dodana!', 'success')
            return redirect(url_for('dashboard'))
        
        study_sessions = StudySession.query.filter_by(user_id=current_user.id).all()
        achievements = Achievement.query.filter_by(user_id=current_user.id).all()
        achievement_form = AchievementForm()
        plan_form = StudyPlanForm()
        study_plans = StudyPlan.query.filter_by(user_id=current_user.id).all()
        return render_template('dashboard.html', name=current_user.username, study_form=form, achievement_form=achievement_form, plan_form=plan_form, study_sessions=study_sessions, achievements=achievements, study_plans=study_plans)

    @app.route('/delete_session/<int:session_id>', methods=['POST'])
    @login_required
    def delete_session(session_id):
        session = StudySession.query.get_or_404(session_id)
        if session.user_id != current_user.id:
            abort(403)
        db.session.delete(session)
        db.session.commit()
        flash('Sesja nauki została usunięta.', 'success')
        return redirect(url_for('dashboard'))

    @app.route('/add_achievement', methods=['POST'])
    @login_required
    def add_achievement():
        form = AchievementForm()
        if form.validate_on_submit():
            new_achievement = Achievement(
                description=form.description.data,
                subject=form.subject.data,
                date=form.achievement_date.data,
                user_id=current_user.id
            )
            db.session.add(new_achievement)
            db.session.commit()
            flash('Osiągnięcie zostało dodane!', 'success')
            return redirect(url_for('dashboard'))
        
        study_sessions = StudySession.query.filter_by(user_id=current_user.id).all()
        achievements = Achievement.query.filter_by(user_id=current_user.id).all()
        study_form = StudySessionForm()
        plan_form = StudyPlanForm()
        study_plans = StudyPlan.query.filter_by(user_id=current_user.id).all()
        return render_template('dashboard.html', name=current_user.username, study_form=study_form, achievement_form=form, plan_form=plan_form, study_sessions=study_sessions, achievements=achievements, study_plans=study_plans)


    @app.route('/delete_achievement/<int:achievement_id>', methods=['POST'])
    @login_required
    def delete_achievement(achievement_id):
        achievement = Achievement.query.get_or_404(achievement_id)
        if achievement.user_id != current_user.id:
            abort(403)
        db.session.delete(achievement)
        db.session.commit()
        flash('Osiągnięcie zostało usunięte.', 'success')
        return redirect(url_for('dashboard'))
    
    @app.route('/add_plan', methods=['POST'])
    @login_required
    def add_plan():
        form = StudyPlanForm()
        if form.validate_on_submit():
            new_plan = StudyPlan(
                subject=form.subject.data,
                planned_date=form.planned_date.data,
                user_id=current_user.id
            )
            db.session.add(new_plan)
            db.session.commit()
            flash('Plan nauki został dodany!', 'success')
            return redirect(url_for('dashboard'))
        
        study_sessions = StudySession.query.filter_by(user_id=current_user.id).all()
        achievements = Achievement.query.filter_by(user_id=current_user.id).all()
        study_form = StudySessionForm()
        achievement_form = AchievementForm()
        plan_form = form
        study_plans = StudyPlan.query.filter_by(user_id=current_user.id).all()
        return render_template('dashboard.html', name=current_user.username, study_form=study_form, achievement_form=achievement_form, plan_form=plan_form, study_sessions=study_sessions, achievements=achievements, study_plans=study_plans)
    
    @app.route('/delete_plan/<int:plan_id>', methods=['POST'])
    @login_required
    def delete_plan(plan_id):
        plan = StudyPlan.query.get_or_404(plan_id)
        if plan.user_id != current_user.id:
            abort(403)
        db.session.delete(plan)
        db.session.commit()
        flash('Plan nauki został usunięty.', 'success')
        return redirect(url_for('dashboard'))

    @app.route('/stats')
    @login_required
    def stats():
        user_id = current_user.id

        study_sessions = StudySession.query.filter_by(user_id=user_id).all()
        study_plans = StudyPlan.query.filter_by(user_id=user_id).all()
        achievements = Achievement.query.filter_by(user_id=user_id).all()

        if not (study_sessions or study_plans or achievements):
            flash('Brak danych do wygenerowania wykresów.', 'warning')
            return render_template('advanced_stats.html', study_sessions=[], study_plans=[], achievements=[])

        return render_template('advanced_stats.html', study_sessions=study_sessions, study_plans=study_plans, achievements=achievements)

    @app.route('/generate_advanced_plot')
    @login_required
    def generate_advanced_plot():
        user_id = current_user.id

        study_sessions = StudySession.query.filter_by(user_id=user_id).all()
        achievements = Achievement.query.filter_by(user_id=user_id).all()

        if not (study_sessions or achievements):
            return jsonify({"message": "Brak danych do wygenerowania wykresu"}), 400

        sessions_df = pd.DataFrame([(session.subject, session.duration, session.date) for session in study_sessions], columns=['Subject', 'Duration', 'Date'])
        achievements_df = pd.DataFrame([(ach.description, ach.subject, ach.date) for ach in achievements], columns=['Description', 'Subject', 'Date'])

        fig = go.Figure()

        color_map = {}
        colors = ['blue', 'green', 'red', 'orange', 'purple', 'brown', 'pink', 'gray', 'olive', 'cyan']

        if not sessions_df.empty:
            sessions_df['Date'] = pd.to_datetime(sessions_df['Date'])
            sessions_df = sessions_df.sort_values(by='Date')
            subjects = sessions_df['Subject'].unique()
            for i, subject in enumerate(subjects):
                color_map[subject] = colors[i % len(colors)]

                subject_df = sessions_df[sessions_df['Subject'] == subject].copy()
                subject_df['CumulativeDuration'] = subject_df['Duration'].cumsum()
                fig.add_trace(go.Scatter(
                    x=subject_df['Date'], 
                    y=subject_df['CumulativeDuration'], 
                    mode='lines', 
                    name=f'Sesje nauki: {subject}',
                    line=dict(color=color_map[subject])
                ))

                if not achievements_df.empty:
                    subject_achievements = achievements_df[achievements_df['Subject'] == subject]
                    if not subject_achievements.empty:
                        fig.add_trace(go.Scatter(
                            x=subject_achievements['Date'],
                            y=[subject_df['CumulativeDuration'].max()] * len(subject_achievements),
                            mode='markers',
                            marker=dict(size=10, color=color_map[subject]),
                            name=f'Osiągnięcia: {subject}',
                            text=subject_achievements['Description'],
                            hoverinfo='text+name'
                        ))

        fig.update_layout(
            title='Postępy nauki w czasie',
            xaxis_title='Data',
            yaxis_title='Czas trwania (minuty)',
            legend_title='Legenda'
        )

        static_dir = os.path.join(app.root_path, 'static')
        if not os.path.exists(static_dir):
            os.makedirs(static_dir)
        file_path = os.path.join(static_dir, f'advanced_stats_{user_id}.html')
        fig.write_html(file_path)

        return jsonify({"message": "Wykres wygenerowany pomyślnie", "url": url_for('static', filename=f'advanced_stats_{user_id}.html')}), 200

    @app.route('/download_plot/<filename>')
    @login_required
    def download_plot(filename):
        static_dir = os.path.join(app.root_path, 'static')
        return send_from_directory(directory=static_dir, path=filename, as_attachment=True)




    @app.route('/export_detailed_report', methods=['POST'])
    @login_required
    def export_detailed_report():
        format = request.form.get('exportFormat')
        user_id = current_user.id

        study_sessions = StudySession.query.filter_by(user_id=user_id).all()
        study_plans = StudyPlan.query.filter_by(user_id=user_id).all()
        achievements = Achievement.query.filter_by(user_id=user_id).all()

        if not (study_sessions or study_plans or achievements):
            flash('Brak danych do eksportowania.', 'warning')
            return redirect(url_for('dashboard'))

        sessions_data = [{'Subject': session.subject, 'Duration': session.duration, 'Date': session.date.strftime('%Y-%m-%d')} for session in study_sessions]
        plans_data = [{'Subject': plan.subject, 'Planned Date': plan.planned_date.strftime('%Y-%m-%d')} for plan in study_plans]
        achievements_data = [{'Subject': ach.subject, 'Description': ach.description, 'Date': ach.date.strftime('%Y-%m-%d')} for ach in achievements]

        if format == 'csv':
            si = StringIO()
            cw = csv.writer(si)
            
            cw.writerow(['Sesje Nauki'])
            cw.writerow(['Subject', 'Duration', 'Date'])
            cw.writerows([[data['Subject'], data['Duration'], data['Date']] for data in sessions_data])
            cw.writerow([])  
            
            cw.writerow(['Planowane Sesje Nauki'])
            cw.writerow(['Subject', 'Planned Date'])
            cw.writerows([[data['Subject'], data['Planned Date']] for data in plans_data])
            cw.writerow([])
            
            cw.writerow(['Osiągnięcia'])
            cw.writerow(['Subject', 'Description', 'Date'])
            cw.writerows([[data['Subject'], data['Description'], data['Date']] for data in achievements_data])
            
            output = make_response(si.getvalue())
            output.headers["Content-Disposition"] = "attachment; filename=detailed_report.csv"
            output.headers["Content-type"] = "text/csv"
            return output

        elif format == 'pdf':
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            
            pdf.cell(200, 10, txt="Sesje Nauki", ln=True, align='C')
            pdf.ln(10)
            pdf.cell(50, 10, txt="Subject", border=1)
            pdf.cell(40, 10, txt="Duration", border=1)
            pdf.cell(50, 10, txt="Date", border=1)
            pdf.ln(10)
            for data in sessions_data:
                pdf.cell(50, 10, txt=data['Subject'], border=1)
                pdf.cell(40, 10, txt=str(data['Duration']), border=1)
                pdf.cell(50, 10, txt=data['Date'], border=1)
                pdf.ln(10)
            
            pdf.ln(10)
            
            pdf.cell(200, 10, txt="Planowane Sesje Nauki", ln=True, align='C')
            pdf.ln(10)
            pdf.cell(50, 10, txt="Subject", border=1)
            pdf.cell(50, 10, txt="Planned Date", border=1)
            pdf.ln(10)
            for data in plans_data:
                pdf.cell(50, 10, txt=data['Subject'], border=1)
                pdf.cell(50, 10, txt=data['Planned Date'], border=1)
                pdf.ln(10)
            
            pdf.ln(10)
            
            pdf.cell(200, 10, txt="Osiągnięcia", ln=True, align='C')
            pdf.ln(10)
            pdf.cell(50, 10, txt="Subject", border=1)
            pdf.cell(80, 10, txt="Description", border=1)
            pdf.cell(50, 10, txt="Date", border=1)
            pdf.ln(10)
            for data in achievements_data:
                pdf.cell(50, 10, txt=data['Subject'], border=1)
                pdf.cell(80, 10, txt=data['Description'], border=1)
                pdf.cell(50, 10, txt=data['Date'], border=1)
                pdf.ln(10)
            
            output = make_response(pdf.output(dest='S').encode('latin1'))
            output.headers["Content-Disposition"] = "attachment; filename=detailed_report.pdf"
            output.headers["Content-type"] = "application/pdf"
            return output

        else:
            flash('Nieznany format eksportu.', 'danger')
            return redirect(url_for('dashboard'))

    @app.route('/check_data', methods=['GET'])
    @login_required
    def check_data():
        study_sessions = StudySession.query.filter_by(user_id=current_user.id).all()
        achievements = Achievement.query.filter_by(user_id=current_user.id).all()
        
        has_data = bool(study_sessions or achievements)
        return jsonify({'hasData': has_data})

    @app.route('/save_session', methods=['POST'])
    @login_required
    def save_session():
        data = request.get_json()
        try:
            date_obj = datetime.strptime(data['date'], '%Y-%m-%d').date()
            new_session = StudySession(
                subject=data['subject'],
                duration=data['duration'],
                date=date_obj, 
                user_id=current_user.id
            )
            db.session.add(new_session)
            db.session.commit()
            return jsonify({"message": "Sesja nauki zapisana pomyślnie"}), 200
        except Exception as e:
            return jsonify({"message": str(e)}), 400
    
