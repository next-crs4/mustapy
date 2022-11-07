TARGETS=all install build clean uninstall

all:
	@echo "Try one of: ${TARGETS}"

install: build
		/opt/conda/envs/musta/bin/pip install dist/*.whl

build: clean
	/opt/conda/envs/musta/bin/python setup.py bdist_wheel

clean:
	/opt/conda/envs/musta/bin/python setup.py clean --all
	find . -regex '.*\(\.pyc\|\.pyo\)' -exec rm -fv {} \;
	rm -rf dist *.egg-info


uninstall:
		/opt/conda/envs/musta/bin/pip uninstall -y musta