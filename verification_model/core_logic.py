import os
from urllib import response
import requests
import zipfile
import io
import re
import shutil
import tempfile
import google.generativeai as genai
from pylint.lint import Run
from contextlib import redirect_stdout
from dotenv import load_dotenv
import json

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def start_evaluation_process(request_data, db_ref):
    student_id = request_data.studentId
    github_url = request_data.projectLink
    
    if github_url.endswith('/'): github_url = github_url[:-1]
    
    temp_parent = tempfile.mkdtemp()
    success = False
    
    for branch in ["main", "master"]:
        download_url = f"{github_url}/archive/refs/heads/{branch}.zip"
        response = requests.get(download_url)
        if response.status_code == 200:
            z = zipfile.ZipFile(io.BytesIO(response.content))
            z.extractall(temp_parent)
            folder_name = z.namelist()[0].split('/')[0]
            project_path = os.path.join(temp_parent, folder_name)
            success = True
            break
            
    if not success:
        db_ref[student_id] = {"status": "Error", "feedback": {"suggestions": "Could not download repository."}}
        return

    try:
        all_code = ""
        valid_ext = ('.py', '.js', '.jsx', '.ts', '.tsx', '.html', '.css', '.cpp', '.h')
        
        for root, _, files in os.walk(project_path):
            if any(x in root for x in ['node_modules', '.git']): continue
            for file in files:
                if file.endswith(valid_ext):
                    path = os.path.join(root, file)
                    with open(path, 'r', encoding='utf-8') as f:
                        all_code += f"\n--- File: {file} ---\n" + f.read()

        model = genai.GenerativeModel('gemini-3-flash-preview')
        prompt = f"""
        You are an expert code reviewer for the Syntra.AI platform.
        Evaluate the following project code based on the track: {request_data.trackId}.
        
        Return the result STRICTLY as a JSON object with this structure:
        {{
            "score": number,
            "status": "Passed" or "Failed",
            "feedback": {{
                "strengths": ["list of strings"],
                "weaknesses": ["list of strings"],
                "suggestions": "string"
            }},
            "requirements_met": [
                {{"feature": "feature name", "status": boolean}}
            ]
        }}

        Code Content:
        {all_code}
        """
        
        response = model.generate_content(prompt)
        
        json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
        res_text = json_match.group(0) if json_match else response.text
        final_result = json.loads(res_text)
        
        if "requirements_met" not in final_result:
            final_result["requirements_met"] = []

        db_ref[student_id] = final_result

    except Exception as e:
        db_ref[student_id] = {"status": "Error", "message": str(e)}
    finally:
        shutil.rmtree(temp_parent) 