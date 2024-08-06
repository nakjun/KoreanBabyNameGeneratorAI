import streamlit as st
import openai
import re
import os

# OpenAI API 키 설정
openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_baby_names(last_name):
    prompt = f"""2020년 이후 한국의 최근 작명 트렌드를 반영한 '{last_name}'씨의 아기 이름 5개를 추천해주세요. 한자어로 지은 이름 4개와 한글 이름 1개를 추천해주세요.
    각 이름에 대해 다음 형식으로 제공해주세요:
    1. 이름(한글): [한글이름]
    2. 이름(한자): [한자이름] (한자어로 지은 경우에만)
    3. 의미: [이름의 의미 설명]
    4. 특징: [이름의 특징이나 트렌드 관련 설명]

    각 이름은 번호를 매겨 구분해주세요."""
    
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "당신은 한국의 아기 이름 추천 전문가입니다. 2020년 이후 아기 이름 트렌드에 맞춰서 아기 이름을 추천해주세요."},
            {"role": "user", "content": prompt}
        ]
    )
    
    return response.choices[0].message.content

def parse_names(content):
    names = re.split(r'\n\s*\n', content)  # 빈 줄로 이름들을 분리
    parsed_names = []
    for name in names:
        name_dict = {}
        lines = name.strip().split('\n')
        for line in lines:
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.split('.', 1)[-1].strip()  # 번호 제거
                name_dict[key.strip()] = value.strip()
        if name_dict:  # 빈 딕셔너리가 아닌 경우만 추가
            parsed_names.append(name_dict)
    return parsed_names

st.set_page_config(page_title="아기 이름 추천 서비스", page_icon="👶", layout="wide")

st.title("👶 아기 이름 추천 서비스")
st.markdown("---")

col1, col2 = st.columns([1, 2])

with col1:
    last_name = st.text_input("성씨를 입력해주세요:")
    if st.button("이름 추천받기"):
        if last_name:
            with st.spinner("이름을 생성중입니다..."):
                baby_names = generate_baby_names(last_name)
                parsed_names = parse_names(baby_names)
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
        st.info("이 이름들은 AI에 의해 생성되었습니다. 실제 작명 시 전문가의 조언을 받는 것이 좋습니다.")