import json
from datetime import datetime
from collections import Counter
import random

class AIAgent:
    """وكيل ذكي للدعم النفسي والاجتماعي للمسنين"""
    
    def __init__(self, db_session):
        self.db = db_session
    
    def analyze_elderly_behavior(self, user_id):
        """تحليل سلوك المسن"""
        from app.models import Interaction, User
        
        user = self.db.query(User).filter_by(id=user_id).first()
        interactions = self.db.query(Interaction).filter_by(user_id=user_id).all()
        
        if not interactions:
            return self._get_default_analysis(user)
        
        interaction_types = [i.interaction_type for i in interactions]
        total_duration = sum(i.duration_seconds or 0 for i in interactions)
        
        # حساب مؤشرات الصحة النفسية
        engagement_score = min(100, len(interactions) * 8 + (total_duration / 60))
        
        # تصنيف الحالة
        if engagement_score < 30:
            mood_status = 'withdrawn'  # منعزل
            status_ar = 'منعزل'
            suggested_activity = 'outgoing_call'
            color = '🔴'
        elif engagement_score < 60:
            mood_status = 'stable'  # مستقر
            status_ar = 'مستقر'
            suggested_activity = 'memory_game'
            color = '🟡'
        else:
            mood_status = 'active'  # نشط
            status_ar = 'نشط'
            suggested_activity = 'meditation'
            color = '🟢'
        
        return {
            'user_id': user_id,
            'username': user.username,
            'mood_status': mood_status,
            'mood_status_ar': status_ar,
            'color': color,
            'engagement_score': engagement_score,
            'total_interactions': len(interactions),
            'favorite_activity': Counter(interaction_types).most_common(1)[0][0] if interaction_types else 'none',
            'suggested_activity': suggested_activity,
            'last_active': interactions[-1].created_at if interactions else None
        }
    
    def _get_default_analysis(self, user):
        return {
            'user_id': user.id,
            'username': user.username,
            'mood_status': 'new',
            'mood_status_ar': 'جديد',
            'color': '⚪',
            'engagement_score': 0,
            'total_interactions': 0,
            'favorite_activity': 'none',
            'suggested_activity': 'welcome',
            'last_active': None
        }
    
    def generate_daily_greeting(self, user_id):
        """توليد تحية يومية مخصصة"""
        analysis = self.analyze_elderly_behavior(user_id)
        
        greetings = {
            'withdrawn': [
                "صباح الخير يا جدي! اليوم يوم جديد مليء بالأمل. كيف يمكنني مساعدتك؟",
                "أهلاً بك! أنا هنا لأسمعك. هل تريد التحدث مع أحد أفراد العائلة؟"
            ],
            'stable': [
                "صباح النور! كيف كان نومك الليلة؟",
                "أهلاً بك! لدي اليوم لعبة جديدة لتنشيط الذاكرة، هل تريد تجربتها؟"
            ],
            'active': [
                "صباح الخير! أنا سعيد برؤيتك اليوم. ماذا تحب أن نفعل؟",
                "مرحباً! أحب حماسك اليوم. هل تريد جلسة استرخاء أم لعبة؟"
            ],
            'new': [
                "مرحباً بك! أنا صديقك الافتراضي. كيف تشعر اليوم؟",
                "أهلاً! أنا هنا لمساعدتك. هل تريد التعرف على ما يمكننا فعله معاً؟"
            ]
        }
        
        greeting_list = greetings.get(analysis['mood_status'], greetings['stable'])
        return random.choice(greeting_list)
    
    def suggest_activity(self, user_id):
        """اقتراح نشاط مناسب لحالة المسن"""
        analysis = self.analyze_elderly_behavior(user_id)
        
        activities = {
            'withdrawn': {
                'type': 'family_call',
                'name': 'اتصال بأحد أفراد العائلة',
                'description': 'لقد مر وقت طويل منذ آخر مكالمة. هل تريد التواصل مع أحبائك؟',
                'priority': 'high'
            },
            'stable': {
                'type': 'memory_game',
                'name': 'لعبة تنشيط الذاكرة',
                'description': 'لعبة ممتعة لتنشيط الذاكرة وتحفيز العقل',
                'priority': 'medium'
            },
            'active': {
                'type': 'meditation',
                'name': 'جلسة استرخاء وتأمل',
                'description': 'جلسة استرخاء قصيرة لتحسين المزاج',
                'priority': 'low'
            },
            'new': {
                'type': 'welcome_tour',
                'name': 'جولة تعريفية',
                'description': 'تعرف على ميزات التطبيق وأصدقائك الافتراضيين',
                'priority': 'high'
            }
        }
        
        return activities.get(analysis['mood_status'], activities['stable'])
    
    def get_mood_insight(self, user_id):
        """توليد رؤية نفسية للمسن"""
        analysis = self.analyze_elderly_behavior(user_id)
        
        insights = {
            'withdrawn': "نلاحظ أنك لم تتفاعل كثيراً مؤخراً. تواصلك مع العائلة قد يحسن مزاجك.",
            'stable': "أنت في حالة مستقرة. الحفاظ على هذا النشاط مفيد لصحتك النفسية.",
            'active': "تفاعلك الممتاز يحسن صحتك النفسية. استمر في الأنشطة التي تستمتع بها!",
            'new': "مرحباً بك! التفاعل المنتظم مع التطبيق يساعد في تحسين المزاج وتقليل الشعور بالوحدة."
        }
        
        return insights.get(analysis['mood_status'], insights['stable'])
    
    def generate_weekly_report(self, user_id):
        """توليد تقرير أسبوعي للأسرة (للبحث العلمي)"""
        from app.models import Interaction, MoodAssessment
        
        interactions = self.db.query(Interaction).filter_by(user_id=user_id).all()
        assessments = self.db.query(MoodAssessment).filter_by(user_id=user_id).order_by(MoodAssessment.assessment_date.desc()).limit(2).all()
        
        recent_assessment = assessments[0] if assessments else None
        previous_assessment = assessments[1] if len(assessments) > 1 else None
        
        # حساب التغير في المقاييس النفسية
        loneliness_change = 0
        depression_change = 0
        satisfaction_change = 0
        
        if recent_assessment and previous_assessment:
            loneliness_change = previous_assessment.loneliness_score - recent_assessment.loneliness_score
            depression_change = previous_assessment.depression_score - recent_assessment.depression_score
            satisfaction_change = recent_assessment.life_satisfaction_score - previous_assessment.life_satisfaction_score
        
        return {
            'user_id': user_id,
            'week_start': datetime.utcnow().date(),
            'total_interactions': len(interactions),
            'loneliness_change': loneliness_change,
            'depression_change': depression_change,
            'satisfaction_change': satisfaction_change,
            'loneliness_improved': loneliness_change > 0,
            'depression_improved': depression_change > 0,
            'satisfaction_improved': satisfaction_change > 0,
            'recommendations': self._generate_recommendations(loneliness_change, depression_change)
        }
    
    def _generate_recommendations(self, loneliness_change, depression_change):
        recommendations = []
        if loneliness_change > 0:
            recommendations.append("✅ تحسن مستوى الوحدة - استمر في التواصل مع العائلة")
        elif loneliness_change < 0:
            recommendations.append("⚠️ زيادة الشعور بالوحدة - يوصى بزيادة التفاعلات الاجتماعية")
        
        if depression_change > 0:
            recommendations.append("✅ تحسن المزاج - النشاطات الحالية مفيدة")
        elif depression_change < 0:
            recommendations.append("⚠️ انخفاض المزاج - يوصى بجلسات استرخاء إضافية")
        
        return recommendations
