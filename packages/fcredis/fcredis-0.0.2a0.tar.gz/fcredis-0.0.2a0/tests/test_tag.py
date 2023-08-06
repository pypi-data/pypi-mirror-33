from fcredis import tag


def test_user_info_enum():
    assert tag.UserInfoEnum.USER_ID.name == "USER_ID"
    assert tag.UserInfoEnum.USER_ID.lower() == "user_id"
