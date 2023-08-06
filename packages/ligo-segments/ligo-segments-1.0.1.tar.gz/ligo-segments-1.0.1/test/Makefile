PYTHON ?= python

check : \
	segments_verify
	@echo "All Tests Passed"

define printpassfail
	{ echo "Pass" ; true ; } || { echo "Fail" ; false ; }
endef

SERVEFILESPORT := 16543

define servefilesstart
	{ $(PYTHON) -c "from six.moves.socketserver import TCPServer ; from six.moves.SimpleHTTPServer import SimpleHTTPRequestHandler ; TCPServer(('127.0.0.1', $(SERVEFILESPORT)), SimpleHTTPRequestHandler).serve_forever()" & sleep 1 ; }
endef
define servefilesstop
	{ killall $(PYTHON) ; sleep 1 ; true ; }
endef

segments_verify :
	@echo "=== start segments_verify ===>"
	$(PYTHON) segments_verify.py && $(printpassfail)
	@echo "<=== end segments_verify ==="
