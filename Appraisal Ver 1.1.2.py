import pandas as pd
import streamlit as st
from streamlit_drawable_canvas import st_canvas


# Set page config to ensure the sidebar is properly handled
st.set_page_config(page_title="KPI Performance Dashboard", layout="wide", initial_sidebar_state="expanded")

# Streamlit sidebar widget to select the month with a unique key
month_select = st.sidebar.selectbox('Select a Month:', ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'], key="month_select")

# Define file paths for all 12 months (Monthly Files)
file_paths = {
    "January": r"C:\Users\lenovo\Downloads\New folder\1-January 2024-2023-Appraisal Parameters Data (10).xlsx",
    "February": r"C:\Users\lenovo\Downloads\New folder\2-February 2024-2023-Appraisal Parameters Data (9).xlsx",
    # Add other months if needed
}

# Define KPI target scores dictionary
kpi_target_scores = {
    "New Business Monthly Premium": 25,
    "No of Issued Policies": 5,
    "Average Premium": 5,
    "Personal Sales": 5,
    "New Business(Production)": 10,
    "Renewal Business(Production)": 10,
    "No of Active Units": 5,
    "No of Active Agents": 5,
    "Issuing Agents": 5,
    "Potential AKI Qualifiers": 5,
    "Current Year Persistency": 5,
    "Second Year Persistency": 5,
    "Cases Converted on Maturity": 0,
    "Premium Converted on Maturity": 10
}

# Load the data based on the selected month
file_path = file_paths.get(month_select)

# Check if file exists for the selected month
if file_path:
    df = pd.read_excel(file_path, sheet_name=f"Performance-{month_select} 2024")
    df_budget = pd.read_excel(file_path, sheet_name="2024B")
    df_2023 = pd.read_excel(file_path, sheet_name="2023A")
    df_budget_2023 = pd.read_excel(file_path, sheet_name="2023B")

    # Clean up the data for regions and agencies
    regions = ["Nairobi 1", "Western", "Coast", "Central", "Nairobi 2", "Alternative"]

    # Create Region and Agency columns based on the 'REGIONS' column
    df['Region'] = df['REGIONS'].apply(lambda x: x if x in regions else None)
    df['Agency'] = df['REGIONS'].apply(lambda x: None if x in regions else x)

    # Remove rows where both Region and Agency are None (optional)
    df_filtered = df.dropna(subset=['Region', 'Agency'], how='all')

    # Streamlit sidebar widget to select the region with a unique key
    selected_region = st.sidebar.selectbox('Select a Region:', ['All Regions'] + regions, key="region_select")
    if selected_region != 'All Regions':
        df_filtered = df_filtered[df_filtered['Region'] == selected_region]

    # Streamlit sidebar widget to select the agency with a unique key
    agency_list = df_filtered[df_filtered['Region'] == selected_region]['Agency'].dropna().unique().tolist() if selected_region != 'All Regions' else df_filtered['Agency'].dropna().unique().tolist()
    selected_agency = st.sidebar.selectbox('Select an Agency:', ['All Agencies'] + agency_list, key="agency_select")
    if selected_agency != 'All Agencies':
        df_filtered = df_filtered[df_filtered['Agency'] == selected_agency]

    # Transpose the actual performance data (df_filtered)
    df_transposed_actual = df_filtered.set_index('REGIONS').T

    # Select and clean up target data from the 2024B sheet (budget data)
    df_budget_clean = df_budget[['REGIONS', 'New Business Monthly Premium', 'No of Issued Policies',
                                 'Average Premium', 'Personal Sales', 'New Business(Production)',
                                 'Renewal Business(Production)', 'No of Active Units', 'No of Active Agents',
                                 'Issuing Agents', 'Potential AKI Qualifiers', 'Current Year Persistency',
                                 '1st Year Persistency', 'Second Year Persistency', 'Cases Converted on Maturity',
                                 'Premium Converted on Maturity']]

    # Set index to 'REGIONS' for easier mapping
    df_budget_clean.set_index('REGIONS', inplace=True)

    # Select and clean up budget data from the 2023B sheet (2023 budget data)
    df_budget_2023_clean = df_budget_2023[['REGIONS', 'New Business Monthly Premium', 'No of Issued Policies',
                                            'Average Premium', 'Personal Sales', 'New Business(Production)',
                                            'Renewal Business(Production)', 'No of Active Units', 'No of Active Agents',
                                            'Issuing Agents', 'Potential AKI Qualifiers', 'Current Year Persistency',
                                            '1st Year Persistency', 'Second Year Persistency', 'Cases Converted on Maturity',
                                            'Premium Converted on Maturity']]

    # Set index to 'REGIONS' for easier mapping
    df_budget_2023_clean.set_index('REGIONS', inplace=True)

    # Initialize a new list to store the results
    final_result_ytd_list = []

    # For each KPI in the actual data, look for the corresponding target and calculate % achieved
    for kpi in df_transposed_actual.index:
        for region in df_transposed_actual.columns:
            actual_value = pd.to_numeric(df_transposed_actual.at[kpi, region], errors='coerce')

            # Get the corresponding target value from the budget (2024B)
            if region in df_budget_clean.index:
                target_value = pd.to_numeric(df_budget_clean.at[region, kpi], errors='coerce') if kpi in df_budget_clean.columns else None
            else:
                target_value = None

            # Get the corresponding 2023 actual value from the 2023A sheet
            if region in df_2023['REGIONS'].values:
                actual_2023_value = pd.to_numeric(df_2023.loc[df_2023['REGIONS'] == region, kpi].values[0], errors='coerce') if kpi in df_2023.columns else None
            else:
                actual_2023_value = None

            # Get the corresponding 2023 budget value from the 2023B sheet
            if region in df_budget_2023_clean.index:
                budget_2023_value = pd.to_numeric(df_budget_2023_clean.at[region, kpi], errors='coerce') if kpi in df_budget_2023_clean.columns else None
            else:
                budget_2023_value = None

            # Calculate the achieved % and store the results
            if target_value is not None and actual_value is not None:
                achieved_percentage = (actual_value / target_value) * 100
            else:
                achieved_percentage = None

            if actual_2023_value is not None and budget_2023_value is not None:
                achieved_percentage_2023 = (actual_2023_value / budget_2023_value) * 100
            else:
                achieved_percentage_2023 = None

            # Calculate growth % for the YTD
            if actual_value is not None and actual_2023_value is not None:
                growth_percentage = ((actual_value - actual_2023_value) / actual_2023_value) * 100
            else:
                growth_percentage = None

            # Get the KPI target score from the dictionary
            kpi_target_score = kpi_target_scores.get(kpi, None)

            # Calculate Actual_KPI_Score for 2024
            if achieved_percentage is not None and kpi_target_score is not None:
                if achieved_percentage > 100:
                    actual_kpi_score_2024 = kpi_target_score
                else:
                    actual_kpi_score_2024 = kpi_target_score * (achieved_percentage / 100)
            else:
                actual_kpi_score_2024 = None

            # Calculate Actual_KPI_Score for 2023
            if achieved_percentage_2023 is not None and kpi_target_score is not None:
                if achieved_percentage_2023 > 100:
                    actual_kpi_score_2023 = kpi_target_score
                else:
                    actual_kpi_score_2023 = kpi_target_score * (achieved_percentage_2023 / 100)
            else:
                actual_kpi_score_2023 = None

            # Prepare the data for YTD and monthly combination
            final_result_ytd_list.append({
                'Region': region,
                'KPI': kpi,
                'KPI Target Score': kpi_target_score,
                f'Actual_{month_select}_2024': actual_value,
                f'Budget_{month_select}_2024': target_value,
                f'Actual_{month_select}_2023': actual_2023_value,
                f'Budget_{month_select}_2023': budget_2023_value,
                f'%_Achieved_{month_select}_2024': achieved_percentage,
                f'%_Achieved_{month_select}_2023': achieved_percentage_2023,
                f'%_Growth_{month_select}_2024': growth_percentage,
                f'%_Growth_{month_select}_2023': growth_percentage,
                'Actual_KPI_Score_2024': actual_kpi_score_2024,
                'Actual_KPI_Score_2023': actual_kpi_score_2023
            })

    # Create a DataFrame for the final result
    final_result_ytd_df = pd.DataFrame(final_result_ytd_list)

    # Format the percentage columns to display as percentages with two decimal places
    for col in final_result_ytd_df.columns:
        if "Achieved" in col or "Growth" in col:
            final_result_ytd_df[col] = final_result_ytd_df[col].apply(lambda x: f"{x:.2f}%" if x is not None else None)

    # Calculate Total Score for the month and the growth from the previous month
    total_score_2024 = final_result_ytd_df['Actual_KPI_Score_2024'].sum()
    total_score_2023 = final_result_ytd_df['Actual_KPI_Score_2023'].sum()
    growth_from_previous_month = ((total_score_2024 - total_score_2023) / total_score_2023) * 100 if total_score_2023 != 0 else None

    # Display Appraisal Information
    team_leader = df_filtered['Name of Team Leader'].iloc[0] if 'Name of Team Leader' in df_filtered.columns else "Not Available"
    agency_name = selected_agency if selected_agency != "All Agencies" else ""
    designation = "AGENCY SALES TEAM LEADER"
    appraisal_date = f"{month_select} 2024"

    st.markdown(f"### APPRAISAL FOR THE MONTH OF {month_select.upper()} 2024 AND YTD {month_select.upper()}")
    st.markdown(f"**NAME**: {team_leader}")
    st.markdown(f"**AGENCY**: {agency_name}")
    st.markdown(f"**DESIGNATION**: {designation}")
    st.markdown(f"**DATE**: {appraisal_date}")

    # Display the table
    st.write(final_result_ytd_df)

    # Display the total scores and growth comparison
    st.markdown(f"### Total Score for {month_select} 2024: {total_score_2024:.2f}")
    st.markdown(f"### Total Score for {month_select} 2023: {total_score_2023:.2f}")
    if growth_from_previous_month is not None:
        st.markdown(f"### Growth from previous month: {growth_from_previous_month:.2f}%")
else:
    st.write("No data available for the selected month.")

# Assuming 'df_filtered' and other relevant data are already loaded

# Display Appraisal Information
team_leader = df_filtered['Name of Team Leader'].iloc[0] if 'Name of Team Leader' in df_filtered.columns else "Not Available"
agency_name = selected_agency if selected_agency != "All Agencies" else ""
designation = "AGENCY SALES TEAM LEADER"
appraisal_date = f"{month_select} 2024"


# Decision Based on Current Score
decision = ''
if total_score_2024 > 100:
    decision = f'Exceptional performance - Retain {team_leader})'
elif 91 <= total_score_2024 <= 100:
    decision = f'Commendable - Retain {team_leader})'
elif 80 <= total_score_2024 <= 90:
    decision = f'Satisfactory - Retain {team_leader})'
elif 61 <= total_score_2024 <= 79:
    decision = f'Below Expectations - Retrain {team_leader})'
elif 60 <= total_score_2024 <= 57:
    decision = f'Unsatisfactory - Performance Improvement Plan {team_leader})'   
else:
    decision = f'Poor Performance - Consider Role Change for {team_leader})'
        
st.markdown(f"**Performance Decision**: {decision}")

# Function to limit text input to a certain number of words per line
def limit_words_per_line(text, max_words_per_line=15):
    lines = text.split("\n")
    formatted_lines = []
    for line in lines:
        words = line.split()
        formatted_line = ' '.join(words[:max_words_per_line])
        formatted_lines.append(formatted_line)
    return "\n".join(formatted_lines)

# Team leader (for demo)
team_leader = df_filtered['Name of Team Leader'].iloc[0] if 'Name of Team Leader' in df_filtered.columns else "Not Available"

# Create the collapsible assessment form for Team Leader
with st.expander(f"Assessment for {team_leader} ({month_select} 2024)", expanded=False):
    # SECTION 2 - Appraisee's Comment for the Month
    st.subheader("Appraisee's Comment for the Month")

    # Appraisee's input fields (book-style comment sections)
    st.markdown("**Strength** (Write in Book Style):")
    strength = st.text_area("Strength", placeholder="Write your strength here...", height=150, key="strength")
    strength = limit_words_per_line(strength)

    # Add Submit Button
    submit_button = st.button("Submit")

    # Handle the submit action with validation
    if submit_button:
        if not strength.strip():
            st.warning("Strength input cannot be empty. Please write something.")
        elif count_words(strength) < 10:
            st.warning("Please write at least 10 words in your Strength input.")
        else:
            # When the input is valid, process the data
            st.success("Your Strength input has been successfully submitted:")
            st.write(strength)  # You can save this to a file, process it, or use it however you need

    st.markdown("**Opportunities** (Write in Book Style):")
    opportunities = st.text_area("Opportunities", placeholder="Write your opportunities here...", height=150, key="opportunities")
    opportunities = limit_words_per_line(opportunities)

    st.markdown("**Challenges** (Write in Book Style):")
    challenges = st.text_area("Challenges", placeholder="Write your challenges here...", height=150, key="challenges")
    challenges = limit_words_per_line(challenges)

    st.markdown("**Overall Comment** (Write in Book Style):")
    overall_comment = st.text_area("Overall Comment", placeholder="Write your overall comment here...", height=150, key="overall_comment")
    overall_comment = limit_words_per_line(overall_comment)

    st.markdown("**Assistance Required to Improve** (Write in Book Style):")
    assistance = st.text_area("Assistance", placeholder="Write assistance required here...", height=150, key="assistance")
    assistance = limit_words_per_line(assistance)

    st.markdown("**Goals for the Next Performance Review** (Write in Book Style):")
    goals_next_review = st.text_area("Goals Next Review", placeholder="Write your goals here...", height=150, key="goals_next_review")
    goals_next_review = limit_words_per_line(goals_next_review)

    # Appraisee's name and signature input fields
    st.text_input("Name of Appraisee", key="appraisee_name")
    
    # **Drawing Signature Online - Canvas**
    st.markdown("### Appraisee Signature (draw your signature):")
    appraisee_signature_canvas = st_canvas(
        fill_color="white",  # Background color of the canvas
        stroke_color="black",  # Color of the signature
        stroke_width=2,  # Thickness of the signature line
        width=500,  # Width of the canvas
        height=200,  # Height of the canvas
        drawing_mode="freedraw",  # Mode that allows freehand drawing
        key="appraisee_signature_canvas",
    )

    # Display the signature as an image if drawn
    if appraisee_signature_canvas.image_data is not None:
        st.image(appraisee_signature_canvas.image_data, caption="Your Signature", use_container_width=True)

    # Option to upload signature image (fallback)
    uploaded_signature = st.file_uploader("Upload Signature Image (optional)", type=["png", "jpg", "jpeg"], key="appraisee_signature_image")
    if uploaded_signature is not None:
        st.image(uploaded_signature, caption="Uploaded Signature Image", use_container_width=True)

    # Appraiser's Comment for the Month
    st.subheader("Appraiser's Comment for the Month")

    # Appraiser's input fields
    st.markdown("**Strength** (Write in Book Style):")
    appraiser_strength = st.text_area("Appraiser Strength", placeholder="Write the appraiser's strength here...", height=150, key="appraiser_strength")
    appraiser_strength = limit_words_per_line(appraiser_strength)

    st.markdown("**Opportunities** (Write in Book Style):")
    appraiser_opportunities = st.text_area("Appraiser Opportunities", placeholder="Write the appraiser's opportunities here...", height=150, key="appraiser_opportunities")
    appraiser_opportunities = limit_words_per_line(appraiser_opportunities)

    st.markdown("**Challenges** (Write in Book Style):")
    appraiser_challenges = st.text_area("Appraiser Challenges", placeholder="Write the appraiser's challenges here...", height=150, key="appraiser_challenges")
    appraiser_challenges = limit_words_per_line(appraiser_challenges)

    st.markdown("**Overall Comment** (Write in Book Style):")
    appraiser_overall_comment = st.text_area("Appraiser Overall Comment", placeholder="Write appraiser's overall comment here...", height=150, key="appraiser_overall_comment")
    appraiser_overall_comment = limit_words_per_line(appraiser_overall_comment)

    # Appraiser's designation and signature input fields
    st.text_input("Designation", value="AGENCY SALES TEAM LEADER", key="appraiser_designation", disabled=True)
    st.text_input("Name of Appraiser", key="appraiser_name")

    # **Drawing Signature Online - Canvas for Appraiser**
    st.markdown("### Appraiser Signature (draw your signature):")
    appraiser_signature_canvas = st_canvas(
        fill_color="white",  # Background color of the canvas
        stroke_color="black",  # Color of the signature
        stroke_width=2,  # Thickness of the signature line
        width=500,  # Width of the canvas
        height=200,  # Height of the canvas
        drawing_mode="freedraw",  # Mode that allows freehand drawing
        key="appraiser_signature_canvas",
    )

    # Display the signature as an image if drawn
    if appraiser_signature_canvas.image_data is not None:
        st.image(appraiser_signature_canvas.image_data, caption="Appraiser Signature", use_container_width=True)

    # Option to upload signature image for appraiser (fallback)
    uploaded_signature_appraiser = st.file_uploader("Upload Appraiser's Signature Image (optional)", type=["png", "jpg", "jpeg"], key="appraiser_signature_image")
    if uploaded_signature_appraiser is not None:
        st.image(uploaded_signature_appraiser, caption="Uploaded Appraiser Signature Image", use_container_width=True)

    # Final Remarks from Head Office
    st.subheader("Final Remarks From Head Office")
    head_office_remarks = st.text_area("Remarks", placeholder="Write final remarks from Head Office...", height=150, key="head_office_remarks")
    head_office_remarks = limit_words_per_line(head_office_remarks)
