import decol
import os
import pytest

@pytest.fixture
def runner():
    from click.testing import CliRunner
    return CliRunner()

@pytest.fixture
def input_text():
    return os.linesep.join([u'head1,head2,head3', u'a,b,c', u'1,2,3']) + os.linesep

# ----------
# Unit tests
# ----------
# Test discontinuous slice
def test_dslice_empty_array():
    assert decol.util.dslice([], [1,2,3]) == []
    assert decol.util.dslice(None, [1,2,3]) == []

def test_dslice_empty_indexes():
    assert decol.util.dslice([1,2,3], []) == []
    assert decol.util.dslice([1,2,3], None) == []

def test_dslice_single():
    assert decol.util.dslice([1,2,3], [1]) == [2]

def test_dslice_multi():
    assert decol.util.dslice([1,2,3], [0,2]) == [1,3]

# -----------------
# Integration tests
# -----------------
# General tests; separators, empty inputs
def test_empty_file(runner):
    result = runner.invoke(decol.cli.main, ['-', '-'], input=u'')
    assert result.exit_code == 0
    assert result.output == u''

def test_input_sep_drop_first(runner, input_text):
    input_text = input_text.replace(u',', u':')
    result = runner.invoke(decol.cli.main, ['-s', ':', '-c', '1', '-', '-'], input=input_text)
    assert result.exit_code == 0
    assert result.output == u'head2:head3\nb:c\n2:3\n'.replace('\n', os.linesep)

def test_output_sep(runner, input_text):
    result = runner.invoke(decol.cli.main, ['-o', ':', '-', '-'], input=input_text)
    assert result.exit_code == 0
    assert result.output == input_text.replace(u',', u':')

def test_drop_none(runner, input_text):
    result = runner.invoke(decol.cli.main, ['-', '-'], input=input_text)
    assert result.exit_code == 0
    assert result.output == input_text

def test_drop_none_keep(runner, input_text):
    result = runner.invoke(decol.cli.main, ['--keep', '-', '-'], input=input_text)
    assert result.exit_code == 0
    assert result.output == u''


# Test column index handling
def test_drop_first(runner, input_text):
    result = runner.invoke(decol.cli.main, ['-c', '1', '-', '-'], input=input_text)
    assert result.exit_code == 0
    assert result.output == u'head2,head3\nb,c\n2,3\n'.replace('\n', os.linesep)

def test_drop_last(runner, input_text):
    result = runner.invoke(decol.cli.main, ['-c', '3', '-', '-'], input=input_text)
    assert result.exit_code == 0
    assert result.output == u'head1,head2\na,b\n1,2\n'.replace('\n', os.linesep)

def test_drop_multi_continuous(runner, input_text):
    result = runner.invoke(decol.cli.main, ['-c', '1,2', '-', '-'], input=input_text)
    assert result.exit_code == 0
    assert result.output == u'head3\nc\n3\n'.replace('\n', os.linesep)

def test_drop_multi_discontinuous(runner, input_text):
    result = runner.invoke(decol.cli.main, ['-c', '1,3', '-', '-'], input=input_text)
    assert result.exit_code == 0
    assert result.output == u'head2\nb\n2\n'.replace('\n', os.linesep)

def test_drop_last_negative_index(runner, input_text):
    result = runner.invoke(decol.cli.main, ['-c', '-1', '-', '-'], input=input_text)
    assert result.exit_code == 0
    assert result.output == u'head1,head2\na,b\n1,2\n'.replace('\n', os.linesep)

def test_drop_nonexistent_index(runner, input_text):
    result = runner.invoke(decol.cli.main, ['-c', '4', '-', '-'], input=input_text)
    assert result.exit_code == 0
    assert result.output == input_text

def test_keep_first(runner, input_text):
    result = runner.invoke(decol.cli.main, ['-c', '1', '--keep', '-', '-'], input=input_text)
    assert result.exit_code == 0
    assert result.output == u'head1\na\n1\n'.replace('\n', os.linesep)

def test_keep_last(runner, input_text):
    result = runner.invoke(decol.cli.main, ['-c', '3', '--keep', '-', '-'], input=input_text)
    assert result.exit_code == 0
    assert result.output == u'head3\nc\n3\n'.replace('\n', os.linesep)

def test_keep_multi_continuous(runner, input_text):
    result = runner.invoke(decol.cli.main, ['-c', '1,2', '--keep', '-', '-'], input=input_text)
    assert result.exit_code == 0
    assert result.output == u'head1,head2\na,b\n1,2\n'.replace('\n', os.linesep)

def test_keep_multi_discontinuous(runner, input_text):
    result = runner.invoke(decol.cli.main, ['-c', '1,3', '--keep', '-', '-'], input=input_text)
    assert result.exit_code == 0
    assert result.output == u'head1,head3\na,c\n1,3\n'.replace('\n', os.linesep)

def test_keep_multi_reorder(runner, input_text):
    result = runner.invoke(decol.cli.main, ['-c', '2,1', '--keep', '-', '-'], input=input_text)
    assert result.exit_code == 0
    assert result.output == u'head2,head1\nb,a\n2,1\n'.replace('\n', os.linesep)

def test_keep_last_negative_index(runner, input_text):
    result = runner.invoke(decol.cli.main, ['-c', '-1', '--keep', '-', '-'], input=input_text)
    assert result.exit_code == 0
    assert result.output == u'head3\nc\n3\n'.replace('\n', os.linesep)

def test_keep_nonexistent_index(runner, input_text):
    result = runner.invoke(decol.cli.main, ['-c', '4', '--keep', '-', '-'], input=input_text)
    assert result.exit_code == 0
    assert result.output == u''

# Now repeat above tests for headers except for reorder and negative index
# tests.
def test_drop_first_header(runner, input_text):
    result = runner.invoke(decol.cli.main, ['-H', 'head1', '-', '-'], input=input_text)
    assert result.exit_code == 0
    assert result.output == u'head2,head3\nb,c\n2,3\n'.replace('\n', os.linesep)

def test_drop_last_header(runner, input_text):
    result = runner.invoke(decol.cli.main, ['-H', 'head3', '-', '-'], input=input_text)
    assert result.exit_code == 0
    assert result.output == u'head1,head2\na,b\n1,2\n'.replace('\n', os.linesep)

def test_drop_multi_continuous_header(runner, input_text):
    result = runner.invoke(decol.cli.main, ['-H', 'head1,head2', '-', '-'], input=input_text)
    assert result.exit_code == 0
    assert result.output == u'head3\nc\n3\n'.replace('\n', os.linesep)

def test_drop_multi_discontinuous_header(runner, input_text):
    result = runner.invoke(decol.cli.main, ['-H', 'head1,head3', '-', '-'], input=input_text)
    assert result.exit_code == 0
    assert result.output == u'head2\nb\n2\n'.replace('\n', os.linesep)

def test_drop_nonexistent_header(runner, input_text):
    result = runner.invoke(decol.cli.main, ['-H', 'head4', '-', '-'], input=input_text)
    assert result.exit_code == 0
    assert result.output == input_text

def test_keep_first_header(runner, input_text):
    result = runner.invoke(decol.cli.main, ['-H', 'head1', '--keep', '-', '-'], input=input_text)
    assert result.exit_code == 0
    assert result.output == u'head1\na\n1\n'.replace('\n', os.linesep)

def test_keep_last_header(runner, input_text):
    result = runner.invoke(decol.cli.main, ['-H', 'head3', '--keep', '-', '-'], input=input_text)
    assert result.exit_code == 0
    assert result.output == u'head3\nc\n3\n'.replace('\n', os.linesep)

def test_keep_multi_continuous_header(runner, input_text):
    result = runner.invoke(decol.cli.main, ['-H', 'head1,head2', '--keep', '-', '-'], input=input_text)
    assert result.exit_code == 0
    assert result.output == u'head1,head2\na,b\n1,2\n'.replace('\n', os.linesep)

def test_keep_multi_discontinuous_header(runner, input_text):
    result = runner.invoke(decol.cli.main, ['-H', 'head1,head3', '--keep', '-', '-'], input=input_text)
    assert result.exit_code == 0
    assert result.output == u'head1,head3\na,c\n1,3\n'.replace('\n', os.linesep)

def test_keep_nonexistent_header(runner, input_text):
    result = runner.invoke(decol.cli.main, ['-H', 'head4', '--keep', '-', '-'], input=input_text)
    assert result.exit_code == 0
    assert result.output == u''

# Test ranges
def test_drop_range(runner, input_text):
    result = runner.invoke(decol.cli.main, ['-c', '1:2', '-', '-'], input=input_text)
    assert result.exit_code == 0
    assert result.output == u'head3\nc\n3\n'.replace('\n', os.linesep)

def test_drop_range_negative_indexes(runner, input_text):
    result = runner.invoke(decol.cli.main, ['-c', '-3:-2', '-', '-'], input=input_text)
    assert result.exit_code == 0
    assert result.output == u'head3\nc\n3\n'.replace('\n', os.linesep)

def test_drop_range_of_one(runner, input_text):
    result = runner.invoke(decol.cli.main, ['-c', '2:2', '-', '-'], input=input_text)
    assert result.exit_code == 0
    assert result.output == u'head1,head3\na,c\n1,3\n'.replace('\n', os.linesep)

def test_drop_range_with_single(runner, input_text):
    result = runner.invoke(decol.cli.main, ['-c', '1:2,3', '-', '-'], input=input_text)
    assert result.exit_code == 0
    assert result.output == u''

def test_keep_range(runner, input_text):
    result = runner.invoke(decol.cli.main, ['-c', '1:2', '--keep', '-', '-'], input=input_text)
    assert result.exit_code == 0
    assert result.output == u'head1,head2\na,b\n1,2\n'.replace('\n', os.linesep)

def test_keep_range_negative_indexes(runner, input_text):
    result = runner.invoke(decol.cli.main, ['-c', '-3:-2', '--keep', '-', '-'], input=input_text)
    assert result.exit_code == 0
    assert result.output == u'head1,head2\na,b\n1,2\n'.replace('\n', os.linesep)

def test_keep_range_of_one(runner, input_text):
    result = runner.invoke(decol.cli.main, ['-c', '2:2', '--keep', '-', '-'], input=input_text)
    assert result.exit_code == 0
    assert result.output == u'head2\nb\n2\n'.replace('\n', os.linesep)

def test_keep_range_with_single(runner, input_text):
    result = runner.invoke(decol.cli.main, ['-c', '1:2,3', '--keep', '-', '-'], input=input_text)
    assert result.exit_code == 0
    assert result.output == input_text
