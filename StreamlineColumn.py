from libraries import UB_Reactions, SHS_Reactions,CHS_Reactions,UC_Reactions
from fpdf import FPDF
from fpdf import FPDF, XPos, YPos
import requests
import webbrowser
import numpy as np
import matplotlib.pyplot as plt
from pdf2image import convert_from_path
from libraries import uc_beams, ub_beams, padstones, load_data
from libraries import choose_beam
import math
import streamlit as st 
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


def get_inputs():
    title_of_work = st.text_input("Enter the title of the work", value="")
    title_of_work = title_of_work.upper()  # Convert the title to uppercase after input

    job_title = st.text_input("Job Title", value="Harleydene Sandgate Lane Storrington",)

    initials = st.text_input("Initials", value="MM", )
    initials = initials.upper()  # Convert initials to uppercase after input

    item = st.text_input("Item", value="Structural Calculations",)

    rev = st.text_input("Revision", value="", )

    sheet_number = st.number_input("Sheet Number", min_value=1, value=1, step=1)

    job_number = st.number_input("Job Number", value=0, )

    date = st.text_input("Date", value = "", )


    return  title_of_work, job_title, initials, item, rev, sheet_number, job_number, date

reaction = st.number_input("What is your Reaction",min_value= 0, value = 1)
def effective_length_adjust():
    effective_length = st.number_input("What is your effective length", min_value=0.0, value=1.0, step=0.1)

    if effective_length is not None:
        if effective_length <1:
            effective_length = 1
        elif effective_length >1 and effective_length<=1.5:
            effective_length = 1.5
        elif effective_length >1.5 and effective_length <=2:
            effective_length = 2.0
        elif effective_length >2 and effective_length <=2.5:
            effective_length = 2.5
        elif effective_length >2.5 and effective_length <=3:
            effective_length = 3
        elif effective_length >3 and effective_length <=3.5:
            effective_length = 3.5
        elif effective_length >3.5 and effective_length <=4:
            effective_length = 4
        elif effective_length >4 and effective_length <14:
            effective_length = np.ceil(effective_length)
        
    return effective_length

columns = ["SHS","CHS","UC","UB","OTHER"]           

def column_choice(effective_length):
    type_column_choice = st.selectbox("Choose a column type", columns)
    
    if type_column_choice == 'UB':
        beam_options = {key: UB_Reactions[key]['Description'] for key in UB_Reactions}
        choice = st.selectbox("Select a UB beam", options=list(beam_options.keys()), format_func=lambda x: beam_options[x])
        
        column_display = UB_Reactions[choice]["Description"]
        column_width = UB_Reactions[choice]["Width"]
        Moment_capacity = UB_Reactions[choice]["Buckling Lengths and Values"][effective_length]["Moment"]
        axial_capacity_at_effective_length = UB_Reactions[choice]["Buckling Lengths and Values"][effective_length]["Reaction"]
    
    elif type_column_choice == 'SHS':
        beam_options = {key: SHS_Reactions[key]['Description'] for key in SHS_Reactions}
        choice = st.selectbox("Select a SHS beam", options=list(beam_options.keys()), format_func=lambda x: beam_options[x])
        
        column_display = SHS_Reactions[choice]["Description"]
        column_width = SHS_Reactions[choice]["width"]
        axial_capacity_at_effective_length = SHS_Reactions[choice]["Buckling Lengths and Reactions"][effective_length]
        Moment_capacity = SHS_Reactions[choice]["Moment"]
    
    elif type_column_choice == 'CHS':
        beam_options = {key: CHS_Reactions[key]['Description'] for key in CHS_Reactions}
        choice = st.selectbox("Select a CHS beam", options=list(beam_options.keys()), format_func=lambda x: beam_options[x])
        
        column_display = CHS_Reactions[choice]["Description"]
        column_width = CHS_Reactions[choice]["width"]
        axial_capacity_at_effective_length = CHS_Reactions[choice]["Buckling Lengths and Reactions"][effective_length]
        Moment_capacity = CHS_Reactions[choice]["Moment"]
    
    elif type_column_choice == 'UC':
        beam_options = {key: UC_Reactions[key]['Description'] for key in UC_Reactions}
        choice = st.selectbox("Select a UC beam", options=list(beam_options.keys()), format_func=lambda x: beam_options[x])
        
        column_display = UC_Reactions[choice]["Description"]
        column_width = UC_Reactions[choice]["Width"]
        Moment_capacity = UC_Reactions[choice]["Buckling Lengths and Values"][effective_length]["Moment"]
        axial_capacity_at_effective_length = UC_Reactions[choice]["Buckling Lengths and Values"][effective_length]["Reaction"]
    
    elif type_column_choice == 'OTHER':
        column_display = st.text_input("Please enter the description of the column: ").strip()
        column_width = st.number_input("Please enter the width of the column in mm: ", min_value=0.0)
        axial_capacity_at_effective_length = st.number_input("Please enter the axial capacity at the effective length of the column in kN: ", min_value=0.0)
        Moment_capacity = st.number_input("Please enter the moment capacity of the column in kNmm: ", min_value=0.0)
        choice = None
    
    return column_display, column_width, type_column_choice, choice, Moment_capacity, axial_capacity_at_effective_length

def column(reaction, column_display, column_width, effective_length, type_column_choice, choice, Moment_capacity, axial_capacity_at_effective_length):
    moment = reaction * (0.1 + float(column_width))
    result = moment / Moment_capacity + reaction / axial_capacity_at_effective_length
    
    if result >= 1:
        st.write(f"Reaction: {reaction:.2f}")
        st.write(f"Axial Capacity: {axial_capacity_at_effective_length:.2f}")
        st.write(f"Moment: {moment:.2f}")
        st.write(f"Moment Capacity: {Moment_capacity:.2f}")
        st.write(f"Sum: {result:.2f}")
        column_display, column_width, type_column_choice, choice, Moment_capacity, axial_capacity_at_effective_length = column_choice(effective_length)
    
    return Moment_capacity, axial_capacity_at_effective_length, result, moment, reaction, column_display, effective_length, type_column_choice, choice
    
def column(reaction, column_display, column_width, effective_length, type_column_choice, choice, Moment_capacity, axial_capacity_at_effective_length):
    moment = reaction * (0.1 + float(column_width))
    result = moment / Moment_capacity + reaction / axial_capacity_at_effective_length
    
    if result >= 1:
        st.write(f"Reaction: {reaction:.2f}")
        st.write(f"Axial Capacity: {axial_capacity_at_effective_length:.2f}")
        st.write(f"Moment: {moment:.2f}")
        st.write(f"Moment Capacity: {Moment_capacity:.2f}")
        st.write(f"Sum: {result:.2f}")
        st.warning("Column doesn't hold up...")
    else:
        st.success("Column Holds up well  ")
    
    return Moment_capacity, axial_capacity_at_effective_length, result, moment, reaction, column_display, effective_length, type_column_choice, choice




    



title_of_work, job_title, initials, item, rev, sheet_number, job_number, Date = get_inputs()
effective_length = effective_length_adjust()
column_display, column_width,type_column_choice,choice,Moment_capacity, axial_capacity_at_effective_length = column_choice(effective_length)
Moment_capacity,axial_capacity_at_effective_length,result,moment,reaction,column_display,effective_length,type_column_choice,choice = column(reaction,column_display, column_width, effective_length,type_column_choice,choice,Moment_capacity,axial_capacity_at_effective_length)


class PDF(FPDF):
    def header(self):
        """
        Method to add a header to each page.
        """
        # Scale the image to width 50 mm and height 30 mm
        page_number = self.page_no()
        #self.image("z:\Pdf's Adverts and Logo\logo.jpg", 10, 10, 50)
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
        self.cell(cell_width_1, 10, f'DATE {Date}', border=True, align='L')
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


pdf = PDF('P', 'mm', 'A4')

pdf.set_auto_page_break(auto = 1, margin = 10)
#Add a page
pdf.add_page()

#specify font
pdf.set_font('Times', 'B', 18)
pdf.set_y(50)
pdf.cell(0,10,f'{title_of_work}',new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
pdf.set_font('Times', '', 11)
pdf.cell(0,10,f"Try {column_display}",new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
pdf.cell(0,10,f'Effective length = {effective_length:.2f} m',new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='L')
pdf.cell(0,10,f'Total Reaction, R = {reaction:.2f} kN',new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='L')
pdf.cell(0,10,f'Total Moment, M = R(0.1+w) = {moment:.2f} kNm',new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='L')
pdf.cell(0,10,f'Compressive Force Capacity, Fc = {axial_capacity_at_effective_length:.2f} kN',new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='L')
pdf.cell(0,10,f'Moment Capacity, Mc = {Moment_capacity:.2f} kNm',new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='L')
pdf.cell(0,10,f'R/Fc + M/Mc = {result:.2f} <1',new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='L')
pdf.set_font('Times', 'B', 18)
pdf.cell(0,10,f'Therfore use: {column_display}',new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')



final_q = st.checkbox("Do you want to add any additional information?")
if final_q:
    pdf.set_font('Times', 'B', 11)
    pdf.ln(1)
    final_words = st.text_input("What would you like to add: ")
    page_width = pdf.w - 2 * pdf.l_margin
    pdf.multi_cell(page_width, 11, final_words, 0, 'L')
else:
    None
    
finish = st.button("Finish")
if finish:
    pdf.output(f'{job_number} {job_title} Sheet{sheet_number} ')
    pdf_file_path = os.path.abspath(f'{job_number} {job_title} Sheet{sheet_number} ')
    chrome_command = ["start", "chrome", pdf_file_path]
    subprocess.run(chrome_command, shell=True)
else:
    None

def reset_inputs():
    st.session_state.distributed_loads = []
    st.session_state.point_loads = []
    
clear = st.button("Clear")

if clear:
    reset_inputs()
    st.success("Inputs have been reset.")
else:
    None
    