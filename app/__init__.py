from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
import os
import json
from datetime import datetime, timedelta

from app.models import db, User, Interaction, MoodAssessment
from app.ai_agent import AIAgent

# Initialize extensions
login_manager = LoginManager()


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def create_app():
    app = Flask(__name__)
    
    # Config
    app.config['SECRET_KEY'] = 'your-secret-key-change-this'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///elderly_care.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'login'
    login_manager.login_message = 'Please log in to access this page.'
    
    # Create tables
    with app.app_context():
        db.create_all()
        
        # Create demo elderly user for testing
        if not User.query.filter_by(email='demo@elderly.com').first():
            demo_user = User(
                username='Ahmed',
                email='demo@elderly.com',
                age=72,
                interests='family,history,nature',
                role='elderly'
            )
            demo_user.set_password('demo123')
            db.session.add(demo_user)
            
            # Add demo family member
            demo_user.family_members = json.dumps([
                {'id': 1, 'name': 'سارة', 'relation': 'ابنة', 'phone': '+966500000001'},
                {'id': 2, 'name': 'أحمد', 'relation': 'ابن', 'phone': '+966500000002'}
            ])
            
            db.session.commit()
            print("✅ Demo user created: email='demo@elderly.com', password='demo123'")
    
    # Initialize AI Agent
    ai_agent = AIAgent(db.session)
    
    # ===========================================================
    # Routes
    # ===========================================================
    
    @app.route('/')
    def index():
        return render_template('index.html', title='Elderly AR Companion')
    
    @app.route('/ar-companion')
    @login_required
    def ar_companion():
        return render_template('ar_companion.html', title='AR Companion')
    
    @app.route('/dashboard')
    @login_required
    def dashboard():
        analysis = ai_agent.analyze_elderly_behavior(current_user.id)
        activity = ai_agent.suggest_activity(current_user.id)
        greeting = ai_agent.generate_daily_greeting(current_user.id)
        insight = ai_agent.get_mood_insight(current_user.id)
        
        # Get recent interactions
        interactions = Interaction.query.filter_by(user_id=current_user.id).order_by(Interaction.created_at.desc()).limit(10).all()
        
        return render_template('dashboard.html',
                              title='My Dashboard',
                              analysis=analysis,
                              activity=activity,
                              greeting=greeting,
                              insight=insight,
                              interactions=interactions)
    
    @app.route('/api/log-interaction', methods=['POST'])
    @login_required
    def log_interaction():
        data = request.get_json()
        
        interaction = Interaction(
            user_id=current_user.id,
            interaction_type=data.get('type', 'unknown'),
            duration_seconds=data.get('duration', 0),
            completion=data.get('completion', 100),
            metadata=json.dumps(data.get('metadata', {}))
        )
        db.session.add(interaction)
        
        # Update last active
        current_user.last_active = datetime.utcnow()
        db.session.commit()
        
        return jsonify({'status': 'success'})
    
    @app.route('/api/mood-assessment', methods=['POST'])
    @login_required
    def submit_mood_assessment():
        data = request.get_json()
        
        assessment = MoodAssessment(
            user_id=current_user.id,
            loneliness_score=data.get('loneliness', 5),
            depression_score=data.get('depression', 5),
            life_satisfaction_score=data.get('satisfaction', 20)
        )
        db.session.add(assessment)
        
        # Update mood history
        avg_score = (assessment.loneliness_score + (27 - assessment.depression_score) + assessment.life_satisfaction_score) / 3
        current_user.add_mood_entry(avg_score, f'Assessment completed')
        db.session.commit()
        
        return jsonify({'status': 'success', 'message': 'Assessment saved'})
    
    @app.route('/api/get-recommendation')
    @login_required
    def get_recommendation():
        activity = ai_agent.suggest_activity(current_user.id)
        return jsonify(activity)
    
    @app.route('/api/get-greeting')
    @login_required
    def get_greeting():
        greeting = ai_agent.generate_daily_greeting(current_user.id)
        return jsonify({'greeting': greeting})
    
    @app.route('/api/family-members')
    @login_required
    def get_family_members():
        family = current_user.get_family_members()
        return jsonify(family)
    
    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if request.method == 'POST':
            username = request.form['username']
            email = request.form['email']
            password = request.form['password']
            age = request.form.get('age', 65)
            interests = request.form.get('interests', '')
            
            if User.query.filter_by(email=email).first():
                flash("Email already exists", "danger")
                return redirect(url_for('register'))
            
            new_user = User(
                username=username,
                email=email,
                age=age,
                interests=interests,
                role='elderly'
            )
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()
            
            flash("Registration successful! Please log in.", "success")
            return redirect(url_for('login'))
        
        return render_template('register.html', title='Register')
    
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            email = request.form['email']
            password = request.form['password']
            user = User.query.filter_by(email=email).first()
            
            if user and user.check_password(password):
                login_user(user)
                session['user_id'] = user.id
                session['username'] = user.username
                flash("Login successful!", "success")
                return redirect(url_for('dashboard'))
            else:
                flash("Invalid credentials", "danger")
                return redirect(url_for('login'))
        
        return render_template('login.html', title='Login')
    
    @app.route('/logout')
    def logout():
        logout_user()
        session.clear()
        flash("You have been logged out.", "info")
        return redirect(url_for('index'))
    
    # ===========================================================
    # Research & Export Routes
    # ===========================================================
    
    @app.route('/api/export-research-data')
    @login_required
    def export_research_data():
        """تصدير البيانات للورقة العلمية"""
        import csv
        from io import StringIO
        from flask import make_response
        
        assessments = MoodAssessment.query.filter_by(user_id=current_user.id).order_by(MoodAssessment.assessment_date).all()
        
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(['Date', 'Loneliness Score', 'Depression Score', 'Life Satisfaction Score', 'Overall Score'])
        
        for a in assessments:
            overall = (a.loneliness_score + (27 - a.depression_score) + a.life_satisfaction_score) / 3
            writer.writerow([
                a.assessment_date.strftime('%Y-%m-%d'),
                a.loneliness_score,
                a.depression_score,
                a.life_satisfaction_score,
                round(overall, 2)
            ])
        
        response = make_response(output.getvalue())
        response.headers['Content-Disposition'] = 'attachment; filename=research_data.csv'
        response.headers['Content-type'] = 'text/csv'
        return response
    
    # ===========================================================
    # Language Settings
    # ===========================================================
    
    @app.route('/set_language/<lang>')
    def set_language(lang):
        if lang in ['en', 'ar']:
            session['language'] = lang
        return redirect(request.referrer or url_for('index'))
    
    @app.context_processor
    def inject_language():
        current_lang = session.get('language', 'en')
        return {'current_lang': current_lang, 'is_rtl': current_lang == 'ar'}
    
    @app.before_request
    def set_default_language():
        if 'language' not in session:
            session['language'] = 'en'
    
    return app
