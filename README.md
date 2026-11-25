# Streamlit Grade & Calculator

A **Streamlit** web app with two tools side by side:

- **🎓 Grade Calculator:** enter a mark from 0 to 100 and get a letter grade (A ≥ 90, B ≥ 80, C ≥ 70, D ≥ 60, otherwise E).
- **🧮 Calculator:** a button-based calculator with a styled display and a large keypad.

It's the browser version of the [student-grade-cli](https://github.com/jaganathgitr-lang/student-grade-cli) script, with custom CSS: Streamlit's dev toolbar is hidden, and the styles are scoped to each panel.

## Run
```bash
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
streamlit run streamlit_grade_system.py
```
The app opens at http://localhost:8501.

## Tech stack
Python · Streamlit · custom CSS
