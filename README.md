🧪 Interactive Periodic Table: Trends Heatmap
An interactive data visualization tool designed for middle school and highschool science classrooms as well as chemistry enthusiasts. This app transforms the traditional static periodic table into a dynamic heatmap, allowing users to visualize different chemical properties across the periodic table.

**[🔗 View the Live App Here](https://periodictabletrends.streamlit.app/)**

🌟 Features
Dynamic Heatmapping: Instantly visualize trends like Electronegativity, Ionization Energy, Atomic Mass, and Boiling Point.
Real-World Data: Powered by the mendeleev Python library, providing accurate scientific data for all 118 elements.
Educational Insights: Designed specifically for middle and highschool science standards to help students identify patterns.

🛠️ The Tech Stack
Python
Streamlit
Plotly Express
Mendeleev Library
NumPy for grid manipulation and coordinate mapping.

🚀 Getting Started
Prerequisites
Ensure you have Python installed, then clone this repository:
Bash
git clone https://github.com/bubblilotus/periodic-table-heatmap.git
cd periodic-table-heatmap
Installation
Create a virtual environment:
Bash
python -m venv .venv
source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
Install the requirements:

Bash
pip install -r requirements.txt
Running the App
Launch the Streamlit server:

Bash
streamlit run app.py
📊 Scientific Logic
The app uses a custom 18x10 coordinate grid to map elements based on their Period and Group. Special logic is included to:
Correctly position the Lanthanides and Actinides below the main table.
Handle missing data for synthetic elements.

👩‍🏫 About the Creator
Developed by Ms. Kay, a middle school science teacher and programmer dedicated to making STEM education more visual, accessible, and data-driven.
