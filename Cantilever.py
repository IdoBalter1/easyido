import streamlit as st 
import sys
from fpdf import FPDF, XPos, YPos
import requests
import webbrowser
import numpy as np
import matplotlib.pyplot as plt
from pdf2image import convert_from_path
from libraries import uc_beams, ub_beams, padstones, load_data
from libraries import choose_beam
from PIL import Image
import math
import subprocess
import os
import platform



def app():

    job_title = st.session_state.get("job_title", "")
    initials = st.session_state.get("initials", "MM").upper()
    item = st.session_state.get("item", "Structural Calculations")
    rev = st.session_state.get("rev", "")
    job_number = st.session_state.get("job_number", 0)
    date = st.session_state.get("date", "")
    image = st.session_state.get("image", "") or None

    materials = ["Steel"]

    def choose_padstone():
        
        st.write("Choose a padstone from the library:")
        
        # Create a list of options for the selectbox
        padstone_options = [(f"{padstone['description']} (Area: {padstone['Area']} mm²)", key) for key, padstone in padstones.items()]
        padstone_options.append(("OTHER", "other"))  # Adding the "OTHER" option

        # Use `padstone_options` in your selectbox
        selected_label, selected_key = st.selectbox("Select a padstone:", padstone_options)

        if selected_key != "other":
            selected_padstone = padstones[selected_key]  # Get the selected padstone details
            area = selected_padstone['Area']
            description = selected_padstone['description']
            st.write(f"You have selected: {description}")
            st.write(f"**Padstone Area: {area} mm²**")
            return area, description

        # For custom padstone option
        else:
            custom_name = st.text_input("Enter the name of your custom padstone: ",value = "NAME")
            custom_area = st.number_input("Enter the area of your custom padstone in mm²: ", min_value=0.0,value =10000.0, step=0.00000000000000000000001)
            custom_area = round(custom_area)
            if custom_name:
                st.write(f"You have entered a custom padstone with an area of {custom_area} mm².")
                area = custom_area
                description = custom_name
                return area, description

        return None, None  # Return None if no selection is made




    def get_inputs():
        title_of_work1 = st.text_input("Enter title of the work", value="", key="title_of_work1") 
        title_of_work1 = title_of_work1.upper()  # Convert the title to uppercase after input


        sheet_number1 = st.number_input("Enter Sheet Number", min_value=1.0, value=1.0, step=0.00000000000000000000001, key="sheet_number1")
        sheet_number1 = round(sheet_number1)



        return  title_of_work1, sheet_number1,

    title_of_work1, sheet_number1 = get_inputs()
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
            self.cell(cell_width_1, 10, f'SHEET {int(sheet_number1) + (page_number - 1)}', border=True, align='L')
            self.cell(cell_width_1, 10, f'REV {rev}', border=True, align='L')
            self.ln()

        def footer(self):
            """
            Method to add a footer to each page with page number.
            """
            self.set_y(-15)
            self.set_font('Times', 'I', 11)
            self.cell(0, 10, f'Page {self.page_no()}/{{nb}}', align='C')
    def get_user_input():
        material = "Steel"
        span = st.number_input("Enter the span (in m):",min_value=0.0 ,value=1.00, step = 0.00000000000000000000001)
        span = round(span,2)
        #st.number_input.


        if material == "Steel":
            effective_length_factor = st.number_input("Enter the effective length factor:", min_value=0.0,value =1.2, step = 0.00000000000000000000001)
            effective_length_factor = round(effective_length_factor, 3)
            self_weight = st.number_input("Enter the self-weight:", min_value=0.0,value =0.4, step = 0.00000000000000000000001)
            self_weight_safety_factor = 1.4
            effective_length = span * effective_length_factor
        else:
            effective_length = None
            self_weight = None
            self_weight_safety_factor = None

        if material == "Steel":
            padstone_input = st.checkbox("Do you want a padstone calculation?")
            if padstone_input:
                strength = st.number_input("What is the strength of the material for padstone (N/mm^2)?", min_value=0.0,value = 3.5,step = 0.00000000000000000000001)
                strength = round(strength,2)
            else:
                strength = None
        else:
            padstone_input = False
            strength = None


        return span, effective_length, padstone_input, strength ,material,self_weight_safety_factor, self_weight

    # Now, call get_user_input() to gather other inputs, and manage loads with the session state
    span, effective_length, padstone_input, strength, material,self_weight_safety_factor, self_weight = get_user_input()
    # Initialize session state
    if "distributed_loads" not in st.session_state:
        st.session_state.distributed_loads = []

    if "point_loads" not in st.session_state:
        st.session_state.point_loads = []

    st.session_state.self_weight = []
        
    if self_weight is not None:
        st.session_state.self_weight.append({"code":"self_weight","distance": span, "magnitude": self_weight, "total_loading": self_weight, "factored_loading": self_weight_safety_factor * self_weight})
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

        for load in st.session_state.self_weight:
            total_loading += load['magnitude']
            factored_loading += load['factored_loading']

        return total_loading, factored_loading, total_point_loading, factored_point_loading

    def get_load_arrays():
        pointLoads = np.array([[load['position'], load['magnitude']] for load in st.session_state.point_loads])
        distributedLoads = np.array([[0, span, load['magnitude']*load['distance']] for load in st.session_state.distributed_loads])
        if self_weight is not None:
            if distributedLoads.size == 0:
                distributedLoads = np.array([[0, span, self_weight]])
            else:
                distributedLoads = np.vstack((distributedLoads, [0, span, self_weight]))        
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
            
        if self_weight is not None:
            total_self_weight_loading = self_weight * 1  # Distributed load over 1m
            factored_self_weight_loading = total_self_weight_loading * 1.4  # Apply the safety factor

            loadings.append([
                "Self-weight",        # Load type
                f"{self_weight:.2f}",  # Magnitude of the self-weight
                "1.00",               # Distance is 1 meter for self-weight
                "-",                  # No point load for self-weight
                "-",                  # No factored point load
                f"{total_self_weight_loading:.2f}",  # Total distributed load for self-weight
                f"{factored_self_weight_loading:.2f}"  # Factored distributed load for self-weight
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
            cols = st.columns([2.4, 1, 1, 1, 1, 1])
            with cols[0]:
                load_type = st.selectbox(
                    f"Load {idx + 1} Type",
                    [(value['description'], key) for key, value in load_data.items()],
                    index=0 if load['code'] is None else [key for key, _ in load_data.items()].index(load['code']),
                    format_func=lambda x: x[0]  # Display only the description
                )
                load['code'] = load_type[1]  # Store the key instead of the description

            with cols[1]:
                load['distance'] = st.number_input(f"Distance {idx + 1} (m)", value=load['distance'], min_value=0.0,step = 0.00000000000000000000001)
                load['distance'] = round(load['distance'],2)

            with cols[2]:
                weight = load_data[load['code']]['weight'] if load['code'] else 0.0
                load['magnitude'] = st.number_input(f"Magnitude {idx + 1} (kN/m²)", value=weight, min_value=0.0,step = 0.00000000000000000000001)
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
                load['postiion'] = round(load['position'],2)
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

    for load in st.session_state.self_weight:
        table_data.append([
            "self weight", self_weight, "-", "-", "-", self_weight,self_weight*1.5])

    # Display the Table
    st.write("### Load Data Table")
    st.table([header] + table_data)

    pointLoads, distributedLoads = get_load_arrays()


    A = 0
    B = span
    divs = 10000
    delta = span / divs
    X = np.arange(0, span + delta, delta)
    nPL = pointLoads.shape[0]
    nUDL = distributedLoads.shape[0]
    reactions = np.array([0.0, 0, 0])
    shearForce = np.zeros(len(X))
    bendingMoment = np.zeros(len(X))
    max_def = span/360

    # Reaction calculation for point loads
    # Reaction calculation for point loads (PL) on cantilever
    def reactions_PL(n):
        xp = pointLoads[n, 0]  # Location of point load
        fy = pointLoads[n, 1]  # Magnitude of point load
        
        # Vertical reaction at A is the sum of all point loads
        moment_p = fy * xp  # Moment is calculated about the fixed end at A
        
        Va = fy  # The vertical reaction at A due to the point load
        Ma = moment_p  # Moment reaction at A due to the point load

        return Va, Ma

    PL_record = np.empty((0, 2))
    if nPL > 0:
        for n in range(nPL):
            Va, Ma = reactions_PL(n)
            PL_record = np.append(PL_record, [[Va, Ma]], axis=0)
            
            reactions[0] += Va  # Add to the vertical reaction at A
            reactions[1] += Ma  # Add to the moment reaction at A

    # Calculate shear and moment for point loads
    def shear_moment_PL(n):
        xp = pointLoads[n, 0]  # Location of point load (x-coordinate)
        fy = pointLoads[n, 1]  # Magnitude of point load
        va = PL_record[n, 0]   # Vertical reaction at A (fixed end)
        ma = PL_record[n, 1]   # Moment reaction at A (fixed end)
        
        Shear = np.zeros(len(X))
        Moment = np.zeros(len(X))
        
        for i, x in enumerate(X):
            shear = 0 
            moment = 0
            
            # Shear and moment due to reaction at A (fixed end)
            if x > A:
                shear += va  # Shear from reaction at A
                moment += ma - va * x  # Moment reaction at A (constant moment reaction)
            
            # If the point load is applied at the free end (x == span)
            if x > xp:  # General case for point load at an arbitrary location
                shear -= fy
                moment += fy * (x - xp)  # Subtract moment contribution after the point load position
            
            Shear[i] = shear
            Moment[i] = moment

        return Shear, Moment

    if nPL > 0:
        for n in range(nPL):
            Shear, Moment = shear_moment_PL(n)
            shearForce += Shear
            bendingMoment += Moment

    # Reaction calculation for UDLs on cantilever
    def reactions_UDL(n):
        xStart = distributedLoads[n, 0]  # Start of UDL
        xEnd = distributedLoads[n, 1]    # End of UDL
        fy = distributedLoads[n, 2]      # Magnitude of UDL per unit length
        
        fy_Res = fy * (xEnd - xStart)  # Total load from UDL
        X_Res = xStart + 0.5 * (xEnd - xStart)  # Location of the resultant force of UDL
        
        moment_p = fy_Res * X_Res  # Moment about the fixed end (A)
        
        Va = fy_Res  # Total vertical reaction at A
        Ma = moment_p  # Moment reaction at A

        return Va, Ma

    UDL_record = np.empty((0, 2))
    if nUDL > 0:
        for n in range(nUDL):
            Va, Ma = reactions_UDL(n)
            UDL_record = np.append(UDL_record, [[Va, Ma]], axis=0)
            
            reactions[0] += Va  # Add to the vertical reaction at A
            reactions[1] += Ma  # Add to the moment reaction at A

    # Calculate shear and moment for UDLs
    def shear_moment_UDL(n):
        xStart = distributedLoads[n, 0]  # Start of UDL
        xEnd = distributedLoads[n, 1]    # End of UDL
        fy = distributedLoads[n, 2]      # UDL intensity
        va = UDL_record[n, 0]   # Vertical reaction at A
        ma = UDL_record[n, 1]   # Moment reaction at A
        
        Shear = np.zeros(len(X))
        Moment = np.zeros(len(X))
        
        for i, x in enumerate(X):
            shear = 0
            moment = 0
            
            if x >= A:  # Shear and moment due to reaction at A
                shear += va
                moment += ma -va*x  # Moment at A remains constant (largest moment)
            
            if x > xStart and x <= xEnd:  # Shear and moment due to UDL
                shear -= fy * (x - xStart)
                moment += fy * (x - xStart) * (x - xStart) * 0.5
            
            elif x > xEnd:  # Beyond the UDL region
                shear += fy * (xEnd - xStart)
                moment += fy * (xEnd - xStart) * (x - xEnd)
            
            Shear[i] = shear
            Moment[i] = moment

        return Shear, Moment

    if nUDL > 0:
        for n in range(nUDL):
            Shear, Moment = shear_moment_UDL(n)
            shearForce += Shear
            bendingMoment += Moment

    # Final reactions at A for cantilever
    r1 = reactions[0]  # Vertical reaction at A
    r2 = reactions[1]  # Moment reaction at A

    st.write(f"Left Reaction = {r1}, Moment at fixed end = {r2}")


    # Calculating the maximum bending moment
    if len(bendingMoment) > 0:
        max_bending_moment = np.max(np.abs(bendingMoment))
        moment_safety_factor = 1.5* max_bending_moment
        W_equiv = max_bending_moment/span
        E = 205*10**9
        #print(f"The maximum bending moment is {max_bending_moment:.3f} kNm")



    # Create a new figure with a specific size
        fig, ax = plt.subplots(1, 2, figsize=(12, 6))

        # Shear Force Diagram
        ax[0].plot(X, shearForce, label='Shear Force')
        ax[0].fill_between(X, shearForce, color='skyblue', alpha=0.4)
        ax[0].set_xlabel('Position along the beam (m)')
        ax[0].set_ylabel('Shear Force (kN)')
        ax[0].set_title('Shear Force Diagram')
        ax[0].legend()
        ax[0].grid(True)

        # Bending Moment Diagram
        ax[1].plot(X, bendingMoment, label='Bending Moment', color='r')
        ax[1].fill_between(X, bendingMoment, color='red', alpha=0.2)
        ax[1].set_xlabel('Position along the beam (m)')
        ax[1].set_ylabel('Bending Moment (kNm)')
        ax[1].set_title('Bending Moment Diagram')
        ax[1].legend()
        ax[1].grid(True)

        # Adjust layout
        plt.tight_layout()

        # Save the figure if needed
        plt.savefig('shear_force_bending_moment.png')
        st.pyplot(fig)
    
    Ma = round(r2,2)    
    moment_safety_factor = 1.5* r2
    W_equiv = r2/span
    E = 205*10**9
    I_min = (W_equiv*10**3*span**3/(3*E*max_def)) *10**8
    pdf = PDF('P', 'mm', 'A4')

    pdf.set_auto_page_break(auto = 1, margin = 10)
    #Add a page
    pdf.add_page()
    #specify font
    pdf.set_font('Times', 'B', 18)
    pdf.set_y(50)
    pdf.cell(0,10,f'{title_of_work1}',new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
    pdf.set_font('Times', '', 11)
    pdf.cell(50,10,f'Span = {span} m',new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='L')
    if material == 'Steel':
        pdf.cell(50,10,f'Effective length = {effective_length:.2f} m',new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='L')
    else:
        None
    if material == 'Steel' or material =='Timber':
        pdf.cell(0,10,f'Allowable Deflection = {max_def:.2f} mm',new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='L')
    else:
        None


    pdf.set_font("Times",size =  11)

    with pdf.table() as table:
        for data_row in data:
            row = table.row()
            for datum in data_row:
                row.cell(datum)
    # Get the current y position after the table
    current_y = pdf.get_y()
    image_height = 70
    # Position the image 10mm below the table
    if current_y + image_height> pdf.h -pdf.b_margin :
        pdf.add_page()
        image_y = pdf.y + 10
    else:
        image_y = pdf.get_y() + 10

    # Add the image below the table
    pdf.image('shear_force_bending_moment.png', 25, image_y,150)
    pdf.set_y(image_y + image_height + 10)

    # Add further content below the image
    reactions = [r1,r2]
    pdf.set_font("Times",size =  11)
    current_y = pdf.get_y()
    text_height = 60
    if current_y + text_height> pdf.h -pdf.b_margin :
        pdf.add_page()
        text_y = pdf.y
    else:
        text_y = pdf.get_y()
    pdf.set_y(text_y)
    E = 205 * 10**9
    st.write("The effective length is " + str(round(effective_length, 2)) + " m, minimum second moment of area is " + str(round(I_min, 2)) + " cm^4, The minimum moment required " + str(round(Ma, 1)) + " kNm")
    st.write("The Maximum Deflection is " + str(round(max_def, 2)) + " mm")
    beam_display, second_moment_chosen,Moment_at_effective_length, new_effective_length, choice1,z, breadth, depth = choose_beam(effective_length,moment_safety_factor)
    if second_moment_chosen is not None and Moment_at_effective_length is not None:
        if second_moment_chosen<=I_min or Moment_at_effective_length<=moment_safety_factor:
            st.warning(f"The second moment of area chosen is {second_moment_chosen} cm^4, the required second moment of area is {np.ceil(I_min)} cm^4, the moment at the effective length is {Moment_at_effective_length} kNm, the required moment is {moment_safety_factor:.1f} kNm ⚠️")
        else:
            st.success("The Beam matches the requirement 😊")


    if choice1 == 'UC' or choice1 == 'UB' or choice1 == 'OTHER' or choice1 == 'PFC':
        pdf.cell(0, 10, f"Maximum Factored Moment = {moment_safety_factor:.2f} kNm", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='L')
        pdf.cell(0,10,f'Minimum Second Moment of Area required = {I_min:.2f} cm^4', new_x=XPos.LMARGIN, new_y=YPos.NEXT, align = 'L')
        pdf.set_font('Times', 'B', 18)
        pdf.cell(0,10,f'Therefore Use Beam : {beam_display}',new_x=XPos.LMARGIN, new_y=YPos.NEXT, align = 'L')
        pdf.set_font('Times', '', 11)
        pdf.cell(0,10,f'Moment of Beam Chosen at Effective Length of {new_effective_length}m = {Moment_at_effective_length} kNm', new_x=XPos.LMARGIN, new_y=YPos.NEXT, align = 'L')
        pdf.cell(0,10,f'Second Moment of Area of Beam Chosen = {second_moment_chosen} cm^4', new_x=XPos.LMARGIN, new_y=YPos.NEXT, align = 'L')
    elif choice1 == 'FB':
        pdf.cell(0,10,f'Flitch Capacity = 275 N/mm^2', new_x = XPos.LMARGIN, new_y = YPos.NEXT, align = 'L')
        pdf.set_font('Times', 'B', 18)
        pdf.cell(0,10,f'Therefore Use : Flitch Beam {breadth}x{depth}mm Thk STEEL PLATE',new_x=XPos.LMARGIN, new_y=YPos.NEXT, align = 'L')
        pdf.set_font('Times', 'B', 11)
        pdf.cell(0,10,f'Flitch loading = {z:.2f} N/mm^2', new_x=XPos.LMARGIN, new_y=YPos.NEXT, align = 'L')
    current_y = pdf.get_y()
    text_height = 20
    if current_y + text_height> pdf.h -pdf.b_margin :
        pdf.add_page()
        text_y = pdf.y
    else:
        text_y = pdf.get_y()
    pdf.set_y(text_y)
    pdf.cell(0, 10, f'Reaction at Fixed End = {r1:.2f} kN', new_x=XPos.LMARGIN, new_y=YPos.NEXT, align = 'L')
    pdf.cell(0, 10, f'Moment at Fixed End = {r2:.2f} kN', new_x=XPos.LMARGIN, new_y=YPos.NEXT, align = 'L')

    if padstone_input == True:
        padstone_area = max(reactions)*1.5*10**3*3.5/(1.5*strength)
        st.write(f"**minimum area is {np.ceil(padstone_area)} mm^2**")
        area = 0
        description = 'Unkown Description'
        if area<padstone_area:
            area, description = choose_padstone()
            
        if area<padstone_area:
            st.warning(f"Padstone area is {area} mm^2, the minimum area is {np.ceil(padstone_area)} mm^2 ⚠️")
        else:
            st.success(f"Padstone area is {area} mm^2, the minimum area is {np.ceil(padstone_area)} mm^2 😊")
        

        pdf.cell(0, 10, f'Padstone Area Required = {round(padstone_area)} mm^2', new_x=XPos.LMARGIN, new_y=YPos.NEXT, align = 'L')
        pdf.set_font('Times', 'B',18)
        pdf.cell(0, 10, f'Use {description}', new_x=XPos.LMARGIN, new_y=YPos.NEXT, align = 'L')
        pdf.set_font('Times', '', 11)
        pdf.cell(0, 10, f'Area of Padstone Chosen = {round(area)} > {round(padstone_area)} ', new_x=XPos.LMARGIN, new_y=YPos.NEXT, align = 'L')
    else:
        None
    


    
    final_q = st.checkbox("Do you want to add any additional information?")
    if final_q:
        pdf.set_font('Times', 'B', 11)
        pdf.ln(1)
        final_words = st.text_input("What would you like to add: ")
        page_width = pdf.w - 2 * pdf.l_margin
        pdf.multi_cell(page_width, 11, final_words, 0, 'L')
    else:
        None
        
    pdf_file_path = f'{job_number}_{job_title}_Sheet_{sheet_number1}.pdf'
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
        