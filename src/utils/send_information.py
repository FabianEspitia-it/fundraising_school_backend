import requests
import os
"""
def send_information(user_data: dict, startup_name: str = "", startup_url: str = "", job_title: str = "", main_industry: str = "", company_name: str = "", job_level: str = "", ecosystem_role: str = "", fund_name: str = "", job_title_3: str = ""):
    FIRST_URL =  os.getenv('FIRST_MANU_URL')
    SECOND_URL = os.getenv('SECOND_MANU_URL')
    THIRD_URL = os.getenv('THIRD_MANU_URL')

    headers = {
        "Content-Type": "application/json; charset=utf-8"
    }

    data = {
        "name": "Form Attendees Inve industry", 
        "site": "66225b4e6f1e157782b0aaac",
        "Form Attendees Name": user_data["name"],
        "Form Attendees Email": user_data["email"],
        "Form Attendees Linkedin": user_data["linkedin"],
        "Form Attendees Phone": f"+{user_data['country_code']} {user_data['phone_number']}",
        "Form Attendees Country": user_data["location"],
        "You want to attend as?": user_data["role"], 
        "Startup Name": startup_name,
        "Startup URL": startup_url,
        "Job Title": job_title,
        "Main Industry": main_industry,
        "Company Name": company_name,
        "Job Level": job_level,
        "Ecosystem Rol": ecosystem_role,
        "Fund Name": fund_name,
        "Job Title 3": job_title_3
    }


    urls = [FIRST_URL, SECOND_URL, THIRD_URL]
    responses = []

    for url in urls:
        response = requests.post(url, headers=headers ,data=data)
        if response.status_code == 200:
            responses.append({"url": url, "status": "success", "details": response.json()})
        else:
            responses.append({"url": url, "status": "error", "details": response.text})
    
    return responses


print(send_information({"name": "John Doe", "email": " joe@gmail.com", "linkedin": "linkedin.com/johndoe", "phone_number": "3202377112", "country_code": "57", "location": "Colombia", "role": "Investor"}))
"""