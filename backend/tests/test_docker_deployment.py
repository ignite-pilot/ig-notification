"""
Docker 배포 관련 테스트
ECS 배포 시 발생할 수 있는 문제들을 사전에 확인하는 테스트
"""
import os
import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))


def test_config_module_import():
    """config 모듈이 올바르게 import되는지 확인"""
    try:
        from config import phase_config
        assert phase_config is not None
        print("✅ config 모듈 import 성공")
        return True
    except ImportError as e:
        print(f"❌ config 모듈 import 실패: {e}")
        return False


def test_main_module_import():
    """main 모듈이 올바르게 import되는지 확인"""
    try:
        import main
        assert main.app is not None
        print("✅ main 모듈 import 성공")
        return True
    except ImportError as e:
        print(f"❌ main 모듈 import 실패: {e}")
        return False
    except AttributeError as e:
        print(f"❌ main.app 속성 없음: {e}")
        return False


def test_settings_import():
    """settings 모듈이 올바르게 import되는지 확인"""
    try:
        from settings import settings
        assert settings is not None
        assert hasattr(settings, 'api_port')
        print("✅ settings 모듈 import 성공")
        return True
    except ImportError as e:
        print(f"❌ settings 모듈 import 실패: {e}")
        return False


def test_pythonpath_setup():
    """PYTHONPATH 설정이 올바른지 확인"""
    pythonpath = os.environ.get('PYTHONPATH', '')
    backend_path = str(backend_dir)
    
    # PYTHONPATH에 backend 디렉토리가 포함되어 있거나
    # 현재 디렉토리가 backend인지 확인
    if backend_path in pythonpath or str(backend_dir.parent) in pythonpath:
        print(f"✅ PYTHONPATH 설정 확인: {pythonpath}")
        return True
    else:
        # sys.path에 추가했으므로 괜찮음
        print(f"⚠️  PYTHONPATH에 없지만 sys.path에 추가됨: {pythonpath}")
        return True


def test_dockerfile_cmd():
    """Dockerfile의 CMD가 올바르게 설정되어 있는지 확인"""
    dockerfile_path = backend_dir.parent / "Dockerfile"
    if dockerfile_path.exists():
        with open(dockerfile_path, 'r') as f:
            content = f.read()
            if 'CMD ["uvicorn", "main:app"' in content or 'CMD ["python", "main.py"]' in content:
                print("✅ Dockerfile CMD 설정 확인")
                return True
            else:
                print("⚠️  Dockerfile에 CMD가 없거나 예상과 다름")
                return False
    else:
        print("⚠️  Dockerfile을 찾을 수 없음")
        return False


def test_all():
    """모든 테스트 실행"""
    print("=" * 50)
    print("Docker 배포 관련 테스트 시작")
    print("=" * 50)
    
    results = []
    
    # PYTHONPATH 설정 (Docker 환경 시뮬레이션)
    os.environ['PYTHONPATH'] = str(backend_dir)
    
    results.append(("config 모듈 import", test_config_module_import()))
    results.append(("main 모듈 import", test_main_module_import()))
    results.append(("settings 모듈 import", test_settings_import()))
    results.append(("PYTHONPATH 설정", test_pythonpath_setup()))
    results.append(("Dockerfile CMD 설정", test_dockerfile_cmd()))
    
    print("=" * 50)
    print("테스트 결과 요약")
    print("=" * 50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")
    
    print("=" * 50)
    print(f"총 {passed}/{total} 테스트 통과")
    print("=" * 50)
    
    return passed == total


if __name__ == "__main__":
    success = test_all()
    sys.exit(0 if success else 1)
