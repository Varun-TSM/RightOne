import pandas as pd

def load_jd(jd_text, extract_fn):
    try:
        jd_result = extract_fn(jd_text)
        if jd_result:
            jd_result['required_skills'] = ', '.join(jd_result.get('required_skills', []))
            jd_df = pd.DataFrame([jd_result])
            return jd_result, jd_df
        return None, None
    except Exception as e:
        raise e


