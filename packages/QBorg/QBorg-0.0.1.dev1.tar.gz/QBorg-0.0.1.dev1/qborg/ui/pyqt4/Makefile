# A literal space.
SPACE :=
SPACE +=

PYLUPDATE4 ?= pylupdate4
LRELEASE ?= lrelease
PYRCC4 ?= pyrcc4

L10N := de_CH rm_CH
SRC_DIR ?= ../../
TRANSLATIONS_DIR := ./translations

SRCS = $(abspath $(shell find '$(SRC_DIR)' -iname '*.ui' -o -iname '*.py'))

# Qt translations

%.qm: %.ts
	$(LRELEASE) '$<'

.PHONY: update_translations compile_translations

.ONESHELL:
update_translations:
	cd '$(TRANSLATIONS_DIR)'
	$(PYLUPDATE4) $(SRCS) -ts $(addprefix ./,$(addsuffix .ts,$(L10N)))

compile_translations: $(patsubst %.ts,%.qm,$(wildcard $(TRANSLATIONS_DIR)/*.ts))

# Qt resources

.PHONY: resources.py
resources.py: misc/qborg.qrc
	$(PYRCC4) -py3 -o '$@' '$<'

.PHONY: compile_resources
compile_resources: resources.py

clean:
	find '$(TRANSLATIONS_DIR)' -iname '*.qm' -delete
	$(RM) resources.py
