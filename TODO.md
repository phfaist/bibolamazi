
TODO LIST & THOUGHTS
====================

Rough order by priority, top is highest priority.

- [ ] Remove Python2 support & 2-compat-3 code.  Several reasons to do so:

      1) Avoid tons of unicode string bugs
      
      2) Remove past/future dependency
      
      3) Avoid problems like \u being interpolated in raw strings (!!!) [see
      https://stackoverflow.com/a/7602511/1694896]
      
      4) Less maintenance effort
      
      5) Python2 will no longer be supported soon
      
      ### Fixed in v4.3 ???

- [ ] BUG: arXiv access persists on re-trying to fetch info from arXiv for
      invalid entry ids, even if a previous attempt returned an
      "not-found/invalid identifier" error from the server.

      ### Fixed in v4.3 ???

- [ ] More aggressive caching in duplicates.  If the entry list collected from
      the sources hasn't changed, don't re-process duplicates...

- [ ] Centralize duplicate detection mechanism, like the arXiv accessor, so that several
      filters can use the functionality if required.
      
      ?? is this really necessary ??
      
- [ ] Integration and tests with other bibliography managers? Zotero? What do
      people use?
      


Graveyard
=========

Order chonologically, top is last.

- [-] Think about directly accessing Mendeley library (via API)? Is this possible?

      * How to store credentials? In a private hidden `~/.bibolamazi/` file?
        Don't store?  --> might be unsafe/hinder usability/...

      * Note: this would hinder collaborations, if the required library cannot
        be accessed by other people
        
      NO (at least at this point).  I don't see a reliable way of doing this
      such that sources are also accessible to collaborators.

- [-] Flags for bibolamazifile? e.g. what to do when one gets a repeated key name?

      * one should be able to set flags in the bibolamazi file. Add cmd
        e.g. `flag:` or `config:` ?

      * On second thought, is this really necessary? One unique behavior might
        be preferrable.
        
      NO. Keep a well-defined single unambiguous behavior.

- [-] Sources & filters --> combine into "plugins" ... or not... ?
  
      NO. This would wreck havoc in the GUI and would require changing a lot of
      things



Completed Tasks
===============

Order chonologically, top is last.

- [x] Git/github filter packages? E.g., specify

        package: git@github.com:phfaist/myfilterpackage.git
      
      to automatically download & use the given filter package?
      
      [PROBLEM: Need git integration for that. I'm not sure I want to package
      all of that together into the bibolamazi app.] -- no git needed, download
      archives directly from github.
      
      [HTTPS filter packages? e.g., use raw access?] -- only github repos.

      [IDEA: fetch git ZIP/TAR.GZ package of the whole repository.  Only
      re-download if a newer version is available.] -- yes.
      
- [x] What to do for repeated key names in different sources?

      * Idea: detect duplicates silently, but report error if entries are different. 
        (configurable with flag? see below?)


- [x] Don't crash for a syntax error in the bibtex file!!!  ***DONE


- [x] Use something like: "
      \edef\@citeb{\expandafter\@firstofone\@citeb\@empty}% " in duplicates
      filter, to allow for spaces in citation keys ***DONE

- [x] Empty line in config section terminates the command (***DONE)

      --> otherwise if one forgets the 'src:' or 'filter:', the given sources or
          command are interpreted as further options to the previous command,
          which can be very confusing.


- [x] loggers should be cleaned up -- modules should request their logger with
      `logging.getLogger("...")`, and the log handler should only be set up in
      `core/main.py`.

      * Messages produced in the GUI should also use python loggers.

      (***DONE)


