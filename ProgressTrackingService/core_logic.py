import os
import json
import google.generativeai as genai


genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

def calculate_roadmap_weights(track_name: str, roadmap_courses: list) -> dict:
    
    
    try:
        #model = genai.GenerativeModel('gemini-3-flash-preview')
        PRIMARY_MODEL = genai.GenerativeModel('gemini-3-flash-preview')
        FALLBACK_MODEL = genai.GenerativeModel('gemma-4-31b-it')
        
        prompt = f"""
        You are an expert academic advisor in computer science and curriculum design.
        Analyze the following technical track: "{track_name}"
        And the following list of courses in its roadmap: {roadmap_courses}
        
        Assign a relative weight (importance score) to each course based on its importance, difficulty, and relevance to the overall track.
        
        CRITICAL RULES:
        1. The SUM of all weights MUST BE EXACTLY 1.0.
        2. Return ONLY a valid JSON object where the keys are the EXACT course names from the list, and the values are their weights as floats.
        3. Do not include any markdown formatting like ```json or any conversational text.
        """
            
        #response = model.generate_content(prompt)
        #response_text = response.text.strip()
        
        #if response_text.startswith("```"):
            #response_text = response_text.replace("```json", "").replace("```", "").strip()

        raw_response_text = ""
        
        try:
            print("Trying primary model (Gemini) for roadmap weights...")
            response = PRIMARY_MODEL.generate_content(prompt)
            raw_response_text = response.text.strip()
        except Exception as api_err:
            print(f"Gemini failed due to: {api_err}. Switching to fallback model (Gemma)...")
            try:
                response = FALLBACK_MODEL.generate_content(prompt)
                raw_response_text = response.text.strip()
            except Exception as fallback_err:
                raise Exception(f"Both models failed. Gemma error: {fallback_err}")
        
        if raw_response_text.startswith("```"):
            raw_response_text = raw_response_text.replace("```json", "").replace("```", "").strip()
        else:
            json_match = re.search(r'\{.*\}', raw_response_text, re.DOTALL)
            if json_match:
                raw_response_text = json_match.group(0)
        
        weights_dict = json.loads(response_text)
        return weights_dict
        
    except Exception as e:
        print(f"Error calling Gemini, switching to Fallback: {e}")

        equal_weight = round(1.0 / len(roadmap_courses), 2)
        return {course: equal_weight for course in roadmap_courses}
