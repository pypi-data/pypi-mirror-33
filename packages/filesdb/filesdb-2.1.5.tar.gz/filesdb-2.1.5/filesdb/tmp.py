


@pytest.mark.skipIf(not os.path.exists('old_style.db'), msg='test database not found')
def test_back_compat():
    assert len(filesdb.search({}, wd='.', db='old_style.db')) == 1
    with pytest.raises(sqlite3.IntegrityError):
        filesdb.add({'test': 1, 'test2': '2'}, wd='.', db='old_style.db')
    filesdb.add({'test': 2, 'test2': '2'}, wd='.', db='old_style.db')
