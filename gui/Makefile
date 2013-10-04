


QTAUTODIR = qtauto

all: $(QTAUTODIR)/bibolamazi_res_rc.py $(QTAUTODIR)/ui_mainwidget.py $(QTAUTODIR)/ui_openbibfile.py



$(QTAUTODIR)/%_rc.py: %.qrc
	pyrcc4 -o $@ $<

$(QTAUTODIR)/ui_%.py: %.ui
	pyuic4 -o $@ $<
