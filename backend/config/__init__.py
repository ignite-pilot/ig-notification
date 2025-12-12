"""
Phase별 설정 모듈
"""
import os

# Phase 선택 (환경 변수 또는 기본값: local)
PHASE = os.getenv("PHASE", "local").lower()

if PHASE == "alpha":
    from .alpha import AlphaConfig as PhaseConfig
elif PHASE == "local":
    from .local import LocalConfig as PhaseConfig
else:
    # 기본값은 local
    from .local import LocalConfig as PhaseConfig

# 현재 Phase 설정
phase_config = PhaseConfig()

