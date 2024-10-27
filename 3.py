import streamlit as st
import PyPDF2
import difflib
import io
from typing import Tuple, List
import base64

def extract_text_from_pdf(pdf_file) -> str:
    """PDF 파일에서 텍스트 추출"""
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        st.error(f"PDF 파일 읽기 오류: {str(e)}")
        return None

def analyze_differences(text1: str, text2: str, case_sensitive: bool = True) -> Tuple[List[str], int]:
    """텍스트 차이점 분석"""
    if not case_sensitive:
        text1 = text1.lower()
        text2 = text2.lower()
    
    lines1 = text1.splitlines()
    lines2 = text2.splitlines()
    
    result = []
    diff_count = 0
    
    max_len = max(len(lines1), len(lines2))
    lines1.extend([''] * (max_len - len(lines1)))
    lines2.extend([''] * (max_len - len(lines2)))
    
    for i, (line1, line2) in enumerate(zip(lines1, lines2)):
        if line1 != line2:
            diff_count += 1
            result.append(f"\n{i+1}  차이점 #{diff_count}:")
            result.append("-" * 50)
            
            result.append(f"▶ 줄 내용:")
            result.append(f"{i+1}  텍스트1: '{line1}'")
            result.append(f"{i+1}  텍스트2: '{line2}'\n")
            
            space_diff1 = len(line1) - len(line1.lstrip())
            space_diff2 = len(line2) - len(line2.lstrip())
            if space_diff1 != space_diff2:
                result.append(f"▶ 들여쓰기 차이:")
                result.append(f"  텍스트1: {space_diff1}칸")
                result.append(f"  텍스트2: {space_diff2}칸\n")
            
            special_chars1 = [char for char in line1 if not char.isalnum() and not char.isspace()]
            special_chars2 = [char for char in line2 if not char.isalnum() and not char.isspace()]
            if special_chars1 != special_chars2:
                result.append(f"▶ 특수문자 차이:")
                result.append(f"  텍스트1: {special_chars1 if special_chars1 else '[없음]'}")
                result.append(f"  텍스트2: {special_chars2 if special_chars2 else '[없음]'}")
            
            result.append("-" * 50)
    
    return result, diff_count

def highlight_differences(text1: str, text2: str) -> Tuple[str, str]:
    """HTML로 차이점 하이라이트"""
    lines1 = text1.splitlines()
    lines2 = text2.splitlines()
    
    d = difflib.Differ()
    diff = list(d.compare(lines1, lines2))
    
    html1 = []
    html2 = []
    
    for i, line in enumerate(diff, 1):
        if line.startswith('  '):  # 동일한 줄
            html1.append(f"<div>{i}  {line[2:]}</div>")
            html2.append(f"<div>{i}  {line[2:]}</div>")
        elif line.startswith('- '):  # text1에만 있는 줄
            html1.append(f"<div style='background-color: #ffcccc'>{i}  {line[2:]}</div>")
        elif line.startswith('+ '):  # text2에만 있는 줄
            html2.append(f"<div style='background-color: #ccffcc'>{i}  {line[2:]}</div>")
    
    return "\n".join(html1), "\n".join(html2)

def get_file_download_link(text: str, filename: str) -> str:
    """파일 다운로드 링크 생성"""
    b64 = base64.b64encode(text.encode()).decode()
    return f'<a href="data:file/txt;base64,{b64}" download="{filename}">결과 다운로드</a>'

def main():
    st.set_page_config(page_title="텍스트 비교 프로그램", layout="wide")
    
    st.title("텍스트 & PDF 비교 프로그램")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("첫 번째 텍스트/PDF")
        file1 = st.file_uploader("파일 업로드", type=["txt", "pdf"], key="file1")
        text1 = st.text_area("또는 텍스트 직접 입력:", height=300, key="text1")
        
        if file1:
            if file1.type == "application/pdf":
                text1 = extract_text_from_pdf(file1)
            else:
                text1 = file1.getvalue().decode('utf-8')
    
    with col2:
        st.subheader("두 번째 텍스트/PDF")
        file2 = st.file_uploader("파일 업로드", type=["txt", "pdf"], key="file2")
        text2 = st.text_area("또는 텍스트 직접 입력:", height=300, key="text2")
        
        if file2:
            if file2.type == "application/pdf":
                text2 = extract_text_from_pdf(file2)
            else:
                text2 = file2.getvalue().decode('utf-8')
    
    options_col1, options_col2, _ = st.columns([1, 1, 2])
    
    with options_col1:
        case_sensitive = st.checkbox("대소문자 구분", value=True)
    
    with options_col2:
        compare_mode = st.radio("비교 모드", ["상세 비교", "단어 단위 비교"], horizontal=True)
    
    if st.button("텍스트 비교", type="primary"):
        if not text1 or not text2:
            st.warning("⚠️ 두 텍스트를 모두 입력해주세요.")
            return
        
        # 차이점 분석
        result, diff_count = analyze_differences(text1, text2, case_sensitive)
        
        # 결과 표시
        st.subheader("비교 결과")
        
        if diff_count > 0:
            st.info(f"총 {diff_count}개의 차이점이 발견되었습니다.")
            
            # 차이점 하이라이트 표시
            html1, html2 = highlight_differences(text1, text2)
            
            result_col1, result_col2 = st.columns(2)
            
            with result_col1:
                st.markdown("<h4>텍스트 1 (하이라이트)</h4>", unsafe_allow_html=True)
                st.markdown(f"<div style='background-color: white; padding: 10px; font-family: monospace;'>{html1}</div>", unsafe_allow_html=True)
            
            with result_col2:
                st.markdown("<h4>텍스트 2 (하이라이트)</h4>", unsafe_allow_html=True)
                st.markdown(f"<div style='background-color: white; padding: 10px; font-family: monospace;'>{html2}</div>", unsafe_allow_html=True)
            
            # 상세 분석 결과
            with st.expander("상세 분석 결과 보기", expanded=True):
                st.text("\n".join(result))
            
            # 결과 다운로드 링크
            result_text = "\n".join(result)
            st.markdown(get_file_download_link(result_text, "comparison_result.txt"), unsafe_allow_html=True)
        else:
            st.success("두 텍스트가 완전히 동일합니다.")

if __name__ == "__main__":
    main()