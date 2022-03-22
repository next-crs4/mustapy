MUSTA_DIR=${HOME}/musta
TARGETS=all install build clean uninstall

all:
	@echo "Try one of: ${TARGETS}"

install: build
		/opt/conda/envs/snakemake/bin/pip install dist/*.whl

build: clean
	/opt/conda/envs/snakemake/bin/python setup.py bdist_wheel

clean:
	/opt/conda/envs/snakemake/bin/python setup.py clean --all
	find . -regex '.*\(\.pyc\|\.pyo\)' -exec rm -fv {} \;
	rm -rf dist *.egg-info

config:
	mkdir -p ${MUSTA_DIR}
	if [ ! -f ${MUSTA_DIR}/musta_config.yml ]; then \
		cp musta/config/musta_config.yml ${MUSTA_DIR}; \
	fi

uninstall:
		/opt/conda/envs/snakemake/bin/pip uninstall -y musta