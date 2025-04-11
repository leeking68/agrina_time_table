
import streamlit as st
import csv
from collections import defaultdict
from io import StringIO

st.set_page_config(page_title="출석부 곡 매칭기", layout="centered")

st.title("🎵 출석부 기반 가능한 곡 추출기")
st.write("1. CSV 파일을 업로드하세요.\n2. 버튼을 누르면 가능한 곡이 분석됩니다.\n3. 결과를 CSV로 다운로드 하세요.")

uploaded_file = st.file_uploader("📂 CSV 파일 업로드", type=["csv"])

def load_schedule_and_songs_from_csv(file_content):
    schedule_dict = {}
    result_by_time = defaultdict(list)

    file_content.seek(0)
    reader = list(csv.reader(StringIO(file_content.read().decode("utf-8"))))

    for row in reader[1:12]:
        time = row[0].strip()
        if not time:
            continue
        attendees = [name.strip() for name in row[1].split(',') if name.strip()]
        schedule_dict[time] = attendees

    for row in reader[13:]:
        song_name = row[0].strip()
        if not song_name:
            break
        required_people = [
            name.strip() for name in row[1:10]
            if name.strip() and name.strip().upper() != 'X'
        ]
        for time, attendees in schedule_dict.items():
            if all(person in attendees for person in required_people):
                result_by_time[time].append(song_name)

    return result_by_time

if uploaded_file:
    if st.button("🎯 가능한 곡 추출"):
        try:
            results = load_schedule_and_songs_from_csv(uploaded_file)
        except Exception as e:
            st.error(f"❌ 오류 발생: {e}")
        else:
            if results:
                st.success("✅ 가능한 곡 추출 완료!")
                csv_lines = [["시간", "가능한 곡"]]
                for time, songs in sorted(results.items()):
                    csv_lines.append([time, ", ".join(songs)])

                # 미리보기
                for line in csv_lines[1:]:
                    st.write(f"**{line[0]}**: {line[1]}")

                # 다운로드용 CSV 문자열 생성
                output = StringIO()
                writer = csv.writer(output)
                writer.writerows(csv_lines)
                csv_data = output.getvalue().encode("utf-8-sig")

                st.download_button(
                    label="📥 결과 CSV 다운로드",
                    data=csv_data,
                    file_name="시간대별_가능한곡.csv",
                    mime="text/csv"
                )
            else:
                st.warning("⚠️ 가능한 곡이 없습니다. 출석부 데이터를 확인해주세요.")
