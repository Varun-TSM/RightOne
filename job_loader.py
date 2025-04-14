import pandas as pd

def parse_and_save_job_description(jd_data):
    # Combine the list of required_skills into a single string
    jd_data['required_skills'] = ', '.join(jd_data['required_skills'])

    # Convert the job description data (jd_data) into a DataFrame
    jd_df = pd.DataFrame([jd_data])

    # Save the DataFrame as an Excel file
    jd_df.to_excel('job_description.xlsx', index=False)
    print("Job description saved to job_description.xlsx")


