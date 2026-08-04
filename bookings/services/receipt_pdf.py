# Compatibility wrapper. Canonical implementation lives in bookings.infrastructure.receipt_pdf.
# New code should import from bookings.infrastructure.receipt_pdf.
#
# This wrapper uses sys.modules replacement so that monkeypatch.setattr()
# on private functions (e.g. _build_pdf_bytes) works identically to
# patching the canonical module. This is required because tests use
# monkeypatch.setattr(receipt_pdf, "_build_pdf_bytes", ...).
import importlib
import sys

sys.modules[__name__] = importlib.import_module("bookings.infrastructure.receipt_pdf")
