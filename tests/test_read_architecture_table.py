from databasers_utils import read_architecture_table


def test_read_architecture_table():
    # br_ibge_pib.uf
    arch1 = read_architecture_table(
        "https://docs.google.com/spreadsheets/d/12F5NzhOYlN_bi9flLBEdXDWpa5iVakSP4EKm9UoyWuo/edit?usp=drive_link"
    )
    arch2 = read_architecture_table(
        "https://docs.google.com/spreadsheets/d/12F5NzhOYlN_bi9flLBEdXDWpa5iVakSP4EKm9UoyWuo/edit#gid=0"
    )

    assert arch1.shape == arch2.shape
