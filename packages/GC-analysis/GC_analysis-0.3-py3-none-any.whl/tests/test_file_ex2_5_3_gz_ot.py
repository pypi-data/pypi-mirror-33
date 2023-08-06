"""
Test_1
"""

import filecmp
import subprocess


def test_1():
    """Test_1"""
    subprocess.run(["python3", "./scripts/GC_analysis.py",
                    "-i", "./tests/ex2.fasta",
                    "-o", "./tests/ex2_5_3_gz_ot_test",
                    "-w", "5",
                    "-s", "3",
                    "-f", "gzip",
                    "-ot"])
    subprocess.run(["gzip", "-d", "-f", "./tests/ex2_5_3_gz_ot_test.wig.gz"])
    assert filecmp.cmp("./tests/ex2_5_3_gz_ot_test.wig", "./tests/ex2_5_3_ot.wig")


if __name__ == "__main__":
    test_1()
