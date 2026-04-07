import json

from chempy import balance_stoichiometry
from chempy.util.parsing import formula_to_composition
import re
import random
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(
    page_title="STOICHIO",
    page_icon="🧱",
    initial_sidebar_state="expanded"
)
st.markdown("""
    <style>
    *{
    padding-top: 0;
    }
    .element-container {
        display: flex;
        justify-content: center;
        width: 100%;
    }

    .stText, .stMarkdown {
        text-align: center;
        width: 100%;
    }
    .main-title {
        font-family: 'Playfair Display', serif;
        font-size: 50px;
        font-weight: 800;
        letter-spacing: 12px; /* This is the 'tracked out' look */
        text-align: center;
        margin-bottom: 0px;
        margin-top: 0;
        color: #1E1E1E;
        text-transform: uppercase;
    }

    .tagline {
        font-family: 'Montserrat', sans-serif;
        font-size: 18px;
        font-style: italic;
        font-weight: 300;
        text-align: center;
        color: #555555;
        margin-top: -10px; 
    </style>
    """, unsafe_allow_html=True)

st.markdown('<p class="main-title">STOICHIO</p>', unsafe_allow_html=True)
st.markdown('<p class="tagline">balance equations, one block at a time.</p>', unsafe_allow_html=True)
st.markdown("---")
ALL_ELEMENTS = {}
#a catalog of all our lego brick emojis
LEGO_CATALOG = ["🟥", "🟦", "🟧", "🟨", "🟩", "🟪", "⬛", "⬜", "🟫"]
#functions
#equation splitter - splits equation into reatacts and products
def equation_splitter(equation):
    #returns a tuple of 2 strings
    #ex: ["h2 + o2", "h2o"
    sides = equation.split('->')
    reactants = [r.strip() for r in sides[0].split('+')]
    products = [p.strip() for p in sides[1].split('+')]
    return [set(reactants), set(products)]
#balancer - calculates the right coefficients to balance the reactants and products
def balance(reactants, products):
    #returns a tuple of 2 dictionaries containing the reactants with their new coefficients
    #and the products with their new coefficients
    #ex: [{'h2': 2, 'o2': 1},{'h2o': 2}]
    return balance_stoichiometry(reactants, products)
#counter - gives the counts for each individual element involved
def counter(coefficients):
    total_inventory = {}
    for molecule, coefficient in coefficients.items():
        #ex: formula_to_composition('H2O') -> {'H': 2, 'O': 1}
        atoms_in_molecule = formula_to_composition(molecule)
        for atom, count in atoms_in_molecule.items():
            total_bricks = count * coefficient
            total_inventory[atom] = total_inventory.get(atom, 0) + total_bricks
    return total_inventory
#clean up the equation, no coefficients at the beginning
def clean_equation(equation):
    #wherever there's a number followed by text, replace the number with nothing/erase it
    return re.sub(r'^\d+', '', equation).strip()
#verify that a valid equation was entered
def is_valic_equation(input):
    #check if it's empty
    if not user_input.strip():
        return False, "Please enter an equation to start building!"
    # This regex looks for a lowercase letter not preceded by an uppercase one
    if re.search(r'(?<![A-Z])[a-z]', user_input):
        return False, "⚠️ Scientific Notation Error: Elements must start with a Capital Letter (e.g., H2O, not h2o)."
    #check for improper ending with a + or an arrow
    if user_input.strip().endswith('+') or user_input.strip().endswith('->'):
        return False, "⚠️ Incomplete Equation: Don't leave a '+' or '->' hanging at the end."
    return True, ""
#load the elements from mendeleev only once
def load_elements():
    #dictionary with atomic number as the key
    elements = {}
    with open('periodic_table.json', 'r') as f:
        elements = json.load(f)
    return elements
#draw each molecule with legos
#select a random lego brick to represent an element
def get_emoji_palette(unique_elements):
    shuffled_pool = random.sample(LEGO_CATALOG, len(LEGO_CATALOG))
    #create the map: {'H': '⬜', 'O': '🟥'}
    return {element: shuffled_pool[i] for i, element in enumerate(unique_elements)}
#draw the legos for a molecule
def draw_lego_molecule(molecule_composition, palette):
    #molecule comes in in the form of a dictionary
    #ex: for H2O {'H': 2, 'O': 1}, {'H': '⬜', 'O': '🟥'}
    molecule_stack = []
    #loop through the molecules
    for element, count in molecule_composition.items():
        #get the brick emoji assigned for that element
        #add a default emoji in case student types element we can't identify
        emoji = palette.get(element, "❓")
        molecule_stack.extend([emoji] * count) #ex: O here would be 🟥🟥
    lego_tower = "".join(reversed(molecule_stack))
    st.text(lego_tower)
#draw 1 side
def draw_side(molecule_list, side_prefix, palette):
    num_cols = len(molecule_list) + (len(molecule_list) - 1)
    cols = st.columns(num_cols)

    col_idx = 0
    for i, formula in enumerate(molecule_list):
        with cols[col_idx]:
            state_key = f"{side_prefix}_{formula}"
            if state_key not in st.session_state:
                st.session_state[state_key] = 1

            #top button
            st.button("▲", key=f"up_{state_key}", use_container_width=True)
            if st.session_state[f"up_{state_key}"]:  # Button handling
                st.session_state[state_key] += 1
                st.rerun()

            #text line
            coeff = st.session_state[state_key]
            st.markdown(f"<h3 style='text-align: center; margin: 0;'>{coeff} {formula}</h3>", unsafe_allow_html=True)

            #botton button
            st.button("▼", key=f"down_{state_key}", use_container_width=True)
            if st.session_state[f"down_{state_key}"]:
                if st.session_state[state_key] > 1:
                    st.session_state[state_key] -= 1
                    st.rerun()

            #legos
            st.write("")
            for _ in range(coeff):
                comp = formula_to_composition(formula)
                draw_lego_molecule(comp, palette)
                st.markdown("<div style='margin-bottom: 5px;'></div>", unsafe_allow_html=True)

        col_idx += 1

        #+ sign
        if i < len(molecule_list) - 1:
            with cols[col_idx]:
                st.markdown("<h1 style='text-align: center; margin-top: 45px;'>+</h1>", unsafe_allow_html=True)
            col_idx += 1
def get_atom_info(atomic_number):
    a_n_str = str(atomic_number)
    return ALL_ELEMENTS.get(a_n_str, {})
def get_persistent_palette(unique_elements):
    #check if we already have a palette saved in memory
    if 'molecule_palette' not in st.session_state:
        shuffled_pool = random.sample(LEGO_CATALOG, len(LEGO_CATALOG))
        #create palette once and save to the memory
        st.session_state.molecule_palette = {
            element: shuffled_pool[i] for i, element in enumerate(unique_elements)
        }

    return st.session_state.molecule_palette
def draw_legend(palette):
    st.write("---")
    #create a column for each element in the palette
    cols = st.columns(len(palette))
    for i, (element, emoji) in enumerate(palette.items()):
        with cols[i]:
            #show the emoji and the element name together
            element_info = get_atom_info(element)
            element_name = element_info.get('name')
            element_sym = element_info.get('symbol')
            st.markdown(f"<div style='text-align: center; font-size: 20px;'>{emoji} = {element_name}({element_sym})</div>",
                        unsafe_allow_html=True)
    st.write("---")
def draw_atom_counter(reac_totals, prod_totals, palette):
    st.write("### 📊 Atom Scoreboard")
    col_reac, col_spacer, col_prod = st.columns([4, 1, 4])

    with col_reac:
        st.markdown("**Reactant Totals**")
        for atom, count in reac_totals.items():
            emoji = palette.get(atom, "❓")
            #green if it matches the other side, Red if it doesn't
            color = "green" if count == prod_totals.get(atom, 0) else "#FF4B4B"
            st.markdown(f"{emoji} {atom}: <span style='color:{color}; font-weight:bold; font-size:20px;'>{count}</span>", unsafe_allow_html=True)

    with col_prod:
        st.markdown("**Product Totals**")
        for atom, count in prod_totals.items():
            emoji = palette.get(atom, "❓")
            color = "green" if count == reac_totals.get(atom, 0) else "#FF4B4B"
            st.markdown(f"{emoji} {atom}: <span style='color:{color}; font-weight:bold; font-size:20px;'>{count}</span>", unsafe_allow_html=True)
ALL_ELEMENTS = load_elements()
equation = "2h2 + o2 -> h2o"
clean = clean_equation(equation)     # Result: "h2 + o2 -> h2o"
# formatted = format_equation(clean)   # Result: "H2 + O2 -> H2O"
#text input for the equation
user_input = st.text_input("Enter a chemical equation (e.g., H2 + O2 -> H2O):", "H2 + O2 -> H2O")
isValid, error_msg = is_valic_equation(user_input)
if not isValid:
    st.error(error_msg)
    st.stop()
#check if the equation has changed since the last run
if "current_equation" not in st.session_state or st.session_state.current_equation != user_input:
    #update the stored equation
    st.session_state.current_equation = user_input

    #clear old coefficients
    for key in list(st.session_state.keys()):
        if key.startswith("reac_") or key.startswith("prod_") or key == "molecule_palette":
            del st.session_state[key]

    st.rerun()
clean = clean_equation(user_input)
# formatted = format_equation(clean)

try:
    reactants_list, products_list = equation_splitter(clean)
except Exception:
    st.error("Make sure to use ' + ' and ' -> ' in your equation!")
    st.stop()

all_atoms = set()
for m in reactants_list | products_list:
    all_atoms.update(formula_to_composition(m).keys())

palette = get_persistent_palette(all_atoms)
all_molecules = reactants_list | products_list
unique_atoms = set()
for m in all_molecules:
    unique_atoms.update(formula_to_composition(m).keys())

#one palette for the whole screen
palette = get_persistent_palette(unique_atoms)
col_left, col_mid, col_right = st.columns([4, 1, 4])

with col_left:
    st.subheader("Reactant Side")
    draw_side(reactants_list, "reac", palette)

with col_mid:
    st.markdown("<h1 style='text-align: center; margin-top: 100px;'>→</h1>", unsafe_allow_html=True)

with col_right:
    st.subheader("Product Side")
    draw_side(products_list, "prod", palette)

draw_legend(palette)


#total atoms in reactants
total_reac_atoms = {}
for mol in reactants_list:
    coeff = st.session_state.get(f"reac_{mol}", 1)
    comp = formula_to_composition(mol)
    for atom, count in comp.items():
        total_reac_atoms[atom] = total_reac_atoms.get(atom, 0) + (count * coeff)

#total atoms in products
total_prod_atoms = {}
for mol in products_list:
    coeff = st.session_state.get(f"prod_{mol}", 1)
    comp = formula_to_composition(mol)
    for atom, count in comp.items():
        total_prod_atoms[atom] = total_prod_atoms.get(atom, 0) + (count * coeff)

#compare and give feedback
if total_reac_atoms == total_prod_atoms:
    st.balloons()
    st.success("✅ Perfectly Balanced! The Law of Conservation of Mass is happy.")
else:
    st.info("Keep counting those bricks! Do the left and right sides match yet?")

#dictionaries to store the math
reac_totals = {}
for mol in reactants_list:
    coeff = st.session_state.get(f"reac_{mol}", 1)
    comp = formula_to_composition(mol)
    for atom, count in comp.items():
        reac_totals[atom] = reac_totals.get(atom, 0) + (count * coeff)

prod_totals = {}
for mol in products_list:
    coeff = st.session_state.get(f"prod_{mol}", 1)
    comp = formula_to_composition(mol)
    for atom, count in comp.items():
        prod_totals[atom] = prod_totals.get(atom, 0) + (count * coeff)

# draw_atom_counter(reac_totals, prod_totals, palette)
with st.sidebar:
    st.markdown("### 📊 Live Atom Count")
    #two mini columns inside the sidebar
    side_col1, side_col2 = st.columns(2)

    with side_col1:
        st.write("**Reactants**")
        for atom, count in reac_totals.items():
            atom_info = get_atom_info(atom)
            atom_name = atom_info.get('name', 'Unknown')
            atom_sym = atom_info.get('symbol', 'Unknown')
            emoji = palette.get(atom, "❓")
            #match = green, mismatch = red
            match = count == prod_totals.get(atom, 0)
            color = "#28a745" if match else "#FF4B4B"
            st.markdown(f"{emoji} {atom_sym}: <span style='color:{color}; font-weight:bold;'>{count}</span>",
                        unsafe_allow_html=True)

    with side_col2:
        st.write("**Products**")
        for atom, count in prod_totals.items():
            atom_info = get_atom_info(atom)
            atom_name = atom_info.get('name', 'Unknown')
            atom_sym = atom_info.get('symbol', 'Unknown')
            emoji = palette.get(atom, "❓")
            match = count == reac_totals.get(atom, 0)
            color = "#28a745" if match else "#FF4B4B"
            st.markdown(f"{emoji} {atom_sym}: <span style='color:{color}; font-weight:bold;'>{count}</span>",
                        unsafe_allow_html=True)

    st.markdown("---")
    if reac_totals == prod_totals:
        st.success("Balanced!")
    else:
        st.warning("Keep building...")
with st.sidebar:
    if st.button("🔀 Shuffle Brick Colors"):
        if 'molecule_palette' in st.session_state:
            del st.session_state.molecule_palette
            st.rerun()