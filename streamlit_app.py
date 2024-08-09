import streamlit as st
import openai
import re
import os
import json

# OpenAI API 키 설정
openai.api_key = os.getenv("OPENAI_API_KEY")

def contains_english(text):
    # 텍스트에 영어 문자가 있는지 확인하는 함수
    return bool(re.search(r'[a-zA-Z]', text))

def generate_baby_names(last_name, gender, style, length, repetition_syllable):
    # 성별, 스타일, 이름 길이에 따라 프롬프트 조정
    gender_text = "남자" if gender == "남자" else "여자"
    style_text = "인기 있는" if style == "인기 있는 이름" else "특별하고 독특하면서 기억에 남을"
    length_text = {        
        "2글자": "두 글자",
        "외자": "한 글자",
        "상관없음": "한 글자 또는 두 글자"
    }[length]

    #돌림자가 입력된 경우 프롬프트에 포함
    if repetition_syllable:
        repetition_text = (
            f"이름에는 '{repetition_syllable}' 돌림자를 첫 번째 글자나 두 번째 글자에 넣어 각각 5개의 이름을 생성해줘. "
            f"그 중에서 {last_name}씨와 잘 어울리는 가장 적합한 5개의 이름을 선택해줘."
        )
    else:
        repetition_text = ""

    prompt = f"""
    '{last_name}'씨의 {gender_text} 아기 이름을 {style_text} 스타일로 5개를 JSON 형식으로 추천해줘.
    이름은 입력한 {last_name}씨를 제외하고 {length_text} 이름으로 추천해줘.
    항상 한자어로 지은 이름 4개와 한글 이름 1개를 추천해줘. 예쁘고 사랑받을 수 있는 이름으로 추천해줘.
    한자어로 지은 경우에는 한자의 음독, 훈독 내용을 이름(한자) 부분에 포함해줘.
    {repetition_text}
    
    각 이름은 다음 형식의 JSON 객체로 제공해줘:
    {{
        "이름(한글)": "한글이름",
        "이름(한자)": "한자이름", 
        "의미": "이름의 의미 설명",
        "특징": "이름의 특징이나 트렌드 관련 설명"
    }}

    위 형식을 따르는 JSON 배열로 결과를 반환해줘.
    """
    
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "당신은 한국의 아기 이름 추천 전문가입니다. 입력한 조건에 맞게 적절한 이름을 추천해주세요."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )
    
    return response.choices[0].message.content

def parse_names(json_content):
    try:
        # JSON 문자열이 추가적인 문자열로 감싸져 있는 경우 이를 정리하여 순수 JSON 데이터만 추출
        json_start = json_content.find('[')
        json_end = json_content.rfind(']') + 1
        pure_json = json_content[json_start:json_end]

        # JSON 문자열을 파싱하여 Python 리스트로 변환
        parsed_names = json.loads(pure_json)
        return parsed_names
    except json.JSONDecodeError as e:
        st.error("JSON 파싱에 실패했습니다. 응답 내용을 확인하세요.")
        st.error(e)
        return []

st.set_page_config(page_title="아기 이름 추천 서비스", page_icon="👶", layout="wide")

st.title("👶 아기 이름 추천 서비스")
st.markdown("---")

col1, col2 = st.columns([1, 2])

with col1:
    last_name = st.text_input("성씨를 입력해주세요:")
    gender = st.selectbox("아기의 성별을 선택해주세요:", ("남자", "여자"))
    style = st.selectbox("이름 스타일을 선택해주세요:", ("인기 있는 이름", "특이한 이름"))
    length = st.selectbox("이름 길이를 선택해주세요:", ("2글자", "외자", "상관없음"))
    repetition_syllable = st.text_input("돌림자를 입력해주세요:")

    if st.button("이름 추천받기"):
        # 영어 문자가 포함되어 있는지 확인
        if contains_english(last_name) or contains_english(repetition_syllable):
            st.error("성씨나 돌림자에 영어 문자가 포함되어 있습니다. 한글만 입력해주세요.")
        elif last_name:
            with st.spinner("이름을 생성중입니다..."):
                baby_names_json = generate_baby_names(last_name, gender, style, length, repetition_syllable)
                parsed_names = parse_names(baby_names_json)
                st.session_state.names = parsed_names
                st.success("추천 이름이 생성되었습니다!")
        else:
            st.warning("성씨를 입력해주세요.")

with col2:
    if 'names' in st.session_state:
        for i, name in enumerate(st.session_state.names, 1):
            with st.expander(f"**추천 이름 {i}:** {name.get('이름(한글)', '')}"):
                if '이름(한자)' in name:
                    st.markdown(f"**한자:** {name['이름(한자)']}")
                st.markdown(f"**의미:** {name.get('의미', '')}")
                st.markdown(f"**특징:** {name.get('특징', '')}")
        
        st.markdown("---")
        st.info("이 이름들은 AI에 의해 추천되었습니다. 실제 작명 시 전문가의 조언을 받는 것이 좋습니다.")

st.markdown("---")
st.markdown(
    """
    <div style='text-align: center;'>
        <p>개발자 정보: <a href='mailto:njsung1217@gmail.com'>njsung1217@gmail.com</a> | <a href='https://github.com/nakjun' target='_blank'>GitHub Profile</a></p>
    </div>
    """,
    unsafe_allow_html=True
)