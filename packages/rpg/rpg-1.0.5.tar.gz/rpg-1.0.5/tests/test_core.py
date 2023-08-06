"""Tests for core.py"""
import pytest
from .context import rpg
from rpg import core
from rpg import rule
from rpg import enzyme
from rpg import digest
from rpg import sequence

def test_handle_errors(capsys):
    """Test function 'handle_errors(msg="", err=1, error_type="")'"""
    # Error, then exit
    message = "This is a test"
    error = 0
    error_type = "Test "
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        core.handle_errors(message, error, error_type)
    _, err = capsys.readouterr()
    assert err == "Test Error: This is a test\n"
    assert pytest_wrapped_e.type == SystemExit
    assert pytest_wrapped_e.value.code == 1

    # Warning test
    message = "This is a test"
    error = 1
    error_type = "Test "
    core.handle_errors(message, error, error_type)
    _, err = capsys.readouterr()
    assert err == "Test Warning: This is a test\n"

    # Writing in stderr test
    message = "This is a test"
    error = 2
    error_type = "Test "
    core.handle_errors(message, error, error_type)
    _, err = capsys.readouterr()
    assert err == "Test This is a test\n"

    # Default parameters
    message = "This is a test"
    core.handle_errors(message)
    _, err = capsys.readouterr()
    assert err == "Warning: This is a test\n"

def test_get_header():
    """Test function 'get_header(fmt="fasta")'"""
    res_fasta = None
    res_csv = "Original_header,No_peptide,Enzyme,Cleaving_pos,Peptide_size,Pe"\
              "ptide_mass,pI,Sequence"
    res_tsv = "Original_header\tNo_peptide\tEnzyme\tCleaving_pos\tPeptide_siz"\
              "e\tPeptide_mass\tpI\tSequence"
    assert core.get_header() == res_fasta
    assert core.get_header("csv") == res_csv
    assert core.get_header("tsv") == res_tsv
    assert core.get_header("pwet") == res_fasta

def test_output_results(capsys, tmpdir):
    """Test function 'output_results(output_file, all_seq_digested,
                                     fmt, quiet, verbose)'"""
    # Test file not found
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        core.output_results("/tmp", None, "csv", False, False)
    _, err = capsys.readouterr()
    assert err == "File Error: /tmp can't be open in 'w' mode\n"
    assert pytest_wrapped_e.type == SystemExit
    assert pytest_wrapped_e.value.code == 1

    a_rule = {}
    rule_txt = "(S)(D,)"
    a_rule[rule_txt] = True
    all_rules = rule.create_rules(a_rule)
    enz1 = enzyme.Enzyme(-1, "fake_enzyme1", all_rules)
    enzymes = [enz1]
    mode = "sequential"

    # CSV output
    seq = "WQSDESDFZQSDESDF"
    all_seq_digested = digest.digest_from_input(seq, enzymes, mode)
    output_file = tmpdir.join("test_result.csv")
    fmt = "csv"
    quiet = False
    verbose = 0
    core.output_results(str(output_file), all_seq_digested, fmt, quiet, verbose)
    out, err = capsys.readouterr()
    assert out == output_file.read()
    assert output_file.read() == "Original_header,No_peptide,Enzyme,Cleaving_"\
                                 "pos,Peptide_size,Peptide_mass,pI,Sequence\n"\
                                 "Input,0,fake_enzyme1,4,4,534.52598,3.6,WQSD"\
                                 "\nInput,1,fake_enzyme1,7,3,349.29758,3.4,ES"\
                                 "D\nInput,2,fake_enzyme1,12,5,495.48938,3.6,"\
                                 "FZQSD\nInput,3,fake_enzyme1,15,3,349.29758,"\
                                 "3.4,ESD\nInput,4,fake_enzyme1,16,1,165.1918"\
                                 "8,5.54,F\n"

    # TSV output
    output_file = tmpdir.join("test_result.tsv")
    fmt = "tsv"
    quiet = False
    verbose = 0
    core.output_results(str(output_file), all_seq_digested, fmt, quiet, verbose)
    out, err = capsys.readouterr()
    assert out == output_file.read()
    assert output_file.read() == "Original_header\tNo_peptide\tEnzyme\tCleavi"\
                                 "ng_pos\tPeptide_size\tPeptide_mass\tpI\tSeq"\
                                 "uence\nInput\t0\tfake_enzyme1\t4\t4\t534.52"\
                                 "598\t3.6\tWQSD\nInput\t1\tfake_enzyme1\t7\t"\
                                 "3\t349.29758\t3.4\tESD\nInput\t2\tfake_enzy"\
                                 "me1\t12\t5\t495.48938\t3.6\tFZQSD\nInput\t3"\
                                 "\tfake_enzyme1\t15\t3\t349.29758\t3.4\tESD"\
                                 "\nInput\t4\tfake_enzyme1\t16\t1\t165.19188"\
                                 "\t5.54\tF\n"

    # Fasta output
    output_file = tmpdir.join("test_result.fasta")
    fmt = "fasta"
    quiet = False
    verbose = 0
    core.output_results(str(output_file), all_seq_digested, fmt, quiet, verbose)
    out, err = capsys.readouterr()
    assert out == output_file.read()
    assert output_file.read() == ">Input_0_fake_enzyme1_4_4_534.52598_3.6\nWQ"\
                                 "SD\n>Input_1_fake_enzyme1_7_3_349.29758_3.4"\
                                 "\nESD\n>Input_2_fake_enzyme1_12_5_495.48938"\
                                 "_3.6\nFZQSD\n>Input_3_fake_enzyme1_15_3_349"\
                                 ".29758_3.4\nESD\n>Input_4_fake_enzyme1_16_1"\
                                 "_165.19188_5.54\nF\n"

    # CSV output in quiet
    seq = "WQSDESDFZQSDESDF"
    all_seq_digested = digest.digest_from_input(seq, enzymes, mode)
    output_file = tmpdir.join("test_result.csv")
    fmt = "csv"
    quiet = True
    verbose = 0
    core.output_results(str(output_file), all_seq_digested, fmt, quiet,
                        verbose)
    out, err = capsys.readouterr()
    # Quiet
    assert out == ""
    assert output_file.read() == "Original_header,No_peptide,Enzyme,Cleaving_"\
                                 "pos,Peptide_size,Peptide_mass,pI,Sequence\n"\
                                 "Input,0,fake_enzyme1,4,4,534.52598,3.6,WQSD"\
                                 "\nInput,1,fake_enzyme1,7,3,349.29758,3.4,ES"\
                                 "D\nInput,2,fake_enzyme1,12,5,495.48938,3.6,"\
                                 "FZQSD\nInput,3,fake_enzyme1,15,3,349.29758,"\
                                 "3.4,ESD\nInput,4,fake_enzyme1,16,1,165.1918"\
                                 "8,5.54,F\n"

    # CSV output in verbose > 2
    seq = "WQSDESDFZQSDESDF"
    all_seq_digested = digest.digest_from_input(seq, enzymes, mode)
    output_file = tmpdir.join("test_result.csv")
    fmt = "csv"
    quiet = False
    verbose = 3
    core.output_results(str(output_file), all_seq_digested, fmt, quiet,
                        verbose)
    out, err = capsys.readouterr()
    assert output_file.read() == "Original_header,No_peptide,Enzyme,Cleaving_"\
                                 "pos,Peptide_size,Peptide_mass,pI,Sequence\n"\
                                 "Input,0,fake_enzyme1,4,4,534.52598,3.6,WQSD"\
                                 "\nInput,1,fake_enzyme1,7,3,349.29758,3.4,ES"\
                                 "D\nInput,2,fake_enzyme1,12,5,495.48938,3.6,"\
                                 "FZQSD\nInput,3,fake_enzyme1,15,3,349.29758,"\
                                 "3.4,ESD\nInput,4,fake_enzyme1,16,1,165.1918"\
                                 "8,5.54,F\n"
    # Verbose > 2
    assert out == "\nNumber of cleavage: 4\nCleavage position: 4, 7, 12, 15\n"\
                  "Number of miscleavage: 0\nmiscleavage position: \nmis"\
                  "cleavage ratio: 0.00%\nSmallest peptide size: 1\nN termin"\
                  "al peptide: WQSD\nC terminal peptide: F\n" + \
                  output_file.read()

def test_peptide():
    """Test class 'Peptide'"""
    header = "Test"
    seq = "QWSDESDF"
    enz_name = "fake_enzyme"
    pep0 = sequence.Peptide(header, seq, enz_name, 1, 3)
    # Test function '__repr__()'
    print_res = pep0.__repr__()
    assert print_res == "Original header: Test\nNo. peptide: 1\nEnzyme: fake_"\
                        "enzyme\nCleav. pos: 3\nPep. size: 8\nPep. mass: 1012"\
                        ".98488\nPep. pI: 3.29\nSequence: QWSDESDF\n"

    # Test function '__eq__()'
    pep1 = sequence.Peptide(header, seq, enz_name, 1, 3)
    assert pep0 == pep1

    # Test function '__ne__()'
    pep2 = sequence.Peptide(header, seq, enz_name, 1, 2)
    pep3 = sequence.Peptide(header, seq, enz_name, 2, 3)
    pep4 = sequence.Peptide(header, seq, enz_name + "A", 1, 3)
    pep5 = sequence.Peptide(header, seq + "A", enz_name, 1, 3)
    pep6 = sequence.Peptide(header + "A", seq, enz_name, 1, 3)
    assert pep0 != pep2
    assert pep0 != pep3
    assert pep0 != pep4
    assert pep0 != pep5
    assert pep0 != pep6

    # Test function '__format__()'
    format_res = pep0.__format__("csv")
    assert format_res == "Test,1,fake_enzyme,3,8,1012.98488,3.29,QWSDESDF"
    format_res = pep2.__format__("tsv")
    assert format_res == "Test\t1\tfake_enzyme\t2\t8\t1012.98488\t3.29\tQWSD"\
                         "ESDF"
    format_res = pep3.__format__("fasta")
    assert format_res == ">Test_2_fake_enzyme_3_8_1012.98488_3.29\nQWSDESDF"

    # Test function 'def get_isoelectric_point():'
    assert pep3.get_isoelectric_point() == 3.29
