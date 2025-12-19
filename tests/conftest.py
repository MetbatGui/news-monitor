"""pytest 설정 파일

src/ 디렉토리를 Python path에 추가합니다.
"""

import sys
from pathlib import Path

# 프로젝트 루트의 src 디렉토리를 sys.path에 추가
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))
