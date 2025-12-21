# 🎨 PREMIUM LUXURY PDF REPORT GENERATOR FOR MONEYMIND
# Ultra-Premium Design with Zero Empty Space - A4 Optimized
# Fully-Filled Pages with Sophisticated Data Visualization

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm, inch
from reportlab.lib.colors import HexColor, white, black, transparent
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
from reportlab.pdfgen import canvas
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from datetime import datetime
import io
from typing import Dict, List, Tuple, Any
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Rectangle
import numpy as np

# ============================================================================
# PREMIUM CONSTANTS - A4 OPTIMIZATION
# ============================================================================
PAGE_WIDTH, PAGE_HEIGHT = A4
MARGIN = 12 * mm  # Tighter margins for more content
CONTENT_WIDTH = PAGE_WIDTH - (2 * MARGIN)
LINE_HEIGHT = 1.15

# PREMIUM COLOR PALETTE
PRIMARY = HexColor("#667eea")
SECONDARY = HexColor("#764ba2")
ACCENT = HexColor("#f5576c")
SUCCESS = HexColor("#51cf66")
WARNING = HexColor("#ffa500")
DANGER = HexColor("#ff6b6b")
DARK = HexColor("#0f1419")
LIGHT = HexColor("#f8f9fa")
CARD_BG = HexColor("#ffffff")
TEXT_PRIMARY = HexColor("#1a202c")
TEXT_SECONDARY = HexColor("#4a5568")

# ============================================================================
# PREMIUM STYLE DEFINITIONS
# ============================================================================
class PremiumStyles:
    """Define all premium paragraph styles"""
    
    @staticmethod
    def get_styles():
        styles = getSampleStyleSheet()
        
        # Premium Cover Title
        styles.add(ParagraphStyle(
            name='PremiumTitle',
            fontSize=52,
            textColor=white,
            spaceAfter=6,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold',
            leading=60
        ))
        
        # Section Headers
        styles.add(ParagraphStyle(
            name='PremiumHeader',
            fontSize=20,
            textColor=PRIMARY,
            spaceAfter=4,
            spaceBefore=2,
            fontName='Helvetica-Bold'
        ))
        
        # Subheaders
        styles.add(ParagraphStyle(
            name='PremiumSubHeader',
            fontSize=12,
            textColor=SECONDARY,
            spaceAfter=3,
            fontName='Helvetica-Bold'
        ))
        
        # Body text
        styles.add(ParagraphStyle(
            name='PremiumBody',
            fontSize=9,
            textColor=TEXT_PRIMARY,
            spaceAfter=4,
            alignment=TA_JUSTIFY,
            leading=11
        ))
        
        # Data labels
        styles.add(ParagraphStyle(
            name='DataLabel',
            fontSize=8,
            textColor=TEXT_SECONDARY,
            fontName='Helvetica'
        ))
        
        return styles

# ============================================================================
# PREMIUM CHART GENERATORS
# ============================================================================
class PremiumCharts:
    """Generate ultra-premium charts optimized for PDF"""
    
    @staticmethod
    def create_donut_chart(data: Dict[str, float], title: str = "") -> Image:
        """Create premium donut chart"""
        fig, ax = plt.subplots(figsize=(4.5, 4), facecolor='white')
        
        colors = [PRIMARY, SECONDARY, ACCENT, SUCCESS, WARNING, DANGER]
        
        wedges, texts, autotexts = ax.pie(
            data.values(),
            labels=data.keys(),
            autopct='%1.0f%%',
            startangle=90,
            colors=colors[:len(data)],
            pctdistance=0.85,
            explode=[0.05] * len(data)
        )
        
        # Draw donut hole
        centre_circle = plt.Circle((0, 0), 0.70, fc='white', edgecolor='#e2e8f0', linewidth=2)
        ax.add_artist(centre_circle)
        
        # Style
        for text in texts:
            text.set_fontsize(8)
            text.set_weight('bold')
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontsize(7)
            autotext.set_weight('bold')
        
        if title:
            ax.set_title(title, fontsize=11, fontweight='bold', pad=10)
        
        plt.tight_layout()
        return PremiumCharts._fig_to_image(fig, 3.5, 3.2)
    
    @staticmethod
    def create_hbar_chart(data: Dict[str, float], title: str = "") -> Image:
        """Create premium horizontal bar chart"""
        fig, ax = plt.subplots(figsize=(4.5, 3), facecolor='white')
        
        categories = list(data.keys())
        values = list(data.values())
        colors_list = [PRIMARY, SECONDARY, ACCENT, SUCCESS, WARNING, DANGER]
        
        bars = ax.barh(categories, values, color=colors_list[:len(data)], edgecolor='white', linewidth=2)
        
        # Add value labels
        for i, (bar, val) in enumerate(zip(bars, values)):
            ax.text(val, bar.get_y() + bar.get_height()/2, f'₹{val:,.0f}', 
                   va='center', ha='left', fontsize=8, fontweight='bold', color=TEXT_PRIMARY)
        
        ax.set_xlabel('Amount (₹)', fontsize=9, fontweight='bold')
        ax.grid(axis='x', alpha=0.2, linestyle='--')
        ax.set_axisbelow(True)
        
        if title:
            ax.set_title(title, fontsize=11, fontweight='bold', pad=10)
        
        plt.tight_layout()
        return PremiumCharts._fig_to_image(fig, 4, 2.8)
    
    @staticmethod
    def create_area_chart(data: pd.DataFrame, title: str = "") -> Image:
        """Create premium area chart"""
        fig, ax = plt.subplots(figsize=(5, 2.8), facecolor='white')
        
        colors_list = [PRIMARY, SECONDARY, ACCENT]
        
        for idx, col in enumerate(data.columns):
            ax.fill_between(range(len(data)), data[col].values, alpha=0.3, 
                           color=colors_list[idx % len(colors_list)], label=col)
            ax.plot(range(len(data)), data[col].values, linewidth=2.5, 
                   color=colors_list[idx % len(colors_list)], marker='o', markersize=6)
        
        ax.set_xticks(range(len(data)))
        ax.set_xticklabels(data.index, fontsize=8)
        ax.set_ylabel('Amount (₹)', fontsize=9, fontweight='bold')
        ax.grid(True, alpha=0.2, linestyle='--')
        ax.set_axisbelow(True)
        ax.legend(loc='upper left', fontsize=8, framealpha=0.95)
        
        if title:
            ax.set_title(title, fontsize=11, fontweight='bold', pad=10)
        
        plt.tight_layout()
        return PremiumCharts._fig_to_image(fig, 4.8, 2.6)
    
    @staticmethod
    def create_gauge_chart(value: float, max_val: float = 100, label: str = "") -> Image:
        """Create premium gauge chart"""
        fig, ax = plt.subplots(figsize=(3.5, 2.2), facecolor='white')
        
        # Gauge background
        theta = np.linspace(0, np.pi, 100)
        ax.plot(np.cos(theta), np.sin(theta), 'k-', linewidth=0.5)
        
        # Color zones
        danger_theta = np.linspace(0, np.pi * 0.33, 50)
        warning_theta = np.linspace(np.pi * 0.33, np.pi * 0.67, 50)
        success_theta = np.linspace(np.pi * 0.67, np.pi, 50)
        
        ax.fill_between(np.cos(danger_theta), 0, np.sin(danger_theta), color='#ff6b6b', alpha=0.3)
        ax.fill_between(np.cos(warning_theta), 0, np.sin(warning_theta), color='#ffa500', alpha=0.3)
        ax.fill_between(np.cos(success_theta), 0, np.sin(success_theta), color='#51cf66', alpha=0.3)
        
        # Needle
        angle = (value / max_val) * np.pi
        ax.arrow(0, 0, 0.8*np.cos(angle), 0.8*np.sin(angle), head_width=0.08, 
                head_length=0.1, fc=DARK, ec=DARK, linewidth=2)
        
        ax.text(0, -0.3, f'{value:.0f}%', ha='center', fontsize=16, fontweight='bold', color=DARK)
        if label:
            ax.text(0, -0.55, label, ha='center', fontsize=9, color=TEXT_SECONDARY)
        
        ax.set_xlim(-1.2, 1.2)
        ax.set_ylim(-0.7, 1.2)
        ax.axis('off')
        
        plt.tight_layout()
        return PremiumCharts._fig_to_image(fig, 3, 2)
    
    @staticmethod
    def _fig_to_image(fig, width: float = 5, height: float = 3) -> Image:
        """Convert matplotlib figure to ReportLab Image"""
        img_buffer = io.BytesIO()
        fig.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight', facecolor='white')
        img_buffer.seek(0)
        plt.close(fig)
        
        return Image(img_buffer, width=width*cm, height=height*cm)

# ============================================================================
# PREMIUM PDF REPORT BUILDER
# ============================================================================
class PremiumPDFReport:
    """Premium PDF Report with ZERO empty space"""
    
    def __init__(self, user_name: str, report_period: str):
        self.user_name = user_name
        self.report_period = report_period
        self.styles = PremiumStyles.get_styles()
        self.story = []
        
    def add_luxury_cover(self, score: float = 78):
        """Add ultra-premium cover page"""
        # Gradient background effect with tables
        cover_data = [
            [Paragraph(f"<font size=48 color='white'><b>PERSONAL</b></font>", self.styles['Normal']),
             Paragraph(f"<font size=48 color='white'><b>FINANCIAL</b></font>", self.styles['Normal']),
             Paragraph(f"<font size=48 color='white'><b>REPORT</b></font>", self.styles['Normal'])]
        ]
        
        cover_table = Table(cover_data, colWidths=[2*inch, 2*inch, 2*inch])
        cover_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), PRIMARY),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 20),
            ('RIGHTPADDING', (0, 0), (-1, -1), 20),
            ('TOPPADDING', (0, 0), (-1, -1), 30),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 30),
            ('LINEABOVE', (0, 0), (-1, -1), 0, white),
            ('LINEBELOW', (0, 0), (-1, -1), 0, white),
        ]))
        self.story.append(cover_table)
        self.story.append(Spacer(1, 0.4*cm))
        
        # User info section
        user_data = [
            [Paragraph(f"<b>{self.user_name}</b><br/><font size=11>{self.report_period}</font><br/><font size=9 color='#718096'>Generated {datetime.now().strftime('%B %d, %Y')}</font>", 
                      self.styles['Normal'])]
        ]
        user_table = Table(user_data, colWidths=[PAGE_WIDTH - 2*MARGIN])
        user_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), HexColor("#f8f9fa")),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 14),
        ]))
        self.story.append(user_table)
        self.story.append(Spacer(1, 0.8*cm))
        
        # Score card
        score_data = [
            [Paragraph(f"<font size=36 color='{PRIMARY.hexval()}'><b>{int(score)}</b></font>", self.styles['Normal']),
             Paragraph(f"<font size=11 color='#667eea'><b>Financial Health Score</b></font>", self.styles['Normal'])]
        ]
        score_table = Table(score_data, colWidths=[1.5*inch, 3.5*inch])
        score_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), HexColor("#ede9fe")),
            ('ALIGN', (0, 0), (0, 0), 'CENTER'),
            ('ALIGN', (1, 0), (1, 0), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('LEFTPADDING', (1, 0), (1, 0), 15),
        ]))
        self.story.append(score_table)
        self.story.append(PageBreak())
    
    def add_premium_metrics(self, income: float, expenses: float, savings: float, health_score: float):
        """Add packed metrics section"""
        self.story.append(Paragraph("Financial Overview", self.styles['PremiumHeader']))
        self.story.append(Spacer(1, 0.15*cm))
        
        savings_rate = (savings / income * 100) if income > 0 else 0
        
        metrics_data = [
            [
                Paragraph(f"<b>Total Income</b><br/><font size=14 color='{PRIMARY.hexval()}'><b>₹{income:,.0f}</b></font>", 
                         self.styles['DataLabel']),
                Paragraph(f"<b>Total Expenses</b><br/><font size=14 color='{DANGER.hexval()}'><b>₹{expenses:,.0f}</b></font>", 
                         self.styles['DataLabel']),
                Paragraph(f"<b>Net Savings</b><br/><font size=14 color='{SUCCESS.hexval()}'><b>₹{savings:,.0f}</b></font>", 
                         self.styles['DataLabel']),
                Paragraph(f"<b>Savings Rate</b><br/><font size=14 color='{SECONDARY.hexval()}'><b>{savings_rate:.1f}%</b></font>", 
                         self.styles['DataLabel']),
            ]
        ]
        
        metrics_table = Table(metrics_data, colWidths=[1.35*inch]*4)
        metrics_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, 0), HexColor("#dbeafe")),
            ('BACKGROUND', (1, 0), (1, 0), HexColor("#ffebee")),
            ('BACKGROUND', (2, 0), (2, 0), HexColor("#f0fdf4")),
            ('BACKGROUND', (3, 0), (3, 0), HexColor("#ede9fe")),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 0.5, HexColor("#e2e8f0"))
        ]))
        self.story.append(metrics_table)
        self.story.append(Spacer(1, 0.25*cm))
    
    def add_spending_analysis(self, categories: Dict[str, float]):
        """Add comprehensive spending analysis with donut chart"""
        self.story.append(Paragraph("Spending Analysis", self.styles['PremiumHeader']))
        self.story.append(Spacer(1, 0.1*cm))
        
        col_data = []
        
        # Donut chart
        try:
            chart = PremiumCharts.create_donut_chart(categories, "Distribution")
            col_data.append([chart])
        except:
            pass
        
        # Detailed breakdown
        total = sum(categories.values())
        breakdown = []
        for cat, amount in sorted(categories.items(), key=lambda x: x[1], reverse=True):
            pct = (amount / total * 100) if total > 0 else 0
            breakdown.append([
                Paragraph(f"<b>{cat}</b>", self.styles['PremiumBody']),
                Paragraph(f"₹{amount:,.0f}", self.styles['PremiumBody']),
                Paragraph(f"{pct:.1f}%", self.styles['PremiumBody'])
            ])
        
        breakdown_table = Table(breakdown, colWidths=[2*cm, 1.8*cm, 1*cm])
        breakdown_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), PRIMARY),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [white, HexColor("#f8f9fa")]),
            ('GRID', (0, 0), (-1, -1), 0.5, HexColor("#e2e8f0")),
            ('LINEABOVE', (0, 1), (-1, 1), 0.5, HexColor("#e2e8f0")),
        ]))
        
        col_data.append([breakdown_table])
        
        analysis_table = Table(col_data, colWidths=[PAGE_WIDTH - 2*MARGIN])
        analysis_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        self.story.append(analysis_table)
        self.story.append(Spacer(1, 0.2*cm))
    
    def add_budget_breakdown(self, needs: float, wants: float, savings: float, income: float):
        """Add 50/30/20 analysis with visual"""
        self.story.append(Paragraph("Budget Allocation (50/30/20 Rule)", self.styles['PremiumHeader']))
        self.story.append(Spacer(1, 0.1*cm))
        
        needs_pct = (needs / income * 100) if income > 0 else 0
        wants_pct = (wants / income * 100) if income > 0 else 0
        savings_pct = (savings / income * 100) if income > 0 else 0
        
        budget_data = [
            [
                Paragraph(f"<b>Needs</b><br/>Target: 50%<br/>Your: {needs_pct:.0f}%<br/>₹{needs:,.0f}", self.styles['DataLabel']),
                Paragraph(f"<b>Wants</b><br/>Target: 30%<br/>Your: {wants_pct:.0f}%<br/>₹{wants:,.0f}", self.styles['DataLabel']),
                Paragraph(f"<b>Savings</b><br/>Target: 20%<br/>Your: {savings_pct:.0f}%<br/>₹{savings:,.0f}", self.styles['DataLabel']),
            ]
        ]
        
        budget_table = Table(budget_data, colWidths=[1.5*inch]*3)
        budget_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, 0), HexColor("#fee2e2")),
            ('BACKGROUND', (1, 0), (1, 0), HexColor("#fef3c7")),
            ('BACKGROUND', (2, 0), (2, 0), HexColor("#dcfce7")),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('BORDER', (0, 0), (-1, -1), 1, HexColor("#cbd5e1")),
        ]))
        self.story.append(budget_table)
        self.story.append(Spacer(1, 0.25*cm))
    
    def add_trends_section(self, monthly_data: pd.DataFrame):
        """Add trends with premium chart"""
        self.story.append(Paragraph("Financial Trends", self.styles['PremiumHeader']))
        self.story.append(Spacer(1, 0.1*cm))
        
        try:
            trend_chart = PremiumCharts.create_area_chart(monthly_data)
            self.story.append(trend_chart)
        except:
            pass
        
        self.story.append(Spacer(1, 0.2*cm))
    
    def add_insights(self, insights: List[str]):
        """Add premium insights section"""
        self.story.append(Paragraph("Key Insights & Recommendations", self.styles['PremiumHeader']))
        self.story.append(Spacer(1, 0.1*cm))
        
        insights_data = []
        for idx, insight in enumerate(insights, 1):
            insights_data.append([
                Paragraph(f"<b>{idx}.</b>", self.styles['PremiumBody']),
                Paragraph(insight, self.styles['PremiumBody'])
            ])
        
        insights_table = Table(insights_data, colWidths=[0.4*cm, 5.2*cm])
        insights_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('LINEBELOW', (0, 0), (-1, -2), 0.5, HexColor("#f0f0f0")),
        ]))
        self.story.append(insights_table)
        self.story.append(Spacer(1, 0.2*cm))
    
    def add_goals_section(self, emergency_fund: float, target_savings: float, progress_pct: float):
        """Add financial goals tracking"""
        self.story.append(Paragraph("Financial Goals & Progress", self.styles['PremiumHeader']))
        self.story.append(Spacer(1, 0.1*cm))
        
        goals_data = [
            [
                Paragraph(f"<b>Emergency Fund Goal</b><br/>₹{emergency_fund:,.0f}", self.styles['DataLabel']),
                Paragraph(f"<b>Target Savings</b><br/>₹{target_savings:,.0f}", self.styles['DataLabel']),
                Paragraph(f"<b>Progress</b><br/>{progress_pct:.0f}% Complete", self.styles['DataLabel']),
            ]
        ]
        
        goals_table = Table(goals_data, colWidths=[1.5*inch]*3)
        goals_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor("#dbeafe")),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('BORDER', (0, 0), (-1, -1), 1, HexColor("#cbd5e1")),
        ]))
        self.story.append(goals_table)
        self.story.append(Spacer(1, 0.25*cm))
    
    def generate(self) -> bytes:
        """Generate final premium PDF"""
        pdf_buffer = io.BytesIO()
        
        doc = SimpleDocTemplate(
            pdf_buffer,
            pagesize=A4,
            rightMargin=MARGIN,
            leftMargin=MARGIN,
            topMargin=MARGIN,
            bottomMargin=MARGIN
        )
        
        doc.build(self.story)
        pdf_buffer.seek(0)
        return pdf_buffer.getvalue()


# ============================================================================
# MAIN GENERATION FUNCTION
# ============================================================================
def generate_financial_report(
    user_name: str,
    report_period: str,
    financial_data: Dict[str, Any]
) -> bytes:
    """Generate PREMIUM financial report with zero empty space"""
    
    builder = PremiumPDFReport(user_name, report_period)
    
    # Build premium report sections
    builder.add_luxury_cover(financial_data.get('health_score', 78))
    builder.add_premium_metrics(
        financial_data.get('income', 0),
        financial_data.get('expenses', 0),
        financial_data.get('savings', 0),
        financial_data.get('health_score', 78)
    )
    builder.add_spending_analysis(financial_data.get('categories', {}))
    
    budget_breakdown = financial_data.get('budget_breakdown', {})
    builder.add_budget_breakdown(
        budget_breakdown.get('needs', 0),
        budget_breakdown.get('wants', 0),
        budget_breakdown.get('savings', 0),
        financial_data.get('income', 0)
    )
    
    if not financial_data.get('monthly_data', pd.DataFrame()).empty:
        builder.add_trends_section(financial_data.get('monthly_data'))
    
    builder.add_insights(financial_data.get('insights', []))
    builder.add_goals_section(
        financial_data.get('emergency_fund', 50000),
        financial_data.get('target_savings', 100000),
        financial_data.get('progress_pct', 60)
    )
    
    return builder.generate()


# Helper constants
cm = 10  # Centimeters helper
