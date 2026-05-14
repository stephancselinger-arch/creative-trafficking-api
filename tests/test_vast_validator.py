import pytest
from app.services.vast_validator import validate_vast_xml


VALID_VAST_2 = """<?xml version="1.0" encoding="UTF-8"?>
<VAST version="2.0">
  <Ad id="1">
    <InLine>
      <AdSystem>TestAdServer</AdSystem>
      <AdTitle>Test Video Ad</AdTitle>
      <Impression><![CDATA[https://track.example.com/impression]]></Impression>
      <Creatives>
        <Creative>
          <Linear>
            <Duration>00:00:30</Duration>
            <MediaFiles>
              <MediaFile type="video/mp4" delivery="progressive" width="1920" height="1080">
                <![CDATA[https://cdn.example.com/video.mp4]]>
              </MediaFile>
            </MediaFiles>
            <TrackingEvents>
              <Tracking event="start"><![CDATA[https://t.example.com/start]]></Tracking>
              <Tracking event="firstQuartile"><![CDATA[https://t.example.com/q1]]></Tracking>
              <Tracking event="midpoint"><![CDATA[https://t.example.com/mid]]></Tracking>
              <Tracking event="thirdQuartile"><![CDATA[https://t.example.com/q3]]></Tracking>
              <Tracking event="complete"><![CDATA[https://t.example.com/complete]]></Tracking>
            </TrackingEvents>
          </Linear>
        </Creative>
      </Creatives>
    </InLine>
  </Ad>
</VAST>"""


def test_valid_vast():
    result = validate_vast_xml(VALID_VAST_2)
    assert result.valid
    assert result.version == "2.0"
    assert result.duration_seconds == 30
    assert result.media_file_count == 1
    assert "complete" in result.tracking_events


def test_missing_impression():
    xml = VALID_VAST_2.replace(
        "<Impression><![CDATA[https://track.example.com/impression]]></Impression>", ""
    )
    result = validate_vast_xml(xml)
    assert not result.valid
    assert any("Impression" in e for e in result.errors)


def test_missing_media_file():
    xml = VALID_VAST_2.replace(
        '<MediaFile type="video/mp4" delivery="progressive" width="1920" height="1080">\n                <![CDATA[https://cdn.example.com/video.mp4]]>\n              </MediaFile>',
        ""
    )
    result = validate_vast_xml(xml)
    assert not result.valid
    assert any("MediaFile" in e for e in result.errors)


def test_invalid_xml():
    result = validate_vast_xml("<not valid xml>")
    assert not result.valid
    assert any("parse error" in e.lower() for e in result.errors)


def test_missing_tracking_events_warns():
    xml = VALID_VAST_2.replace("<TrackingEvents>", "<!--").replace("</TrackingEvents>", "-->")
    result = validate_vast_xml(xml)
    assert result.valid
    assert any("tracking" in w.lower() for w in result.warnings)


def test_duration_parsing():
    result = validate_vast_xml(VALID_VAST_2)
    assert result.duration_seconds == 30
