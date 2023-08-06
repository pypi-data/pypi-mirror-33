# OS detection
ifeq ($(OS),Windows_NT)
$(info WARNING: Windows NT is not supported. Things are likely to break.)
else
	OS := $(shell uname -s)
	VFB ?=
	ifeq ($(OS),Darwin)
		# We assume that all Macs have a display server running
		HEADLESS := 0
	else
		ifdef DISPLAY
			HEADLESS := 0
		else
			HEADLESS := 1
		endif
		ifeq ($(VFB),)
			ifneq ($(shell which xvfb-run 2>&-),)
				# Use virtual framebuffers if possible for GUI tests
				XVFBFLAGS ?=
				VFB := '$(shell which xvfb-run 2>&-)' --auto-servernum $(XVFBFLAGS)
			endif
		endif
	endif
endif

ifneq ($(HEADLESS),0)
# Display warning on headless systems
$(info WARNING: Your system is headless. You might run into problems when trying to run QBorg.)
endif


BASE_DIR := $(shell dirname '$(realpath $(lastword $(MAKEFILE_LIST)))')
SRC_DIR := $(BASE_DIR)/qborg

SYSTEMPYTHON := '$(shell which python3 python 2>&- | head -n 1)'
VIRTUALENV_BIN := $(shell which virtualenv 2>&-)

VENV := ./venv
VENVPYTHON := '$(VENV)/bin/python3'

# Unset PYTHONHOME environment variable, because that's what a virtualenv's
# activate script does, too
unexport PYTHONHOME

# Hackety-hack around OS X system Python bustage.
# The need for this should go away with a future OS X/Xcode update.
PIP_INSTALL = \
$(if $(CFLAGS),CFLAGS='$(CFLAGS)') \
$(if $(LDFLAGS),LDFLAGS='$(LDFLAGS)') \
$(if $(ARCHFLAGS),ARCHFLAGS='$(ARCHFLAGS)') \
$(VENVPYTHON) -m pip install $(PIPFLAGS) --disable-pip-version-check


# PHONY targets

.PHONY: help
help:
	$(info )
	$(info Welcome to QBorg.)
	$(info )
	$(info You can choose between these targets:)
	$(info )
	$(info * help				Display this help page.)
	$(info )
	$(info QBorg:)
	$(info * virtualenv			Create a virtual environment.)
	$(info * develop			"setup.py develop" in the virtualenv.)
	$(info * install			"setup.py install")
	$(info * clean				Clean up.)
	$(info * lint				Run the linter.)
	$(info * test				Run tests.)
	$(info * dist				Create dist package for PyPI.)
	$(info )
	$(info Documentation:)
	$(info * docs				Generate the HTML documentation.)
	$(info * docs/{format}			Generate the documentation in {format}.)
	$(info )
	$(info Qt frontend:)
	$(info * ui/pyqt4/update_translations	Update the Linguist translation files from the source code)
	$(info * ui/pyqt4/compile_translations	Compile translations to be used by the application)
	$(info * ui/pyqt4/compile_resources	Compile the Qt resources file)
	$(info )
	@: # noop (needed to suppress "nothing to be done")


$(VENV):
ifndef SYSTEMPYTHON
	$(error Cannot find Python)
endif
# Configure virtualenv
ifdef VIRTUALENV_BIN
	$(VIRTUALENV_BIN) --python=$(SYSTEMPYTHON) --system-site-packages '$(VENV)'
else
	$(SYSTEMPYTHON) -m venv --system-site-packages '$(VENV)'
endif

.PRECIOUS: $(VENV)/.%_reqs
$(VENV)/.%_reqs: $(BASE_DIR)/requirements.d/%.txt | $(VENV)
# Install requirements for %
	$(PIP_INSTALL) -r '$(BASE_DIR)/requirements.d/$*.txt'
	@touch '$@'


.PHONY: virtualenv
virtualenv: | $(VENV) $(VENV)/.app_reqs
	$(info Created virtualenv in "$(VENV)". Run `make develop` to install an editable QBorg into the virtualenv.)


.PHONY: develop
develop: | $(VENV) $(VENV)/.development_reqs
	$(VENVPYTHON) setup.py develop


.PHONY: install
install:
	$(SYSTEMPYTHON) setup.py install


.PHONY: clean
clean:
	$(RM) -R '$(VENV)'
	$(RM) -R ./dist/
	$(RM) ./*coverage*.xml
	find '$(SRC_DIR)' -iname '*.pyc' -delete
	find '$(SRC_DIR)' -type d -name '__pycache__' -delete


.PHONY: lint
lint: | $(VENV)/.development_reqs
	$(VENVPYTHON) -m flake8 --show-source .


.PHONY: test
test: | $(VENV)/.development_reqs
ifeq ($(or $(subst 1,,$(HEADLESS)),$(VFB)),)
	$(error Your system is headless and lacks Xvfb support.)
endif
	$(VFB) $(VENVPYTHON) -m pytest --verbose --cov '$(SRC_DIR)'

.PHONY: dist
dist: | $(VENV)/.development_reqs
# Ensure all the Qt files are up to date
	$(MAKE) ui/pyqt4/compile_translations
	$(MAKE) ui/pyqt4/compile_resources
# Wrap everything up in a sdist tarball
	$(VENVPYTHON) setup.py --no-user-cfg sdist --formats=gztar

# Docs

.PHONY: docs
docs: docs/html
	$(info The generated documentation is in "$(BASE_DIR)/docs/_build/html")

docs/%: | $(VENV)/.docs_reqs
	PATH="$(abspath $(VENV))/bin:$$PATH" $(MAKE) -C docs '$(notdir $@)'


# PyQt4 UI

ui/pyqt4/%:
	$(MAKE) -C 'qborg/$(patsubst %/,%,$(dir $@))' '$(notdir $@)'


# Interactive targets

.PHONY: run # considered interactive since it does not terminate on its own
run: | $(VENV)/.app_reqs
	$(VENVPYTHON) -m qborg
