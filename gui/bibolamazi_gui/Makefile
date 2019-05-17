


QTAUTODIR = qtauto


TARGETS = $(QTAUTODIR)/bibolamazi_res_rc.py \
	 $(QTAUTODIR)/ui_startupwidget.py \
	 $(QTAUTODIR)/ui_openbibfile.py \
	 $(QTAUTODIR)/ui_newbibolamazifiledialog.py \
	 $(QTAUTODIR)/ui_helpbrowser.py \
	 $(QTAUTODIR)/ui_sourcelisteditor.py \
	 $(QTAUTODIR)/ui_filterinstanceeditor.py \
	 $(QTAUTODIR)/ui_filterpackagepatheditor.py \
	 $(QTAUTODIR)/ui_overlistbuttonwidget.py \
	 $(QTAUTODIR)/ui_settingswidget.py \
	 $(QTAUTODIR)/ui_favoritesoverbtns.py \
	 $(QTAUTODIR)/ui_searchwidget.py \
	 $(QTAUTODIR)/ui_githubreposelector.py \
	 $(QTAUTODIR)/ui_githubauthenticationdialog.py


all: $(TARGETS)

clean:
	rm $(TARGETS)


$(QTAUTODIR)/%_rc.py: %.qrc
	pyrcc5 -o $@ $<

$(QTAUTODIR)/ui_%.py: %.ui
	pyuic5 --from-imports -o $@ $<
