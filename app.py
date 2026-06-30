import streamlit as st
import pandas as pd
import plotly.graph_objects as ui_3d  # 3D 그래픽을 그려줄 강력한 도구

# ==========================================
# 1. 백엔드 엔진 파트 (알고리즘 및 데이터)
# ==========================================
class Item:
    def __init__(self, item_id, length, width, height, weight, destination, color):
        self.item_id = item_id    
        self.length = length      
        self.width = width        
        self.height = height      
        self.weight = weight      
        self.destination = destination  
        self.color = color  # 시각화를 위해 상자마다 색상 부여
        self.x, self.y, self.z = 0, 0, 0

    def get_volume(self):
        return self.length * self.width * self.height

class Container:
    def __init__(self, length, width, height, max_weight):
        self.length = length          
        self.width = width            
        self.height = height          
        self.max_weight = max_weight  
        self.loaded_items = []        

my_container = Container(length=5898, width=2352, height=2393, max_weight=28000)

# 테스트 화물 생성 (보기 편하게 색상 추가: 파랑, 주황, 초록, 빨강)
waiting_list = [
    Item("BOX-A", 1500, 1200, 1000, 500, 1, "royalblue"),
    Item("BOX-C", 1000, 1000, 800, 1200, 1, "forestgreen"),
    Item("BOX-B", 2000, 1500, 1200, 50, 2, "darkorange"),
    Item("BOX-D", 1800, 1200, 1100, 800, 2, "crimson")
]

# 3중 조건 정렬 및 적재
waiting_list.sort(key=lambda box: (-box.destination, -box.weight, -box.get_volume()))

extreme_points = [(0, 0, 0)]  
for box in waiting_list:
    for i, point in enumerate(extreme_points):
        if (point[0] + box.length <= my_container.length and
            point[1] + box.width <= my_container.width and
            point[2] + box.height <= my_container.height):
            
            box.x, box.y, box.z = point[0], point[1], point[2]
            my_container.loaded_items.append(box)
            extreme_points.pop(i)
            
            extreme_points.append((box.x + box.length, box.y, box.z)) 
            extreme_points.append((box.x, box.y + box.width, box.z))  
            extreme_points.append((box.x, box.y, box.z + box.height)) 
            break 

# ==========================================
# 2. 프론트엔드 파트 (스트림릿 웹 화면)
# ==========================================
st.set_page_config(page_title="3D 적재 시뮬레이터", layout="wide")
st.title("📦 3D 컨테이너 적재 최적화 시뮬레이터")
st.subheader("다중 하차(Multi-drop) 및 하중 분산 제약조건 반영 결과")

# 화면을 왼쪽(표)과 오른쪽(3D 가상 컨테이너)으로 반반 쪼개기
left_col, right_col = st.columns([1, 1.2])

with left_col:
    st.markdown("### 📋 실제 적재 좌표 결과")
    packed_data = []
    for box in my_container.loaded_items:
        packed_data.append({
            "화물 ID": box.item_id,
            "목적지": f"Dest {box.destination}",
            "무게 (kg)": box.weight,
            "X 좌표": box.x, "Y 좌표": box.y, "Z 좌표": box.z
        })
    st.dataframe(pd.DataFrame(packed_data), use_container_width=True)
    st.success(f"✅ 총 {len(my_container.loaded_items)}개의 화물 배치 완료")

with right_col:
    st.markdown("### 🧊 3D 컨테이너 가상 적재 레이아웃")
    
    # 3D 도화지 그리기
    fig = ui_3d.Figure()

    # 적재된 상자들을 3D 입체 큐브로 변환하여 도화지에 올리기
    for box in my_container.loaded_items:
        fig.add_trace(ui_3d.Mesh3d(
            x=[box.x, box.x+box.length, box.x+box.length, box.x, box.x, box.x+box.length, box.x+box.length, box.x],
            y=[box.y, box.y, box.y+box.width, box.y+box.width, box.y, box.y, box.y+box.width, box.y+box.width],
            z=[box.z, box.z, box.z, box.z, box.z+box.height, box.z+box.height, box.z+box.height, box.z+box.height],
            i=[7, 0, 0, 0, 4, 4, 6, 6, 4, 0, 3, 2],
            j=[3, 4, 1, 2, 5, 6, 5, 2, 0, 1, 6, 3],
            k=[0, 7, 2, 3, 6, 7, 1, 1, 5, 5, 2, 7],
            opacity=0.7,
            color=box.color,
            name=box.item_id,
            text=f"ID: {box.item_id}<br>무게: {box.weight}kg<br>목적지: Dest {box.destination}",
            hoverinfo="text"
        ))

    # 3D 공간 스케일 및 카메라 시점 설정
    fig.update_layout(
        scene=dict(
            xaxis=dict(title='X (가로)', range=[0, my_container.length]),
            yaxis=dict(title='Y (세로)', range=[0, my_container.width]),
            zaxis=dict(title='Z (높이)', range=[0, my_container.height]),
            aspectmode='manual',
            aspectratio=dict(x=2, y=1, z=1) # 20ft 컨테이너처럼 가로를 길게 조정
        ),
        margin=dict(r=0, l=0, b=0, t=0),
        height=550
    )
    
    # 스트림릿 웹 화면에 3D 그래프 출력하기
    st.plotly_chart(fig, use_container_width=True)