"""
Minimal test of the complete resume generation pipeline.
Run this to verify: Python -> SQLite -> LaTeX -> PDF works.
"""

import sqlite3
import subprocess
import os
from datetime import datetime


class Job:
    """A single job entry for a resume."""
    def __init__(self, title, company, start_date, end_date, description):
        self.title = title
        self.company = company
        self.start_date = start_date
        self.end_date = end_date
        self.description = description


def init_database(db_path="test_resume.db"):
    """Create the database and jobs table."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            company TEXT NOT NULL,
            start_date TEXT NOT NULL,
            end_date TEXT,
            description TEXT
        )
    """)
    
    conn.commit()
    conn.close()
    print(f"✓ Database initialized: {db_path}")


def save_job(job, db_path="test_resume.db"):
    """Save a job to the database."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO jobs (title, company, start_date, end_date, description)
        VALUES (?, ?, ?, ?, ?)
    """, (job.title, job.company, job.start_date, job.end_date, job.description))
    
    conn.commit()
    job_id = cursor.lastrowid
    conn.close()
    print(f"✓ Job saved to database (ID: {job_id})")
    return job_id


def load_all_jobs(db_path="test_resume.db"):
    """Load all jobs from the database."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT title, company, start_date, end_date, description FROM jobs")
    rows = cursor.fetchall()
    
    jobs = [Job(row[0], row[1], row[2], row[3], row[4]) for row in rows]
    conn.close()
    print(f"✓ Loaded {len(jobs)} job(s) from database")
    return jobs


def generate_latex(jobs, output_path="test_resume.tex"):
    """Generate a LaTeX file from job data."""
    
    # Simple LaTeX template
    latex_content = r"""\documentclass[11pt,letterpaper]{article}
\usepackage[margin=1in]{geometry}
\usepackage{enumitem}

\begin{document}

\begin{center}
{\LARGE \textbf{Test Resume}}\\
\vspace{0.5em}
Generated: """ + datetime.now().strftime("%Y-%m-%d %H:%M") + r"""
\end{center}

\section*{Experience}

"""
    
    # Add each job
    for job in jobs:
        end = job.end_date if job.end_date else "Present"
        latex_content += r"\noindent\textbf{" + job.title + r"} \hfill " + job.start_date + " -- " + end + r"\\" + "\n"
        latex_content += r"\textit{" + job.company + r"}" + "\n\n"
        latex_content += job.description + "\n\n"
        latex_content += r"\vspace{1em}" + "\n\n"
    
    latex_content += r"\end{document}"
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(latex_content)
    
    print(f"✓ LaTeX file generated: {output_path}")


def compile_pdf(tex_path="test_resume.tex"):
    """Compile LaTeX to PDF using pdflatex."""
    try:
        # Run pdflatex
        result = subprocess.run(
            ["pdflatex", "-interaction=nonstopmode", tex_path],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            pdf_path = tex_path.replace('.tex', '.pdf')
            print(f"✓ PDF compiled successfully: {pdf_path}")
            return pdf_path
        else:
            print("✗ PDF compilation failed")
            print(result.stdout)
            return None
            
    except FileNotFoundError:
        print("✗ pdflatex not found. Make sure MiKTeX is installed and in your PATH.")
        return None


def cleanup_latex_aux_files(base_name="test_resume"):
    """Remove auxiliary LaTeX files."""
    extensions = ['.aux', '.log', '.out']
    for ext in extensions:
        file_path = base_name + ext
        if os.path.exists(file_path):
            os.remove(file_path)
    print("✓ Cleaned up auxiliary files")


def main():
    """Run the complete test pipeline."""
    print("\n=== Resume Builder Pipeline Test ===\n")
    
    # 1. Initialize database
    init_database()
    
    # 2. Create test job
    test_job = Job(
        title="Bro",
        company="The Boys",
        start_date="Jan 2022",
        end_date="Dec 2023",
        description="YEEEEEt"
    )
    
    # 3. Save to database
    save_job(test_job)
    
    # 4. Load from database
    jobs = load_all_jobs()
    
    # 5. Generate LaTeX
    generate_latex(jobs)
    
    # 6. Compile to PDF
    pdf_path = compile_pdf()
    
    # 7. Cleanup
    cleanup_latex_aux_files()
    
    print("\n=== Pipeline Test Complete ===")
    if pdf_path:
        print(f"\nYour test resume PDF: {os.path.abspath(pdf_path)}")
        print("\nNext steps:")
        print("- Open the PDF to verify it looks correct")
        print("- Try modifying the job data in this script")
        print("- Run again to see changes")
    else:
        print("\nPDF generation failed. Check the error messages above.")


if __name__ == "__main__":
    main()
