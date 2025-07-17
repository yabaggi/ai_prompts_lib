import sqlite3
from io import StringIO
import csv
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# Initialize database
def init_db():
    conn = sqlite3.connect('prompts.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS prompts
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                 group_name TEXT NOT NULL,
                 category TEXT NOT NULL,
                 prompt TEXT NOT NULL)''')
    conn.commit()
    conn.close()

# Insert initial data from CSV string
def insert_initial_data():
    csv_content = """Group,Category,Prompt
Writing & Editing,Text Editing,"Act as an experienced editor. Please first slowly read and analyze the following text without rewriting it: [paste text]. Then provide a numbered list of concise, specific, constructive observations to help me strengthen the piece."
Writing & Editing,Content Creation,"Write a compelling [blog post/article/essay] about [topic] that engages [target audience] and includes [specific points to cover]."
Writing & Editing,Communication,"Act as an expert in clear communication. I need to communicate about [topic] to [specific audience] through [medium: email/presentation/report]. Here's my current draft: [paste content]. Please help me clarify this message."
Writing & Editing,Creative Writing,"Write a short story about [character/situation] in the style of [author/genre]. Include themes of [specific themes]."
Writing & Editing,Persuasive Writing,"Compose a persuasive essay arguing for [position] that addresses potential counterarguments and appeals to [target audience]."
Organization & Planning,Information Structure,"Please organize the following information into a clear, structured format: [paste notes/thoughts/transcript]. Identify the main themes, group related points together, and create a logical flow."
Organization & Planning,Project Management,"Act as an expert project manager. I need to plan [project/task/event] with these constraints: [time/resources/team]. My goal is [desired outcome]. Please draft 3 possible structured plans."
Organization & Planning,Task Planning,"Break down [complex task] into manageable steps with timelines and priorities. Consider [constraints] and suggest tools or resources needed."
Organization & Planning,Content Calendar,"Create a content calendar for [timeframe] focusing on [topics/themes] for [platform/audience]. Include post types, timing, and engagement strategies."
Creative & Innovation,Idea Generation,"Help me explore unusual, creative, unconventional approaches to [topic/challenge]. First, briefly summarize conventional wisdom, then provide 5-7 surprising alternatives."
Creative & Innovation,Brainstorming,"Generate 10 creative solutions for [problem] that haven't been tried before. Focus on [specific constraints or requirements]."
Creative & Innovation,Design Thinking,"Using design thinking principles, help me solve [problem] for [user group]. Walk through empathize, define, ideate, prototype, and test phases."
Learning & Education,Concept Explanation,"Act as a wonderful teacher. I need help understanding [concept] at a [beginner/intermediate/advanced] level. My background is [context]. Please explain in clear, concise language with examples."
Learning & Education,Skill Development,"Act as a patient instructor. I want to learn [skill] and need step-by-step guidance. My current level is [beginner/intermediate/advanced], and I have access to [tools/resources]."
Learning & Education,Study Guide,"Create a comprehensive study guide for [subject/topic] including key concepts, examples, and practice questions suitable for [level/exam]."
Learning & Education,Learning Path,"Design a learning path to master [skill/subject] in [timeframe]. Include resources, milestones, and assessment methods."
Coding & Development,Code Generation,"As a seasoned programmer, write efficient, well-structured code in [programming language] to [perform specific action]. Include comments and error handling."
Coding & Development,Code Review,"Review this code for best practices, potential bugs, security issues, and performance optimizations: [paste code]. Provide specific suggestions for improvement."
Coding & Development,Debugging,"Help me debug this [programming language] code: [paste code]. The expected behavior is [description] but it's currently [actual behavior]."
Coding & Development,Code Explanation,"Explain this code in simple terms: [paste code]. Break down what each part does and how it works together."
Coding & Development,Architecture Design,"Design a software architecture for [project description] that handles [requirements] and scales to [user volume]. Include database design and API structure."
Coding & Development,Code Refactoring,"Refactor this code to improve readability, performance, and maintainability: [paste code]. Follow [specific language] best practices."
Business & Marketing,Market Analysis,"Analyze the market for [product/service] including target audience, competitors, trends, and opportunities. Focus on [specific geographic region or demographic]."
Business & Marketing,Content Strategy,"Develop a content marketing strategy for [business/product] targeting [audience]. Include content types, distribution channels, and success metrics."
Business & Marketing,Email Marketing,"Create an email marketing campaign for [product/service] that increases [specific goal]. Include subject lines, content structure, and call-to-action."
Business & Marketing,Social Media,"Create engaging social media posts for [platform] about [topic/product]. Include hashtags, optimal posting times, and engagement strategies."
Business & Marketing,Sales Copy,"Write compelling sales copy for [product/service] that addresses [target audience] pain points and highlights [key benefits]."
Business & Marketing,Business Plan,"Help me create a business plan section for [business idea] covering [specific area: market analysis/financial projections/marketing strategy]."
Research & Analysis,Information Gathering,"I need to locate specific information about [topic] within [source type]. I'm looking for [exact details] for the purpose of [intended use]."
Research & Analysis,Data Analysis,"Analyze this data [paste data] and identify patterns, trends, and insights. Focus on [specific metrics or relationships]."
Research & Analysis,Competitive Analysis,"Compare [company/product] with its main competitors across [criteria]. Identify strengths, weaknesses, and market positioning."
Research & Analysis,Literature Review,"Conduct a literature review on [topic] covering [timeframe]. Summarize key findings, identify gaps, and suggest research directions."
Personal Productivity,Goal Setting,"Help me create SMART goals for [area of life/work] over [timeframe]. Include specific metrics, deadlines, and accountability measures."
Personal Productivity,Time Management,"Analyze my daily schedule: [describe schedule]. Suggest optimizations for productivity while maintaining work-life balance."
Personal Productivity,Habit Formation,"Design a habit formation plan to [desired habit] in [timeframe]. Include triggers, rewards, and strategies to overcome obstacles."
Personal Productivity,Decision Making,"Help me make a decision about [situation]. List pros and cons, consider long-term implications, and suggest a framework for choosing."
Communication,Presentation,"Create an outline for a [duration] presentation on [topic] for [audience]. Include key points, visual suggestions, and engagement techniques."
Communication,Meeting Facilitation,"Design an agenda for a [meeting type] about [topic] with [number] participants. Include time allocations, discussion prompts, and desired outcomes."
Communication,Conflict Resolution,"Help me address a workplace conflict about [situation]. Suggest communication strategies and potential solutions that benefit all parties."
Communication,Negotiation,"Prepare me for a negotiation about [topic]. Include strategy, key points to cover, potential objections, and win-win solutions."
Technical Writing,Documentation,"Create technical documentation for [system/process] that explains [functionality] to [audience]. Include examples and troubleshooting steps."
Technical Writing,API Documentation,"Write clear API documentation for [endpoint/function] including parameters, response formats, and usage examples."
Technical Writing,User Manual,"Create a user manual section for [feature/product] that guides users through [process] with clear steps and screenshots."
Technical Writing,Requirements Specification,"Write a requirements specification for [project/feature] including functional requirements, constraints, and acceptance criteria."
Finance & Analysis,Budget Planning,"Create a budget plan for [project/personal/business] covering [timeframe] with categories for [specific areas]. Include tracking methods."
Finance & Analysis,Financial Modeling,"Build a financial model for [business/investment] including revenue projections, costs, and key performance indicators over [timeframe]."
Finance & Analysis,Investment Analysis,"Analyze the investment potential of [opportunity] considering risks, returns, market conditions, and alignment with [investment goals]."
Finance & Analysis,Cost-Benefit Analysis,"Conduct a cost-benefit analysis for [decision/project] including quantifiable and qualitative factors over [timeframe]."
Quality Improvement,Process Optimization,"Analyze this process: [describe process]. Identify bottlenecks, inefficiencies, and suggest improvements to reduce time and increase quality."
Quality Improvement,Testing Strategy,"Develop a testing strategy for [product/feature] including test cases, acceptance criteria, and quality assurance measures."
Quality Improvement,Performance Review,"Create a framework for evaluating [performance area] including metrics, feedback mechanisms, and improvement plans."
Quality Improvement,Continuous Improvement,"Design a continuous improvement plan for [area/process] using [methodology: Kaizen/Six Sigma/Lean]. Include measurement and feedback loops."
"""
    
    conn = sqlite3.connect('prompts.db')
    c = conn.cursor()
    
    # Check if data already exists
    c.execute("SELECT COUNT(*) FROM prompts")
    if c.fetchone()[0] > 0:
        conn.close()
        return
    
    # Parse and insert CSV content
    csv_data = StringIO(csv_content)
    reader = csv.DictReader(csv_data)
    for row in reader:
        c.execute("INSERT INTO prompts (group_name, category, prompt) VALUES (?, ?, ?)",
                  (row['Group'], row['Category'], row['Prompt']))
    
    conn.commit()
    conn.close()

# Initialize database and insert data
init_db()
insert_initial_data()

@app.route('/')
def index():
    # Get distinct groups and categories for filters
    conn = sqlite3.connect('prompts.db')
    c = conn.cursor()
    
    # Get distinct groups
    c.execute("SELECT DISTINCT group_name FROM prompts ORDER BY group_name")
    groups = [row[0] for row in c.fetchall()]
    
    # Get distinct categories
    c.execute("SELECT DISTINCT category FROM prompts ORDER BY category")
    categories = [row[0] for row in c.fetchall()]
    
    conn.close()
    
    # Get search parameters
    search_group = request.args.get('group', '')
    search_category = request.args.get('category', '')
    search_query = request.args.get('query', '')
    
    # Build SQL query based on search parameters
    conn = sqlite3.connect('prompts.db')
    c = conn.cursor()
    
    query = "SELECT * FROM prompts WHERE 1=1"
    params = []
    
    if search_group:
        query += " AND group_name = ?"
        params.append(search_group)
    
    if search_category:
        query += " AND category = ?"
        params.append(search_category)
    
    if search_query:
        query += " AND (group_name LIKE ? OR category LIKE ? OR prompt LIKE ?)"
        params.extend([f'%{search_query}%'] * 3)
    
    query += " ORDER BY group_name, category"
    
    c.execute(query, params)
    prompts = c.fetchall()
    conn.close()
    
    return render_template('index.html', 
                          groups=groups, 
                          categories=categories,
                          prompts=prompts,
                          search_group=search_group,
                          search_category=search_category,
                          search_query=search_query)

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        # Check if a file was uploaded
        if 'csv_file' not in request.files:
            flash('No file uploaded', 'error')
            return redirect(request.url)
        
        file = request.files['csv_file']
        
        # Check if file has a filename
        if file.filename == '':
            flash('No selected file', 'error')
            return redirect(request.url)
        
        # Check if file is a CSV
        if not file.filename.endswith('.csv'):
            flash('Please upload a CSV file', 'error')
            return redirect(request.url)
        
        # Read and parse CSV
        try:
            csv_data = file.stream.read().decode('utf-8')
            csv_io = StringIO(csv_data)
            reader = csv.DictReader(csv_io)
            
            conn = sqlite3.connect('prompts.db')
            c = conn.cursor()
            
            inserted_count = 0
            skipped_count = 0
            
            for row in reader:
                # Check if the prompt already exists
                c.execute("SELECT COUNT(*) FROM prompts WHERE group_name = ? AND category = ? AND prompt = ?",
                          (row['Group'], row['Category'], row['Prompt']))
                if c.fetchone()[0] == 0:
                    # Insert new prompt
                    c.execute("INSERT INTO prompts (group_name, category, prompt) VALUES (?, ?, ?)",
                              (row['Group'], row['Category'], row['Prompt']))
                    inserted_count += 1
                else:
                    skipped_count += 1
            
            conn.commit()
            conn.close()
            
            flash(f'Successfully added {inserted_count} new prompts. Skipped {skipped_count} duplicates.', 'success')
            return redirect(url_for('index'))
        
        except Exception as e:
            flash(f'Error processing file: {str(e)}', 'error')
            return redirect(request.url)
    
    return render_template('upload.html')

@app.route('/stats')
def stats():
    conn = sqlite3.connect('prompts.db')
    c = conn.cursor()
    
    # Get total prompts
    c.execute("SELECT COUNT(*) FROM prompts")
    total_prompts = c.fetchone()[0]
    
    # Get total groups
    c.execute("SELECT COUNT(DISTINCT group_name) FROM prompts")
    total_groups = c.fetchone()[0]
    
    # Get total categories
    c.execute("SELECT COUNT(DISTINCT category) FROM prompts")
    total_categories = c.fetchone()[0]
    
    conn.close()
    
    return jsonify({
        'total_prompts': total_prompts,
        'total_groups': total_groups,
        'total_categories': total_categories
    })

if __name__ == '__main__':
    app.run(debug=True)