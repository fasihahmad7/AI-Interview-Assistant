import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime
from typing import Dict, List, Any
from ..database.db_manager import DatabaseManager
from ..utils.config import ROLE_CRITERIA

class Dashboard:
    def __init__(self):
        self.db = DatabaseManager()
        
    def _create_radar_chart(self, performance_data: Dict[str, float], role: str):
        """Create role-specific radar chart."""
        role_info = ROLE_CRITERIA.get(role, ROLE_CRITERIA["Software Engineer"])
        
        categories = (
            role_info['core_skills'][:3] +  # Top 3 core skills
            role_info['practices'][:2] +    # Top 2 practices
            role_info['soft_skills']        # All soft skills
        )
        
        values = [
            performance_data.get(cat.lower().replace(" ", "_"), 0)
            for cat in categories
        ]
        
        fig = go.Figure(data=go.Scatterpolar(
            r=values,
            theta=categories,
            fill='toself',
            name=role
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 10]
                )
            ),
            showlegend=False,
            title=f"{role} Performance Metrics"
        )
        return fig
    
    def _create_progress_chart(self, history_data: List[Dict[str, Any]]):
        """Create progress over time chart with trend lines."""
        if not history_data:
            return None
            
        df = pd.DataFrame(history_data)
        df['date'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('date')
        
        # Calculate moving averages
        df['technical_ma'] = df['technical_score'].rolling(window=3, min_periods=1).mean()
        df['communication_ma'] = df['communication_score'].rolling(window=3, min_periods=1).mean()
        
        fig = px.line(df, x='date', 
                     y=['technical_score', 'communication_score', 'technical_ma', 'communication_ma'],
                     title='Performance Trends',
                     labels={
                         'technical_score': 'Technical',
                         'communication_score': 'Communication',
                         'technical_ma': 'Technical (Trend)',
                         'communication_ma': 'Communication (Trend)'
                     })
        
        fig.update_layout(
            xaxis_title="Interview Date",
            yaxis_title="Score",
            hovermode='x unified'
        )
        return fig
    
    def display_metrics(self, user_id: str, role: str):
        """Display enhanced performance metrics dashboard."""
        recent_interviews = self.db.get_recent_interviews(user_id, limit=5)
        if not recent_interviews:
            st.info("No interview data available yet. Complete some interviews to see your progress!")
            return
        
        # Performance Overview
        st.subheader("📊 Performance Overview")
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Radar chart
            metrics = self._calculate_role_metrics(recent_interviews, role)
            radar_chart = self._create_radar_chart(metrics, role)
            st.plotly_chart(radar_chart, use_container_width=True)
            
        with col2:
            # Summary metrics
            st.markdown("### Key Metrics")
            self._display_summary_metrics(metrics)
        
        # Progress over time
        st.subheader("📈 Progress Analysis")
        col1, col2 = st.columns([3, 1])
        
        with col1:
            progress_chart = self._create_progress_chart(recent_interviews)
            if progress_chart:
                st.plotly_chart(progress_chart, use_container_width=True)
                
        with col2:
            st.markdown("### Improvement Areas")
            self._display_improvement_suggestions(metrics, role)
    
    def _calculate_role_metrics(self, interviews: List[Dict], role: str) -> Dict[str, float]:
        """Calculate comprehensive role-specific metrics."""
        role_info = ROLE_CRITERIA.get(role, ROLE_CRITERIA["Software Engineer"])
        metrics = {}
        
        for skill in role_info['core_skills'] + role_info['practices'] + role_info['soft_skills']:
            skill_key = skill.lower().replace(" ", "_")
            scores = [
                interview['assessment'].get(skill_key, 0)
                for interview in interviews
                if 'assessment' in interview
            ]
            metrics[skill_key] = sum(scores) / len(scores) if scores else 0
            
        return metrics
    
    def _display_summary_metrics(self, metrics: Dict[str, float]):
        """Display summary metrics with visual indicators."""
        for metric, score in metrics.items():
            label = metric.replace("_", " ").title()
            color = self._get_score_color(score)
            st.markdown(
                f'<div style="padding: 10px; margin: 5px 0; border-radius: 5px; '
                f'background-color: {color}; color: white;">'
                f'{label}: {score:.1f}/10</div>',
                unsafe_allow_html=True
            )
    
    def _get_score_color(self, score: float) -> str:
        """Get color based on score."""
        if score >= 8.0:
            return "#28a745"  # Green
        elif score >= 6.5:
            return "#17a2b8"  # Blue
        elif score >= 5.0:
            return "#ffc107"  # Yellow
        else:
            return "#dc3545"  # Red
    
    def _display_improvement_suggestions(self, metrics: Dict[str, float], role: str):
        """Display personalized improvement suggestions."""
        # Find weakest areas
        weak_areas = sorted(metrics.items(), key=lambda x: x[1])[:3]
        
        st.markdown("#### Focus Areas")
        for area, score in weak_areas:
            area_name = area.replace("_", " ").title()
            st.warning(
                f"**{area_name}** (Current: {score:.1f}/10)\n\n"
                f"{self._get_improvement_tip(area, role)}"
            )
    
    def _get_improvement_tip(self, area: str, role: str) -> str:
        """Get specific improvement tip based on area and role."""
        role_info = ROLE_CRITERIA.get(role, ROLE_CRITERIA["Software Engineer"])
        
        tips = {
            "technical_depth": "Focus on advanced concepts and practical applications.",
            "problem_solving": "Practice algorithmic problems and system design.",
            "communication": "Work on explaining technical concepts clearly.",
            "best_practices": "Study industry standards and design patterns."
        }
        
        return tips.get(area, "Continue practicing and gaining experience.")
