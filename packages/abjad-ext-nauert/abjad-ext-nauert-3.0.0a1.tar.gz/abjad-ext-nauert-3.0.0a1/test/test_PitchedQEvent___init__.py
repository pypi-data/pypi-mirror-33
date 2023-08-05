import abjad
import abjadext.nauert


def test_PitchedQEvent___init___01():

    q_event = abjadext.nauert.PitchedQEvent(130, [0, 1, 4])

    assert q_event.offset == abjad.Offset(130)
    assert q_event.pitches == (
        abjad.NamedPitch(0),
        abjad.NamedPitch(1),
        abjad.NamedPitch(4)
        )
    assert q_event.attachments == ()


def test_PitchedQEvent___init___02():

    q_event = abjadext.nauert.PitchedQEvent(
        abjad.Offset(133, 5),
        [abjad.NamedPitch('fss')],
        attachments = ['foo', 'bar', 'baz']
        )

    assert q_event.offset == abjad.Offset(133, 5)
    assert q_event.pitches == (abjad.NamedPitch('fss'),)
    assert q_event.attachments == ('foo', 'bar', 'baz')
