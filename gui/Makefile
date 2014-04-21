


QTAUTODIR = qtauto


TARGETS = $(QTAUTODIR)/bibolamazi_res_rc.py \
	 $(QTAUTODIR)/ui_mainwidget.py \
	 $(QTAUTODIR)/ui_openbibfile.py \
	 $(QTAUTODIR)/ui_helpbrowser.py \
	 $(QTAUTODIR)/ui_sourcelisteditor.py \
	 $(QTAUTODIR)/ui_filterinstanceeditor.py \
	 $(QTAUTODIR)/ui_overlistbuttonwidget.py \
	 $(QTAUTODIR)/ui_settingswidget.py \
	 $(QTAUTODIR)/ui_favoritesoverbtns.py


all: $(TARGETS)

clean:
	rm $(TARGETS)


$(QTAUTODIR)/%_rc.py: %.qrc
	pyrcc4 -o $@ $<

$(QTAUTODIR)/ui_%.py: %.ui
	pyuic4 -o $@ $<
