parse_resume_system_prompt = """
Carefully analyze the following resume text and extract all relevant information:\n\n{extracted_text}\n\n"
                       "Fill in the JSON template below with the extracted information. Follow these guidelines:\n"
                       "1. Only include information that is explicitly stated or can be directly inferred from the resume.\n"
                       "2. Leave fields empty (use null for numbers, empty string for text/dates, or empty array for lists) if the information is not present.\n"
                       "3. Use your best judgment to categorize skills and determine proficiency levels (Based on their projects and courses they have done.).\n"
                       "4. Format dates as ISO 8601 strings (YYYY-MM) when possible.\n"
                       "5. Ensure all extracted information is accurate and relevant to the field it's placed in.\n"
                       "6. cgpa_or_percentage should be a number.\n"
                       "7. For all 'description' fields, write the description in a point wise like, separating the string by using nextLine character. For example: 'This is first point. \\n(nextLine character) This is second line... and so on.'\\n"
                       "8. make sure awards_and_achievements, extra_curricular_activities are an arrays of json items.\n"
                       "9. For the phone number, remove the '+91' prefix if present. Only include the digits of the phone number.\n"
                       "10. For the email, remove the 'mailto:' prefix if present. Only include the email address.\n"
                       "JSON template to fill:"
                       '''
                       {{
                           "personal_information": {{
                               "first_name": "",
                               "last_name": "",
                               "email": "",
                               "phone": "",
                               "expected_salary": null
                           }},
                           "courses": [
                               {{
                                   "course_name": "",
                                   "course_link": "",
                                   "course_provider": "",
                                   "completion_date": ""
                               }}
                           ],
                           "education": [
                               {{
                                   "institution": "",
                                   "degree": "",
                                   "start_date": "",
                                   "end_date": "",
                                   "cgpa_or_percentage": null,
                                   "description": ""
                               }}
                           ],
                           "experience": [
                               {{
                                   "company": "",
                                   "position": "",
                                   "start_date": "",
                                   "end_date": "",
                                   "description": "",
                                   "currently_working": false
                               }}
                           ],
                           "publications": [
                               {{
                                   "name": "",
                                   "link": "",
                                   "date": ""
                               }}
                           ],
                           "skills": [
                               {{
                                   "skill_name": "",
                                   "skill_proficiency": ""
                               }}
                           ],
                           "personal_projects": [
                               {{
                                   "name": "",
                                   "description": "",
                                   "link": "",
                                   "start_date": "",
                                   "end_date": ""
                               }}
                           ],
                           "awards_and_achievements": [
                                {{
                                    "description": "string1.\\nstring2."
                                }}
                           ],
                           "position_of_responsibility": [
                               {{
                                   "title": "",
                                   "organization": "",
                                   "start_date": "",
                                   "end_date": "",
                                   "description": ""
                               }}
                           ],
                           "competitions": [
                               {{
                                   "name": "",
                                   "description": "",
                                   "date": ""
                               }}
                           ],
                           "extra_curricular_activities": [
                                {{
                                    "description": "string1"
                                }}
                            ]
                       }}
                       '''
"""