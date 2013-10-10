


QTAUTODIR = qtauto


TARGETS = $(QTAUTODIR)/bibolamazi_res_rc.py \
	 $(QTAUTODIR)/ui_mainwidget.py \
	 $(QTAUTODIR)/ui_openbibfile.py \
	 $(QTAUTODIR)/ui_helpbrowser.py \
	 $(QTAUTODIR)/ui_sourcelisteditor.py


all: $(TARGETS)

clean:
	rm $(TARGETS)


$(QTAUTODIR)/%_rc.py: %.qrc
	pyrcc4 -o $@ $<

$(QTAUTODIR)/ui_%.py: %.ui
	pyuic4 -o $@ $<
