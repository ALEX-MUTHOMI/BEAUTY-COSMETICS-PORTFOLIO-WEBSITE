from bookings.services.legal import load_legal_markdown_source


def test_cookie_notice_does_not_claim_unconfigured_tracking():
    content = load_legal_markdown_source("COOKIE_NOTICE.md").lower()

    assert "not currently use analytics or marketing cookies" in content
    assert "we sell" not in content
    assert "we currently use third-party advertising" not in content
