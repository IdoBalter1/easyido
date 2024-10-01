import streamlit as st 
from fpdf import FPDF, XPos, YPos
import requests
import webbrowser
import numpy as np
import matplotlib.pyplot as plt
from pdf2image import convert_from_path
from libraries import uc_beams, ub_beams, padstones, load_data
from libraries import choose_beam
import math
import subprocess
import os
import platform

def app():
    span = 1
    job_title = st.session_state.get("job_title", "Harleydene Sandgate Lane Storrington")
    initials = st.session_state.get("initials", "MM").upper()
    item = st.session_state.get("item", "Structural Calculations")
    rev = st.session_state.get("rev", "")
    job_number = st.session_state.get("job_number", 0)
    date = st.session_state.get("date", "")
    image = st.session_state.get("image", "") or None
    material = 'foundation'
    def get_inputs():
        title_of_work = st.text_input("Enter the title of the work", value="Foundations Calculation")
        title_of_work = title_of_work.upper()  # Convert the title to uppercase after input

        sheet_number = st.number_input("Sheet Number", min_value=1.0, value=1.0, step=0.00000000000000000000001)
        sheet_number = round(sheet_number)



        return  title_of_work, sheet_number,

    title_of_work,sheet_number = get_inputs()



    footings = {
        '1': {'description': 'Provide 450mm Wide Foundation ', 'Area': 21500},
        '2': {'description': 'Provide 600mm Wide Foundation', 'Area': 33000},
        '3': {'description': 'Provide 750mm Wide Foundation', 'Area': 44000},}
    def choose_footings():
        # Create a dictionary with descriptions as options instead of keys
        footing_options = {value['description']: key for key, value in footings.items()}
        
        # Add 'Other' option for custom input
        selected_footing_description = st.selectbox(
            "Choose a footing width or enter your own:",
            list(footing_options.keys()) + ['Other']
        )
        
        # Check if the user selects 'Other' and return custom input
        if selected_footing_description == 'Other':
            return st.text_input("Enter your custom footing width")
        else:
            return selected_footing_description



    class PDF(FPDF):
        def header(self):
            """
            Method to add a header to each page.
            """
            # Scale the image to width 50 mm and height 30 mm
            page_number = self.page_no()
            if image is not None:
                self.image(image, 10, 10, 50)
            self.set_y(25)
            self.set_font('Times', '', 11)
            num_cells = 2
            total_width = self.w - 2 * self.l_margin
            cell_width = total_width / num_cells
            self.cell(cell_width, 10, f'JOB TITLE {job_title}', border=True, align='')
            self.cell(cell_width, 10, f'ITEM {item}', border=True, align='L')
            self.ln()
            #z:\Pdf's Adverts and Logo\logo.jpg
            num_cells_1 = 6
            total_width_1 = self.w - 2 * self.l_margin
            cell_width_1 = total_width_1 / num_cells_1
            self.cell(cell_width_1, 10, f'DESIGNED- {initials}', border=True, align='L')
            self.cell(cell_width_1, 10, f'DATE {date}', border=True, align='L')
            self.cell(cell_width_1, 10, f'CHECKED- {initials}', border=True, align='L')
            self.cell(cell_width_1, 10, f'JOB NO. {job_number}', border=True, align='L')
            self.cell(cell_width_1, 10, f'SHEET {int(sheet_number) + (page_number - 1)}', border=True, align='L')
            self.cell(cell_width_1, 10, f'REV {rev}', border=True, align='L')
            self.ln()

        def footer(self):
            """
            Method to add a footer to each page with page number.
            """
            self.set_y(-15)
            self.set_font('Times', 'I', 11)
            self.cell(0, 10, f'Page {self.page_no()}/{{nb}}', align='C')

    if "distributed_loads" not in st.session_state:
        st.session_state.distributed_loads = []

    if "point_loads" not in st.session_state:
        st.session_state.point_loads = []

    # Functions for adding/removing loads
    def add_distributed_load():
        st.session_state.distributed_loads.append({"code": None, "distance": 0.0, "magnitude": 0.0, "total_loading": 0.0, "factored_loading": 0.0})

    def add_point_load():
        st.session_state.point_loads.append({"magnitude": 0.0, "position": 0.0, "factored_point_loading": 0.0})

    def remove_distributed_load(index):
        st.session_state.distributed_loads.pop(index)
        
    def remove_point_load(index):
        st.session_state.point_loads.pop(index)
    # Helper function to get the total and factored values for point and distributed loads
    def calculate_totals():
        total_loading = 0
        factored_loading = 0
        total_point_loading = 0
        factored_point_loading = 0

        # Calculate totals for distributed loads
        for load in st.session_state.distributed_loads:
            total_loading += load['total_loading']
            factored_loading += load['factored_loading']

        # Calculate totals for point loads
        for load in st.session_state.point_loads:
            total_point_loading += load['magnitude']
            factored_point_loading += load['factored_point_loading']

        return total_loading, factored_loading, total_point_loading, factored_point_loading

    def get_load_arrays():
        pointLoads = np.array([[load['position'], load['magnitude']] for load in st.session_state.point_loads])
        distributedLoads = np.array([[0, span, load['magnitude']*load['distance']] for load in st.session_state.distributed_loads])
        return pointLoads, distributedLoads

    def get_data():
        # Define the header for the table
        data = [["Loading Type", "Magnitude (kN/m^2 or kN)", "Distance (m)", "Point Loading (kN)", "Factored Point Loading (kN)", "Total Loading (kN/m)", "Factored Loading (kN/m)"]]

        # Prepare the load data rows (distributed and point loads)
        loadings = []

        # Add distributed loads to the table
        for load in st.session_state.distributed_loads:
            # Safely fetch the description based on load code, default to 'Unknown Load' if code is invalid
            description = load_data.get(load['code'], {}).get('description', 'Unknown Load')
            magnitude = load['magnitude']
            distance = load['distance']
            total_loading = load['total_loading']
            factored_loading = load['factored_loading']

            loadings.append([
                description,
                f"{magnitude:.2f}",  # Magnitude of the distributed load
                f"{distance:.2f}",   # Distance over which the load acts
                "-",                 # No point load for distributed load
                "-",                 # No factored point load
                f"{total_loading:.2f}",     # Total distributed load
                f"{factored_loading:.2f}"   # Factored distributed load
            ])

        # Add point loads to the table
        for load in st.session_state.point_loads:
            magnitude = load['magnitude']
            position = load['position']
            factored_point_loading = load['factored_point_loading']

            loadings.append([
                "Point Load",        # Load type
                "-",                 # No magnitude for point load (it's a single point load)
                "-",                 # No distance for point load
                f"{magnitude:.2f}",  # Magnitude of the point load
                f"{factored_point_loading:.2f}",  # Factored point load
                "-",                 # No total load for point load
                "-"                  # No factored total load for point load
            ])

        # Add the loadings to the data
        data.extend(loadings)

        # Calculate the totals for distributed and point loads
        total_distributed_loading, factored_distributed_loading, total_point_loading, factored_point_loading = calculate_totals()

        # Append totals to the data
        data.append([
            "Total", "-", "-",  # No specific load type, magnitude, or distance for totals
            f"{total_point_loading:.2f}",  # Total point loading
            f"{factored_point_loading:.2f}",  # Factored total point loading
            f"{total_distributed_loading:.2f}",  # Total distributed loading
            f"{factored_distributed_loading:.2f}"  # Factored total distributed loading
        ])

        return data

    def display_distributed_loads():
        st.write("### Distributed Loads")
        for idx, load in enumerate(st.session_state.distributed_loads):
            cols = st.columns([2, 1, 1, 1.5, 1, 1])
            with cols[0]:
                load_type = st.selectbox(f"Load {idx + 1} Type", 
                                        [(key, value['description']) for key, value in load_data.items()],
                                        index=0 if load['code'] is None else [key for key, _ in load_data.items()].index(load['code']))
                load['code'] = load_type[0]

            with cols[1]:
                load['distance'] = st.number_input(f"Distance {idx + 1} (m)", value=load['distance'], min_value=0.0,step = 0.00000000000000000000001)
                load['distance'] = round(load['distance'],2)
            with cols[2]:
                weight = load_data[load['code']]['weight'] if load['code'] else 0.0
                load['magnitude'] = st.number_input(f"Magnitude {idx + 1} (kN/m^2)", value=weight, min_value=0.0,step = 0.00000000000000000000001)
                load['magnitude'] = round(load['magnitude'],2)
            # Calculate total and factored loading
            total_loading = load['magnitude'] * load['distance']
            factored_loading = total_loading * load_data[load['code']]['safety_factor']
            load['total_loading'] = total_loading
            load['factored_loading'] = factored_loading

            with cols[3]:
                st.write(f"Total: {total_loading:.2f} kN/m")

            with cols[4]:
                st.write(f"Factored: {factored_loading:.2f} kN/m")

            with cols[5]:
                st.button("Remove", key=f"remove_distributed_{idx}", on_click=remove_distributed_load, args=(idx,))


    # Display Point Loads
    def display_point_loads():
        st.write("### Point Loads")
        for idx, load in enumerate(st.session_state.point_loads):
            cols = st.columns([1.3, 1, 1, 1])
            with cols[0]:
                load['magnitude'] = st.number_input(f"Point Load {idx + 1} Magnitude (kN)", value=load['magnitude'], min_value=0.0,step = 0.00000000000000000000001)
                load['magnitude'] = round(load['magnitude'],2)
            with cols[1]:
                load['position'] = st.number_input(f"Point Load {idx + 1} Position (m)", value=load['position'], min_value=0.0,step = 0.00000000000000000000001)
                load['position'] = round(load['position'],2)
            factored_point_loading = load['magnitude'] * 1.5  # Example safety factor
            load['factored_point_loading'] = factored_point_loading

            with cols[2]:
                st.write(f"Factored Load: {factored_point_loading:.2f} kN")

            with cols[3]:
                st.button("Remove", key=f"remove_point_{idx}", on_click=remove_point_load, args=(idx,))



    # Display Distributed and Point Loads
    display_distributed_loads()
    display_point_loads()

    # Add Buttons to Add New Loads
    if st.button("Add New Distributed Load"):
        add_distributed_load()

    if st.button("Add New Point Load"):
        add_point_load()

    # Calculate and Display Totals
    total_loading, factored_loading, total_point_loading, factored_point_loading = calculate_totals()
    data = get_data()
    st.write("### Summary")
    st.write(f"Total Distributed Loading: {total_loading:.2f} kN")
    st.write(f"Factored Distributed Loading: {factored_loading:.2f} kN")
    st.write(f"Total Point Loading: {total_point_loading:.2f} kN")
    st.write(f"Factored Point Loading: {factored_point_loading:.2f} kN")

    # Prepare the Final Data Table (Similar to Your Script)
    header = ["Loading Type", "Magnitude (kN/m^2 or kN)", "Distance (m)", "Point Loading (kN)", "Factored Point Loading (kN)", "Total Loading (kN/m)", "Factored Loading (kN/m)"]
    table_data = []

    # Append distributed loads
    for load in st.session_state.distributed_loads:
        load_code = load['code'] if load['code'] is not None else 'Unknown'
        description = load_data.get(load_code, {}).get('description', 'Unknown Type')
        table_data.append([
            description, f"{load['magnitude']:.2f}", f"{load['distance']:.2f}", "-", "-", f"{load['total_loading']:.2f}", f"{load['factored_loading']:.2f}"
        ])
    # Append point loads
    for load in st.session_state.point_loads:
        table_data.append([
            "Point Load", "-", "-", f"{load['magnitude']:.2f}", f"{load['factored_point_loading']:.2f}", "-", "-"
        ])

    # Display the Table
    st.write("### Load Data Table")
    st.table([header] + table_data)

    pointLoads, distributedLoads = get_load_arrays()

    total_of_totals = total_loading + total_point_loading
    pdf = PDF('P', 'mm', 'A4')

    pdf.set_auto_page_break(auto = 1, margin = 10)
    #Add a page
    pdf.add_page()

    #specify font
    pdf.set_font('Times', 'B', 18)
    pdf.set_y(50)
    pdf.cell(0,10,f'{title_of_work}',new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
    pdf.set_font('Times', '', 11)

    pdf.set_font("Times",size =  11)

    with pdf.table() as table:
        for data_row in data:
            row = table.row()
            for datum in data_row:
                row.cell(datum)
                
    gbp = st.number_input("What is the Ground Bearing Pressure: ",value = 100.0, min_value = 0.0,step = 0.00000000000000000000001 )
    gbp = round(gbp)

    Area = total_of_totals / gbp
    st.write(f'**The Area is {Area:.2f} m^2**')
    description = choose_footings()



    pdf.cell(0,10,f'Total Loading is: {total_of_totals:.2f} kN',new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
    pdf.cell(0,10,f'The Ground Bearing Pressure is: {gbp:.2f} kN/m^2',new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
    pdf.set_font('Times', 'B', 18)
    pdf.cell(0,10,f'Area Required For Foundation is: {Area:.2f} m^2',new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
    pdf.set_font('Times', '', 16)
    pdf.cell(0,10,f'Description: {description}',new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')

    final_q = st.checkbox("Do you want to add any additional information?")
    if final_q:
        pdf.set_font('Times', 'B', 11)
        pdf.ln(1)
        final_words = st.text_input("What would you like to add: ")
        page_width = pdf.w - 2 * pdf.l_margin
        pdf.multi_cell(page_width, 11, final_words, 0, 'C')
    else:
        None
        
    pdf_file_path = f'{job_number}_{job_title}_Sheet_{sheet_number}.pdf'
    pdf.output(pdf_file_path)
    finish = st.button("Finish")
    if finish:
       with open(pdf_file_path, "rb") as pdf_file:
        st.download_button(
            label="Download PDF",
            data=pdf_file,
            file_name=os.path.basename(pdf_file_path),
            mime="application/pdf"
        )

    def reset_inputs():
        st.session_state.distributed_loads = []
        st.session_state.point_loads = []
        
    clear = st.button("Clear")

    if clear:
        reset_inputs()
        st.success("Inputs have been reset 😊.")
    else:
        None
        
        
