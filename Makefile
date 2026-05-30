.PHONY: install test run clean demo frontend

install:
	pip install -e ".[dev]"

test:
	python -m pytest tests/ -v

run:
	python -m uvicorn src.api.app:app --host 0.0.0.0 --port 8060 --reload

frontend:
	@echo "启动 API 后，用浏览器打开 frontend/index.html"
	@echo "API 地址: http://localhost:8060"
	@echo "API 文档: http://localhost:8060/docs"

demo:
	@python -c "\
from src.core.huangji_algorithm import HuangjiEngine; \
from src.core.tiangan_dizhi import year_ganzhi; \
from src.data.interpretations import INTERPRETATIONS; \
import sys; \
year = int(sys.argv[1]) if len(sys.argv) > 1 else 2026; \
e = HuangjiEngine(); \
chain = e.compute_chain(year); \
gz = year_ganzhi(year); \
print(f'{year}年({gz.name}) 九层卦象链:'); \
print(f'  元:{chain.yuan} 会:{chain.hui} 运:{chain.yun}'); \
print(f'  世:{chain.shi} 十年:{chain.ten_year} 岁:{chain.sui}'); \
interp = INTERPRETATIONS.get(chain.sui.name); \
print(f'  岁卦解读: {interp.xiang_ci if interp else \"待补充\"}'); \
"

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	rm -rf .pytest_cache dist *.egg-info
